import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import './App.css';
import CompanySnapshots from './components/CompanySnapshots';
import NewsSentiment from './components/NewsSentiment';
import FinancialStatements from './components/FinancialStatements';
import ValuationTables from './components/ValuationTables';
import HistoricalValuation from './components/HistoricalValuation';
import SwotAnalysis from './components/SwotAnalysis';
import RiskGrowth from './components/RiskGrowth';
import InvestmentThesis from './components/InvestmentThesis';
import AgentWorkflow from './components/AgentWorkflow';
import FileViewer from './components/FileViewer';
import WorkflowList from './components/WorkflowList';
import WorkflowDetail from './components/WorkflowDetail';

function MainApp() {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('section1');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showWorkflow, setShowWorkflow] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);

  const sections = [
    { id: 'section1', title: 'Company Snapshots', icon: '🏢', category: 'Overview', component: CompanySnapshots },
    { id: 'section2', title: 'News & Sentiment', icon: '📰', category: 'Market Intelligence', component: NewsSentiment },
    { id: 'section3', title: 'Financial Statements', icon: '📊', category: 'Financial Analysis', component: FinancialStatements },
    { id: 'section4', title: 'Valuation Tables', icon: '💰', category: 'Valuation', component: ValuationTables },
    { id: 'section5', title: 'Historical Valuation', icon: '📈', category: 'Valuation', component: HistoricalValuation },
    { id: 'section6', title: 'SWOT Analysis', icon: '🎯', category: 'Strategic Analysis', component: SwotAnalysis },
    { id: 'section7', title: 'Risk & Growth', icon: '⚠️', category: 'Risk Assessment', component: RiskGrowth },
    { id: 'section8', title: 'Investment Thesis', icon: '💡', category: 'Recommendations', component: InvestmentThesis },
    { id: 'section9', title: 'Document Library', icon: '📁', category: 'Resources', component: FileViewer },
  ];

  const ActiveComponent = sections.find(s => s.id === activeSection)?.component || CompanySnapshots;
  const activeTitle = sections.find(s => s.id === activeSection)?.title || 'Company Snapshots';

  const groupedSections = sections.reduce((acc, section) => {
    if (!acc[section.category]) {
      acc[section.category] = [];
    }
    acc[section.category].push(section);
    return acc;
  }, {});

  const handleExportPDF = () => {
    const link = document.createElement('a');
    link.href = '/Investment_Pitchbook_20251224_074240.pdf';
    link.download = 'Investment_Pitchbook_20251224_074240.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
      <div className="app">
        {/* Professional Header */}
        <header className="header">
          <div className="header-content">
            <div className="header-left">
              <div className="logo">IP</div>
              <div className="header-text">
                <h1>Investment Portfolio Analysis</h1>
                <p>Comprehensive Equity Research & Valuation Report</p>
              </div>
            </div>
            <div className="header-right">
              <div className="header-date">
                <div className="header-label">Report Date</div>
                <div className="header-value">{new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</div>
              </div>
              <div className="confidential-badge">
                <span>Status:</span> <strong>Confidential</strong>
              </div>
            </div>
          </div>
        </header>

        <div className="layout">
          {/* Enhanced Sidebar */}
          <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
            <div className="sidebar-header-nav">
              {!sidebarCollapsed && <h3>Navigation</h3>}
              <button className="collapse-btn" onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
                {sidebarCollapsed ? '☰' : '‹'}
              </button>
            </div>

            <nav className="sidebar-nav">
              {Object.entries(groupedSections).map(([category, items]) => (
                <div key={category} className="nav-category">
                  {!sidebarCollapsed && <div className="category-label">{category}</div>}
                  {items.map((section) => (
                    <button
                      key={section.id}
                      className={`nav-item ${activeSection === section.id ? 'active' : ''}`}
                      onClick={() => setActiveSection(section.id)}
                    >
                      <span className="nav-icon">{section.icon}</span>
                      {!sidebarCollapsed && <span className="nav-title">{section.title}</span>}
                    </button>
                  ))}
                </div>
              ))}
            </nav>

            {!sidebarCollapsed && (
              <div className="sidebar-footer">
                <h4>Companies Under Analysis</h4>
                <div className="company-cards">
                  <div className="company-card vodafone">
                    <div className="company-name">Vodafone Idea</div>
                    <div className="company-sector">Telecommunications</div>
                  </div>
                  <div className="company-card apollo">
                    <div className="company-name">Apollo Micro</div>
                    <div className="company-sector">Defense & Aerospace</div>
                  </div>
                </div>
              </div>
            )}
          </aside>

          {/* Main Content Area */}
          <main className="main-content">
            {/* Breadcrumb */}
            <div className="breadcrumb">
              <div className="breadcrumb-left">
                <div className="breadcrumb-label">Current Section</div>
                <h2>{activeTitle}</h2>
              </div>
              <div className="breadcrumb-actions">
                <button className="btn-secondary" onClick={() => navigate('/workflows')}>
                  📊 View Workflows
                </button>
                <button className="btn-workflow" onClick={() => setShowWorkflow(true)}>
                  🤖 Start Agent Analysis
                </button>
                <button className="btn-primary" onClick={handleExportPDF}>📥 Export PDF</button>
              </div>
            </div>

            {/* Content */}
            <div className="content-wrapper">
              {!analysisComplete ? (
                <div className="analysis-pending">
                  <div className="pending-content">
                    <h2>AI-Powered Investment Analysis</h2>
                    <p>Click "Start Agent Analysis" to generate comprehensive investment reports</p>
                    <p className="pending-subtitle">Our multi-agent system will analyze financial statements, news sentiment, peer comparisons, and generate detailed investment recommendations.</p>
                    <button className="btn-start-large" onClick={() => setShowWorkflow(true)}>
                      Start Agent Analysis
                    </button>
                  </div>
                </div>
              ) : (
                <ActiveComponent data={analysisData} />
              )}
            </div>
          </main>
        </div>

        {/* Professional Footer */}
        <footer className="footer">
          <div className="footer-content">
            <div className="footer-section">
              <h4>Disclaimer</h4>
              <p>This report is for informational purposes only and does not constitute investment advice. Past performance is not indicative of future results. Please consult with a qualified financial advisor before making investment decisions.</p>
            </div>
            <div className="footer-section">
              <h4>Methodology</h4>
              <p>Analysis based on publicly available financial data, market research, and industry reports. Valuation models include DCF, comparable company analysis, and precedent transactions.</p>
            </div>
            <div className="footer-section">
              <h4>Contact</h4>
              <p>For inquiries regarding this investment analysis report, please contact your relationship manager or email: research@investmentportfolio.com</p>
            </div>
          </div>
          <div className="footer-bottom">
            © {new Date().getFullYear()} Investment Portfolio Analytics. All rights reserved. | Confidential & Proprietary
          </div>
        </footer>

        {/* Agent Workflow Modal */}
        {showWorkflow && (
          <AgentWorkflow 
            onClose={() => setShowWorkflow(false)} 
            onComplete={(data) => {
              setAnalysisComplete(true);
              setAnalysisData(data);
              setShowWorkflow(false);
            }}
          />
        )}
      </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        {/* Workflow Routes */}
        <Route path="/workflows" element={<WorkflowList />} />
        <Route path="/workflow/:id" element={<WorkflowDetail />} />
        
        {/* Main App Route */}
        <Route path="/" element={<MainApp />} />
      </Routes>
    </Router>
  );
}

export default App;
