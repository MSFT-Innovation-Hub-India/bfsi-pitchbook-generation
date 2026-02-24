import React, { useState, useEffect, useRef } from 'react';
import cosmosDBService from '../services/cosmosdb';
import './AgentWorkflow.css';

const AgentWorkflow = ({ onClose, onComplete }) => {
  const [messages, setMessages] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [currentAgent, setCurrentAgent] = useState(null);
  const [completedAgents, setCompletedAgents] = useState([]);
  const [showLeftPanel, setShowLeftPanel] = useState(true);
  const [showRightPanel, setShowRightPanel] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(null); // Agent selected by orchestrator
  const [arrowDirection, setArrowDirection] = useState(null); // 'to' or 'from'
  // eslint-disable-next-line no-unused-vars
  const [currentWorkflowId, setCurrentWorkflowId] = useState(null); // Track current workflow
  const eventSourceRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Updated agent structure with formal role names and proper hierarchy
  const agents = [
    {
      id: 'coordinator',
      name: 'Coordinator',
      displayName: 'Workflow Orchestrator',
      icon: '🎯',
      color: '#667eea',
      description: 'Coordinates agent tasks',
      level: 0,
      position: 'center'
    },
    {
      id: 'validator',
      name: 'Validator',
      displayName: 'Quality Validator',
      icon: '✅',
      color: '#10b981',
      description: 'Validates section outputs',
      level: 0,
      position: 'right'
    },
    {
      id: 'financial',
      name: 'FinancialDocumentsAgent',
      displayName: 'Financial Analyst',
      icon: '📊',
      color: '#f093fb',
      description: 'Analyzes financial documents',
      level: 1,
      position: 'left'
    },
    {
      id: 'peer',
      name: 'PeerComparisonAgent',
      displayName: 'Peer Comparison Analyst',
      icon: '🔍',
      color: '#4facfe',
      description: 'Compares peer companies',
      level: 1,
      position: 'center'
    },
    {
      id: 'news',
      name: 'NewsSentimentAgent',
      displayName: 'Market Insights Analyst',
      icon: '📰',
      color: '#fa709a',
      description: 'Analyzes news & sentiment',
      level: 1,
      position: 'right'
    }
  ];

  // Map backend names to display names
  const agentNameMap = {
    'FinancialDocumentsAgent': 'Financial Analyst',
    'Financial Documents Agent': 'Financial Analyst',
    'Financial Documents': 'Financial Analyst',
    'PeerComparisonAgent': 'Peer Comparison Analyst',
    'Peer Comparison Agent': 'Peer Comparison Analyst',
    'Peer Comparison': 'Peer Comparison Analyst',
    'NewsSentimentAgent': 'Market Insights Analyst',
    'News Sentiment Agent': 'Market Insights Analyst',
    'News Sentiment': 'Market Insights Analyst',
    'ValuationAgent': 'Valuation Analyst',
    'Valuation Agent': 'Valuation Analyst',
    'Valuation': 'Valuation Analyst',
    'InvestmentThesisAgent': 'Investment Thesis Analyst',
    'Investment Thesis Agent': 'Investment Thesis Analyst',
    'Validator': 'Quality Validator',
    'Coordinator': 'Workflow Orchestrator',
    'Orchestrator': 'Workflow Orchestrator'
  };

  const cleanAgentName = (name) => {
    if (!name) return name;
    // Remove emoji prefixes
    const cleaned = name.replace(/^[📊💰📈📰🎯✅🔍]\s*/, '').trim();
    return agentNameMap[cleaned] || cleaned;
  };

  // Extract agent from orchestrator's message content (currently unused but kept for future use)
  // eslint-disable-next-line no-unused-vars
  const extractSelectedAgent = (messageContent) => {
    console.log('─────────────────────────────────────────────');
    console.log('🔍 EXTRACT AGENT CALLED');
    console.log('Input:', messageContent?.substring(0, 200));
    
    // Check for participant pattern (even with spaces: "part icipant")
    const hasParticipant = messageContent && (
      messageContent.includes('participant') || 
      messageContent.includes('part icipant') ||
      messageContent.includes('part_icipant')
    );
    console.log('Has participant?', hasParticipant);
    
    if (!messageContent || !hasParticipant) {
      console.log('❌ Early exit: no participant in message');
      console.log('─────────────────────────────────────────────');
      return null;
    }
    
    // Handle multiple possible patterns for malformed JSON keys
    // Pattern 1: " selected _part icipant " (with any amount of spaces)
    console.log('Trying Pattern 1: malformed key with spaces...');
    let match = messageContent.match(/"\s*selected\s*_?\s*part\s*_?\s*icipant\s*"\s*:\s*"\s*([^"]+)\s*"/i);
    if (match) {
      console.log('✅ Pattern 1 matched!');
      console.log('Full match:', match[0]);
      console.log('Captured group:', match[1]);
    }
    
    // Pattern 2: selected_participant (normalized)
    if (!match) {
      console.log('Trying Pattern 2: normalized key...');
      match = messageContent.match(/selected_participant\s*[:=]\s*["']([^"']+)["']/i);
      if (match) {
        console.log('✅ Pattern 2 matched!');
        console.log('Captured group:', match[1]);
      }
    }
    
    // Pattern 3: Just look for participant: value
    if (!match) {
      console.log('Trying Pattern 3: simple participant...');
      match = messageContent.match(/participant\s*[:=]\s*["']([^"']+)["']/i);
      if (match) {
        console.log('✅ Pattern 3 matched!');
        console.log('Captured group:', match[1]);
      }
    }
    
    if (match) {
      const value = match[1].trim();  // Trim spaces from the value
      console.log('✅ Extracted value:', value);
      const result = mapAgentNameToVisualization(value);
      console.log('─────────────────────────────────────────────');
      return result;
    }
    
    console.log('❌ No pattern matched!');
    console.log('Message excerpt:', messageContent.substring(0, 200));
    console.log('─────────────────────────────────────────────');
    return null;
  };

  // Map orchestrator's agent names to our visualization agent names
  const mapAgentNameToVisualization = (agentName) => {
    console.log('│ 🗺️  MAP AGENT NAME');
    console.log('│ Input:', agentName);
    
    if (!agentName) {
      console.log('│ ❌ No agent name provided');
      return null;
    }
    
    // Remove ALL spaces and normalize, also remove 'Agent' suffix
    let normalized = agentName.replace(/\s+/g, '').trim();
    console.log('│ After space removal:', normalized);
    
    // Remove 'Agent' suffix if present
    normalized = normalized.replace(/Agent$/i, '');
    console.log('│ After Agent suffix removal:', normalized);
    
    // Map agent names to visualization agent.name values (matches agents array above)
    const mapping = {
      'Validator': 'Validator',
      'QualityValidator': 'Validator',
      'FinancialDocuments': 'FinancialDocumentsAgent',
      'FinancialDocumentsAgent': 'FinancialDocumentsAgent',
      'FinancialAnalyst': 'FinancialDocumentsAgent',
      'PeerComparison': 'PeerComparisonAgent',
      'PeerComparisonAgent': 'PeerComparisonAgent',
      'PeerComparisonAnalyst': 'PeerComparisonAgent',
      'NewsSentiment': 'NewsSentimentAgent',
      'NewsSentimentAgent': 'NewsSentimentAgent',
      'MarketInsightsAnalyst': 'NewsSentimentAgent',
      'Valuation': 'PeerComparisonAgent',  // Map to Peer since Valuation not in viz
      'ValuationAgent': 'PeerComparisonAgent',
      'InvestmentThesis': null,  // No arrow for this one
      'InvestmentThesisAgent': null
    };
    
    const result = mapping[normalized] || null;
    console.log('│ Mapping lookup: mapping[' + normalized + '] =', result);
    console.log('│ Available mappings:', Object.keys(mapping));
    
    if (!result) {
      console.log('│ ⚠️  No mapping found! Possible typo or unmapped agent');
    } else {
      console.log('│ ✅ Mapped to:', result);
    }
    
    return result;
  };



  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // ROBUST Parser that handles malformed JSON with spaces in keys
  const parseMessageContent = (content, agentName) => {
    if (!content) return content;

    // Try to detect JSON-like content even with malformed keys
    if (content.includes('selected') && content.includes('participant')) {
      try {
        // Method 1: Try direct parse
        const data = JSON.parse(content);
        return formatOrchestratorMessage(data);
      } catch (e) {
        // Method 2: Clean up malformed JSON with spaces in keys
        try {
          let fixed = content
            .replace(/"\s*selected\s*_?\s*part\s*icipant\s*"/gi, '"selected_participant"')
            .replace(/"\s*instruction\s*"/gi, '"instruction"')
            .replace(/"\s*finish\s*"/gi, '"finish"');
          
          const data = JSON.parse(fixed);
          return formatOrchestratorMessage(data);
        } catch (e2) {
          // Method 3: Regex extraction as fallback
          const participantMatch = content.match(/(?:selected[_\s]*participant|participant)["\s:]+["']?([^"',}]+)/i);
          const instructionMatch = content.match(/instruction["\s:]+["']?([^"'}]+)/i);
          
          if (participantMatch || instructionMatch) {
            const participant = participantMatch ? participantMatch[1].trim() : '';
            const instruction = instructionMatch ? instructionMatch[1].trim() : '';
            return formatOrchestratorMessage({
              selected_participant: participant,
              instruction: instruction
            });
          }
        }
      }
    }

    // Handle finish flag
    if (content.includes('finish') && (content.includes('true') || content.includes('True'))) {
      return '✅ Round Complete';
    }

    // Try to parse JSON messages from agents (with ```json blocks)
    const jsonMatch = content.match(/```json\s*\n(.*?)\n```/s);
    if (jsonMatch) {
      try {
        const jsonData = JSON.parse(jsonMatch[1]);
        const sectionTitle = jsonData.section_title || jsonData.title || 'Data';
        const itemCount = jsonData.slides?.length || 
                         jsonData.companies?.length || 
                         Object.keys(jsonData.key_metrics || {}).length ||
                         0;

        return `✅ Completed: ${sectionTitle}${itemCount > 0 ? ` (${itemCount} items)` : ''}`;
      } catch (e) {
        // If parsing fails, continue
      }
    }

    // Parse Validator messages
    if (content.includes('SECTION:') || content.includes('AGENT:')) {
      const sectionMatch = content.match(/SECTION:\s*(\d+)\s*[-:]\s*([^\n]+)/i);
      const agentMatch = content.match(/AGENT:\s*([^\n,]+)/i);
      const requestMatch = content.match(/REQUEST:\s*(.+?)(?:\n|$)/is);

      if (sectionMatch || agentMatch) {
        let result = '';
        
        if (sectionMatch) {
          result = `📋 Section ${sectionMatch[1]}: ${sectionMatch[2].trim()}`;
        }
        
        if (agentMatch) {
          const targetAgent = cleanAgentName(agentMatch[1].trim());
          result += result ? `\n🎯 Assigned to: ${targetAgent}` : `🎯 Agent: ${targetAgent}`;
        }

        if (requestMatch) {
          const requestText = requestMatch[1].trim();
          const shortRequest = requestText.length > 80 ? requestText.substring(0, 80) + '...' : requestText;
          result += `\n📝 Task: ${shortRequest}`;
        }

        return result || content;
      }
    }

    // Truncate long messages
    if (content.length > 150) {
      return content.substring(0, 150) + '...';
    }

    return content;
  };

  // Format orchestrator selection message
  const formatOrchestratorMessage = (data) => {
    const participant = data.selected_participant || data.participant || '';
    const instruction = data.instruction || '';
    const finish = data.finish;

    if (finish) {
      return '✅ Round Complete';
    }

    if (!participant && !instruction) {
      return null; // Skip empty
    }

    const cleanParticipant = cleanAgentName(participant);
    const shortInstruction = instruction.length > 100
      ? instruction.substring(0, 100) + '...'
      : instruction;

    let result = '';
    if (cleanParticipant) {
      result += `🎯 Agent Selected: ${cleanParticipant}`;
    }
    if (shortInstruction) {
      result += result ? `\n📋 Instruction: ${shortInstruction}` : `📋 Instruction: ${shortInstruction}`;
    }

    return result || null;
  };

  const startWorkflow = async () => {
    setIsRunning(true);
    setMessages([]);
    setCurrentAgent(null);
    setCompletedAgents([]);
    setSelectedAgent(null);
    setArrowDirection(null);

    // Create new workflow in Cosmos DB
    const { workflowId } = await cosmosDBService.createWorkflow({
      status: 'failed',
      companies: ['Vodafone Idea', 'Apollo Micro Systems']
    });
    setCurrentWorkflowId(workflowId);
    console.log('📝 Created workflow in Cosmos DB:', workflowId);

    // USE MOCK DATA instead of backend
    console.log('🎭 Starting MOCK workflow...');
    
    // Fetch mock data
    fetch('/workflow.json')
      .then(response => response.json())
      .then(mockData => {
        const messages = mockData.messages;
        let currentIndex = 0;

        // Function to process next message
        const processNextMessage = async () => {
          if (currentIndex >= messages.length) {
            console.log('✅ Mock workflow complete');
            
            // Update workflow status to completed
            if (workflowId) {
              await cosmosDBService.updateWorkflowStatus(workflowId, 'completed');
            }
            
            setIsRunning(false);
            setSelectedAgent(null);
            setArrowDirection(null);
            return;
          }

          const data = messages[currentIndex];
          currentIndex++;
          
          console.log('📨 Processing mock message:', data);
          
          // Save message to Cosmos DB
          if (workflowId) {
            await cosmosDBService.addMessage(workflowId, {
              type: data.type,
              agent: data.agent,
              message: data.message,
              timestamp: data.timestamp,
              data: data.data
            });
          }
          
          // Handle end of stream
          if (data.type === 'end' || data.type === 'complete') {
            setIsRunning(false);
            setSelectedAgent(null);
            setArrowDirection(null);
            
            // Add final message
            setMessages(prev => [...prev, {
              type: data.type,
              agent_name: data.agent || 'System',
              content: parseMessageContent(data.message, data.agent),
              timestamp: data.timestamp,
              metadata: data.data
            }]);
            
            // Update workflow status
            if (workflowId) {
              await cosmosDBService.updateWorkflowStatus(workflowId, 'completed');
            }
            
            // Load the final output and call onComplete
            console.log('✅ Analysis complete, loading results...');
            fetch('/pitchbook_final_output.txt')
              .then(response => response.text())
              .then(outputData => {
                console.log('📊 Loaded analysis results');
                if (onComplete) {
                  onComplete({ outputData });
                }
              })
              .catch(error => {
                console.error('Failed to load results:', error);
                if (onComplete) {
                  onComplete({ error: 'Failed to load results' });
                }
              });
            
            return;
          }

          // Add message to display
          setMessages(prev => [...prev, {
            type: data.type,
            agent_name: data.agent || 'System',
            content: parseMessageContent(data.message, data.agent),
            timestamp: data.timestamp,
            metadata: data.data
          }]);

          // Handle orchestrator selecting an agent
          if (data.agent === 'Workflow Orchestrator' || data.agent === 'Coordinator') {
            console.log('🎯 ORCHESTRATOR selecting agent');
            console.log('Metadata:', data.data);
            
            // Clear previous highlighting first
            setSelectedAgent(null);
            setArrowDirection(null);
            setCurrentAgent(null);
            
            const participantFromMetadata = data.data?.selected_participant;
            console.log('Participant:', participantFromMetadata);
            
            let targetAgent = null;
            if (participantFromMetadata) {
              targetAgent = mapAgentNameToVisualization(participantFromMetadata);
              console.log('Mapped to:', targetAgent);
            }
            
            if (targetAgent) {
              // Use setTimeout to ensure state clears first
              setTimeout(() => {
                setSelectedAgent(targetAgent);
                setArrowDirection('to');
                setCurrentAgent(targetAgent);
                console.log('✅ Arrow TO:', targetAgent);
              }, 100);
            }
          }

          // Handle agent responses (no return arrows for specialist agents)
          if (data.type === 'agent_response' || data.type === 'section_start') {
            const displayName = data.agent;
            console.log('📢 Agent response from:', displayName);
            
            // Clear highlighting and arrows immediately
            setSelectedAgent(null);
            setArrowDirection(null);
            setCurrentAgent(null);
          }

          // Mark agent as completed
          if (data.type === 'section_complete') {
            if (data.agent && !completedAgents.includes(data.agent)) {
              setCompletedAgents(prev => [...prev, data.agent]);
            }
          }

          // Schedule next message with delay (2-3 seconds)
          const delay = Math.floor(Math.random() * 1000) + 2000; // 2-3 seconds
          setTimeout(processNextMessage, delay);
        };

        // Start processing
        processNextMessage();
      })
      .catch(error => {
        console.error('Failed to load mock data:', error);
        setIsRunning(false);
        setMessages([{
          type: 'error',
          agent_name: 'System',
          content: '❌ Failed to load mock workflow data.',
          timestamp: new Date().toISOString()
        }]);
      });
  };

  const stopWorkflow = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsRunning(false);
    setCurrentAgent(null);
  };

  const resetWorkflow = () => {
    setMessages([]);
    setCurrentAgent(null);
    setCompletedAgents([]);
    setIsRunning(false);
  };

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const getAgentStatus = (agentName) => {
    if (completedAgents.includes(agentName)) return 'completed';
    // Agent is active when it has arrow pointing to it or is selected
    if (selectedAgent === agentName && arrowDirection === 'to') return 'active';
    return 'pending';
  };

  // Group agents by level for tree layout
  const agentsByLevel = agents.reduce((acc, agent) => {
    if (!acc[agent.level]) acc[agent.level] = [];
    acc[agent.level].push(agent);
    return acc;
  }, {});

  return (
    <div className="agent-workflow-overlay">
      <div className="agent-workflow-container">
        <div className="workflow-header">
          <div className="workflow-title">
            <h2>Pitchbook Generation Workflow</h2>
          </div>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="workflow-content">
          {/* Left Message Popup */}
          <div className={`message-popup-left ${showLeftPanel ? 'visible' : ''}`}>
            <div className="popup-header">
              <div className="popup-title">
                <span className="popup-icon">📨</span>
                <h3>Agent Messages</h3>
              </div>
              <div className="message-count">{messages.length}</div>
              <button className="popup-toggle" onClick={() => setShowLeftPanel(false)}>
                ‹
              </button>
            </div>
            <div className="popup-messages">
              {messages.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">💬</div>
                  <p>No messages yet.<br/>Start the workflow to see agent communication.</p>
                </div>
              ) : (
                messages.map((msg, index) => (
                  <div key={index} className={`message-item ${msg.type}`}>
                    <div className="message-header">
                      <span className="message-agent">
                        <span className="message-agent-icon">
                          {msg.agent_name === 'System' ? '⚙️' : 
                           msg.agent_name === 'Workflow Orchestrator' || msg.agent_name === 'Coordinator' ? '🎯' :
                           msg.agent_name === 'Quality Validator' ? '✅' :
                           msg.agent_name === 'Financial Analyst' ? '📊' :
                           msg.agent_name === 'Peer Comparison Analyst' ? '🔍' :
                           msg.agent_name === 'Market Insights Analyst' ? '📰' : '🤖'}
                        </span>
                        {msg.agent_name || 'System'}
                      </span>
                    </div>
                    <div className="message-content">{msg.content}</div>
                    {msg.metadata && Object.keys(msg.metadata).length > 0 && (
                      <div className="conversation-data">
                        {Object.entries(msg.metadata)
                          .filter(([key, value]) => value !== null && value !== undefined)
                          .map(([key, value]) => (
                            <div key={key} className="conversation-data-item">
                              <strong>{key}:</strong> {typeof value === 'object' ? JSON.stringify(value, null, 2) : value}
                            </div>
                          ))}
                      </div>
                    )}
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Tree Diagram Container */}
          <div className={`tree-diagram-container ${showLeftPanel ? 'shifted' : ''}`}>
            <div className="agent-tree">
              {Object.keys(agentsByLevel).sort().map((level, levelIndex) => (
                <React.Fragment key={level}>
                  <div className="tree-level">
                    {agentsByLevel[level].map((agent) => (
                      <div key={agent.id} className={`agent-node agent-position-${agent.position}`}>
                        {/* Horizontal arrow FROM Coordinator TO Validator (right-pointing) */}
                        {agent.name === 'Validator' && selectedAgent === 'Validator' && arrowDirection === 'to' && (
                          <div className="arrow-indicator arrow-horizontal-right">
                            <div className="arrow-line-h"></div>
                            <div className="arrow-head-h">▶</div>
                          </div>
                        )}
                        {/* Horizontal arrow FROM Validator back TO Coordinator (left-pointing) */}
                        {agent.name === 'Coordinator' && selectedAgent === 'Validator' && arrowDirection === 'from' && (
                          <div className="arrow-indicator arrow-horizontal-left">
                            <div className="arrow-head-h">◀</div>
                            <div className="arrow-line-h"></div>
                          </div>
                        )}
                        {/* Vertical arrow TO specialist agents */}
                        {agent.level === 1 && selectedAgent === agent.name && arrowDirection === 'to' && (
                          <div className="arrow-indicator arrow-vertical-down">
                            <div className="arrow-line-v"></div>
                            <div className="arrow-head-v">▼</div>
                          </div>
                        )}
                        {/* Vertical arrow FROM specialist agents */}
                        {agent.level === 1 && selectedAgent === agent.name && arrowDirection === 'from' && (
                          <div className="arrow-indicator arrow-vertical-up">
                            <div className="arrow-head-v">▲</div>
                            <div className="arrow-line-v"></div>
                          </div>
                        )}
                        {/* Debug: Log when rendering */}
                        {(() => {
                          if (selectedAgent && (selectedAgent === agent.name || arrowDirection)) {
                            console.log(`Rendering agent ${agent.name}:`, {
                              selectedAgent,
                              agentName: agent.name,
                              arrowDirection,
                              matches: selectedAgent === agent.name,
                              showArrowTo: selectedAgent === agent.name && arrowDirection === 'to',
                              showArrowFrom: selectedAgent === agent.name && arrowDirection === 'from'
                            });
                          }
                          return null;
                        })()}
                        <div 
                          className={`agent-card ${getAgentStatus(agent.name)} ${selectedAgent === agent.name ? 'selected' : ''}`}
                          style={{ '--agent-color': agent.color }}
                        >
                          <div className="agent-status-badge">
                            {getAgentStatus(agent.name) === 'completed' && (
                              <div className="status-check">✓</div>
                            )}
                            {getAgentStatus(agent.name) === 'active' && (
                              <div className="status-spinner">
                                <div className="spinner" style={{ borderTopColor: agent.color }}></div>
                              </div>
                            )}
                            {getAgentStatus(agent.name) === 'pending' && (
                              <div className="status-pending">○</div>
                            )}
                          </div>
                          <div className="agent-icon">{agent.icon}</div>
                          <div className="agent-name">{agent.displayName}</div>
                          <div className="agent-desc">{agent.description}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {/* Connection Arrow between levels */}
                  {levelIndex < Object.keys(agentsByLevel).length - 1 && (
                    <div className={`connection-arrow ${completedAgents.length > levelIndex ? 'active' : ''}`}>
                      ↓
                    </div>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* Right Message Popup (for alternative view or additional info) */}
          <div className={`message-popup-right ${showRightPanel ? 'visible' : ''}`}>
            <div className="popup-header">
              <div className="popup-title">
                <span className="popup-icon">📊</span>
                <h3>Workflow Stats</h3>
              </div>
              <button className="popup-toggle" onClick={() => setShowRightPanel(false)}>
                ›
              </button>
            </div>
            <div className="popup-messages">
              <div className="empty-state">
                <div className="empty-icon">📈</div>
                <p>
                  <strong>Total Agents:</strong> {agents.length}<br/>
                  <strong>Completed:</strong> {completedAgents.length}<br/>
                  <strong>Active:</strong> {currentAgent ? 1 : 0}<br/>
                  <strong>Pending:</strong> {agents.length - completedAgents.length - (currentAgent ? 1 : 0)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Workflow Controls */}
        <div className="workflow-controls">
          {!isRunning ? (
            <>
              <button className="btn-start" onClick={startWorkflow}>
                Start Analysis
              </button>
              <button className="btn-reset" onClick={resetWorkflow}>
                <span className="btn-icon">⟳</span>
                Reset
              </button>
            </>
          ) : (
            <button className="btn-stop" onClick={stopWorkflow}>
              <span className="btn-icon">■</span>
              Stop
            </button>
          )}
          <div className="workflow-status">
            {isRunning ? (
              <span className="status-running">
                <span className="pulse-dot"></span>
                Running...
              </span>
            ) : (
              <span className="status-idle">Ready</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentWorkflow;
