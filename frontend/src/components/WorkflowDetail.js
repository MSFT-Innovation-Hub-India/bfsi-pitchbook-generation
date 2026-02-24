import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import cosmosDBService from '../services/cosmosdb';
import CompanySnapshots from './CompanySnapshots';
import NewsSentiment from './NewsSentiment';
import FinancialStatements from './FinancialStatements';
import ValuationTables from './ValuationTables';
import HistoricalValuation from './HistoricalValuation';
import SwotAnalysis from './SwotAnalysis';
import RiskGrowth from './RiskGrowth';
import InvestmentThesis from './InvestmentThesis';
import './WorkflowDetail.css';

const WorkflowDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [workflow, setWorkflow] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('timeline');

  const fetchWorkflowDetail = async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('📊 Fetching workflow:', id);
      
      // Try multi-level fallback: Cosmos DB -> localStorage -> mock workflow
      let workflow = await cosmosDBService.getWorkflow(id);
      
      // If not found in Cosmos DB, try localStorage
      if (!workflow) {
        console.log('📦 Not in Cosmos DB, checking localStorage...');
        workflow = cosmosDBService.getFromLocalStorage(id);
      }
      
      // If still not found, try mock workflow as fallback
      if (!workflow) {
        console.log('📦 Not in localStorage, checking mock workflow...');
        try {
          const response = await fetch('/workflow.json');
          const mockData = await response.json();
          
          // Use mock workflow if ID matches or as default
          if (mockData.id === id || mockData.workflowId === id) {
            workflow = mockData;
          }
        } catch (err) {
          console.error('Error loading mock workflow:', err);
        }
      }
      
      if (workflow) {
        console.log('✅ Workflow loaded:', workflow.id, `(${workflow.messages?.length || 0} messages)`);
        setWorkflow(workflow);
      } else {
        setError('Workflow not found');
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching workflow:', err);
      setError('Failed to load workflow details');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflowDetail();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const getMessageIcon = (type) => {
    const icons = {
      system: '🖥️',
      orchestrator: '🎯',
      agent_response: '🤖',
      complete: '✅',
      error: '❌'
    };
    return icons[type] || '📝';
  };

  const getMessageTypeClass = (type) => {
    return `message-type-${type.replace('_', '-')}`;
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getAgentColor = (agent) => {
    const colors = {
      'System': '#718096',
      'Workflow Orchestrator': '#667eea',
      'Quality Validator': '#48bb78',
      'Financial Analyst': '#3182ce',
      'Market Insights Analyst': '#d69e2e',
      'Peer Comparison Analyst': '#9f7aea'
    };
    return colors[agent] || '#a0aec0';
  };

  const getSectionBreakdown = () => {
    if (!workflow?.messages) return [];
    
    const sections = [];
    let currentSection = null;
    
    workflow.messages.forEach((msg) => {
      if (msg.type === 'agent_response' && msg.data?.section) {
        const sectionNum = msg.data.section;
        if (!currentSection || currentSection.number !== sectionNum) {
          currentSection = {
            number: sectionNum,
            agent: msg.agent,
            status: msg.data.completed ? 'completed' : 'in-progress',
            timestamp: msg.timestamp
          };
          sections.push(currentSection);
        }
      }
    });
    
    return sections;
  };

  const getAgentStats = () => {
    if (!workflow?.messages) return [];
    
    const stats = {};
    workflow.messages.forEach((msg) => {
      if (msg.agent && msg.type === 'agent_response') {
        if (!stats[msg.agent]) {
          stats[msg.agent] = { count: 0, agent: msg.agent };
        }
        stats[msg.agent].count++;
      }
    });
    
    return Object.values(stats).sort((a, b) => b.count - a.count);
  };

  const handleDownloadPDF = () => {
    const link = document.createElement('a');
    link.href = '/Investment_Pitchbook_20251224_074240.pdf';
    link.download = 'Investment_Pitchbook_20251224_074240.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="workflow-detail-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading workflow details...</p>
        </div>
      </div>
    );
  }

  if (error || !workflow) {
    return (
      <div className="workflow-detail-container">
        <div className="error-state">
          <span className="error-icon">⚠️</span>
          <p>{error || 'Workflow not found'}</p>
          <button onClick={() => navigate('/workflows')} className="back-button">
            ← Back to Workflows
          </button>
        </div>
      </div>
    );
  }

  const sections = getSectionBreakdown();
  const agentStats = getAgentStats();

  return (
    <div className="workflow-detail-container">
      {/* Header */}
      <div className="workflow-detail-header">
        <button onClick={() => navigate('/workflows')} className="back-button-header">
          ← Back
        </button>
        <div className="header-content">
          <h1 className="workflow-title">
            <span className="title-icon">📊</span>
            {workflow.workflowId || workflow.id}
          </h1>
          <p className="workflow-meta">
            Created: {new Date(workflow.createdAt).toLocaleString()} • 
            Status: <span className={`status-${workflow.status}`}>{workflow.status}</span>
            <br />
            <small style={{ color: '#94a3b8' }}>Viewing completed workflow execution history</small>
          </p>
        </div>
        <div className="workflow-actions">
          {workflow.status === 'completed' && (
            <>
              <button className="action-button" onClick={() => setActiveTab('output')}>
                <span>📊</span> View Output
              </button>
              <button className="action-button" onClick={handleDownloadPDF}>
                <span>📥</span> Download Pitchbook
              </button>
            </>
          )}
          {workflow.status === 'failed' && (
            <div className="failed-badge" style={{ padding: '12px 24px', background: '#fee2e2', color: '#b91c1c', borderRadius: '8px', fontWeight: '600' }}>
              ❌ Workflow Failed
            </div>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="workflow-stats-grid">
        <div className="stat-card">
          <div className="stat-icon">💬</div>
          <div className="stat-content">
            <div className="stat-value">{workflow.messages?.length || 0}</div>
            <div className="stat-label">Total Messages</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <div className="stat-value">{sections.length}</div>
            <div className="stat-label">Sections Completed</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🤖</div>
          <div className="stat-content">
            <div className="stat-value">{agentStats.length}</div>
            <div className="stat-label">Agents Involved</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs-container">
        <button
          className={`tab ${activeTab === 'timeline' ? 'active' : ''}`}
          onClick={() => setActiveTab('timeline')}
        >
          Agents
        </button>
        {workflow.status === 'completed' && (
          <button
            className={`tab ${activeTab === 'output' ? 'active' : ''}`}
            onClick={() => setActiveTab('output')}
          >
            Output
          </button>
        )}
      </div>

      {/* Content */}
      <div className="workflow-content">
        {workflow.status === 'failed' && activeTab === 'timeline' && (
          <div style={{ padding: '32px', textAlign: 'center', background: '#fee2e2', borderRadius: '12px', marginBottom: '24px' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>\u274c</div>
            <h2 style={{ color: '#b91c1c', marginBottom: '12px' }}>Workflow Failed</h2>
            <p style={{ color: '#7f1d1d', marginBottom: '20px' }}>
              This workflow encountered an error during execution. Check the agent activity below for details.
            </p>
          </div>
        )}
        
        {activeTab === 'timeline' && (
          <div className="timeline-view">
            <div className="timeline-two-column">
              <div className="timeline-left">
                <h2 className="section-title">Agent Activity</h2>
                <div className="timeline">
                  {workflow.messages.map((message, index) => (
                    <div key={index} className={`timeline-item ${getMessageTypeClass(message.type)}`}>
                      <div className="timeline-marker">
                        <div
                          className="timeline-dot"
                          style={{ backgroundColor: getAgentColor(message.agent) }}
                        />
                        {index < workflow.messages.length - 1 && <div className="timeline-line" />}
                      </div>
                      <div className="timeline-content">
                        <div className="timeline-header">
                          <div className="agent-name-badge">
                            <span className="agent-icon">{getMessageIcon(message.type)}</span>
                            <strong>{message.agent || 'System'}</strong>
                          </div>
                          <span className="timeline-time">{formatTimestamp(message.timestamp)}</span>
                        </div>
                        <div className="timeline-message">
                          {message.message}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="timeline-right">
                <h2 className="section-title">Agent Summary</h2>
                <div className="agents-grid">
                  {agentStats.map((stat) => (
                    <div key={stat.agent} className="agent-card">
                      <div
                        className="agent-avatar"
                        style={{ backgroundColor: getAgentColor(stat.agent) }}
                      >
                        🤖
                      </div>
                      <div className="agent-info">
                        <h3 className="agent-name">{stat.agent}</h3>
                        <p className="agent-stat">{stat.count} responses</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'output' && (
          <div className="output-view">
            <h2 className="section-title">Generated Pitchbook Output</h2>
            <div className="output-sections">
              <div className="output-section">
                <h3 className="output-section-title">🏢 Company Snapshots</h3>
                <CompanySnapshots data={null} />
              </div>
              <div className="output-section">
                <h3 className="output-section-title">📰 News & Sentiment</h3>
                <NewsSentiment data={null} />
              </div>
              <div className="output-section">
                <h3 className="output-section-title">📊 Financial Statements</h3>
                <FinancialStatements data={null} />
              </div>
              <div className="output-section">
                <h3 className="output-section-title">💰 Valuation Tables</h3>
                <ValuationTables data={null} />
              </div>
              <div className="output-section">
                <h3 className="output-section-title">📈 Historical Valuation</h3>
                <HistoricalValuation data={null} />
              </div>
              <div className="output-section">
                <h3 className="output-section-title">🎯 SWOT Analysis</h3>
                <SwotAnalysis data={null} />
              </div>
              <div className="output-section">
                <h3 className="output-section-title">⚠️ Risk & Growth</h3>
                <RiskGrowth data={null} />
              </div>
              <div className="output-section">
                <h3 className="output-section-title">💡 Investment Thesis</h3>
                <InvestmentThesis data={null} />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkflowDetail;
