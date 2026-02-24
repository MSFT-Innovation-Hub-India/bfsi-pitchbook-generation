"""
Cosmos DB Service - Backend with Managed Identity Support
Handles workflow persistence using Azure Managed Identity or connection string
"""

import os
from datetime import datetime
from typing import List, Dict, Optional
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential


class CosmosDBService:
    def __init__(self):
        """Initialize Cosmos DB client with Managed Identity or connection string"""
        
        # Option 1: Use Managed Identity (production)
        if os.getenv('AZURE_COSMOS_ENDPOINT'):
            endpoint = os.getenv('AZURE_COSMOS_ENDPOINT')
            credential = DefaultAzureCredential()
            self.client = CosmosClient(endpoint, credential=credential)
            print("✅ Cosmos DB connected using Managed Identity")
        
        # Option 2: Use connection string (fallback)
        elif os.getenv('COSMOS_CONNECTION_STRING'):
            connection_string = os.getenv('COSMOS_CONNECTION_STRING')
            self.client = CosmosClient.from_connection_string(connection_string)
            print("✅ Cosmos DB connected using connection string")
        
        else:
            raise ValueError("No Cosmos DB credentials found in environment")
        
        # Database and container configuration from environment
        self.database_name = os.getenv('COSMOS_DATABASE_NAME', 'pitchbook_d')
        self.container_name = os.getenv('COSMOS_CONTAINER_NAME', 'pitchbook_c')
        
        self.database = self.client.get_database_client(self.database_name)
        self.container = self.database.get_container_client(self.container_name)
    
    def generate_workflow_id(self) -> str:
        """Generate unique workflow ID"""
        timestamp = datetime.utcnow().isoformat().split('T')[0]
        import random
        import string
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"workflow-{timestamp}-{random_str}"
    
    def create_workflow(self, workflow_data: Dict) -> Dict:
        """Create a new workflow document"""
        workflow_id = self.generate_workflow_id()
        
        document = {
            'id': workflow_id,
            'workflowId': workflow_id,
            'createdAt': datetime.now().astimezone().isoformat(),
            'status': 'in_progress',
            'messages': [],
            **workflow_data
        }
        
        created = self.container.create_item(body=document)
        print(f"📝 Workflow created: {workflow_id}")
        return created
    
    def get_workflow(self, workflow_id: str) -> Dict:
        """Get workflow by ID"""
        try:
            return self.container.read_item(item=workflow_id, partition_key=workflow_id)
        except Exception as e:
            print(f"❌ Error getting workflow {workflow_id}: {e}")
            raise
    
    def add_message(self, workflow_id: str, message: Dict) -> Dict:
        """Add message to workflow"""
        workflow = self.get_workflow(workflow_id)
        
        if 'messages' not in workflow:
            workflow['messages'] = []
        
        message_with_timestamp = {
            **message,
            'timestamp': message.get('timestamp', datetime.now().astimezone().isoformat())
        }
        
        workflow['messages'].append(message_with_timestamp)
        
        updated = self.container.replace_item(
            item=workflow_id,
            body=workflow
        )
        
        print(f"✅ Message added to workflow {workflow_id}")
        return updated
    
    def update_workflow_status(self, workflow_id: str, status: str) -> Dict:
        """Update workflow status"""
        workflow = self.get_workflow(workflow_id)
        workflow['status'] = status
        workflow['completedAt'] = datetime.now().astimezone().isoformat()
        
        updated = self.container.replace_item(
            item=workflow_id,
            body=workflow
        )
        
        print(f"✅ Workflow {workflow_id} status updated to {status}")
        return updated
    
    def get_all_workflows(self) -> List[Dict]:
        """Get all workflows ordered by creation date"""
        query = "SELECT * FROM c ORDER BY c.createdAt DESC"
        
        workflows = list(self.container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        print(f"📊 Retrieved {len(workflows)} workflows")
        return workflows
    
    def get_completed_workflows(self) -> List[Dict]:
        """Get only completed workflows"""
        query = "SELECT * FROM c WHERE c.status = 'completed' ORDER BY c.createdAt DESC"
        
        workflows = list(self.container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        print(f"📊 Retrieved {len(workflows)} completed workflows")
        return workflows


# Singleton instance
cosmos_service = None

def get_cosmos_service() -> Optional[CosmosDBService]:
    """Get or create Cosmos DB service instance"""
    global cosmos_service
    
    if cosmos_service is None:
        try:
            cosmos_service = CosmosDBService()
        except Exception as e:
            print(f"⚠️ Cosmos DB not available: {e}")
            return None
    
    return cosmos_service
