"""
FastAPI Backend for Pitchbook Investment Analysis
=================================================
REST API + SSE real-time streaming for group chat agent progress
"""

import asyncio
import json
import uuid
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from typing import Optional, AsyncIterator
import sys
import os

# Add current directory to path FIRST for imports
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables BEFORE any other imports
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')  # Load from backend directory

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import the group chat orchestration
from simple_groupchat import main as run_groupchat, BASE_DIR

# Import Cosmos DB service
try:
    from services.cosmos_service import get_cosmos_service
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False
    print("⚠️ Cosmos DB service not available - workflows will not be persisted")

app = FastAPI(title="Pitchbook Investment Analysis API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
analysis_sessions = {}
event_queues = defaultdict(asyncio.Queue)


class ProgressEmitter:
    """Helper class to emit progress events to SSE stream"""
    
    def __init__(self, analysis_id: str):
        self.id = analysis_id
        self.queue = event_queues[analysis_id]
        self.events = []
    
    async def emit(self, event_type: str, agent: str, message: str, data: dict = None):
        """Emit progress event to SSE stream"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "agent": agent,
            "message": message,
            "data": data or {}
        }
        self.events.append(event)
        await self.queue.put(event)
        # Note: Don't print here to avoid infinite loop with captured_print


class GroupChatMiddleware:
    """Middleware to capture group chat messages and stream via SSE"""
    
    def __init__(self, progress: ProgressEmitter):
        self.progress = progress
        self.current_section = None
        self.message_count = 0
    
    def parse_message_content(self, agent_name: str, raw_message: str) -> dict:
        """Helper function to parse and format agent messages - handles malformed JSON"""
        import re
        import json
        
        clean_message = raw_message.strip()
        result = {
            "display_name": "",
            "formatted_message": "",
            "event_type": "agent_message",
            "metadata": {}
        }
        
        # Map to formal display names (matching frontend)
        display_name_map = {
            "FinancialDocumentsAgent": "Financial Analyst",
            "PeerComparisonAgent": "Peer Comparison Analyst",
            "ValuationAgent": "Valuation Analyst",
            "NewsSentimentAgent": "Market Insights Analyst",
            "InvestmentThesisAgent": "Investment Thesis Analyst",
            "Validator": "Quality Validator",
            "Coordinator": "Workflow Orchestrator",
            "Orchestrator": "Workflow Orchestrator"
        }
        result["display_name"] = display_name_map.get(agent_name, agent_name)
        
        # ===== VALIDATOR PARSING =====
        if agent_name == "Validator":
            section_match = re.search(r'SECTION:\s*(\d+)\s*[-:]\s*([^\n]+)', clean_message, re.IGNORECASE)
            agent_match = re.search(r'AGENT:\s*([^\n,]+)', clean_message, re.IGNORECASE)
            request_match = re.search(r'REQUEST:\s*(.+?)(?:\n|$)', clean_message, re.DOTALL | re.IGNORECASE)
            
            if section_match or agent_match:
                parts = []
                
                if section_match:
                    section_num = section_match.group(1)
                    section_title = section_match.group(2).strip()
                    self.current_section = f"Section {section_num}"
                    parts.append(f"📋 Section {section_num}: {section_title}")
                
                if agent_match:
                    target_agent = agent_match.group(1).strip()
                    clean_target = target_agent.replace("Agent", "").strip()
                    parts.append(f"🎯 Assigned to: {clean_target}")
                
                if request_match:
                    request_text = request_match.group(1).strip()
                    request_summary = request_text[:80] + "..." if len(request_text) > 80 else request_text
                    parts.append(f"📝 Task: {request_summary}")
                
                result["event_type"] = "validator"
                result["formatted_message"] = "\n".join(parts)
                result["metadata"] = {"section": self.current_section}
                return result
        
        # ===== ORCHESTRATOR/COORDINATOR PARSING =====
        if agent_name == "Coordinator":
            if '{' in clean_message and ('selected' in clean_message.lower() or 'participant' in clean_message.lower()):
                participant = ""
                instruction = ""
                finish = False
                
                # Method 1: Try standard JSON parse
                try:
                    data = json.loads(clean_message)
                    participant = data.get("selected_participant", "")
                    instruction = data.get("instruction", "")
                    finish = data.get("finish", False)
                except json.JSONDecodeError:
                    # Method 2: Fix malformed JSON with spaces in keys
                    try:
                        fixed = clean_message
                        fixed = re.sub(r'"\s*selected\s*_?\s*part\s*icipant\s*"', '"selected_participant"', fixed, flags=re.IGNORECASE)
                        fixed = re.sub(r'"\s*instruction\s*"', '"instruction"', fixed, flags=re.IGNORECASE)
                        fixed = re.sub(r'"\s*finish\s*"', '"finish"', fixed, flags=re.IGNORECASE)
                        
                        data = json.loads(fixed)
                        participant = data.get("selected_participant", "")
                        instruction = data.get("instruction", "")
                        finish = data.get("finish", False)
                    except:
                        # Method 3: Regex extraction fallback
                        participant_match = re.search(r'(?:selected[_\s]*participant|participant)["\s:]+["\']?([^"\'",}]+)', clean_message, re.IGNORECASE)
                        instruction_match = re.search(r'instruction["\s:]+["\']?([^"\'"}]+)', clean_message, re.IGNORECASE)
                        finish_match = re.search(r'finish["\s:]+\s*(true|false)', clean_message, re.IGNORECASE)
                        
                        if participant_match:
                            participant = participant_match.group(1).strip()
                        if instruction_match:
                            instruction = instruction_match.group(1).strip()
                        if finish_match:
                            finish = finish_match.group(1).lower() == 'true'
                
                # Format the output
                if finish:
                    result["event_type"] = "orchestrator"
                    result["formatted_message"] = "✅ Round Complete"
                    return result
                
                if not participant and not instruction:
                    result["formatted_message"] = None
                    return result
                
                # Clean participant name
                participant_clean = participant \
                    .replace("FinancialDocumentsAgent", "Financial Research Analyst") \
                    .replace("Financial Documents Agent", "Financial Research Analyst") \
                    .replace("PeerComparisonAgent", "Competitive Intelligence Specialist") \
                    .replace("Peer Comparison Agent", "Competitive Intelligence Specialist") \
                    .replace("ValuationAgent", "Valuation Specialist") \
                    .replace("Valuation Agent", "Valuation Specialist") \
                    .replace("NewsSentimentAgent", "Market Insights Analyst") \
                    .replace("News Sentiment Agent", "Market Insights Analyst") \
                    .replace("InvestmentThesisAgent", "Investment Thesis Analyst") \
                    .replace("Validator", "Quality Validator") \
                    .replace("Agent", "").strip()
                
                instruction_display = instruction[:100] + "..." if len(instruction) > 100 else instruction
                
                result["event_type"] = "orchestrator"
                parts = []
                if participant_clean:
                    parts.append(f"🎯 Agent Selected: {participant_clean}")
                if instruction_display:
                    parts.append(f"📋 Instruction: {instruction_display}")
                
                result["formatted_message"] = "\n".join(parts) if parts else None
                # Send BOTH the cleaned participant AND original selected_participant
                result["metadata"] = {
                    "participant": participant_clean, 
                    "selected_participant": participant,  # Original name from orchestrator
                    "instruction": instruction,
                    "finish": finish
                }
                return result
        
        # ===== AGENT RESPONSE WITH JSON BLOCK =====
        json_match = re.search(r'```json\s*\n?([\s\S]*?)\n?```', clean_message)
        if json_match:
            try:
                json_content = json_match.group(1).strip()
                data = json.loads(json_content)
                
                section_title = data.get("section_title", data.get("title", "Data"))
                item_count = 0
                
                for key in ["slides", "companies", "key_metrics", "quarterly_results", "peer_comparison"]:
                    if key in data:
                        items = data[key]
                        if isinstance(items, (list, dict)):
                            item_count = len(items)
                            break
                
                result["event_type"] = "agent_complete"
                result["formatted_message"] = f"✅ Completed: {section_title}"
                if item_count > 0:
                    result["formatted_message"] += f" ({item_count} items)"
                result["metadata"] = {"section": self.current_section, "item_count": item_count}
                return result
            except:
                pass
        
        # ===== FALLBACK: TRUNCATE LONG MESSAGES =====
        max_length = 120
        if len(clean_message) > max_length:
            result["formatted_message"] = clean_message[:max_length] + "..."
        else:
            result["formatted_message"] = clean_message
        
        result["metadata"] = {"section": self.current_section}
        return result
    
    async def on_agent_message(self, agent_name: str, message: str, workflow_id: str = None):
        """Called when agent sends a message - uses parser helper to format"""
        self.message_count += 1
        
        # Skip empty messages
        if not message or not message.strip():
            return
        
        # Parse and format the message
        parsed = self.parse_message_content(agent_name, message)
        
        # Skip if parser says to ignore
        if parsed["formatted_message"] is None:
            return
        
        # Save to Cosmos DB if workflow exists
        if workflow_id and COSMOS_AVAILABLE:
            try:
                cosmos_service = get_cosmos_service()
                if cosmos_service:
                    cosmos_service.add_message(workflow_id, {
                        "type": parsed["event_type"],
                        "agent": parsed["display_name"],
                        "message": parsed["formatted_message"],
                        "data": parsed["metadata"]
                    })
            except Exception as e:
                print(f"⚠️ Could not save message to Cosmos DB: {e}")
        
        # Emit the formatted message
        await self.progress.emit(
            parsed["event_type"],
            parsed["display_name"],
            parsed["formatted_message"],
            parsed["metadata"]
        )
    
    async def on_section_complete(self, section_num: int, section_title: str):
        """Called when a section is completed"""
        await self.progress.emit(
            "section_complete",
            "System",
            f"✅ Section {section_num} completed: {section_title}",
            {"section": section_num, "title": section_title}
        )


async def run_analysis_with_streaming(analysis_id: str):
    """Run the group chat and stream progress via SSE"""
    progress = ProgressEmitter(analysis_id)
    middleware = GroupChatMiddleware(progress)
    
    # Cosmos DB workflow persistence
    workflow_id = None
    cosmos_service = get_cosmos_service() if COSMOS_AVAILABLE else None
    
    try:
        # Initialize
        await progress.emit("info", "System", "🚀 Starting Pitchbook Investment Analysis")
        await progress.emit("info", "System", "📋 Initializing 8-section analysis workflow")
        await asyncio.sleep(0.5)
        
        # Create workflow in Cosmos DB
        if cosmos_service:
            try:
                workflow_doc = cosmos_service.create_workflow({
                    "company": "Vodafone Idea & Apollo Micro Systems",
                    "analysisId": analysis_id
                })
                workflow_id = workflow_doc['id']
                print(f"💾 Workflow created in Cosmos DB: {workflow_id}")
            except Exception as e:
                print(f"⚠️ Could not create workflow in Cosmos DB: {e}")
        
        # Phase 1: Setup
        await progress.emit("phase", "System", "🔄 PHASE 1: Agent Setup & Document Loading")
        await asyncio.sleep(0.3)
        
        await progress.emit("step", "System", "📄 Loading PDF documents...")
        await progress.emit("info", "System", "  • vodafone_quaterly_reports.pdf")
        await progress.emit("info", "System", "  • vodafone_concall_transcript.pdf")
        await progress.emit("info", "System", "  • ams_quaterly_reports.pdf")
        await progress.emit("info", "System", "  • ams_concall_transcript.pdf")
        await asyncio.sleep(0.5)
        
        await progress.emit("step", "System", "🤖 Creating specialist agents...")
        await progress.emit("agent_created", "FinancialDocumentsAgent", "📊 Financial Documents Agent initialized")
        await asyncio.sleep(0.2)
        await progress.emit("agent_created", "PeerComparisonAgent", "💰 Peer Comparison Agent initialized")
        await asyncio.sleep(0.2)
        await progress.emit("agent_created", "NewsSentimentAgent", "📰 News Sentiment Agent initialized")
        await asyncio.sleep(0.2)
        await progress.emit("agent_created", "ValuationAgent", "📈 Valuation Agent initialized")
        await asyncio.sleep(0.2)
        await progress.emit("agent_created", "Orchestrator", "🎯 Orchestrator Agent initialized")
        await asyncio.sleep(0.2)
        await progress.emit("agent_created", "Validator", "✅ Validator Agent initialized")
        await asyncio.sleep(0.5)
        
        # Phase 2: Group Chat
        await progress.emit("phase", "System", "🤖 PHASE 2: Multi-Agent Group Chat (8 Sections)")
        await progress.emit("step", "System", "🔄 Starting round-robin discussion...")
        await asyncio.sleep(0.5)
        
        # Temporarily replace print - observe messages WITHOUT interfering
        import builtins
        original_print = builtins.print
        
        # State tracking for agent messages
        current_speaking_agent = None
        message_buffer = []
        
        def captured_print(*args, **kwargs):
            """Capture and observe print statements WITHOUT modifying them"""
            nonlocal current_speaking_agent, message_buffer
            
            # ALWAYS call original print first to preserve Azure's internal behavior
            original_print(*args, **kwargs)
            
            message = " ".join(str(arg) for arg in args)
            
            # Skip noise patterns
            noise_patterns = [
                "Rate Limiter", "Throttling", "Authorizing", "Agent Cooldown",
                "💾", "✅ Uploaded", "Creating vector store", "Vector store:", "====", "----"
            ]
            if any(pattern in message for pattern in noise_patterns):
                return
            
            # Detect agent headers: [groupchat_agent:AgentName]
            if message.strip().startswith("[groupchat_agent:"):
                # Flush previous agent's complete message
                if current_speaking_agent and message_buffer:
                    combined = "\n".join(message_buffer).strip()
                    if combined and len(combined) > 20:
                        asyncio.create_task(middleware.on_agent_message(current_speaking_agent, combined, workflow_id))
                    message_buffer = []
                
                # Extract new agent name
                import re
                agent_match = re.search(r'\[groupchat_agent:(\w+)\]', message)
                if agent_match:
                    current_speaking_agent = agent_match.group(1)
            
            # Buffer content for current agent
            elif current_speaking_agent and message.strip():
                if not message.strip().startswith("[groupchat_agent:"):
                    message_buffer.append(message)
        
        builtins.print = captured_print
        
        try:
            # Run the actual group chat with message observation
            await progress.emit("agent_running", "GroupChat", "⏳ Executing multi-agent orchestration...")
            
            # Save initial system message to workflow
            if workflow_id and cosmos_service:
                try:
                    cosmos_service.add_message(workflow_id, {
                        "type": "system",
                        "agent": "GroupChat",
                        "message": "Executing multi-agent orchestration...",
                        "data": {}
                    })
                except Exception as e:
                    print(f"⚠️ Could not save initial message: {e}")
            
            # Just run the groupchat normally
            await run_groupchat()
            
            # Flush any remaining buffered messages
            if current_speaking_agent and message_buffer:
                combined = "\n".join(message_buffer).strip()
                if combined and len(combined) > 20:
                    await middleware.on_agent_message(current_speaking_agent, combined, workflow_id)
            
            await progress.emit("agent_completed", "GroupChat", f"✅ Group chat completed")
            
        finally:
            # Restore original print
            builtins.print = original_print
        
        # Phase 3: Output
        await progress.emit("phase", "System", "📄 PHASE 3: Report Generation")
        await asyncio.sleep(0.5)
        
        output_file = BASE_DIR / "frontend" / "public" / "pitchbook_final_output.txt"
        if output_file.exists():
            file_size = output_file.stat().st_size / 1024  # KB
            await progress.emit("agent_completed", "System", f"✅ Report saved: {output_file.name} ({file_size:.1f} KB)")
        
        # Data file
        data_file = BASE_DIR / "pitchbook_data.json"
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            sections_completed = data.get("metadata", {}).get("sections_completed", 0)
            await progress.emit("info", "System", f"📊 Sections completed: {sections_completed}/8")
        
        # Final completion
        await progress.emit("complete", "System", "🎉 Pitchbook Analysis Complete!", {
            "status": "success",
            "messages": middleware.message_count,
            "output_file": "pitchbook_final_output.txt",
            "data_file": "pitchbook_data.json"
        })
        
        # Add completion message to workflow before marking as completed
        if workflow_id and cosmos_service:
            try:
                # Add final completion message
                cosmos_service.add_message(workflow_id, {
                    "type": "complete",
                    "agent": "System",
                    "message": "Workflow completed successfully!",
                    "data": {
                        "status": "success",
                        "messages": middleware.message_count
                    }
                })
                
                # Update workflow status
                cosmos_service.update_workflow_status(workflow_id, "completed")
                print(f"✅ Workflow marked as completed in Cosmos DB: {workflow_id}")
            except Exception as e:
                print(f"⚠️ Could not update workflow status: {e}")
        
        # Update session
        analysis_sessions[analysis_id]["status"] = "completed"
        analysis_sessions[analysis_id]["completed_at"] = datetime.now().isoformat()
        analysis_sessions[analysis_id]["workflow_id"] = workflow_id
        
    except Exception as e:
        await progress.emit("error", "System", f"❌ Error: {str(e)}")
        
        # Add error message to workflow before marking as failed
        if workflow_id and cosmos_service:
            try:
                # Add error message
                cosmos_service.add_message(workflow_id, {
                    "type": "error",
                    "agent": "System",
                    "message": f"Workflow failed: {str(e)}",
                    "data": {
                        "status": "failed",
                        "error": str(e)
                    }
                })
                
                # Update workflow status to failed
                cosmos_service.update_workflow_status(workflow_id, "failed")
                print(f"❌ Workflow marked as failed in Cosmos DB: {workflow_id}")
            except Exception as db_error:
                print(f"⚠️ Could not update failed workflow status: {db_error}")
        
        analysis_sessions[analysis_id]["status"] = "failed"
        analysis_sessions[analysis_id]["error"] = str(e)
        analysis_sessions[analysis_id]["workflow_id"] = workflow_id
        import traceback
        traceback.print_exc()
    
    finally:
        # Signal stream end
        await progress.queue.put(None)


# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API root - health check"""
    return {
        "service": "Pitchbook Investment Analysis API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "start_analysis": "POST /api/analyze",
            "stream_progress": "GET /api/stream/{analysis_id}",
            "get_status": "GET /api/status/{analysis_id}",
            "get_output": "GET /api/output",
            "get_data": "GET /api/data",
            "docs": "GET /docs"
        }
    }


@app.post("/api/analyze")
async def trigger_analysis(background_tasks: BackgroundTasks):
    """
    Trigger new Pitchbook investment analysis
    
    Returns analysis_id for tracking progress via SSE stream
    """
    analysis_id = str(uuid.uuid4())[:8]
    
    analysis_sessions[analysis_id] = {
        "id": analysis_id,
        "status": "running",
        "started_at": datetime.now().isoformat()
    }
    
    # Start analysis in background
    background_tasks.add_task(run_analysis_with_streaming, analysis_id)
    
    return {
        "analysis_id": analysis_id,
        "status": "started",
        "stream_url": f"/api/stream/{analysis_id}",
        "message": "Analysis started. Connect to stream_url for real-time updates."
    }


@app.get("/api/stream/{analysis_id}")
async def stream_progress(analysis_id: str):
    """
    Stream real-time progress events via Server-Sent Events (SSE)
    
    Event types:
    - info: General information
    - phase: New phase started
    - step: Step in current phase
    - section_start: Section started
    - section_complete: Section completed
    - agent_created: Agent initialized
    - agent_running: Agent executing
    - agent_completed: Agent finished
    - agent_message: Agent sent message in group chat
    - orchestrator_message: Orchestrator message
    - validator_message: Validator message
    - complete: Analysis finished
    - error: Error occurred
    """
    
    async def event_generator() -> AsyncIterator[str]:
        queue = event_queues[analysis_id]
        
        try:
            while True:
                # Wait for next event
                event = await queue.get()
                
                # None signals end of stream
                if event is None:
                    yield f"data: {json.dumps({'type': 'end', 'message': 'Stream closed'})}\n\n"
                    break
                
                # Send event to client
                yield f"data: {json.dumps(event)}\n\n"
                await asyncio.sleep(0.01)
        
        except asyncio.CancelledError:
            print(f"Stream cancelled for analysis {analysis_id}")
        
        finally:
            # Cleanup
            if analysis_id in event_queues:
                del event_queues[analysis_id]
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"
        }
    )


# Backward compatibility endpoint
@app.get("/api/agents/stream/{analysis_id}")
async def stream_progress_legacy(analysis_id: str):
    """Legacy SSE endpoint - redirects to /api/stream/{analysis_id}"""
    return await stream_progress(analysis_id)


@app.get("/api/status/{analysis_id}")
async def get_status(analysis_id: str):
    """Get current status of analysis"""
    session = analysis_sessions.get(analysis_id)
    if not session:
        return {"error": "Analysis not found", "analysis_id": analysis_id}
    
    return session


@app.get("/api/sessions")
async def list_sessions():
    """List all analysis sessions"""
    return {
        "sessions": list(analysis_sessions.values()),
        "total": len(analysis_sessions)
    }


@app.delete("/api/sessions/{analysis_id}")
async def delete_session(analysis_id: str):
    """Delete analysis session"""
    if analysis_id in analysis_sessions:
        del analysis_sessions[analysis_id]
        if analysis_id in event_queues:
            del event_queues[analysis_id]
        return {"message": "Session deleted", "analysis_id": analysis_id}
    return {"error": "Session not found"}


@app.get("/api/output")
async def get_output():
    """Get the generated pitchbook output file"""
    output_file = BASE_DIR / "frontend" / "public" / "pitchbook_final_output.txt"
    if output_file.exists():
        return FileResponse(str(output_file), media_type="text/plain", filename="pitchbook_final_output.txt")
    return {"error": "Output file not found"}


@app.get("/api/data")
async def get_data():
    """Get the collected data JSON"""
    data_file = BASE_DIR / "pitchbook_data.json"
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    return {"error": "Data file not found"}


# ============================================================================
# COSMOS DB ENDPOINTS - Workflow Persistence
# ============================================================================

@app.post("/api/workflows")
async def create_workflow(workflow_data: dict):
    """Create a new workflow in Cosmos DB"""
    if not COSMOS_AVAILABLE:
        return {"error": "Cosmos DB not configured", "success": False}
    
    cosmos_service = get_cosmos_service()
    if not cosmos_service:
        return {"error": "Cosmos DB not available", "success": False}
    
    try:
        workflow = cosmos_service.create_workflow(workflow_data)
        return {
            "success": True,
            "workflowId": workflow['id'],
            "workflow": workflow
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@app.get("/api/workflows")
async def get_all_workflows():
    """Get all workflows from Cosmos DB"""
    if not COSMOS_AVAILABLE:
        return {"error": "Cosmos DB not configured", "workflows": []}
    
    cosmos_service = get_cosmos_service()
    if not cosmos_service:
        return {"error": "Cosmos DB not available", "workflows": []}
    
    try:
        workflows = cosmos_service.get_all_workflows()
        return {"success": True, "workflows": workflows}
    except Exception as e:
        return {"error": str(e), "workflows": []}


@app.get("/api/workflows/completed")
async def get_completed_workflows():
    """Get only completed workflows"""
    if not COSMOS_AVAILABLE:
        return {"error": "Cosmos DB not configured", "workflows": []}
    
    cosmos_service = get_cosmos_service()
    if not cosmos_service:
        return {"error": "Cosmos DB not available", "workflows": []}
    
    try:
        workflows = cosmos_service.get_completed_workflows()
        return {"success": True, "workflows": workflows}
    except Exception as e:
        return {"error": str(e), "workflows": []}


@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get specific workflow by ID"""
    if not COSMOS_AVAILABLE:
        return {"error": "Cosmos DB not configured", "success": False}
    
    cosmos_service = get_cosmos_service()
    if not cosmos_service:
        return {"error": "Cosmos DB not available", "success": False}
    
    try:
        workflow = cosmos_service.get_workflow(workflow_id)
        return {"success": True, "workflow": workflow}
    except Exception as e:
        return {"error": str(e), "success": False}


@app.post("/api/workflows/{workflow_id}/messages")
async def add_workflow_message(workflow_id: str, message: dict):
    """Add message to workflow"""
    if not COSMOS_AVAILABLE:
        return {"error": "Cosmos DB not configured", "success": False}
    
    cosmos_service = get_cosmos_service()
    if not cosmos_service:
        return {"error": "Cosmos DB not available", "success": False}
    
    try:
        workflow = cosmos_service.add_message(workflow_id, message)
        return {"success": True, "workflow": workflow}
    except Exception as e:
        return {"error": str(e), "success": False}


@app.patch("/api/workflows/{workflow_id}/status")
async def update_workflow_status(workflow_id: str, status_data: dict):
    """Update workflow status"""
    if not COSMOS_AVAILABLE:
        return {"error": "Cosmos DB not configured", "success": False}
    
    cosmos_service = get_cosmos_service()
    if not cosmos_service:
        return {"error": "Cosmos DB not available", "success": False}
    
    try:
        status = status_data.get('status', 'completed')
        workflow = cosmos_service.update_workflow_status(workflow_id, status)
        return {"success": True, "workflow": workflow}
    except Exception as e:
        return {"error": str(e), "success": False}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Pitchbook Investment Analysis API",
        "version": "1.0.0",
        "active_sessions": len(analysis_sessions),
        "base_dir": str(BASE_DIR),
        "cosmos_db": "available" if COSMOS_AVAILABLE and get_cosmos_service() else "unavailable"
    }


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("🚀 PITCHBOOK INVESTMENT ANALYSIS API")
    print("=" * 80)
    print("📡 Starting FastAPI server with SSE support...")
    print("🌐 API Docs: http://localhost:8000/docs")
    print("🌐 Frontend: http://localhost:8000/")
    print("🌐 Stream: POST /api/analyze → GET /api/stream/{id}")
    print("=" * 80)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
