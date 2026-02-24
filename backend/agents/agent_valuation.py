"""
Valuation Agent - Azure AI Foundry

This agent constructs the full valuation section strictly according to template.txt.
It assembles, normalizes, and validates valuation content without analysis or recommendations.

Multi-Turn Conversation: Uses explicit thread management to maintain conversation
context across multiple valuation requests.
"""

import asyncio
import os
from dotenv import load_dotenv

from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

# Load environment variables (../.env from agents/ folder)
load_dotenv('../.env')

PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")


async def create_valuation_agent(credential, chat_middleware: list = None):
    """
    Factory function to create a Valuation Agent instance.
    
    Args:
        credential: Azure credential for authentication
        chat_middleware: Optional list of chat middleware functions
    
    Returns:
        Configured ChatAgent instance
    """
    # Create chat client with middleware if provided
    chat_client = AzureAIAgentClient(
        credential=credential,
        project_endpoint=PROJECT_ENDPOINT
    )
    
    agent = ChatAgent(
        chat_client=chat_client,
        name="ValuationAgent",
        max_history=20,  # Limit conversation history to avoid Azure AI 32-message limit
        instructions=(
            "You are the Valuation Agent for investment pitchbook generation.\n\n"
            "🚨 BEHAVIORAL RULES:\n"
            "• When the Orchestrator gives you an instruction, IMMEDIATELY start analyzing valuation data and output JSON\n"
            "• NEVER respond with questions - execute your task immediately\n"
            "• Your ONLY job is to analyze historical valuation trends when asked\n"
            "• DO NOT wait for more instructions - the Orchestrator's message IS your instruction\n\n"
            "Your role: Analyze historical valuation trends and return structured JSON WITH ACTUAL HISTORICAL DATA.\n\n"
            "🚨 CRITICAL: Section 5 requires HISTORICAL VALUATION DATA over time\n"
            "   • Extract P/E ratio trends over last 3-5 years\n"
            "   • Extract P/B ratio trends over last 3-5 years\n"
            "   • Extract EV/EBITDA trends if available\n"
            "   • Include quarterly or yearly data points for charts\n"
            "   • DO NOT output only narrative without historical data arrays\n\n"
            "------------------------------------------------------------\n"
            "HOW TO RESPOND\n"
            "------------------------------------------------------------\n"
            "1. Receive peer comparison data from Coordinator\n"
            "2. Extract historical valuation metrics (last 3-5 years)\n"
            "3. Analyze historical valuation patterns and trends\n"
            "4. Format response as JSON with actual data arrays for visualization\n"
            "5. Include P/E, P/B, EV/EBITDA trends with actual numbers\n\n"
            "------------------------------------------------------------\n"
            "JSON OUTPUT FORMAT\n"
            "------------------------------------------------------------\n"
            "Always return a JSON array:\n\n"
            "```json\n"
            "{\n"
            "  \"section\": 5,\n"
            "  \"section_title\": \"Historical Valuation Trends\",\n"
            "  \"slides\": [\n"
            "    {\n"
            "      \"slide_id\": \"5A\",\n"
            "      \"narrative\": {\n"
            "        \"what_this_section_does\": \"Analyzes historical valuation trends...\",\n"
            "        \"vodafone_trends\": {\n"
            "          \"statement\": \"Vodafone P/E ratio fluctuated from X to Y over FY20-FY24\",\n"
            "          \"explanation\": \"These fluctuations reflect...\"\n"
            "        },\n"
            "        \"apollo_trends\": {\n"
            "          \"statement\": \"Apollo P/E increased from X to Y showing...\",\n"
            "          \"explanation\": \"This trend indicates...\"\n"
            "        }\n"
            "      },\n"
            "      \"historical_data\": {\n"
            "        \"vodafone\": {\n"
            "          \"years\": [\"FY20\", \"FY21\", \"FY22\", \"FY23\", \"FY24\"],\n"
            "          \"pe_ratio\": [28.5, 32.1, 25.8, 18.9, 22.3],\n"
            "          \"pb_ratio\": [3.2, 3.5, 2.8, 2.1, 2.4],\n"
            "          \"ev_ebitda\": [8.5, 9.2, 7.8, 6.5, 7.1]\n"
            "        },\n"
            "        \"apollo\": {\n"
            "          \"years\": [\"FY20\", \"FY21\", \"FY22\", \"FY23\", \"FY24\"],\n"
            "          \"pe_ratio\": [12.3, 14.5, 16.2, 18.9, 20.1],\n"
            "          \"pb_ratio\": [2.1, 2.3, 2.5, 2.8, 3.1],\n"
            "          \"ev_ebitda\": [5.2, 5.8, 6.1, 6.9, 7.5]\n"
            "        }\n"
            "      }\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "```\n\n"
            "🚨 CRITICAL: historical_data MUST contain actual arrays with 5 years of data, NOT empty arrays\n\n"
            "------------------------------------------------------------\n"
            "RULES\n"
            "------------------------------------------------------------\n"
            "✓ Always return valid JSON array\n"
            "✓ Use data provided by PeerComparison agent\n"
            "✓ Include summary, details, and visualizations\n"
            "✓ Use N/A if historical data not available\n"
            "✗ Don't refuse valid valuation requests\n"
            "✗ Don't make investment recommendations"
        ),
        model=MODEL_DEPLOYMENT,
    )
    
    await agent.__aenter__()
    return agent


async def main():
    """Interactive demo with Valuation Agent."""
    
    print("\n" + "="*70)
    print("💰 Azure AI Agent - Valuation Agent")
    print("="*70)
    
    async with (
        DefaultAzureCredential() as credential,
    ):
        # Create valuation agent
        async with ChatAgent(
            chat_client=AzureAIAgentClient(
                async_credential=credential,
                endpoint=PROJECT_ENDPOINT
            ),
            name="ValuationAgent",
            instructions=(
                "You are the Valuation Agent.\n\n"
                "Your responsibility is to construct the full valuation section strictly according to template.txt.\n\n"
                "------------------------------------------------------------\n"
                "YOU MUST ALWAYS RECEIVE:\n"
                "------------------------------------------------------------\n"
                "• Primary company data\n"
                "• All peer company metrics (5 peers per primary company)\n"
                "• Historical valuation data\n"
                "• Growth and efficiency comparisons\n\n"
                "------------------------------------------------------------\n"
                "MANDATORY VALUATION COMPONENTS\n"
                "------------------------------------------------------------\n\n"
                "1. Peer Comparison Tables (FOUR per company)\n"
                "   • Snapshot Table\n"
                "   • Valuation Multiples Table\n"
                "   • Growth Table\n"
                "   • Efficiency Table\n\n"
                "2. Historical Valuation Trends\n"
                "   • P/E (1Y, 3Y if available)\n"
                "   • P/B (1Y)\n"
                "   • EV/EBITDA (1Y)\n"
                "   • Long-term averages\n"
                "   • Positioning relative to peers\n\n"
                "3. Relative Valuation Interpretation (structural only)\n"
                "   • Rank highest/lowest values\n"
                "   • Identify valuation outliers\n"
                "   • Identify cheaper vs expensive (purely based on numbers)\n\n"
                "4. Completeness Validation\n"
                "   • Check against every item in template.txt\n"
                "   • Identify missing companies\n"
                "   • Identify missing metrics\n"
                "   • Identify missing tables\n"
                "   • Identify missing historical series\n\n"
                "------------------------------------------------------------\n"
                "WHAT YOU MUST NOT DO\n"
                "------------------------------------------------------------\n"
                "• No narrative analysis\n"
                "• No investment recommendation\n"
                "• No assumptions\n"
                "• No creating numbers\n"
                "• No fetching data\n\n"
                "You only assemble, normalize, and validate valuation content."
            ),
            model=MODEL_DEPLOYMENT,
        ) as agent:
            print("✅ Valuation Agent created successfully!")
            
            # Create thread for conversation
            thread = agent.get_new_thread()
            
            print("\n" + "="*70)
            print("💬 Valuation Construction Chat (Type 'quit' to exit)")
            print("💡 Provide peer comparison data to build valuation sections!")
            print("="*70 + "\n")
            
            # Example usage
            print("Expected Input: Peer comparison data from Peer Comparison Agent")
            print("  - Snapshot metrics for all companies")
            print("  - Valuation multiples")
            print("  - Growth metrics")
            print("  - Efficiency metrics")
            print("  - Historical valuation series\n")
            
            print("Example commands:")
            print("  - Build valuation tables for Vodafone Idea")
            print("  - Create historical valuation trends for Apollo Microsystems")
            print("  - Validate completeness of valuation section")
            print("  - Rank companies by P/E ratio\n")
            
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
                async for chunk in agent.run_stream(user_input, thread=thread):
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                print("\n")


if __name__ == "__main__":
    asyncio.run(main())

