/**
 * Cosmos DB Service - Frontend
 * 
 * PURPOSE: Persist completed workflow execution history to view later
 * 
 * WORKFLOW:
 * 1. When user runs "Start Agent Analysis", workflow is created with status='in_progress'
 * 2. As agents respond, messages are saved to the workflow
 * 3. When complete, status is updated to 'completed'
 * 4. User can view ALL completed workflows in the Workflows page
 * 5. Each workflow shows STATIC history: agent conversations + outputs (NO re-execution)
 * 
 * DATA FLOW (Updated to use Backend API):
 * - Primary: Backend API → Cosmos DB (with Managed Identity)
 * - Fallback 1: localStorage (browser storage)
 * - Fallback 2: workflow.json (mock data when nothing exists)
 * 
 * Handles workflow data persistence through Backend API
 */

class CosmosDBService {
  constructor() {
    // Backend API configuration
    this.backendUrl = process.env.REACT_APP_API_URL || 'https://pitchbook-backend.agreeablewave-76bf5979.eastus.azurecontainerapps.io';
  }

  /**
   * Generate unique workflow ID
   */
  generateWorkflowId() {
    const timestamp = new Date().toISOString().split('T')[0];
    const randomStr = Math.random().toString(36).substring(2, 8);
    return `workflow-${timestamp}-${randomStr}`;
  }

  /**
   * Create a new workflow document via Backend API
   * Each agent run creates a UNIQUE workflow with new ID
   */
  async createWorkflow(workflowData) {
    try {
      console.log('📝 Creating NEW workflow via backend API');

      // Try Backend API first
      const response = await fetch(`${this.backendUrl}/api/workflows`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(workflowData)
      });

      const result = await response.json();
      
      if (result.success) {
        console.log('✅ Workflow created via Backend API:', result.workflowId);
        return { success: true, workflowId: result.workflowId, document: result.workflow };
      } else {
        throw new Error(result.error || 'Failed to create workflow');
      }
    } catch (error) {
      console.error('❌ Error creating workflow via backend, using localStorage:', error);
      
      // Fallback: save to localStorage
      const workflowId = this.saveToLocalStorage(workflowData);
      console.log('📦 Workflow saved to localStorage:', workflowId);
      console.log('📊 Total workflows in localStorage:', this.getAllFromLocalStorage().length);
      return { success: true, workflowId };
    }
  }

  /**
   * Update workflow with new message
   */
  async addMessage(workflowId, message) {
    try {
      // Try Backend API first
      const response = await fetch(`${this.backendUrl}/api/workflows/${workflowId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(message)
      });

      const result = await response.json();
      
      if (result.success) {
        console.log('✅ Message added via Backend API:', workflowId);
        return { success: true };
      } else {
        throw new Error(result.error || 'Failed to add message');
      }
    } catch (error) {
      console.error('❌ Error adding message via backend, using localStorage:', error);
      
      // Fallback: Update in localStorage
      const workflow = this.getFromLocalStorage(workflowId);
      if (workflow) {
        if (!workflow.messages) {
          workflow.messages = [];
        }
        workflow.messages.push({
          ...message,
          timestamp: message.timestamp || new Date().toISOString()
        });
        this.updateInLocalStorage(workflowId, workflow);
        console.log('✅ Message added to workflow in localStorage:', workflowId);
        return { success: true };
      }
      
      return { success: false, error: 'Workflow not found' };
    }
  }

  /**
   * Update workflow status
   */
  async updateWorkflowStatus(workflowId, status) {
    try {
      // Try Backend API first
      const response = await fetch(`${this.backendUrl}/api/workflows/${workflowId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });

      const result = await response.json();
      
      if (result.success) {
        console.log('✅ Workflow status updated via Backend API:', workflowId, status);
        return { success: true };
      } else {
        throw new Error(result.error || 'Failed to update status');
      }
    } catch (error) {
      console.error('❌ Error updating status via backend, using localStorage:', error);
      
      // Fallback: Update in localStorage
      const workflow = this.getFromLocalStorage(workflowId);
      if (workflow) {
        workflow.status = status;
        workflow.completedAt = new Date().toISOString();
        this.updateInLocalStorage(workflowId, workflow);
        console.log('✅ Workflow status updated in localStorage:', workflowId, status);
        return { success: true };
      }
      
      return { success: false, error: 'Workflow not found' };
    }
  }

  /**
   * Get workflow by ID
   */
  async getWorkflow(workflowId) {
    try {
      const response = await fetch(`${this.backendUrl}/api/workflows/${workflowId}`);
      const result = await response.json();
      
      if (result.success) {
        return result.workflow;
      } else {
        throw new Error(result.error || 'Failed to get workflow');
      }
    } catch (error) {
      console.error('❌ Error getting workflow from backend:', error);
      
      // Fallback: get from localStorage
      return this.getFromLocalStorage(workflowId);
    }
  }

  /**
   * Get all workflows
   * Returns ALL workflow items from Backend API
   * Each item becomes a separate workflow card in the UI
   */
  async getAllWorkflows() {
    try {
      const response = await fetch(`${this.backendUrl}/api/workflows`);
      const result = await response.json();
      
      if (result.workflows) {
        console.log(`📊 Retrieved ${result.workflows.length} workflows from Backend API`);
        return result.workflows;
      } else {
        throw new Error(result.error || 'Failed to get workflows');
      }
    } catch (error) {
      console.error('❌ Error getting workflows from backend:', error);
      
      // Fallback: get from localStorage
      const localWorkflows = this.getAllFromLocalStorage();
      console.log(`📦 Retrieved ${localWorkflows.length} workflows from localStorage`);
      return localWorkflows;
    }
  }

  /**
   * LocalStorage fallback methods
   * Each workflow is a separate item in the array
   */
  saveToLocalStorage(workflow) {
    try {
      const workflowId = this.generateWorkflowId();
      const document = {
        id: workflowId,
        workflowId,
        createdAt: new Date().toISOString(),
        status: 'in_progress',
        messages: [],
        ...workflow
      };

      const workflows = this.getAllFromLocalStorage();
      workflows.push(document); // Add NEW workflow to array
      localStorage.setItem('pitchbook_workflows', JSON.stringify(workflows));
      
      console.log('📦 Workflow saved to localStorage:', workflowId);
      console.log('📊 Total workflows in localStorage:', workflows.length);
      return workflowId;
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  }

  appendToLocalStorage(workflowId, message) {
    try {
      const workflows = this.getAllFromLocalStorage();
      const workflow = workflows.find(w => w.id === workflowId);
      
      if (workflow) {
        workflow.messages.push({
          ...message,
          timestamp: new Date().toISOString()
        });
        localStorage.setItem('pitchbook_workflows', JSON.stringify(workflows));
      }
    } catch (error) {
      console.error('Error appending to localStorage:', error);
    }
  }

  updateInLocalStorage(workflowId, updatedWorkflow) {
    try {
      const workflows = this.getAllFromLocalStorage();
      const index = workflows.findIndex(w => w.id === workflowId);
      
      if (index !== -1) {
        workflows[index] = updatedWorkflow;
        localStorage.setItem('pitchbook_workflows', JSON.stringify(workflows));
        console.log('📦 Workflow updated in localStorage:', workflowId);
      }
    } catch (error) {
      console.error('Error updating in localStorage:', error);
    }
  }

  getFromLocalStorage(workflowId) {
    try {
      const workflows = this.getAllFromLocalStorage();
      return workflows.find(w => w.id === workflowId);
    } catch (error) {
      console.error('Error getting from localStorage:', error);
      return null;
    }
  }

  getAllFromLocalStorage() {
    try {
      const data = localStorage.getItem('pitchbook_workflows');
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error getting all from localStorage:', error);
      return [];
    }
  }

  clearLocalStorage() {
    try {
      localStorage.removeItem('pitchbook_workflows');
      console.log('🗑️ Cleared all workflows from localStorage');
    } catch (error) {
      console.error('Error clearing localStorage:', error);
    }
  }
}

// Export singleton instance
const cosmosDBService = new CosmosDBService();

// Expose to window for debugging
if (typeof window !== 'undefined') {
  window.cosmosDBService = cosmosDBService;
}

export default cosmosDBService;
