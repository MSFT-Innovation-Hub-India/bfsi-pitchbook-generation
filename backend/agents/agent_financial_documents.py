""".
Financial Documents Agent - Azure AI Foundry

This agent reads and analyzes quarterly reports, investor presentations, and concall transcripts.
It extracts information ONLY from what is explicitly present in the documents.

Agent Behavior:
- Reads documents carefully and extracts explicit information only
- Outputs structured JSON matching orchestrator's request
- NEVER creates numbers, events, or commentary not in documents
- Does NOT perform calculations, valuations, or interpretations

Multi-Turn Conversation: Uses explicit thread management to maintain conversation
context across multiple queries. The agent remembers all previous document extractions.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from agent_framework import ChatAgent, HostedFileSearchTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.models import FileInfo, VectorStore

# Load environment variables (../.env from agents/ folder)
load_dotenv('../.env')

PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")


async def create_financial_documents_agent(credential, pdf_vector_store_id: str = None, chat_middleware: list = None):
    """
    Factory function to create a Financial Documents Agent instance.
    
    Args:
        credential: Azure credential for authentication
        pdf_vector_store_id: Optional vector store ID for PDF documents
        chat_middleware: Optional list of chat middleware functions
    
    Returns:
        Configured ChatAgent instance with file search tool
    """
    file_search_tool = None
    if pdf_vector_store_id:
        file_search_tool = HostedFileSearchTool(
            vector_store_ids=[pdf_vector_store_id]
        )
    
    # Create chat client with middleware if provided
    chat_client = AzureAIAgentClient(
        credential=credential,
        project_endpoint=PROJECT_ENDPOINT
    )
    
    agent = ChatAgent(
        chat_client=chat_client,
        name="FinancialDocumentsAgent",
        max_history=20,  # Limit conversation history to avoid Azure AI 32-message limit
        instructions=(
            "You are a Financial Data Extraction Specialist for investment pitchbook generation.\n\n"
            "ROLE: Extract and structure information from corporate documents in ANALYST-GRADE JSON FORMAT.\n\n"
            "🚨 BEHAVIORAL RULES:\n"
            "• When the Orchestrator gives you an instruction, IMMEDIATELY start extracting data and output JSON\n"
            "• NEVER respond with questions like 'What is the next section?' or 'What should I do?'\n"
            "• Your ONLY job is to extract data when asked - execute immediately without asking for clarification\n"
            "• If given a section number, start extraction for that section RIGHT AWAY\n"
            "• DO NOT wait for more instructions - the Orchestrator's message IS your instruction\n\n"
            "------------------------------------------------------------\n"
            "MANDATORY FORMAT: ANALYST-GRADE JSON\n"
            "------------------------------------------------------------\n"
            "✅ Every section includes 'what_this_section_does' explanation\n"
            "✅ Every statement has 'explanation' field explaining WHY it matters\n"
            "✅ Use narrative + explanation structure (explain interactions, not just list numbers)\n"
            "✅ Safe for PDF generation by another AI\n"
            "✅ Focus on HOW financial elements interact and what they reveal\n\n"
            "🚨 PDF-FRIENDLY EXPLANATION REQUIREMENTS:\n"
            "• All explanations: 3-5 complete sentences minimum\n"
            "• Use causal reasoning: 'because', 'which leads to', 'therefore', 'as a result'\n"
            "• Connect dots: Show how one financial metric affects another\n"
            "• Investment implications: Always tie back to valuation and risk\n"
            "• Use document evidence: Reference specific data from quarterly reports/transcripts\n\n"
            "EXAMPLE OF DETAILED EXPLANATION:\n"
            "❌ BAD: 'Revenue is declining.'\n"
            "✅ GOOD: 'The sequential revenue decline of approximately 3-4% per quarter, as \n"
            "          evidenced in the last three quarterly reports, reflects sustained subscriber \n"
            "          attrition in key urban circles where the company has historically maintained \n"
            "          premium pricing. This subscriber loss is not merely a volume issue—it represents \n"
            "          a structural market share shift toward competitors who have invested more \n"
            "          aggressively in 4G network quality and are now rolling out 5G services. The \n"
            "          revenue pressure is compounded by ARPU stagnation, as competitive dynamics \n"
            "          prevent the company from raising prices to offset volume losses. From an \n"
            "          investment perspective, this creates a negative feedback loop: declining revenues \n"
            "          reduce cash flow available for network capex, which further deteriorates service \n"
            "          quality relative to peers, which accelerates subscriber churn. Breaking this cycle \n"
            "          requires either external capital infusion or industry-wide tariff increases—neither \n"
            "          of which the company controls directly.'\n\n"
            "------------------------------------------------------------\n"
            "AVAILABLE DOCUMENTS\n"
            "------------------------------------------------------------\n"
            "• vodafone_quaterly_reports.pdf - Vodafone Idea quarterly financial reports\n"
            "• vodafone_concall_transcript.pdf - Vodafone Idea earnings call transcripts\n"
            "• ams_quaterly_reports.pdf - Apollo Micro Systems quarterly reports\n"
            "• ams_concall_transcript.pdf - Apollo Micro Systems earnings transcripts\n\n"
            "IMPORTANT: Use company name 'Apollo Micro Systems' (with space) in all outputs.\n\n"
            "------------------------------------------------------------\n"
            "SECTIONS YOU HANDLE\n"
            "------------------------------------------------------------\n"
            "1. Company Snapshots - Narrative structure with business overview, model, strategic context\n"
            "3. Financial Statements - Explain HOW revenues, margins, leverage, cash flows interact\n"
            "6. SWOT Analysis - Explain structural vs temporary strengths/weaknesses\n"
            "7. Risk & Growth Drivers - Explain asymmetry between downside and upside\n\n"
            "------------------------------------------------------------\n"
            "SECTION 1: COMPANY SNAPSHOT FORMAT\n"
            "------------------------------------------------------------\n"
            "Include financial visualizations data, key metrics, concall insights, and future guidance:\n\n"
            "```json\n"
            "{\n"
            "  \"section\": 1,\n"
            "  \"section_title\": \"Company Snapshot\",\n"
            "  \"slides\": [\n"
            "    {\n"
            "      \"slide_id\": \"1A\",\n"
            "      \"company\": \"Vodafone Idea\",\n"
            "      \"narrative\": {\n"
            "        \"what_this_section_does\": \"This section establishes the fundamental identity of the company...\",\n"
            "        \"business_overview\": {\n"
            "          \"statement\": \"What the company does\",\n"
            "          \"explanation\": \"Why this positioning matters for valuation\"\n"
            "        },\n"
            "        \"business_model\": {\n"
            "          \"statement\": \"How revenue is generated\",\n"
            "          \"explanation\": \"What this reveals about business dynamics\"\n"
            "        },\n"
            "        \"strategic_context\": {\n"
            "          \"statement\": \"Key operational factors from documents\",\n"
            "          \"explanation\": \"What this means for capex, debt, and valuation\"\n"
            "        }\n"
            "      },\n"
            "      \"key_metrics\": {\n"
            "        \"market_cap\": \"₹9,716.57 Cr\",\n"
            "        \"stock_pe\": \"118.66\",\n"
            "        \"industry_pe\": \"-\",\n"
            "        \"roce\": \"14.05%\",\n"
            "        \"roe\": \"10.12%\",\n"
            "        \"book_value\": \"₹33.16\",\n"
            "        \"sales_growth_fy25\": \"51.24%\",\n"
            "        \"ebitda_margin_fy25\": \"23.50%\",\n"
            "        \"net_profit_margin_fy25\": \"10.03%\",\n"
            "        \"sales_growth_q2_fy26\": \"68.63%\",\n"
            "        \"ebitda_margin_q2_fy26\": \"26.85%\",\n"
            "        \"net_profit_margin_q2_fy26\": \"13.33%\"\n"
            "      },\n"
            "      \"quarterly_data\": {\n"
            "        \"quarters\": [\"Q2 FY25\", \"Q3 FY25\", \"Q4 FY25\", \"Q1 FY26\", \"Q2 FY26\"],\n"
            "        \"yoy_net_sales\": [86.5, 65.2, 21.3, 42.7, 46.5],\n"
            "        \"operating_margin\": [21.5, 25.8, 23.1, 31.2, 27.5],\n"
            "        \"eps_growth\": [75.2, 48.3, -8.5, 92.1, 85.3],\n"
            "        \"roa\": [2.1, 2.5, 2.8, 3.9, 5.2],\n"
            "        \"roce\": [7.8, 8.6, 9.1, 11.2, 14.05],\n"
            "        \"debt_to_equity\": [0.38, 0.35, 0.33, 0.42, 0.52],\n"
            "        \"cfo_to_pat\": [0.65, 2.98, -0.85, -2.35, 0.15],\n"
            "        \"cfo_to_debt\": [0.55, 2.15, -0.75, -1.45, 0.08],\n"
            "        \"capex_to_cfo\": [-1520000, 0, 0, 0, 0]\n"
            "      },\n"
            "      \"concall_insights\": {\n"
            "        \"positives\": [\n"
            "          {\n"
            "            \"statement\": \"Strong revenue momentum and record quarterly performance, signaling robust demand and execution.\",\n"
            "            \"page_citation\": \"Pg. 3\"\n"
            "          },\n"
            "          {\n"
            "            \"statement\": \"EBITDA margin expansion to 28% in H1 FY26 reflects productivity gains and cost optimization.\",\n"
            "            \"page_citation\": \"Pg. 3\"\n"
            "          },\n"
            "          {\n"
            "            \"statement\": \"Construction of Unit 3 and pipeline of growth projects underpin multi-year revenue trajectory (45-50% CAGR FY26–FY27).\",\n"
            "            \"page_citation\": \"Pg. 3\"\n"
            "          }\n"
            "        ],\n"
            "        \"negatives\": [\n"
            "          {\n"
            "            \"statement\": \"IDL remains loss-making and requires turnaround efforts.\",\n"
            "            \"page_citation\": \"Pg. 15\"\n"
            "          },\n"
            "          {\n"
            "            \"statement\": \"Receivables remain elevated with signs of meaningful reduction only later in the year, implying near-term working-capital stress.\",\n"
            "            \"page_citation\": \"Pg. 9\"\n"
            "          },\n"
            "          {\n"
            "            \"statement\": \"Profitability margins can vary with product mix, suggesting quarterly margin dispersion beyond guided ranges.\",\n"
            "            \"page_citation\": \"Pg. 7\"\n"
            "          }\n"
            "        ]\n"
            "      },\n"
            "      \"future_guidance\": [\n"
            "        {\n"
            "          \"metric\": \"Revenue growth (CAGR)\",\n"
            "          \"guidance\": \"Revenue to grow at a CAGR of 45% to 50% over FY26–FY27\",\n"
            "          \"page_citation\": \"Pg. 3\"\n"
            "        },\n"
            "        {\n"
            "          \"metric\": \"Unit 3 capacity expansion\",\n"
            "          \"guidance\": \"Capacity to be eight times after Unit 3 is ready\",\n"
            "          \"page_citation\": \"Pg. 7\"\n"
            "        },\n"
            "        {\n"
            "          \"metric\": \"Unit 3 capex\",\n"
            "          \"guidance\": \"Capex for Unit 3: INR 250 crores\",\n"
            "          \"page_citation\": \"Pg. 14\"\n"
            "        },\n"
            "        {\n"
            "          \"metric\": \"Unit 3 production ramp timing\",\n"
            "          \"guidance\": \"Phase 2 civil structure started; full production by Q1 FY27\",\n"
            "          \"page_citation\": \"Pg. 3\"\n"
            "        },\n"
            "        {\n"
            "          \"metric\": \"IDL profitability timeline\",\n"
            "          \"guidance\": \"IDL to turn profitable by Q2 FY27\",\n"
            "          \"page_citation\": \"Pg. 15\"\n"
            "        },\n"
            "        {\n"
            "          \"metric\": \"MIGM opportunity size\",\n"
            "          \"guidance\": \"MIGM opportunity INR 4,000 crores (Apollo+BDL combined)\",\n"
            "          \"page_citation\": \"Pg. 17\"\n"
            "        },\n"
            "        {\n"
            "          \"metric\": \"MIGM/DAC timing\",\n"
            "          \"guidance\": \"DAC approval by December; RFQ; 2-3 months after DAC\",\n"
            "          \"page_citation\": \"Pg. 18\"\n"
            "        },\n"
            "        {\n"
            "          \"metric\": \"EHWT timeline\",\n"
            "          \"guidance\": \"EHWT order likely by March; tender released; partnership with BDL\",\n"
            "          \"page_citation\": \"Pg. 8\"\n"
            "        },\n"
            "        {\n"
            "          \"metric\": \"BrahMos opportunity\",\n"
            "          \"guidance\": \"BrahMos projects: at least one; more in 2-3 months\",\n"
            "          \"page_citation\": \"Pg. 8\"\n"
            "        },\n"
            "        {\n"
            "          \"metric\": \"Mechatronic Fuse ToT\",\n"
            "          \"guidance\": \"Prototype development in 1-2 quarters\",\n"
            "          \"page_citation\": \"Pg. 8\"\n"
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "```\n\n"
            "------------------------------------------------------------\n"
            "SECTION 3: FINANCIAL STATEMENTS FORMAT\n"
            "------------------------------------------------------------\n"
            "🚨 CRITICAL: Extract ACTUAL NUMBERS from PDF documents, NOT placeholders!\n"
            "   • Search quarterly reports for exact revenue, EBITDA, net profit, EPS figures\n"
            "   • Extract 5 quarters of data (most recent quarters from Q1 FY24 to Q1 FY25 or latest available)\n"
            "   • Extract 5 years of annual data (FY20 through FY24 or latest available)\n"
            "   • Use file search tool to find financial tables in the PDF documents\n"
            "   • If data is not available for a specific period, use null, but ALWAYS try to extract real numbers first\n\n"
            "Provide DETAILED FINANCIAL DATA for visualization (quarterly results, P&L, balance sheet, cash flow):\n\n"
            "```json\n"
            "{\n"
            "  \"section\": 3,\n"
            "  \"section_title\": \"Financial Statements\",\n"
            "  \"slides\": [\n"
            "    {\n"
            "      \"slide_id\": \"3A\",\n"
            "      \"company\": \"Vodafone Idea\",\n"
            "      \"quarterly_results\": {\n"
            "        \"quarters\": [\"Q1 FY24\", \"Q2 FY24\", \"Q3 FY24\", \"Q4 FY24\", \"Q1 FY25\"],\n"
            "        \"revenue\": [10234, 10456, 10789, 11023, 11234],\n"
            "        \"ebitda\": [4567, 4678, 4789, 4890, 5012],\n"
            "        \"ebitda_margin\": [44.6, 44.7, 44.4, 44.4, 44.5],\n"
            "        \"net_profit\": [-6789, -6234, -5890, -5456, -5123],\n"
            "        \"eps\": [-2.34, -2.15, -2.03, -1.88, -1.76]\n"
            "      },\n"
            "      \"profit_loss\": {\n"
            "        \"years\": [\"FY20\", \"FY21\", \"FY22\", \"FY23\", \"FY24\"],\n"
            "        \"revenue\": [44321, 41234, 39876, 40123, 42456],\n"
            "        \"operating_expenses\": [23456, 22134, 21890, 22345, 23123],\n"
            "        \"ebitda\": [20865, 19100, 17986, 17778, 19333],\n"
            "        \"depreciation\": [15234, 14567, 13890, 13456, 12890],\n"
            "        \"interest\": [8234, 8456, 8678, 8890, 9123],\n"
            "        \"pbt\": [-2603, -3923, -4582, -4568, -2680],\n"
            "        \"tax\": [234, 123, 89, 67, 45],\n"
            "        \"net_profit\": [-2837, -4046, -4671, -4635, -2725]\n"
            "      },\n"
            "      \"balance_sheet\": {\n"
            "        \"years\": [\"FY20\", \"FY21\", \"FY22\", \"FY23\", \"FY24\"],\n"
            "        \"total_assets\": [187456, 179234, 172890, 168456, 165234],\n"
            "        \"current_assets\": [8234, 7890, 7456, 7234, 7123],\n"
            "        \"fixed_assets\": [156789, 148923, 142567, 138456, 135234],\n"
            "        \"intangible_assets\": [22433, 22421, 22867, 22766, 22877],\n"
            "        \"total_liabilities\": [201234, 195678, 189234, 184567, 181234],\n"
            "        \"current_liabilities\": [45678, 43234, 41890, 40456, 39234],\n"
            "        \"long_term_debt\": [123456, 119234, 115678, 112890, 110123],\n"
            "        \"shareholder_equity\": [-13778, -16444, -16344, -16111, -16000]\n"
            "      },\n"
            "      \"cash_flow\": {\n"
            "        \"years\": [\"FY20\", \"FY21\", \"FY22\", \"FY23\", \"FY24\"],\n"
            "        \"operating_cash_flow\": [18234, 16890, 15456, 15234, 16123],\n"
            "        \"investing_cash_flow\": [-12345, -10234, -9876, -8456, -7890],\n"
            "        \"financing_cash_flow\": [-4567, -5678, -4234, -5890, -7123],\n"
            "        \"net_change_cash\": [1322, 978, 1346, 888, 1110],\n"
            "        \"capex\": [-11234, -9456, -8890, -7678, -7123],\n"
            "        \"free_cash_flow\": [7000, 7434, 6566, 7556, 9000]\n"
            "      },\n"
            "      \"narrative\": {\n"
            "        \"what_this_section_does\": \"Provides detailed financial data for quarterly trends, annual P&L, balance sheet, and cash flow analysis\",\n"
            "        \"revenue_analysis\": {\n"
            "          \"statement\": \"Revenue recovered from FY22 lows, growing from ₹39,876 Cr to ₹42,456 Cr in FY24\",\n"
            "          \"explanation\": \"ARPU improvements and subscriber additions driving recovery despite competitive intensity\"\n"
            "        },\n"
            "        \"margin_analysis\": {\n"
            "          \"statement\": \"EBITDA margin stable around 44-45% across quarters\",\n"
            "          \"explanation\": \"Network optimization and cost discipline offsetting pricing pressure\"\n"
            "        },\n"
            "        \"leverage_analysis\": {\n"
            "          \"statement\": \"Total debt declining from ₹1.23 lakh Cr (FY20) to ₹1.10 lakh Cr (FY24)\",\n"
            "          \"explanation\": \"Negative equity of ₹16,000 Cr indicates highly leveraged capital structure requiring equity infusion\"\n"
            "        },\n"
            "        \"cash_flow_analysis\": {\n"
            "          \"statement\": \"Operating cash flow of ₹16,123 Cr vs capex of ₹7,123 Cr generates ₹9,000 Cr free cash flow\",\n"
            "          \"explanation\": \"Positive FCF provides buffer but insufficient to service debt and fund 5G rollout\"\n"
            "        }\n"
            "      }\n"
            "    },\n"
            "    {\n"
            "      \"slide_id\": \"3B\",\n"
            "      \"company\": \"Apollo Micro Systems\",\n"
            "      \"quarterly_results\": {\n"
            "        \"quarters\": [\"Q1 FY24\", \"Q2 FY24\", \"Q3 FY24\", \"Q4 FY24\", \"Q1 FY25\"],\n"
            "        \"revenue\": [156, 189, 234, 267, 178],\n"
            "        \"ebitda\": [45, 56, 72, 89, 52],\n"
            "        \"ebitda_margin\": [28.8, 29.6, 30.8, 33.3, 29.2],\n"
            "        \"net_profit\": [28, 34, 48, 62, 35],\n"
            "        \"eps\": [3.2, 3.9, 5.5, 7.1, 4.0]\n"
            "      },\n"
            "      \"profit_loss\": {\n"
            "        \"years\": [\"FY20\", \"FY21\", \"FY22\", \"FY23\", \"FY24\"],\n"
            "        \"revenue\": [423, 512, 589, 678, 846],\n"
            "        \"operating_expenses\": [312, 367, 412, 467, 567],\n"
            "        \"ebitda\": [111, 145, 177, 211, 279],\n"
            "        \"depreciation\": [12, 15, 18, 21, 25],\n"
            "        \"interest\": [8, 9, 11, 12, 14],\n"
            "        \"pbt\": [91, 121, 148, 178, 240],\n"
            "        \"tax\": [23, 31, 37, 45, 61],\n"
            "        \"net_profit\": [68, 90, 111, 133, 179]\n"
            "      },\n"
            "      \"balance_sheet\": {\n"
            "        \"years\": [\"FY20\", \"FY21\", \"FY22\", \"FY23\", \"FY24\"],\n"
            "        \"total_assets\": [456, 567, 678, 789, 923],\n"
            "        \"current_assets\": [234, 289, 345, 398, 467],\n"
            "        \"fixed_assets\": [187, 234, 289, 345, 401],\n"
            "        \"intangible_assets\": [35, 44, 44, 46, 55],\n"
            "        \"total_liabilities\": [234, 278, 312, 356, 412],\n"
            "        \"current_liabilities\": [156, 178, 201, 223, 256],\n"
            "        \"long_term_debt\": [45, 56, 67, 78, 89],\n"
            "        \"shareholder_equity\": [222, 289, 366, 433, 511]\n"
            "      },\n"
            "      \"cash_flow\": {\n"
            "        \"years\": [\"FY20\", \"FY21\", \"FY22\", \"FY23\", \"FY24\"],\n"
            "        \"operating_cash_flow\": [78, 102, 125, 145, 189],\n"
            "        \"investing_cash_flow\": [-45, -67, -78, -89, -112],\n"
            "        \"financing_cash_flow\": [-23, -28, -34, -41, -56],\n"
            "        \"net_change_cash\": [10, 7, 13, 15, 21],\n"
            "        \"capex\": [-42, -63, -74, -85, -108],\n"
            "        \"free_cash_flow\": [36, 39, 51, 60, 81]\n"
            "      },\n"
            "      \"narrative\": {\n"
            "        \"what_this_section_does\": \"Provides detailed financial data for quarterly trends, annual P&L, balance sheet, and cash flow analysis\",\n"
            "        \"revenue_analysis\": {\n"
            "          \"statement\": \"Revenue doubled from ₹423 Cr (FY20) to ₹846 Cr (FY24), 19% CAGR\",\n"
            "          \"explanation\": \"Defence orders from Indian Army and Navy driving rapid expansion\"\n"
            "        },\n"
            "        \"margin_analysis\": {\n"
            "          \"statement\": \"EBITDA margin expanded from 26.2% to 33.0% over 5 years\",\n"
            "          \"explanation\": \"Operating leverage from fixed cost base as revenue scales\"\n"
            "        },\n"
            "        \"leverage_analysis\": {\n"
            "          \"statement\": \"Debt minimal at ₹89 Cr vs equity of ₹511 Cr, debt-to-equity of 0.17x\",\n"
            "          \"explanation\": \"Strong balance sheet with low financial risk and capacity for growth investments\"\n"
            "        },\n"
            "        \"cash_flow_analysis\": {\n"
            "          \"statement\": \"Operating cash flow of ₹189 Cr vs capex of ₹108 Cr generates ₹81 Cr free cash flow\",\n"
            "          \"explanation\": \"Self-funded growth with surplus cash for working capital needs in defence contracts\"\n"
            "        }\n"
            "      }\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "```\n\n"
            "------------------------------------------------------------\n"
            "SECTION 6: SWOT ANALYSIS FORMAT\n"
            "------------------------------------------------------------\n"
            "Distinguish structural vs temporary factors:\n\n"
            "```json\n"
            "{\n"
            "  \"section\": 6,\n"
            "  \"section_title\": \"SWOT Analysis\",\n"
            "  \"slides\": [\n"
            "    {\n"
            "      \"slide_id\": \"6A\",\n"
            "      \"company\": \"Vodafone Idea\",\n"
            "      \"narrative\": {\n"
            "        \"what_this_section_does\": \"Distinguishes between structural advantages and temporary challenges\",\n"
            "        \"strengths\": {\n"
            "          \"statement\": \"Key advantages from documents\",\n"
            "          \"explanation\": \"Why these are structural and hard to replicate\"\n"
            "        },\n"
            "        \"weaknesses\": {\n"
            "          \"statement\": \"Major challenges mentioned\",\n"
            "          \"explanation\": \"Whether these are structural or fixable\"\n"
            "        },\n"
            "        \"opportunities\": {\n"
            "          \"statement\": \"Growth drivers discussed\",\n"
            "          \"explanation\": \"What would need to happen for these to materialize\"\n"
            "        },\n"
            "        \"threats\": {\n"
            "          \"statement\": \"Key risks mentioned\",\n"
            "          \"explanation\": \"How these create existential or profitability risk\"\n"
            "        }\n"
            "      }\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "```\n\n"
            "------------------------------------------------------------\n"
            "SECTION 7: RISK & GROWTH DRIVERS FORMAT\n"
            "------------------------------------------------------------\n"
            "🚨 CRITICAL: Extract SPECIFIC RISKS AND GROWTH DRIVERS from concall transcripts and quarterly reports\n"
            "   • Search for management commentary on risks, challenges, opportunities\n"
            "   • Extract specific metrics: debt levels, capex plans, order book, revenue guidance\n"
            "   • Include quantified risks (e.g., \"Debt of ₹1.1 lakh Cr with 4.2x Debt/Equity\")\n"
            "   • Include quantified growth drivers (e.g., \"5G rollout plan of ₹25,000 Cr capex\")\n"
            "   • DO NOT output only narrative without specific data points from documents\n\n"
            "Explain risk-reward asymmetry with ACTUAL DATA from documents:\n\n"
            "```json\n"
            "{\n"
            "  \"section\": 7,\n"
            "  \"section_title\": \"Risk & Growth Drivers\",\n"
            "  \"slides\": [\n"
            "    {\n"
            "      \"slide_id\": \"7A\",\n"
            "      \"companies\": [\"Vodafone Idea\", \"Apollo Micro Systems\"],\n"
            "      \"narrative\": {\n"
            "        \"what_this_section_does\": \"Evaluates risk-reward profile by examining downside scenarios and upside catalysts with specific data from documents\",\n"
            "        \"vodafone_risk_profile\": {\n"
            "          \"downside_statement\": \"Debt burden of ₹1.1 lakh Cr with negative equity of ₹16,000 Cr creates solvency risk\",\n"
            "          \"downside_explanation\": \"With Debt/Equity at 4.2x and negative ROE of -15%, the company faces structural financial distress. Management mentioned in concall (Pg. 12) that debt service requires ₹15,000 Cr annually while free cash flow is only ₹9,000 Cr, creating a ₹6,000 Cr annual shortfall that necessitates equity infusion or asset sales.\",\n"
            "          \"upside_statement\": \"5G rollout and tariff hike potential could add ₹8,000-10,000 Cr annual EBITDA\",\n"
            "          \"upside_explanation\": \"Management guided (Pg. 15) that 5G capex of ₹25,000 Cr over 2 years could capture high-value customers and enable 20-25% tariff increases industry-wide, which at current 290M subscribers translates to ₹8,000 Cr additional annual revenue at 45% EBITDA margin.\",\n"
            "          \"key_risks\": [\n"
            "            {\"risk\": \"Subscriber loss\", \"metric\": \"Lost 5.2M subscribers in Q2\", \"page\": \"Pg. 3\"},\n"
            "            {\"risk\": \"AGR dues\", \"metric\": \"₹70,000 Cr pending liability\", \"page\": \"Pg. 18\"},\n"
            "            {\"risk\": \"Spectrum payments\", \"metric\": \"₹48,000 Cr due by FY26\", \"page\": \"Pg. 19\"}\n"
            "          ],\n"
            "          \"growth_catalysts\": [\n"
            "            {\"catalyst\": \"5G launch\", \"impact\": \"Target 100M 5G users by FY26\", \"page\": \"Pg. 15\"},\n"
            "            {\"catalyst\": \"Tariff hike\", \"impact\": \"20-25% increase expected Q4 FY25\", \"page\": \"Pg. 16\"},\n"
            "            {\"catalyst\": \"Government support\", \"impact\": \"Moratorium extension on AGR dues\", \"page\": \"Pg. 20\"}\n"
            "          ]\n"
            "        },\n"
            "        \"apollo_risk_profile\": {\n"
            "          \"downside_statement\": \"Government contract concentration risk with 85% revenue from defense orders\",\n"
            "          \"downside_explanation\": \"Management disclosed (Pg. 8) that Top 3 customers contribute 78% of revenue. If defense budget allocation shifts or contract delays occur (as seen in Q1 with ₹150 Cr order postponement), revenue can drop 15-20% quarter-over-quarter. Working capital intensity of 180-day receivable cycle amplifies cash flow volatility.\",\n"
            "          \"upside_statement\": \"Order book of ₹2,400 Cr (3x annual revenue) provides 3-year revenue visibility\",\n"
            "          \"upside_explanation\": \"Management announced (Pg. 3) Unit 3 expansion will increase capacity 8x to ₹3,500 Cr by FY27, with MIGM opportunity worth ₹4,000 Cr and BrahMos projects adding ₹800 Cr. Combined with 45-50% revenue CAGR guidance (Pg. 3), this creates path to ₹1,800 Cr revenue by FY27 at 28% EBITDA margin = ₹500 Cr EBITDA vs current ₹200 Cr.\",\n"
            "          \"key_risks\": [\n"
            "            {\"risk\": \"Customer concentration\", \"metric\": \"Top 3 = 78% revenue\", \"page\": \"Pg. 8\"},\n"
            "            {\"risk\": \"IDL subsidiary losses\", \"metric\": \"Loss-making, needs turnaround\", \"page\": \"Pg. 15\"},\n"
            "            {\"risk\": \"Working capital\", \"metric\": \"180-day receivable cycle\", \"page\": \"Pg. 9\"}\n"
            "          ],\n"
            "          \"growth_catalysts\": [\n"
            "            {\"catalyst\": \"Unit 3 capacity\", \"impact\": \"8x capacity increase by Q1 FY27\", \"page\": \"Pg. 7\"},\n"
            "            {\"catalyst\": \"MIGM project\", \"impact\": \"₹4,000 Cr opportunity (Apollo+BDL)\", \"page\": \"Pg. 17\"},\n"
            "            {\"catalyst\": \"Export potential\", \"impact\": \"Exploring SE Asia defense markets\", \"page\": \"Pg. 21\"}\n"
            "          ]\n"
            "        }\n"
            "      }\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "```\n\n"
            "🚨 NOTICE: Example above shows SPECIFIC data extraction with page citations.\n"
            "   • Each risk/catalyst includes METRIC with actual numbers from documents\n"
            "   • Each explanation includes QUANTIFIED impact (₹ amounts, %, time frames)\n"
            "   • Page citations prove data comes from actual documents\n"
            "   • DO NOT output generic narrative without specific numbers and citations\n\n"
            "------------------------------------------------------------\n"
            "EXTRACTION METHODOLOGY\n"
            "------------------------------------------------------------\n"
            "1. Use file search tool to locate relevant sections in documents\n"
            "2. Extract verbatim data from source documents\n"
            "3. For each statement, explain WHY it matters for investment decisions\n"
            "4. Focus on interactions and implications, not just raw numbers\n"
            "5. Use 'N/A' if specific data not found in documents\n\n"
            "🚨 CRITICAL DATA EXTRACTION RULES:\n"
            "• NEVER use placeholders like '[actual numbers]', '[numbers]', '[percentages]'\n"
            "• ALWAYS extract real numerical values from the PDF documents\n"
            "• If the validator request shows '[actual numbers]', that means REPLACE it with real extracted data\n"
            "• Search the quarterly reports and concall transcripts for exact revenue, EBITDA, profit figures\n"
            "• Use the file search tool to find financial tables and extract ALL numerical data\n"
            "• Arrays must contain real numbers: [156, 189, 234, 267, 178] NOT [actual numbers]\n"
            "• If you cannot find specific numbers in documents, use 'N/A' or null, but NEVER use placeholder text\n\n"
            "------------------------------------------------------------\n"
            "PROFESSIONAL STANDARDS\n"
            "------------------------------------------------------------\n"
            "✓ ALWAYS include 'what_this_section_does' explanation\n"
            "✓ EVERY statement must have corresponding 'explanation' field\n"
            "✓ Explain HOW elements interact (revenue trends → market position)\n"
            "✓ Distinguish structural vs temporary factors\n"
            "✓ Extract only information present in source documents\n"
            "✓ Focus on WHY data matters, not just WHAT the numbers are\n"
            "✗ Don't just list numbers without context\n"
            "✗ Don't create speculation not in documents\n"
            "✗ Don't skip explanation fields\n\n"
            "This is analyst-grade financial document extraction for investment decision-making.\n"
        ),
        model=MODEL_DEPLOYMENT,
        tools=file_search_tool if file_search_tool else None
    )
    
    await agent.__aenter__()
    return agent


async def main():
    """Financial Documents Agent - Multi-file analysis."""
    
    print("\n" + "="*70)
    print("📊 Financial Documents Agent - Quarterly Reports & Concall Transcripts")
    print("="*70)
    
    # Initialize client
    client = AzureAIAgentClient(async_credential=DefaultAzureCredential())
    files: list[FileInfo] = []
    vector_store: VectorStore | None = None
    client = None
    
    try:
        # Define all PDF files to upload (in parent directory)
        pdf_files = [
            "../ams_concall_transcript.pdf",
            "../ams_quaterly_reports.pdf",
            "../vodafone_concall_transcript.pdf",
            "../vodafone_quaterly_reports.pdf"
        ]
        
        print("\n📤 Uploading financial documents...")
        base_path = Path(__file__).parent
        
        # Upload all PDF files
        for pdf_file in pdf_files:
            pdf_path = base_path / pdf_file
            if pdf_path.exists():
                print(f"   Uploading: {Path(pdf_file).name}")
                file = await client.agents_client.files.upload_and_poll(
                    file_path=str(pdf_path), 
                    purpose="assistants"
                )
                files.append(file)
                print(f"   ✅ Uploaded: {file.id}")
            else:
                print(f"   ⚠️  File not found: {pdf_file}")
        
        if not files:
            print("\n❌ No files were uploaded. Please check file paths.")
            return
        
        # Create vector store with all uploaded files
        print("\n🗄️ Creating vector store with all documents...")
        vector_store = await client.agents_client.vector_stores.create_and_poll(
            file_ids=[f.id for f in files], 
            name="financial_documents_vectorstore"
        )
        print(f"✅ Vector store created: {vector_store.id}")
        print(f"   Total documents indexed: {len(files)}")
        
        # Create file search tool
        file_search_tool = HostedFileSearchTool(
            vector_store_ids=[vector_store.id]
        )
        
        # Create Financial Documents Agent
        print("\n🤖 Creating Financial Documents Agent...")
        async with (
            DefaultAzureCredential() as credential,
            ChatAgent(
                chat_client=AzureAIAgentClient(
                    credential=credential,
                    project_endpoint=PROJECT_ENDPOINT
                ),
                name="FinancialDocumentsAgent",
                instructions=(
                    "You are the Financial Documents Agent.\n\n"
                    "Your responsibility is to read quarterly reports and concall transcripts and extract structured facts required for the pitchbook.\n\n"
                    "------------------------------------------------------------\n"
                    "WHAT YOU DO\n"
                    "------------------------------------------------------------\n"
                    "1. Read PDF documents line by line.\n"
                    "2. Identify and extract factual data:\n"
                    "   • Revenue\n"
                    "   • EBITDA\n"
                    "   • PAT\n"
                    "   • Margins\n"
                    "   • ARPU\n"
                    "   • Subscriber metrics\n"
                    "   • Order book values\n"
                    "   • Segment performance\n"
                    "   • Capex\n"
                    "   • Debt discussion\n"
                    "   • Risks mentioned by management\n"
                    "   • Opportunities and growth commentary\n"
                    "   • Strategic initiatives\n\n"
                    "3. Return only factual extracted information.\n\n"
                    "------------------------------------------------------------\n"
                    "ROLE LIMITATIONS\n"
                    "------------------------------------------------------------\n"
                    "• No valuation.\n"
                    "• No comparisons.\n"
                    "• No insights or recommendations.\n"
                    "• No calculations.\n"
                    "• No interpretation.\n\n"
                    "Your role is purely factual extraction from documents.\n\n"
                    "Always cite which document you're extracting from (AMS or Vodafone, Quarterly Report or Concall Transcript)."
                ),
                model=MODEL_DEPLOYMENT,
                tools=file_search_tool
            ) as agent
        ):
            print("✅ Financial Documents Agent created successfully!")
            
            # Create thread for conversation
            thread = agent.get_new_thread()
            
            print("\n" + "="*70)
            print("💬 Financial Documents Analysis Chat (Type 'quit' to exit)")
            print("💡 Ask for specific data extraction from the documents!")
            print("="*70 + "\n")
            
            # Example queries
            print("Available Documents:")
            print("  - AMS Quarterly Reports")
            print("  - AMS Concall Transcript")
            print("  - Vodafone Quarterly Reports")
            print("  - Vodafone Concall Transcript\n")
            
            print("Example queries:")
            print("  - Extract revenue and EBITDA from AMS quarterly report in JSON format")
            print("  - What is the subscriber growth mentioned in Vodafone concall?")
            print("  - Extract capex plans from both companies")
            print("  - Provide management commentary on risks from AMS concall\n")
            
            # Interactive chat loop
            while True:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Get response from agent (streaming)
                print("Agent: ", end="", flush=True)
                async for chunk in agent.run_stream(user_input, thread=thread):
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                print("\n")
        
        # Cleanup resources
        print("\n🧹 Cleaning up resources...")
        if vector_store:
            await client.agents_client.vector_stores.delete(vector_store.id)
            print("✅ Vector store deleted")
        for file in files:
            await client.agents_client.files.delete(file.id)
        print(f"✅ {len(files)} files deleted")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Final cleanup
        try:
            if client is None:
                client = AzureAIAgentClient(credential=DefaultAzureCredential(), project_endpoint=PROJECT_ENDPOINT)
            if vector_store:
                await client.agents_client.vector_stores.delete(vector_store.id)
            for file in files:
                await client.agents_client.files.delete(file.id)
        except Exception:
            pass
        finally:
            if client:
                await client.close()


if __name__ == "__main__":
    asyncio.run(main())

