# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import cast, Callable, Awaitable
from datetime import datetime

from agent_framework import (
    AgentRunUpdateEvent,
    ChatAgent,
    ChatMessage,
    GroupChatBuilder,
    HostedFileSearchTool,
    HostedCodeInterpreterTool,
    MCPStdioTool,
    Role,
    WorkflowOutputEvent,
)
from agent_framework import ChatContext
from agent_framework.azure import AzureOpenAIChatClient, AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from azure.identity import DefaultAzureCredential  # Sync version for AzureOpenAIChatClient

# Import agent factory functions
from agents.agent_financial_documents import create_financial_documents_agent
from agents.agent_valuation import create_valuation_agent
from agents.peer_comparision_mcp_agent import create_peer_comparison_agent
from agents.agent_news_Sentiment import create_news_sentiment_agent

# Load environment variables from backend/.env file
load_dotenv(Path(__file__).parent / '.env')

PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")  # Load from .env
OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o-mini")  # Load from .env

# Model Configuration
class ModelConfig:
    """Model configuration - stays on gpt-4o-mini to preserve conversation history"""
    MODEL = OPENAI_DEPLOYMENT  # Stay on same model for conversation continuity
    ENDPOINT = OPENAI_ENDPOINT  # Use endpoint from .env (gtartifacts-openai)
    # Using Azure credential authentication instead of API key for better security

# Global Rate Limiter
class GlobalRateLimiter:
    """Enterprise-grade rate limiter to prevent Azure token exhaustion."""
    def __init__(self):
        self.last_call_time = 0
        self.min_delay = 20  # Reduced: Minimum delay between API calls (20 seconds)
        self.call_count = 0
        self.lock = asyncio.Lock()
        self._start_time = None
    
    async def wait_if_needed(self, agent_name: str = "Unknown"):
        """Enforce rate limiting with intelligent wait times."""
        async with self.lock:
            if self._start_time is None:
                self._start_time = asyncio.get_event_loop().time()
            
            now = asyncio.get_event_loop().time()
            time_since_last = now - self.last_call_time
            
            if time_since_last < self.min_delay:
                wait_time = self.min_delay - time_since_last
                print(f"\n🚨 [Rate Limiter] Throttling {agent_name}: waiting {int(wait_time)}s (call #{self.call_count + 1})")
                print(f"   ⏱️  This delay prevents Azure rate limit errors and ensures stability.")
                await asyncio.sleep(wait_time)
            
            self.call_count += 1
            self.last_call_time = asyncio.get_event_loop().time()
            elapsed = int(self.last_call_time - self._start_time)
            print(f"✅ [Rate Limiter] Authorizing {agent_name} (call #{self.call_count}, elapsed: {elapsed}s)")

global_rate_limiter = GlobalRateLimiter()

# Paths
BASE_DIR = Path(__file__).parent
PDF_FILES = [
    "../../ams_concall_transcript.pdf",
    "../../ams_quaterly_reports.pdf",
    "../../vodafone_concall_transcript.pdf",
    "../../vodafone_quaterly_reports.pdf"
]

# MCP Server Path
MCP_SERVER_PATH = BASE_DIR / "mcp"

"""
Pitchbook Group Chat - Complete Multi-Agent Workflow

Uses hybrid approach to avoid rate limits:
- AzureOpenAIChatClient for orchestration agents (no rate limits)
- AzureAIAgentClient only for FinancialDocs agent (file search support)
- Factory functions from individual agent files
- Instructions loaded from .txt files
- All 14 slides processed step-by-step
"""


def _get_chat_client() -> AzureOpenAIChatClient:
    """Create chat client with gpt-4o-mini using Azure credential authentication"""
    print(f"[DEBUG] _get_chat_client called")
    print(f"  Endpoint: {ModelConfig.ENDPOINT}")
    print(f"  Deployment: {ModelConfig.MODEL}")
    print(f"  Using: DefaultAzureCredential (Entra ID authentication)")
    
    # Force token-based authentication by setting environment variable
    # This tells the Azure OpenAI SDK to use Entra ID tokens, not API keys
    os.environ["AZURE_OPENAI_AD_TOKEN"] = "use_credential"
    os.environ.pop("AZURE_OPENAI_API_KEY", None)  # Remove any API key from environment
    
    client = AzureOpenAIChatClient(
        endpoint=ModelConfig.ENDPOINT,
        deployment_name=ModelConfig.MODEL,
        credential=DefaultAzureCredential(),  # Uses Entra ID (Azure AD) authentication
        api_version="2024-10-21"  # Use latest API version with better Entra ID support
    )
    
    # Verify no API key is being used
    print(f"  Client created: {type(client).__name__}")
    print(f"  Environment AZURE_OPENAI_API_KEY removed: {'AZURE_OPENAI_API_KEY' not in os.environ}")
    
    return client


def extract_highlights(text: str, agent_id: str) -> dict:
    """Parse JSON response from agent and extract highlights."""
    import re
    import json
    
    # Try to extract JSON from response
    try:
        # Look for JSON array in response
        json_match = re.search(r'```json\s*(\[.*?\])\s*```', text, re.DOTALL)
        if json_match:
            slides_data = json.loads(json_match.group(1))
        else:
            # Try to parse the entire response as JSON
            slides_data = json.loads(text)
        
        # Extract summary from first slide as highlights
        if isinstance(slides_data, list) and len(slides_data) > 0:
            return slides_data[0].get('summary', {})
        elif isinstance(slides_data, dict):
            return slides_data.get('summary', {})
    except (json.JSONDecodeError, AttributeError):
        # Fallback: extract basic highlights from text
        highlights = {}
        if "FinancialDocumentsAgent" in agent_id:
            revenue_match = re.search(r'Revenue:\s*[₹INR\s]*([\d,\.]+)\s*(million|billion|crores?|B|M)?', text, re.IGNORECASE)
            if revenue_match:
                highlights["revenue"] = f"₹{revenue_match.group(1)} {revenue_match.group(2) or 'M'}"
        elif "NewsSentimentAgent" in agent_id:
            articles_match = re.search(r'ARTICLES ANALYZED:\s*(\d+)', text)
            if articles_match:
                highlights["articles_analyzed"] = articles_match.group(1)
        elif "PeerComparisonAgent" in agent_id:
            highlights["status"] = "Comparison data available"
    
    return highlights


# PDF generation moved to separate file: pitchbook_pdf_agent.py
# The orchestration now only collects data into JSON format


async def rate_limit_middleware(
    context: ChatContext,
    next: Callable[[ChatContext], Awaitable[None]],
) -> None:
    """Professional chat middleware with enterprise-grade rate limiting."""
    
    # Identify agent from context
    agent_name = "Unknown"
    if hasattr(context, 'messages') and context.messages:
        for msg in context.messages[-2:]:
            msg_str = str(msg)
            if "FinancialDocuments" in msg_str:
                agent_name = "FinancialDocuments"
                break
            elif "PeerComparison" in msg_str:
                agent_name = "PeerComparison"
                break
            elif "NewsSentiment" in msg_str:
                agent_name = "NewsSentiment"
                break
            elif "Valuation" in msg_str:
                agent_name = "Valuation"
                break
    
    # Apply global rate limiting
    await global_rate_limiter.wait_if_needed(agent_name)
    
    # Extended cooldown for document-intensive agents
    if agent_name == "FinancialDocuments":
        print(f"📄 [Agent Cooldown] {agent_name}: additional 60s delay for PDF document processing")
        await asyncio.sleep(60)
    elif agent_name == "PeerComparison":
        print(f"📊 [Agent Cooldown] {agent_name}: additional 45s delay for MCP tool operations")
        await asyncio.sleep(45)
    elif agent_name == "NewsSentiment":
        print(f"📰 [Agent Cooldown] {agent_name}: additional 30s delay for web scraping operations")
        await asyncio.sleep(30)
    
    # Retry logic with exponential backoff
    max_retries = 7
    base_delay = 20
    
    for attempt in range(max_retries):
        try:
            await next(context)
            if attempt > 0:
                print(f"[Retry Success] {agent_name} succeeded on attempt {attempt + 1}")
            return
        except Exception as e:
            error_msg = str(e)
            is_rate_limit = "rate limit" in error_msg.lower() or "exceeded" in error_msg.lower()
            is_cancel_error = "cannot cancel run" in error_msg.lower()
            
            # Handle cancellation errors gracefully
            if is_cancel_error:
                print(f"[Info] {agent_name}: Thread state conflict, retrying...")
                if attempt < max_retries - 1:
                    await asyncio.sleep(10)
                    continue
                else:
                    raise
            
            # Handle rate limit errors
            if is_rate_limit:
                import re
                match = re.search(r'retry after (\d+) seconds', error_msg, re.IGNORECASE)
                if match:
                    actual_wait = int(match.group(1)) + 10
                else:
                    actual_wait = min(base_delay * (2 ** attempt), 300)
                
                if attempt < max_retries - 1:
                    print(f"\n[Rate Limit] {agent_name} throttled (attempt {attempt + 1}/{max_retries})")
                    print(f"[Backoff] Waiting {actual_wait}s before retry...")
                    await asyncio.sleep(actual_wait)
                else:
                    print(f"\n[Error] {agent_name} exhausted all {max_retries} retry attempts")
                    print(f"[Recommendation] Increase rate limits or upgrade Azure AI Services tier")
                    raise
            else:
                # Non-recoverable error
                print(f"[Error] {agent_name}: {str(e)[:150]}")
                raise


async def main() -> None:
    print("\n" + "="*80)
    print("🏢 PITCHBOOK GENERATION - ALL SLIDES")
    print("="*80)
    
    # DEBUG: Print environment configuration
    print("\n[DEBUG] Environment Configuration:")
    print(f"  PROJECT_ENDPOINT: {PROJECT_ENDPOINT}")
    print(f"  OPENAI_ENDPOINT: {OPENAI_ENDPOINT}")
    print(f"  OPENAI_DEPLOYMENT: {OPENAI_DEPLOYMENT}")
    
    # Get AzureOpenAIChatClient for orchestration agents (no rate limits)
    chat_client = _get_chat_client()
    
    # Initialize AzureAIAgentClient ONLY for file uploads and FinancialDocs
    # Using AsyncDefaultAzureCredential for deployment flexibility (works with Managed Identity, CLI, etc.)
    print("\n[DEBUG] Creating AsyncDefaultAzureCredential...")
    credential = AsyncDefaultAzureCredential()
    await credential.__aenter__()
    
    print(f"[DEBUG] Creating AzureAIAgentClient with endpoint: {PROJECT_ENDPOINT}")
    upload_client = AzureAIAgentClient(
        credential=credential,
        project_endpoint=PROJECT_ENDPOINT
    )
    
    # Upload PDF files using AzureAIAgentClient
    print("\n📤 Uploading PDF files...")
    pdf_file_ids = []
    for pdf_path in PDF_FILES:
        pdf_full_path = BASE_DIR / pdf_path
        if pdf_full_path.exists():
            print(f"  Uploading {pdf_path}...")
            pdf_file = await upload_client.agents_client.files.upload_and_poll(
                file_path=str(pdf_full_path),
                purpose="assistants"
            )
            pdf_file_ids.append(pdf_file.id)
            print(f"  ✅ Uploaded: {pdf_file.id}")
    
    # Create vector store
    pdf_vector_store_id = None
    if pdf_file_ids:
        print(f"\n📚 Creating vector store...")
        pdf_vector_store = await upload_client.agents_client.vector_stores.create_and_poll(
            file_ids=pdf_file_ids,
            name="pitchbook_pdfs"
        )
        pdf_vector_store_id = pdf_vector_store.id
        print(f"✅ Vector store: {pdf_vector_store_id}")
    
    # Load instructions from files (section-based approach)
    print("\n📄 Loading instructions from files...")
    validator_instructions = (BASE_DIR / "instructions" / "validator_instructions_sections.txt").read_text(encoding='utf-8')
    coordinator_instructions = (BASE_DIR / "instructions" / "coordinator_instructions_sections.txt").read_text(encoding='utf-8')
    print("✅ Instructions loaded")
    
    # Create agents using factory functions
    print("\n🤖 Creating agents...")
    
    # Validator - uses loaded instructions with AzureOpenAIChatClient
    validator = ChatAgent(
        name="Validator",
        description="Generates task lists for each slide",
        instructions=validator_instructions,
        chat_client=chat_client,
    )
    print("✅ Validator agent created")
    
    # FinancialDocs - uses factory function with AzureAIAgentClient
    financial_docs = await create_financial_documents_agent(
        credential=credential,
        pdf_vector_store_id=pdf_vector_store_id,
        chat_middleware=[rate_limit_middleware]
    )
    print("✅ FinancialDocs agent created")
    
    # Valuation - uses factory function
    valuation = await create_valuation_agent(credential=credential, chat_middleware=[rate_limit_middleware])
    print("✅ Valuation agent created")
    
    # NewsSentiment - uses factory function
    news_sentiment = await create_news_sentiment_agent(credential=credential, chat_middleware=[rate_limit_middleware])
    print("✅ NewsSentiment agent created")
    
    # PeerComparison - uses factory function with MCP tool integrated
    print("\n🔧 Creating PeerComparison agent with MCP tool...")
    peer_comparison = await create_peer_comparison_agent(credential=credential, chat_middleware=[rate_limit_middleware])
    print("✅ PeerComparison agent created with MCP support")
    
    # Create Investment Thesis Agent (synthesis agent with conversation history access)
    print("\n📊 Creating Investment Thesis Agent (synthesis)...")
    thesis_agent = chat_client.create_agent(
        name="InvestmentThesisAgent",
        instructions=(
            "You are the Investment Thesis Synthesis Agent.\n\n"
            "ROLE: Review ALL conversation history from the group chat and synthesize an investment thesis for both companies.\n\n"
            "CRITICAL:\n"
            "• You have access to the ENTIRE group chat conversation history\n"
            "• Review responses from ALL previous sections (1-7)\n"
            "• Synthesize insights from: FinancialDocumentsAgent, NewsSentimentAgent, PeerComparisonAgent, ValuationAgent, Validator\n"
            "• Create actionable investment recommendations based on complete analysis\n\n"
            "WHEN CALLED FOR SECTION 8:\n"
            "1. Review conversation history for sections 1-7:\n"
            "   - Section 1: Company Snapshots (business model, key metrics)\n"
            "   - Section 2: News & Sentiment (market perception, trends)\n"
            "   - Section 3: Financial Statements (P&L, balance sheet, cash flow)\n"
            "   - Section 4: Valuation Tables (peer comparison, multiples)\n"
            "   - Section 5: Historical Valuation (trends, cycles)\n"
            "   - Section 6: SWOT Analysis (strengths, weaknesses, opportunities, threats)\n"
            "   - Section 7: Risk & Growth Drivers (downside/upside scenarios)\n\n"
            "2. Synthesize investment thesis for BOTH companies\n"
            "3. Output in analyst-grade JSON format\n\n"
            "OUTPUT FORMAT:\n"
            "{\n"
            "  \"section\": 8,\n"
            "  \"section_title\": \"Investment Thesis & Recommendations\",\n"
            "  \"slides\": [\n"
            "    {\n"
            "      \"slide_id\": \"8A\",\n"
            "      \"companies\": [\"Vodafone Idea\", \"Apollo Micro Systems\"],\n"
            "      \"narrative\": {\n"
            "        \"what_this_section_does\": \"Synthesize all analysis into actionable recommendations\",\n"
            "        \"vodafone_thesis\": {\n"
            "          \"recommendation\": \"BUY/HOLD/SELL with qualifier\",\n"
            "          \"core_thesis\": \"One-sentence investment case\",\n"
            "          \"thesis_explanation\": \"Comprehensive explanation integrating insights from sections 1-7\",\n"
            "          \"investor_suitability\": \"Who should invest and why\",\n"
            "          \"decision_logic\": \"Specific conditions for buy/hold/sell\"\n"
            "        },\n"
            "        \"apollo_thesis\": {\n"
            "          \"recommendation\": \"BUY/HOLD/SELL with qualifier\",\n"
            "          \"core_thesis\": \"One-sentence investment case\",\n"
            "          \"thesis_explanation\": \"Comprehensive explanation integrating insights from sections 1-7\",\n"
            "          \"investor_suitability\": \"Who should invest and why\",\n"
            "          \"decision_logic\": \"Specific conditions for buy/hold/sell\"\n"
            "        }\n"
            "      }\n"
            "    }\n"
            "  ]\n"
            "}\n"
        )
    )
    print("✅ InvestmentThesisAgent created")
    
    # Build workflow with coordinator/moderator
    print("\n🔨 Building workflow...")
    workflow = (
        GroupChatBuilder()
        .set_manager(
            manager=chat_client.create_agent(
                name="Coordinator",
                instructions=coordinator_instructions
            ),
            display_name="Orchestrator"
        )
        .with_termination_condition(
            lambda messages: any("PITCHBOOK COMPLETE" in str(msg) for msg in messages)
        )
        .participants([validator, financial_docs, peer_comparison, valuation, news_sentiment, thesis_agent])
        .build()
    )
    
    task = """
PITCHBOOK GENERATION - SECTION-BASED APPROACH

Generate investment pitchbook for:
1. Vodafone Idea (with peers: BHARTIARTL, INDUSTOWER, TATACOMM, RAILTEL, TTML)
2. Apollo Micro Systems (with peers: PREMIERENE, KAYNES, SYRMA, VIKRAMSOLR, AVALON)

IMPORTANT - COMPANY NAME KEYWORDS:
• For news/searches: Use "Apollo Micro Systems" (with space) NOT "Apollo Microsystems"
• For stock data: Use ticker symbols as provided

Complete 8 SECTIONS (not 14 individual slides):

SECTION 1: Company Snapshots (2 slides - one per company)
SECTION 2: News & Sentiment (2 slides - one per company)
SECTION 3: Financial Statements (2 slides - one per company)
SECTION 4: Valuation Tables (8 slides - 4 per company with peers)
SECTION 5: Historical Valuation Trends (1 slide combined)
SECTION 6: SWOT Analysis (2 slides - one per company)
SECTION 7: Risk & Growth Drivers (1 slide combined)
SECTION 8: Investment Thesis & Recommendation (1 slide combined)

WORKFLOW:
1. Coordinator asks Validator: "What is the next section?"
2. Validator provides ONE section request (simpler, not broken into tasks)
3. Coordinator calls the specified agent
4. Agent provides all data for that section
5. Repeat for all 8 sections

When all sections complete, output: "PITCHBOOK COMPLETE: [JSON]"
"""
    
    print("\n" + "="*80)
    print("PITCHBOOK GENERATION BEGINS")
    print("="*80)
    
    # Create data collection structure (in-memory only, not saved to file)
    # data_file = BASE_DIR / "pitchbook_data_collection.json"  # DISABLED
    collected_data = {
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "companies": ["Vodafone Idea", "Apollo Micro Systems"],
            "sections_completed": 0,
            "total_sections": 8
        },
        "sections": {},  # Organized by section with highlights + details
        "conversation_log": []
    }
    
    # Run with streaming
    final_conversation: list[ChatMessage] = []
    last_executor_id: str | None = None
    current_section = None
    
    # Retry logic with progressive wait times
    max_retries = 4  # Allow 4 retries with increasing wait times
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            async for event in workflow.run_stream(task):
                if isinstance(event, AgentRunUpdateEvent):
                    eid = event.executor_id
                    if eid != last_executor_id:
                        if last_executor_id is not None:
                            print()
                        print(f"\n[{eid}]")
                        last_executor_id = eid
                    
                    # Print and collect data
                    text = str(event.data)
                    print(text, end="", flush=True)
                    
                    # Save to log
                    collected_data["conversation_log"].append({
                        "agent": eid,
                        "message": text,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Extract section number from validator responses
                    if "SECTION:" in text and "Validator" in eid:
                        import re
                        match = re.search(r'SECTION:\s*(\d+)', text)
                        if match:
                            current_section = f"section_{match.group(1)}"
                            if current_section not in collected_data["sections"]:
                                collected_data["sections"][current_section] = {
                                    "section_id": match.group(1),
                                    "title": "",
                                    "agent_responses": [],
                                    "highlights": {},
                                    "details": {},
                                    "status": "in_progress"
                                }
                            # Extract title
                            title_match = re.search(r'SECTION:\s*\d+\s*-\s*(.+)', text)
                            if title_match:
                                collected_data["sections"][current_section]["title"] = title_match.group(1).strip()
                    
                    # Capture agent responses (not orchestrator/validator)
                    if eid in ["groupchat_agent:FinancialDocumentsAgent", 
                               "groupchat_agent:PeerComparisonAgent",
                               "groupchat_agent:NewsSentimentAgent",
                               "groupchat_agent:ValuationAgent"]:
                        if current_section and len(text.strip()) > 10:
                            
                            # Extract highlights and details from response
                            response_data = {
                                "agent": eid.replace("groupchat_agent:", ""),
                                "timestamp": datetime.now().isoformat(),
                                "full_response": text,
                                "highlights": extract_highlights(text, eid),
                                "details": text  # Full response for expandable view
                            }
                            
                            collected_data["sections"][current_section]["agent_responses"].append(response_data)
                            
                            # Save progressively - DISABLED
                            # with open(data_file, 'w', encoding='utf-8') as f:
                            #     json.dump(collected_data, f, indent=2, ensure_ascii=False)
                            # print(f"\n💾 [Progress saved]", end="", flush=True)
                    
                    # Mark section complete
                    if "COMPLETE" in text and current_section:
                        collected_data["sections"][current_section]["status"] = "complete"
                        collected_data["metadata"]["sections_completed"] += 1
                        # with open(data_file, 'w', encoding='utf-8') as f:
                        #     json.dump(collected_data, f, indent=2, ensure_ascii=False)
                
                elif isinstance(event, WorkflowOutputEvent):
                    final_conversation = cast(list[ChatMessage], event.data)
            
            # If we reach here successfully, break the retry loop
            break
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a rate limit error
            if "rate limit" in error_msg.lower() or "exceeded" in error_msg.lower():
                retry_count += 1
                
                # Progressive wait times: 60s, 120s, 180s, 240s
                wait_time = retry_count * 60
                
                print(f"\n\n⚠️ [Rate Limit Error] Token rate limit exceeded")
                print(f"🔄 [Retry Strategy] Progressive backoff: Retry {retry_count}/{max_retries}")
                print(f"⏳ [Wait] Waiting {wait_time}s before retry (staying on gpt-4o-mini)...")
                print(f"   💡 Reason: Conversation history needed for Investment Thesis (Section 8)\n")
                
                await asyncio.sleep(wait_time)
                
                if retry_count < max_retries:
                    print(f"🔁 [Retry {retry_count}/{max_retries}] Resuming workflow...")
                    continue
            else:
                # Non-rate-limit error, re-raise
                print(f"\n❌ [Error] Unexpected error: {error_msg}")
                raise
    
    # If max retries exceeded
    if retry_count >= max_retries:
        print(f"\n❌ [Failed] Max retries ({max_retries}) exceeded. Please try again later.")
        return
    
    # Print final conversation and save
    print("\n\n" + "="*80)
    print("WORKFLOW COMPLETED")
    print("="*80)
    
    if final_conversation:
        print("\n📋 FINAL TRANSCRIPT:")
        print("-" * 80)
        for msg in final_conversation:
            author = getattr(msg, "author_name", "Unknown")
            text = getattr(msg, "text", str(msg))
            print(f"\n[{author}]")
            print(text[:500])  # Print first 500 chars of each message
            if len(text) > 500:
                print(f"... (truncated, {len(text)} total chars)")
            print("-" * 40)
        
        # Save final output to frontend public folder - DISABLED
        # output_file = BASE_DIR / "frontend" / "public" / "pitchbook_final_output.txt"
        # with open(output_file, 'w', encoding='utf-8') as f:
        #     for msg in final_conversation:
        #         author = getattr(msg, "author_name", "Unknown")
        #         text = getattr(msg, "text", str(msg))
        #         f.write(f"\n{'='*80}\n[{author}]\n{'='*80}\n")
        #         f.write(text)
        #         f.write("\n")
        # print(f"\n💾 Complete transcript saved to: {output_file}")
    
    # Save collected data summary - DISABLED
    # print(f"\n💾 Progressive data saved to: {data_file}")
    print(f"   Sections captured: {len(collected_data['sections'])}")
    print(f"   Conversation entries: {len(collected_data['conversation_log'])}")
    
    # Print section summary
    if collected_data['sections']:
        print(f"\n📊 SECTIONS COMPLETED:")
        for section_id, section_data in collected_data['sections'].items():
            status = section_data.get('status', 'unknown')
            response_count = len(section_data.get('agent_responses', []))
            print(f"   • {section_id}: {status} ({response_count} agent responses)")
    else:
        print("\n⚠️  No sections were captured in the data collection file")
    
    # PDF generation moved to separate script (pitchbook_pdf_agent.py)
    print("\n" + "="*80)
    print("📊 DATA COLLECTION COMPLETE")
    print("="*80)
    # print(f"   JSON Data: {data_file}")  # DISABLED - file saving removed
    print(f"\n💡 To generate PDF, run: python pitchbook_pdf_agent.py")
    
    # Cleanup
    print("\n🧹 Cleaning up resources...")
    await financial_docs.__aexit__(None, None, None)
    await peer_comparison.__aexit__(None, None, None)
    await valuation.__aexit__(None, None, None)
    await news_sentiment.__aexit__(None, None, None)
    await credential.__aexit__(None, None, None)
    
    print("\n" + "="*80)
    print("✅ PITCHBOOK DATA COLLECTION COMPLETED")
    print("="*80)
    # print(f"📊 JSON Data: {data_file}")  # DISABLED - file saving removed
    print(f"\n📄 To generate PDF with visualizations:")
    print(f"   python pitchbook_pdf_agent.py")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
