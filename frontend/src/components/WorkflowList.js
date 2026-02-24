import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import cosmosDBService from '../services/cosmosdb';
import './WorkflowList.css';

const WorkflowList = () => {
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      
      console.log('🔍 Fetching all workflows from storage...');
      
      // Try to fetch from Cosmos DB (or localStorage fallback)
      let workflows = await cosmosDBService.getAllWorkflows();
      
      // If Cosmos DB is empty or fails, fallback to localStorage
      if (!workflows || workflows.length === 0) {
        console.log('📦 No workflows in primary storage, checking localStorage...');
        workflows = cosmosDBService.getAllFromLocalStorage();
        
        // If localStorage is also empty, load mock workflow as fallback
        if (workflows.length === 0) {
          console.log('📦 No workflows in localStorage, loading mock workflow as demo...');
          try {
            const response = await fetch('/workflow.json');
            const mockData = await response.json();
            // Use the mock workflow as fallback
            workflows = [mockData];
            console.log('✅ Loaded mock workflow:', mockData.id);
          } catch (err) {
            console.error('Error loading mock workflow:', err);
          }
        }
      }
      
      console.log(`📊 Found ${workflows.length} total workflows`);
      
      // Show ALL workflows (completed, failed, in_progress)
      console.log(`✅ Displaying ${workflows.length} workflows`);
      setWorkflows(workflows);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching workflows:', err);
      
      // Fallback chain: localStorage -> mock workflow
      let localWorkflows = cosmosDBService.getAllFromLocalStorage();
      
      if (localWorkflows.length === 0) {
        // Load mock workflow as last resort
        try {
          const response = await fetch('/workflow.json');
          const mockData = await response.json();
          localWorkflows = [mockData];
        } catch (error) {
          console.error('Error loading mock workflow:', error);
        }
      }
      
      const allWorkflows = localWorkflows; // Show ALL workflows
      setWorkflows(allWorkflows);
      
      if (allWorkflows.length === 0) {
        setError('No workflows found');
      }
      setLoading(false);
    }
  };

  const handleWorkflowClick = (workflowId) => {
    navigate(`/workflow/${workflowId}`);
  };

  const handleNewWorkflow = () => {
    navigate('/');
  };

  const getStatusBadge = (status) => {
    const statusColors = {
      completed: 'bg-green-500',
      in_progress: 'bg-yellow-500',
      failed: 'bg-red-500',
      pending: 'bg-gray-500'
    };
    
    return (
      <span className={`status-badge ${statusColors[status] || 'bg-gray-500'}`}>
        {status.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="workflow-list-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading workflows...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="workflow-list-container">
        <div className="error-state">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
          <button onClick={fetchWorkflows} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="workflow-list-container">
      <div className="workflow-list-header">
        <div className="header-content">
          <h1 className="page-title">
            <span className="title-icon">📊</span>
            Investment Pitchbook Workflows
          </h1>
        </div>
        <button onClick={handleNewWorkflow} className="new-workflow-button">
          <span className="button-icon">➕</span>
          New Pitchbook
        </button>
      </div>

      <div className="workflow-stats">
        <div className="stat-card">
          <span className="stat-value">{workflows.length}</span>
          <span className="stat-label">Total Workflows</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{workflows.filter(w => w.status === 'completed').length}</span>
          <span className="stat-label">Completed</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{workflows.filter(w => w.status === 'failed').length}</span>
          <span className="stat-label">Failed</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">
            {workflows.reduce((total, w) => total + (w.messages?.length || 0), 0)}
          </span>
          <span className="stat-label">Total Messages</span>
        </div>
      </div>

      <div className="workflows-grid">
        {workflows.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">📋</span>
            <h3>No workflows yet</h3>
            <p>Run "Start Agent Analysis" to create your first pitchbook workflow.</p>
            <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '8px' }}>
              Note: Workflows include completed, failed, and in-progress analyses.
            </p>
            <button onClick={handleNewWorkflow} className="start-button">
              Create Pitchbook
            </button>
          </div>
        ) : (
          workflows.map((workflow) => (
            <div
              key={workflow.id}
              className="workflow-card"
              onClick={() => handleWorkflowClick(workflow.id)}
            >
              <div className="workflow-card-header">
                <div className="workflow-info">
                  <h3 className="workflow-title">
                    {workflow.workflowId || workflow.id}
                  </h3>
                  <p className="workflow-timestamp">
                    {formatDate(workflow.createdAt)}
                  </p>
                </div>
                {getStatusBadge(workflow.status)}
              </div>

              <div className="workflow-card-body">
                <div className="workflow-metrics">
                  <div className="metric">
                    <span className="metric-icon">💬</span>
                    <span className="metric-value">
                      {workflow.messages?.length || 0} messages
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-icon">📊</span>
                    <span className="metric-value">
                      {workflow.messages?.filter(m => m.type === 'agent_response').length || 0} responses
                    </span>
                  </div>
                </div>

                <div className="workflow-summary">
                  {workflow.messages && workflow.messages.length > 0 && (
                    <p className="last-message">
                      Last: {workflow.messages[workflow.messages.length - 1].message?.substring(0, 80)}...
                    </p>
                  )}
                </div>
              </div>

              <div className="workflow-card-footer">
                <button className="view-button">
                  View Details →
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default WorkflowList;
