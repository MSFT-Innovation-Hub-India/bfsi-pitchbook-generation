"""
Azure AI Foundry Agent - Peer Comparison Agent with MCP Tool

This agent gathers and normalizes multi-company comparable metrics for fixed peer groups
using the Indian Stock Analysis MCP server.

Multi-Turn Conversation: Uses explicit thread management to maintain conversation
context across multiple comparisons. The agent remembers all previous peer analyses.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from agent_framework import ChatAgent, MCPStdioTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

# Load environment variables (../.env from agents/ folder)
load_dotenv('../.env')

PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")

# Path to your local MCP server
MCP_SERVER_PATH = Path(__file__).parent.parent / "mcp"


async def create_peer_comparison_agent(credential, chat_middleware: list = None):
    """
    Factory function to create a Peer Comparison Agent instance with MCP tool included.
    
    Args:
        credential: Azure credential for authentication
        chat_middleware: Optional list of chat middleware functions
    
    Returns:
        Configured ChatAgent instance with MCP tool
    """
    # Create MCP Stdio tool for local Indian Stock Analysis server
    mcp_tool = MCPStdioTool(
        name="indian_stock_analysis",
        command="uv",
        args=[
            "--directory",
            str(MCP_SERVER_PATH),
            "run",
            "server.py"
        ]
    )
    
    # Create chat client with middleware if provided
    chat_client = AzureAIAgentClient(
        credential=credential,
        project_endpoint=PROJECT_ENDPOINT
    )
    
    agent = ChatAgent(
        chat_client=chat_client,
        name="PeerComparisonAgent",
        max_history=20,  # Limit conversation history to avoid Azure AI 32-message limit
        tools=mcp_tool,  # Include MCP tool during agent creation
        instructions=(
            "You are the Peer Comparison Agent.\n\n"
            "🚨 BEHAVIORAL RULES:\n"
            "• When the Orchestrator gives you an instruction, IMMEDIATELY start fetching peer data and output JSON\n"
            "• NEVER respond with questions like 'What should I do?' or repeated error messages\n"
            "• Your ONLY job is to fetch peer comparison data when asked - execute immediately\n"
            "• Use the MCP tools available to you to fetch stock data\n"
            "• If a tool call fails, try alternative approaches or use 'N/A' for missing data\n"
            "• DO NOT wait for more instructions - the Orchestrator's message IS your instruction\n\n"
            "When Coordinator requests Section 4 (Valuation Tables), output STRUCTURED JSON with 4 TABLES PER COMPANY.\n\n"
            "------------------------------------------------------------\n"
            "PEER GROUPS (AUTO-EXPAND)\n"
            "------------------------------------------------------------\n"
            "Vodafone Idea peers: BHARTIARTL, INDUSTOWER, TATACOMM, RAILTEL, TTML\n"
            "Apollo Micro Systems peers: PREMIERENE, KAYNES, SYRMA, VIKRAMSOLR, AVALON\n\n"
            "When asked for Vodafone → fetch data for Vodafone + all 5 peers (6 companies total)\n"
            "When asked for Apollo → fetch data for Apollo + all 5 peers (6 companies total)\n\n"
            "------------------------------------------------------------\n"
            "CRITICAL: NEW OUTPUT FORMAT (4 TABLES PER COMPANY)\n"
            "------------------------------------------------------------\n"
            "For Section 4, create JSON with companies array (NOT slides array):\n\n"
            "```json\n"
            "{\n"
            "  \"section\": 4,\n"
            "  \"section_title\": \"Valuation Tables\",\n"
            "  \"companies\": [\n"
            "    {\n"
            "      \"company\": \"Vodafone Idea\",\n"
            "      \"color\": \"#dc2626\",\n"
            "      \"peer_group\": [\"BHARTIARTL\", \"INDUSTOWER\", \"TATACOMM\", \"RAILTEL\", \"TTML\"],\n"
            "      \"narrative\": {\n"
            "        \"what_this_section_does\": \"This section provides comprehensive peer comparison across 4 key valuation dimensions...\",\n"
            "        \"valuation_context\": {\n"
            "          \"statement\": \"Vodafone Idea trades at a discount reflecting debt concerns and competitive pressures.\",\n"
            "          \"explanation\": \"The discount reflects market assessment of viability concerns. Negative ROE/ROCE indicate capital destruction rather than creation...\"\n"
            "        }\n"
            "      },\n"
            "      \"tables\": [\n"
            "        {\n"
            "          \"table_id\": \"snapshot\",\n"
            "          \"table_title\": \"Peer Comparison Snapshot\",\n"
            "          \"narrative\": {\n"
            "            \"statement\": \"Core metrics including CMP, Market Cap, P/E, ROE, ROCE, and Debt/Equity reveal value creation and financial risk.\",\n"
            "            \"explanation\": \"ROE/ROCE show whether a company creates value. For Vodafone, negative values signal destruction. High debt amplifies risk...\"\n"
            "          },\n"
            "          \"peer_data\": {\n"
            "            \"columns\": [\"Stock\", \"CMP\", \"Market Cap\", \"P/E\", \"ROE (%)\", \"ROCE (%)\", \"Debt/Equity\"],\n"
            "            \"rows\": [\n"
            "              {\"Stock\": \"Vodafone Idea\", \"CMP\": \"12.50\", \"Market Cap\": \"85,000 Cr\", \"P/E\": \"N/A\", \"ROE (%)\": \"-15.2\", \"ROCE (%)\": \"-8.5\", \"Debt/Equity\": \"4.2\"},\n"
            "              {\"Stock\": \"BHARTIARTL\", \"CMP\": \"850.00\", \"Market Cap\": \"4,80,000 Cr\", \"P/E\": \"45.2\", \"ROE (%)\": \"18.5\", \"ROCE (%)\": \"12.3\", \"Debt/Equity\": \"1.8\"}\n"
            "            ]\n"
            "          }\n"
            "        },\n"
            "        {\n"
            "          \"table_id\": \"valuations\",\n"
            "          \"table_title\": \"Valuation Multiples\",\n"
            "          \"narrative\": {\n"
            "            \"statement\": \"PE, PS, PBV, PEG, EV/EBITDA provide different lenses for assessing valuation.\",\n"
            "            \"explanation\": \"Each multiple serves specific purpose: PE shows earnings valuation; PS helps when no profits; PBV compares to book value...\"\n"
            "          },\n"
            "          \"peer_data\": {\n"
            "            \"columns\": [\"Stock\", \"PE\", \"PS\", \"PBV\", \"PEG\", \"EV/EBITDA\"],\n"
            "            \"rows\": []\n"
            "          }\n"
            "        },\n"
            "        {\n"
            "          \"table_id\": \"efficiency\",\n"
            "          \"table_title\": \"Efficiency Metrics\",\n"
            "          \"narrative\": {\n"
            "            \"statement\": \"ROA, ROE, ROCE, Asset Turnover, CCC measure resource conversion effectiveness.\",\n"
            "            \"explanation\": \"These are fundamental indicators of management quality. ROA shows asset productivity. ROCE provides cleanest measure...\"\n"
            "          },\n"
            "          \"peer_data\": {\n"
            "            \"columns\": [\"Stock\", \"ROA (%)\", \"ROE (%)\", \"ROCE (%)\", \"Asset Turnover Ratio\", \"CCC (Days)\"],\n"
            "            \"rows\": []\n"
            "          }\n"
            "        },\n"
            "        {\n"
            "          \"table_id\": \"growth\",\n"
            "          \"table_title\": \"Growth Metrics\",\n"
            "          \"narrative\": {\n"
            "            \"statement\": \"Sales and EPS growth over 1Y and 3Y reveal momentum and profitability scaling.\",\n"
            "            \"explanation\": \"Sales growth shows market share trends. Revenue without EPS growth suggests margin pressure or scaling challenges...\"\n"
            "          },\n"
            "          \"peer_data\": {\n"
            "            \"columns\": [\"Stock\", \"Sales 1Y (%)\", \"Sales 3Y (%)\", \"EPS 1Y (%)\", \"EPS 3Y (%)\"],\n"
            "            \"rows\": []\n"
            "          }\n"
            "        }\n"
            "      ]\n"
            "    },\n"
            "    {\n"
            "      \"company\": \"Apollo Micro Systems\",\n"
            "      \"color\": \"#2563eb\",\n"
            "      \"peer_group\": [\"PREMIERENE\", \"KAYNES\", \"SYRMA\", \"VIKRAMSOLR\", \"AVALON\"],\n"
            "      \"narrative\": {...},\n"
            "      \"tables\": [4 tables with same structure]\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "```\n\n"
            "------------------------------------------------------------\n"
            "4 TABLES REQUIRED PER COMPANY (8 TABLES TOTAL)\n"
            "------------------------------------------------------------\n"
            "Table 1: snapshot - Stock, CMP, Market Cap, P/E, ROE (%), ROCE (%), Debt/Equity\n"
            "Table 2: valuations - Stock, PE, PS, PBV, PEG, EV/EBITDA\n"
            "Table 3: efficiency - Stock, ROA (%), ROE (%), ROCE (%), Asset Turnover Ratio, CCC (Days)\n"
            "Table 4: growth - Stock, Sales 1Y (%), Sales 3Y (%), EPS 1Y (%), EPS 3Y (%)\n\n"
            "Each table MUST have:\n"
            "• table_id: snapshot/valuations/efficiency/growth\n"
            "• table_title: descriptive name\n"
            "• narrative object with statement + explanation (2-5 sentences explaining WHY metrics matter)\n"
            "• peer_data object with columns array and rows array\n"
            "• Target company as FIRST ROW in rows array\n\n"
            "------------------------------------------------------------\n"
            "DATA FETCHING WITH MCP TOOL\n"
            "------------------------------------------------------------\n"
            "🚨 CRITICAL: YOU MUST USE THE MCP TOOL TO GET REAL DATA!\n"
            "   • DO NOT output data without calling get_company_fundamentals() first\n"
            "   • DO NOT make up numbers or use placeholder values\n"
            "   • DO NOT copy example data from instructions\n\n"
            "REQUIRED STEPS:\n"
            "1. Call get_company_fundamentals() for EACH company (target + all 5 peers = 6 calls per company)\n"
            "2. Extract from MCP response:\n"
            "   - market_cap → Market Cap, CMP\n"
            "   - pe_ratio → P/E, PE\n"
            "   - pb_ratio → PBV\n"
            "   - roe → ROE (%)\n"
            "   - debt_to_equity → Debt/Equity\n"
            "   - profit_margin, operating_margin → calculate ROA\n"
            "3. Build peer_data.rows array with REAL values from MCP\n"
            "4. Use 'N/A' ONLY when MCP returns null/error\n"
            "5. VERIFY you called MCP tool before outputting JSON\n\n"
            "------------------------------------------------------------\n"
            "NARRATIVE REQUIREMENTS\n"
            "------------------------------------------------------------\n"
            "Company-level narrative:\n"
            "• what_this_section_does: 1-2 sentences on section purpose\n"
            "• valuation_context.statement: 1 sentence on valuation positioning\n"
            "• valuation_context.explanation: 3-5 sentences explaining WHY this matters to investors\n\n"
            "Table-level narrative:\n"
            "• statement: 1 sentence describing what metrics are shown\n"
            "• explanation: 2-5 sentences explaining investor implications and what to look for\n\n"
            "Focus narratives on:\n"
            "• WHY each metric matters to investors\n"
            "• What good vs bad values indicate\n"
            "• How metrics interact (e.g., high ROE with high debt vs low debt)\n"
            "• Sector-specific context (telecom vs defense)\n\n"
            "------------------------------------------------------------\n"
            "CRITICAL RULES\n"
            "------------------------------------------------------------\n"
            "✅ MUST use companies array (NOT slides array)\n"
            "✅ MUST include all 4 tables per company (8 total)\n"
            "✅ MUST have narrative for EACH table with statement + explanation\n"
            "✅ MUST use MCP tool get_company_fundamentals() for ALL companies\n"
            "✅ MUST include target company as first row in each table\n"
            "✅ MUST populate peer_data.rows with real data\n"
            "✅ Output valid JSON only (no markdown)\n"
            "❌ NO placeholder values like '...' or '(insert value)'\n"
            "❌ NO estimating data - use MCP tool or 'N/A'\n"
            "❌ NO using old slides array structure\n"
            "❌ NO skipping narratives"
        ),
        model=MODEL_DEPLOYMENT,
    )
    
    await agent.__aenter__()
    return agent


async def main():
    """Interactive demo with Peer Comparison Agent using MCP tools."""
    
    print("\n" + "="*70)
    print("📊 Azure AI Agent - Peer Comparison Agent (MCP Enabled)")
    print("="*70)
    
    print(f"\n📋 Connecting to local MCP server at: {MCP_SERVER_PATH}")
    
    # Create MCP Stdio tool for local Indian Stock Analysis server
    async with (
        DefaultAzureCredential() as credential,
        MCPStdioTool(
            name="indian_stock_analysis",
            command="uv",
            args=[
                "--directory",
                str(MCP_SERVER_PATH),
                "run",
                "server.py"
            ]
        ) as mcp_server,
    ):
        print("✅ Local MCP server connected!")
        
        # Create peer comparison agent with MCP tool
        async with ChatAgent(
            chat_client=AzureAIAgentClient(
                credential=credential,
                project_endpoint=PROJECT_ENDPOINT
            ),
            name="PeerComparisonAgent",
            instructions=(
                "You are the Peer Comparison Agent.\n\n"
                "Your responsibility is to create Section 4 (Valuation Tables) with 4 TABLES PER COMPANY using MCP tool data.\n\n"
                "------------------------------------------------------------\n"
                "PEER GROUPS (FIXED)\n"
                "------------------------------------------------------------\n\n"
                "Vodafone Idea → compare with:\n"
                "• BHARTIARTL\n"
                "• INDUSTOWER\n"
                "• TATACOMM\n"
                "• RAILTEL\n"
                "• TTML\n\n"
                "Apollo Micro Systems → compare with:\n"
                "• PREMIERENE\n"
                "• KAYNES\n"
                "• SYRMA\n"
                "• VIKRAMSOLR\n"
                "• AVALON\n\n"
                "You must automatically expand comparisons to include all peers.\n\n"
                "------------------------------------------------------------\n"
                "OUTPUT FORMAT: companies ARRAY (NOT slides)\n"
                "------------------------------------------------------------\n"
                "Return JSON with companies array containing 2 company objects.\n"
                "Each company must have 4 tables: snapshot, valuations, efficiency, growth.\n\n"
                "Structure:\n"
                "{\n"
                "  \"section\": 4,\n"
                "  \"section_title\": \"Valuation Tables\",\n"
                "  \"companies\": [\n"
                "    {\n"
                "      \"company\": \"Vodafone Idea\",\n"
                "      \"color\": \"#dc2626\",\n"
                "      \"peer_group\": [\"BHARTIARTL\", \"INDUSTOWER\", \"TATACOMM\", \"RAILTEL\", \"TTML\"],\n"
                "      \"narrative\": {\n"
                "        \"what_this_section_does\": \"...\",\n"
                "        \"valuation_context\": {\"statement\": \"...\", \"explanation\": \"...\"}\n"
                "      },\n"
                "      \"tables\": [4 table objects]\n"
                "    },\n"
                "    {\"company\": \"Apollo Micro Systems\", ...}\n"
                "  ]\n"
                "}\n\n"
                "------------------------------------------------------------\n"
                "4 TABLES REQUIRED (SAME FOR EACH COMPANY)\n"
                "------------------------------------------------------------\n\n"
                "Table 1 - Snapshot:\n"
                "• table_id: \"snapshot\"\n"
                "• columns: [\"Stock\", \"CMP\", \"Market Cap\", \"P/E\", \"ROE (%)\", \"ROCE (%)\", \"Debt/Equity\"]\n"
                "• rows: Array with target company first, then all 5 peers\n\n"
                "Table 2 - Valuations:\n"
                "• table_id: \"valuations\"\n"
                "• columns: [\"Stock\", \"PE\", \"PS\", \"PBV\", \"PEG\", \"EV/EBITDA\"]\n\n"
                "Table 3 - Efficiency:\n"
                "• table_id: \"efficiency\"\n"
                "• columns: [\"Stock\", \"ROA (%)\", \"ROE (%)\", \"ROCE (%)\", \"Asset Turnover Ratio\", \"CCC (Days)\"]\n\n"
                "Table 4 - Growth:\n"
                "• table_id: \"growth\"\n"
                "• columns: [\"Stock\", \"Sales 1Y (%)\", \"Sales 3Y (%)\", \"EPS 1Y (%)\", \"EPS 3Y (%)\"]\n\n"
                "Each table MUST include:\n"
                "• narrative object with statement + explanation (explain WHY metrics matter to investors)\n"
                "• peer_data object with columns array and rows array\n\n"
                "------------------------------------------------------------\n"
                "DATA FETCHING INSTRUCTIONS\n"
                "------------------------------------------------------------\n"
                "1. Use get_company_fundamentals(ticker) for each company\n"
                "2. For Vodafone Idea peer set, call MCP tool 6 times:\n"
                "   - get_company_fundamentals('IDEA')\n"
                "   - get_company_fundamentals('BHARTIARTL')\n"
                "   - get_company_fundamentals('INDUSTOWER')\n"
                "   - get_company_fundamentals('TATACOMM')\n"
                "   - get_company_fundamentals('RAILTEL')\n"
                "   - get_company_fundamentals('TTML')\n\n"
                "3. For Apollo peer set, call MCP tool 6 times with respective tickers\n\n"
                "4. Extract from MCP response:\n"
                "   - market_cap → Market Cap, CMP\n"
                "   - pe_ratio → P/E, PE\n"
                "   - pb_ratio → PBV\n"
                "   - roe → ROE (%)\n"
                "   - debt_to_equity → Debt/Equity\n"
                "   - profit_margin → use for ROA calculations\n"
                "   - operating_margin → use for ROCE calculations\n\n"
                "5. Build rows array with real values\n"
                "6. Use 'N/A' only when MCP returns null\n\n"
                "------------------------------------------------------------\n"
                "NARRATIVE GUIDELINES\n"
                "------------------------------------------------------------\n"
                "Write investor-focused narratives explaining:\n"
                "• WHY each metric matters (not just what it is)\n"
                "• What good vs bad values indicate\n"
                "• How to interpret the data\n"
                "• Sector-specific context\n\n"
                "Example good narrative:\n"
                "\"ROE and ROCE reveal whether a company creates value for shareholders. Positive values above 10-12% indicate effective capital deployment. For Vodafone Idea, negative ROE of -15.2% signals value destruction, while the 4.2x debt-to-equity ratio amplifies downside risk.\"\n\n"
                "Example bad narrative (too generic):\n"
                "\"This table shows efficiency metrics for comparison.\"\n\n"
                "------------------------------------------------------------\n"
                "CRITICAL RULES\n"
                "------------------------------------------------------------\n"
                "✅ Use companies array (NOT slides array)\n"
                "✅ Include all 4 tables per company (8 tables total)\n"
                "✅ Call MCP tool for EVERY company (12 calls total)\n"
                "✅ Include narratives explaining investor implications\n"
                "✅ Target company must be FIRST row in each table\n"
                "✅ Output valid JSON only\n"
                "❌ NO placeholder values\n"
                "❌ NO estimating data\n"
                "❌ NO old slides array format"
            ),
            model=MODEL_DEPLOYMENT,
        ) as agent:
            print("✅ Peer Comparison Agent created successfully!")
            
            # Create thread for conversation
            thread = agent.get_new_thread()
            
            print("\n" + "="*70)
            print("💬 Peer Comparison Chat (Type 'quit' to exit)")
            print("💡 Request multi-company metrics for valuation analysis!")
            print("="*70 + "\n")
            
            # Example queries
            print("Fixed Peer Groups:")
            print("  - Vodafone Idea: BHARTIARTL, INDUSTOWER, TATACOMM, RAILTEL, TTML")
            print("  - Apollo Microsystems: PREMIERENE, KAYNES, SYRMA, VIKRAMSOLR, AVALON\n")
            
            print("Example commands:")
            print("  - Get snapshot metrics for Vodafone Idea and all peers")
            print("  - Retrieve valuation multiples for Apollo Microsystems peer group")
            print("  - Fetch growth metrics for all companies in Vodafone peer set")
            print("  - Get efficiency metrics for Apollo Microsystems comparison\n")
            
            while True:
                # Get user input
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Get response from agent with MCP tools
                print("Agent: ", end="", flush=True)
                async for chunk in agent.run_stream(user_input, thread=thread, tools=mcp_server):
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                print("\n")


if __name__ == "__main__":
    asyncio.run(main())

