# Pitchbook Multi-Agent Investment Analysis

AI-powered investment pitchbook generation platform using Azure AI services for automated financial analysis, sentiment analysis, valuation modeling, and comprehensive investment report generation.

## 🚀 Features

✅ **Multi-Agent Architecture** — 6 specialized AI agents for comprehensive investment analysis  
✅ **Real-Time Processing** — Live agent progress tracking via Server-Sent Events (SSE)  
✅ **Azure Integration** — Leverages Azure AI, Azure OpenAI, and Azure AI Services  
✅ **Container-Ready** — Docker support with Azure Container Apps deployment  
✅ **Interactive Dashboard** — React-based UI with multiple analysis sections  
✅ **PDF Generation** — Automated pitchbook creation with analyst-grade formatting

## 🤖 AI Agents

| Agent | Description | Output |
|-------|-------------|--------|
| **Coordinator Agent** | Orchestrates workflow and delegates tasks to specialized agents | Workflow coordination and task management |
| **Financial Documents Agent** | Extracts and analyzes financial statements, metrics, and KPIs | Comprehensive financial data analysis |
| **News Sentiment Agent** | Analyzes market news, sentiment trends, and media coverage | News sentiment report with market insights |
| **Valuation Agent** | Performs DCF modeling, peer comparison, and valuation analysis | Valuation tables and price targets |
| **Peer Comparison MCP Agent** | Interfaces with Model Context Protocol for comparative stock data | Peer analysis and industry benchmarking |
| **PDF Generation Agent** | Synthesizes all outputs into professional investment pitchbook | Final PDF report with recommendations |

## 🛠️ Tech Stack

**Backend:** Python 3.11+, FastAPI, Uvicorn, Azure AI Projects SDK  
**Frontend:** React 18, JavaScript, Recharts, React Router  
**AI:** Azure OpenAI (GPT-4o-mini), Azure AI Services, Model Context Protocol  
**Infrastructure:** Docker, Azure Container Apps, Azure Container Registry  
**Authentication:** Azure Entra ID (DefaultAzureCredential)

## 📦 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Azure subscription with required services
- Azure CLI (`az --version`)

### Local Development

**1. Clone the repository**

```bash
git clone https://github.com/YOUR-USERNAME/pitchbook-investment-analysis.git
cd Pitchbook
```

**2. Set up environment variables**

```bash
# Backend
cd backend
copy .env.example .env
# Edit .env with your Azure credentials

# Frontend
cd ../frontend
copy .env.example .env
# Edit .env with backend URL
```

**3. Install and run backend**

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
uvicorn backend_server:app --host 0.0.0.0 --port 8000 --reload
```

**4. Install and run frontend**

```bash
cd frontend
npm install
npm start
```

**5. Access the application**

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Docker Deployment

```bash
# From Pitchbook root directory
docker-compose up --build
```

This will start:
- **Backend API:** http://localhost:8000
- **Frontend Dashboard:** http://localhost:3000

## ☁️ Azure Deployment

### Azure Container Apps

**Prerequisites**

- Azure CLI installed (`az --version`)
- Azure subscription with required services
- Docker installed

**Deploy Backend and Frontend**

```bash
# 1. Login to Azure
az login

# 2. Create resource group
az group create --name pitchbook-rg --location eastus2

# 3. Create container registry
az acr create --resource-group pitchbook-rg \
  --name pitchbookacr --sku Basic --admin-enabled true

# 4. Get ACR credentials
ACR_USERNAME=$(az acr credential show --name pitchbookacr --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name pitchbookacr --query passwords[0].value -o tsv)

# 5. Create Container Apps environment
az containerapp env create \
  --name pitchbook-env \
  --resource-group pitchbook-rg \
  --location eastus2

# 6. Build and push backend image
az acr build --registry pitchbookacr --image pitchbook-backend:latest ./backend

# 7. Deploy backend
az containerapp create \
  --name pitchbook-backend \
  --resource-group pitchbook-rg \
  --environment pitchbook-env \
  --image pitchbookacr.azurecr.io/pitchbook-backend:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server pitchbookacr.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --cpu 1.0 --memory 2.0Gi \
  --env-vars \
    AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com/" \
    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="gpt-4o-mini" \
    AZURE_AI_PROJECT_ENDPOINT="https://your-project.services.ai.azure.com/api/projects/your-project" \
    AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o-mini" \
    AZURE_SUBSCRIPTION_ID="your-subscription-id" \
    AZURE_LOCATION="eastus2"

# 8. Get backend URL
BACKEND_URL=$(az containerapp show --name pitchbook-backend \
  --resource-group pitchbook-rg \
  --query properties.configuration.ingress.fqdn -o tsv)

echo "Backend URL: https://$BACKEND_URL"

# 9. Build and deploy frontend
az acr build --registry pitchbookacr \
  --image pitchbook-frontend:latest \
  --build-arg REACT_APP_API_URL=https://$BACKEND_URL \
  ./frontend

az containerapp create \
  --name pitchbook-frontend \
  --resource-group pitchbook-rg \
  --environment pitchbook-env \
  --image pitchbookacr.azurecr.io/pitchbook-frontend:latest \
  --target-port 80 \
  --ingress external \
  --registry-server pitchbookacr.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --cpu 0.5 --memory 1.0Gi

# 10. Get frontend URL
FRONTEND_URL=$(az containerapp show --name pitchbook-frontend \
  --resource-group pitchbook-rg \
  --query properties.configuration.ingress.fqdn -o tsv)

echo "Frontend URL: https://$FRONTEND_URL"
echo "Deployment complete! 🎉"
```

### Useful Commands

```bash
# View backend logs
az containerapp logs show --name pitchbook-backend \
  --resource-group pitchbook-rg --follow

# Update backend after code changes
az acr build --registry pitchbookacr --image pitchbook-backend:latest ./backend
az containerapp update --name pitchbook-backend \
  --resource-group pitchbook-rg \
  --image pitchbookacr.azurecr.io/pitchbook-backend:latest

# Update frontend after code changes
az acr build --registry pitchbookacr --image pitchbook-frontend:latest ./frontend
az containerapp update --name pitchbook-frontend \
  --resource-group pitchbook-rg \
  --image pitchbookacr.azurecr.io/pitchbook-frontend:latest

# Scale backend
az containerapp update --name pitchbook-backend \
  --resource-group pitchbook-rg \
  --min-replicas 1 --max-replicas 5

# Delete all resources
az group delete --name pitchbook-rg --yes
```

## 🔧 Configuration

### Required Azure Resources

| Resource | Purpose | Setup |
|----------|---------|-------|
| **Azure AI Project** | AI agent orchestration | Create in Azure AI Studio |
| **Azure OpenAI** | GPT model deployment | Deploy GPT-4o-mini or GPT-4o |
| **Azure Container Registry** | Docker image storage | Create ACR with admin enabled |
| **Azure Container Apps** | Application hosting | Create environment for apps |

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | ✅ | Azure OpenAI service endpoint |
| `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` | ✅ | Model deployment name (e.g., gpt-4o-mini) |
| `AZURE_AI_PROJECT_ENDPOINT` | ✅ | Azure AI Project endpoint URL |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | ✅ | AI model deployment name |
| `AZURE_SUBSCRIPTION_ID` | ✅ | Azure subscription ID |
| `AZURE_LOCATION` | ✅ | Azure region (e.g., eastus2) |
| `AZURE_ENV_NAME` | ⬜ | Environment name (optional) |
| `REACT_APP_API_URL` | ✅ | Frontend: Backend API URL |

> **Note:** API keys are not required. The application uses Azure Entra ID authentication via `DefaultAzureCredential`. For local development, use `az login`.

## 📖 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| **GET** | `/health` | Health check endpoint |
| **POST** | `/analyze` | Start investment analysis workflow |
| **GET** | `/analysis/{session_id}/stream` | SSE stream for real-time progress |
| **GET** | `/analysis/{session_id}/status` | Get analysis status |
| **GET** | `/analysis/{session_id}/result` | Get final analysis result |
| **GET** | `/files/{filename}` | Download generated files (PDF, JSON) |

**Sample Request:**

```json
POST /analyze
{
  "company_name": "Apple Inc.",
  "ticker": "AAPL"
}
```

Interactive documentation available at: `/docs` (Swagger UI)

## 🏗️ Project Structure

```
Pitchbook/
├── backend/                           # FastAPI backend
│   ├── agents/                        # AI agent implementations
│   │   ├── __init__.py
│   │   ├── agent_coordinator.py       #   Workflow coordinator
│   │   ├── agent_financial_documents.py #   Financial analysis agent
│   │   ├── agent_news_Sentiment.py    #   News sentiment agent
│   │   ├── agent_valuation.py         #   Valuation modeling agent
│   │   ├── peer_comparision_mcp_agent.py # Peer comparison agent
│   │   ├── pitchbook_pdf_agent.py     #   PDF generation agent
│   │   └── news_function.py           #   News fetching utilities
│   ├── instructions/                  # Agent prompt templates
│   │   ├── analyst_grade_json_format.txt
│   │   ├── coordinator_instructions_sections.txt
│   │   └── validator_instructions_sections.txt
│   ├── mcp/                           # Model Context Protocol server
│   │   ├── server.py                  #   MCP server implementation
│   │   ├── stock_analyzer.py          #   Stock analysis tools
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── templates/                     # Report templates
│   │   └── template.txt
│   ├── backend_server.py              # FastAPI application
│   ├── simple_groupchat.py            # Agent orchestration
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Backend container image
│   └── .env.example                   # Environment template
├── frontend/                          # React frontend
│   ├── src/
│   │   ├── components/                # UI components
│   │   │   ├── AgentWorkflow.js       #   Workflow monitor
│   │   │   ├── CompanySnapshots.js    #   Company overview
│   │   │   ├── NewsSentiment.js       #   News analysis view
│   │   │   ├── FinancialStatements.js #   Financial data view
│   │   │   ├── ValuationTables.js     #   Valuation metrics
│   │   │   ├── HistoricalValuation.js #   Historical charts
│   │   │   ├── SwotAnalysis.js        #   SWOT analysis view
│   │   │   ├── RiskGrowth.js          #   Risk assessment
│   │   │   ├── InvestmentThesis.js    #   Investment recommendations
│   │   │   └── FileViewer.js          #   Document library
│   │   ├── App.js                     # Main application
│   │   ├── App.css
│   │   └── index.js
│   ├── public/
│   │   ├── index.html
│   │   └── mock_workflow.json
│   ├── Dockerfile                     # Frontend container image
│   ├── package.json                   # Node dependencies
│   ├── nginx.conf                     # Nginx configuration
│   └── .env.example                   # Environment template
├── output/                            # Generated reports
├── docker-compose.yml                 # Local development
├── AZURE_DEPLOYMENT_GUIDE.md          # Detailed deployment guide
├── .gitignore                         # Git ignore rules
└── README.md                          # This file
```

## 🎯 Usage

### Starting Analysis

1. Open the frontend dashboard at http://localhost:3000
2. Click **"Start New Analysis"**
3. Enter company name and ticker symbol (e.g., "Apple Inc.", "AAPL")
4. Watch real-time progress in the **Agent Workflow** panel
5. Navigate through different sections to view results:
   - 🏢 **Company Snapshots** — Overview and key metrics
   - 📰 **News & Sentiment** — Market sentiment analysis
   - 📊 **Financial Statements** — Income statement, balance sheet, cash flow
   - 💰 **Valuation Tables** — DCF, multiples, peer comparison
   - 📈 **Historical Valuation** — Price trends and valuation history
   - 🎯 **SWOT Analysis** — Strengths, weaknesses, opportunities, threats
   - ⚠️ **Risk & Growth** — Risk assessment and growth drivers
   - 💡 **Investment Thesis** — Investment recommendations
   - 📁 **Document Library** — Download generated reports

### Exporting Results

- Click **"Export PDF"** to download the complete pitchbook
- Access generated files in the **Document Library** section
- Files are stored in the `output/` directory

## 🔒 Security

- ✅ **Environment Variables** — Credentials stored in Azure Container Apps configuration (never in code)
- ✅ **Azure Key Vault** — Recommended for production secrets management
- ✅ **CORS** — Properly configured for frontend access only
- ✅ **HTTPS** — Enforced on all Azure deployments
- ✅ **Entra ID Authentication** — Passwordless authentication via `DefaultAzureCredential`
- ✅ **`.gitignore`** — Sensitive files and credentials excluded from source control

## 📊 Monitoring

- 🔍 **Health Check** — `GET /health` endpoint for availability monitoring
- 📝 **Structured Logging** — Console logs with detailed agent execution tracking
- 📈 **Azure Monitor** — Container Apps built-in metrics and log streaming
- 🔴 **Real-time Logs** — `az containerapp logs show --follow`
- 📊 **Application Insights** — Optional integration for advanced telemetry

## 🐛 Debugging

### Local Debugging

```bash
# Backend logs
docker logs pitchbook-backend -f

# Frontend logs
docker logs pitchbook-frontend -f

# Check health endpoints
curl http://localhost:8000/health
curl http://localhost:3000
```

### Azure Debugging

```bash
# View logs
az containerapp logs show --name pitchbook-backend \
  --resource-group pitchbook-rg --follow

# Check app status
az containerapp show --name pitchbook-backend \
  --resource-group pitchbook-rg \
  --query properties.runningStatus

# View environment variables
az containerapp show --name pitchbook-backend \
  --resource-group pitchbook-rg \
  --query properties.template.containers[0].env
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/azure/container-apps/)
- [Azure AI Studio Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## 📄 License

[Add your license information here]

## 🔮 Future Enhancements

- [ ] Multi-company batch analysis
- [ ] Historical analysis comparison
- [ ] Enhanced PDF customization and branding
- [ ] Real-time market data integration
- [ ] User authentication and multi-tenancy
- [ ] Advanced caching for faster analysis
- [ ] Export to PowerPoint and Excel
- [ ] Integration with more financial data providers
- [ ] Custom agent workflows
- [ ] Collaborative editing and sharing

---

**Built with ❤️ using Azure AI Services**
