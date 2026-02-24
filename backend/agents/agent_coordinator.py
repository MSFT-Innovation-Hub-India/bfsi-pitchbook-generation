"""
Coordinator Agent - Azure AI Foundry

This agent manages the complete pitchbook creation process by routing tasks to specialized agents
and ensuring every slide is complete, consistent, and aligned with the template structure.

Multi-Turn Conversation: Uses explicit thread management to maintain conversation
context across the entire pitchbook creation workflow.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from agent_framework import ChatAgent, HostedFileSearchTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.models import FileInfo, VectorStore

# Load environment variables
load_dotenv('../../.env')

PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")


async def create_coordinator_agent(credential, template_vector_store_id: str = None):
    """
    Factory function to create a Coordinator Agent instance.
    
    Args:
        credential: Azure credential for authentication
        template_vector_store_id: Optional vector store ID for template.txt
    
    Returns:
        Configured ChatAgent instance
    """
    file_search_tool = None
    if template_vector_store_id:
        file_search_tool = HostedFileSearchTool(
            vector_store_ids=[template_vector_store_id]
        )
    
    agent = ChatAgent(
        chat_client=AzureAIAgentClient(
            credential=credential,
            project_endpoint=PROJECT_ENDPOINT
        ),
        name="CoordinatorAgent",
        instructions=(
            "You are the Coordinator Agent.\n\n"
            "Your role is to manage the complete pitchbook creation process by routing tasks to the correct "
            "specialized agents and ensuring every slide is complete, consistent, and aligned with the template structure.\n\n"
            "------------------------------------------------------------\n"
            "GLOBAL RESPONSIBILITIES\n"
            "------------------------------------------------------------\n"
            "1. Understand the full pitchbook structure from template.txt.\n"
            "2. Decide which agent should be invoked for each slide.\n"
            "3. Track completeness of every slide and section.\n"
            "4. Supply appropriate context to each agent:\n"
            "   • Names of companies\n"
            "   • Required peer groups\n"
            "   • Section of the template being filled\n"
            "5. Re-run agents if the Slide Validator indicates missing items.\n"
            "6. Assemble all validated sections into a clean final pitchbook.\n\n"
            "------------------------------------------------------------\n"
            "COMPANY GROUPS FOR THIS PROJECT\n"
            "------------------------------------------------------------\n\n"
            "Primary Companies:\n"
            "• Vodafone Idea (IDEA)\n"
            "• Apollo Microsystems (APOLLO)\n\n"
            "Vodafone Idea — Peer Comparison Universe:\n"
            "• BHARTIARTL\n"
            "• INDUSTOWER\n"
            "• TATACOMM\n"
            "• RAILTEL\n"
            "• TTML\n\n"
            "Apollo Microsystems — Peer Comparison Universe:\n"
            "• PREMIERENE\n"
            "• KAYNES\n"
            "• SYRMA\n"
            "• VIKRAMSOLR\n"
            "• AVALON\n\n"
            "You must ALWAYS supply these peer lists to the Peer Comparison Agent and the Valuation Agent "
            "whenever a valuation or comparison section is being prepared.\n\n"
            "------------------------------------------------------------\n"
            "WHEN TO CALL EACH AGENT\n"
            "------------------------------------------------------------\n\n"
            "1. Financial Documents Agent\n"
            "   Use when the section requires data from quarterly reports or concall transcripts.\n"
            "   Sections:\n"
            "   • Company Overview\n"
            "   • Growth Drivers\n"
            "   • Risks\n"
            "   • Opportunities\n"
            "   • Management commentary\n\n"
            "2. Peer Comparison Agent\n"
            "   Use when the section requires multi-company comparison.\n"
            "   Sections:\n"
            "   • All peer comparison tables\n"
            "   • Raw valuation metrics\n"
            "   • Growth metrics\n"
            "   • Efficiency metrics\n"
            "   • Any multi-company dataset input for valuation\n\n"
            "3. Valuation Agent\n"
            "   Use only after the Peer Comparison Agent returns raw data.\n"
            "   Sections:\n"
            "   • Peer valuation tables (4 per company)\n"
            "   • Relative valuation\n"
            "   • Historical valuation\n"
            "   • Comparative ranking\n"
            "   • Valuation completeness check\n\n"
            "4. Slide Validation Agent\n"
            "   Use after each section is drafted.\n"
            "   Sections:\n"
            "   • ALL slides must pass validation before they are accepted.\n\n"
            "5. Slide Builder Agent\n"
            "   Use only when:\n"
            "   • A section is complete\n"
            "   • No missing values\n"
            "   • Template alignment confirmed\n\n"
            "------------------------------------------------------------\n"
            "STRICT COORDINATION RULE\n"
            "------------------------------------------------------------\n"
            "Never assume data. Never generate numbers. Only direct agents to do work according to template.txt.\n\n"
            "You are responsible for ensuring:\n"
            "• Every section is complete\n"
            "• Every section uses the correct agent\n"
            "• Every peer set is correct\n"
            "• All valuation variants are included\n"
            "• No slide proceeds without validation approval"
        ),
        model=MODEL_DEPLOYMENT,
        tools=file_search_tool if file_search_tool else None
    )
    
    await agent.__aenter__()
    return agent


async def main():
    """Interactive demo with Coordinator Agent."""
    
    print("\n" + "="*70)
    print("🎯 Azure AI Agent - Pitchbook Coordinator Agent")
    print("="*70)
    
    # Initialize client
    client = AzureAIAgentClient(credential=DefaultAzureCredential(), project_endpoint=PROJECT_ENDPOINT)
    template_file: FileInfo | None = None
    vector_store: VectorStore | None = None
    
    try:
        # Upload template.txt file
        print("\n📤 Uploading template.txt for pitchbook structure reference...")
        base_path = Path(__file__).parent
        template_path = base_path / "template.txt"
        
        if template_path.exists():
            template_file = await client.agents_client.files.upload_and_poll(
                file_path=str(template_path), 
                purpose="assistants"
            )
            print(f"✅ Template uploaded: {template_file.id}")
            
            # Create vector store with template file
            print("🗄️ Creating vector store for template...")
            vector_store = await client.agents_client.vector_stores.create_and_poll(
                file_ids=[template_file.id], 
                name="pitchbook_template_vectorstore"
            )
            print(f"✅ Vector store created: {vector_store.id}")
        else:
            print("⚠️  template.txt not found in Pitchbook folder")
            print("   Coordinator will proceed without file search tool")
        
        # Create file search tool if template was uploaded
        file_search_tool = None
        if vector_store:
            file_search_tool = HostedFileSearchTool(
                vector_store_ids=[vector_store.id]
            )
    
        async with (
            DefaultAzureCredential() as credential,
            ChatAgent(
                chat_client=AzureAIAgentClient(
                    credential=credential,
                    project_endpoint=PROJECT_ENDPOINT
                ),
                name="CoordinatorAgent",
                instructions=(
                    "You are the Coordinator Agent.\n\n"
                    "Your role is to manage the complete pitchbook creation process by routing tasks to the correct "
                    "specialized agents and ensuring every slide is complete, consistent, and aligned with the template structure.\n\n"
                    "------------------------------------------------------------\n"
                    "GLOBAL RESPONSIBILITIES\n"
                    "------------------------------------------------------------\n"
                    "1. Understand the full pitchbook structure from template.txt.\n"
                "2. Decide which agent should be invoked for each slide.\n"
                "3. Track completeness of every slide and section.\n"
                "4. Supply appropriate context to each agent:\n"
                "   • Names of companies\n"
                "   • Required peer groups\n"
                "   • Section of the template being filled\n"
                "5. Re-run agents if the Slide Validator indicates missing items.\n"
                "6. Assemble all validated sections into a clean final pitchbook.\n\n"
                "------------------------------------------------------------\n"
                "COMPANY GROUPS FOR THIS PROJECT\n"
                "------------------------------------------------------------\n\n"
                "Primary Companies:\n"
                "• Vodafone Idea (IDEA)\n"
                "• Apollo Microsystems (APOLLO)\n\n"
                "Vodafone Idea — Peer Comparison Universe:\n"
                "• BHARTIARTL\n"
                "• INDUSTOWER\n"
                "• TATACOMM\n"
                "• RAILTEL\n"
                "• TTML\n\n"
                "Apollo Microsystems — Peer Comparison Universe:\n"
                "• PREMIERENE\n"
                "• KAYNES\n"
                "• SYRMA\n"
                "• VIKRAMSOLR\n"
                "• AVALON\n\n"
                "You must ALWAYS supply these peer lists to the Peer Comparison Agent and the Valuation Agent "
                "whenever a valuation or comparison section is being prepared.\n\n"
                "------------------------------------------------------------\n"
                "WHEN TO CALL EACH AGENT\n"
                "------------------------------------------------------------\n\n"
                "1. Financial Documents Agent\n"
                "   Use when the section requires data from quarterly reports or concall transcripts.\n"
                "   Sections:\n"
                "   • Company Overview\n"
                "   • Growth Drivers\n"
                "   • Risks\n"
                "   • Opportunities\n"
                "   • Management commentary\n\n"
                "2. Peer Comparison Agent\n"
                "   Use when the section requires multi-company comparison.\n"
                "   Sections:\n"
                "   • All peer comparison tables\n"
                "   • Raw valuation metrics\n"
                "   • Growth metrics\n"
                "   • Efficiency metrics\n"
                "   • Any multi-company dataset input for valuation\n\n"
                "3. Valuation Agent\n"
                "   Use only after the Peer Comparison Agent returns raw data.\n"
                "   Sections:\n"
                "   • Peer valuation tables (4 per company)\n"
                "   • Relative valuation\n"
                "   • Historical valuation\n"
                "   • Comparative ranking\n"
                "   • Valuation completeness check\n\n"
                "4. Slide Validation Agent\n"
                "   Use after each section is drafted.\n"
                "   Sections:\n"
                "   • ALL slides must pass validation before they are accepted.\n\n"
                "5. Slide Builder Agent\n"
                "   Use only when:\n"
                "   • A section is complete\n"
                "   • No missing values\n"
                "   • Template alignment confirmed\n\n"
                "------------------------------------------------------------\n"
                "STRICT COORDINATION RULE\n"
                "------------------------------------------------------------\n"
                "Never assume data. Never generate numbers. Only direct agents to do work according to template.txt.\n\n"
                "You are responsible for ensuring:\n"
                "• Every section is complete\n"
                "• Every section uses the correct agent\n"
                "• Every peer set is correct\n"
                "• All valuation variants are included\n"
                "• No slide proceeds without validation approval"
                ),
                model=MODEL_DEPLOYMENT,
                tools=file_search_tool if file_search_tool else None
            ) as coordinator_agent
        ):
            print("✅ Coordinator Agent created successfully!")
            
            # Create thread for conversation
            thread = coordinator_agent.get_new_thread()
            
            print("\n" + "="*70)
            print("💬 Pitchbook Coordination Chat (Type 'quit' to exit)")
            print("💡 Manage the complete pitchbook creation workflow!")
            print("="*70 + "\n")
            
            # Example usage
            print("Primary Companies:")
            print("  - Vodafone Idea (IDEA) with 5 peers")
            print("  - Apollo Microsystems (APOLLO) with 5 peers\n")
            
            print("Example commands:")
            print("  - Show me the pitchbook template structure")
            print("  - Start pitchbook creation for Vodafone Idea")
            print("  - Generate company overview section")
            print("  - Create valuation comparison for Apollo Microsystems")
            print("  - Validate all sections for completeness\n")
            
            while True:
                # Get user input
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Get response from agent
                print("Agent: ", end="", flush=True)
                async for chunk in coordinator_agent.run_stream(user_input, thread=thread):
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                print("\n")
        
        # Close agent
        await coordinator_agent.__aexit__(None, None, None)
        
        # Cleanup resources
        print("\n🧹 Cleaning up resources...")
        if vector_store:
            await client.agents_client.vector_stores.delete(vector_store.id)
            print("✅ Vector store deleted")
        if template_file:
            await client.agents_client.files.delete(template_file.id)
            print("✅ Template file deleted")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Final cleanup
        try:
            if vector_store:
                await client.agents_client.vector_stores.delete(vector_store.id)
            if template_file:
                await client.agents_client.files.delete(template_file.id)
        except Exception:
            pass
        finally:
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())

