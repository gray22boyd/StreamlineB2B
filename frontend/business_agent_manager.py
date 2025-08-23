"""
Business Agent Manager - Core orchestrator for personalized AI agents

Handles:
- Business-specific agent access control
- Personalized agent instances with business context
- Conversation management and tool execution
- Integration with existing database schema
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


class BusinessAgentManager:
    """
    Central manager for business-specific AI agents.
    
    Each business gets personalized agents that:
    - Use their own credentials (Facebook tokens, etc.)
    - Access their own data (documents, customers)
    - Have customized behavior based on business settings
    """
    
    def __init__(self, business_id: str, user_id: str = None):
        self.business_id = business_id
        self.user_id = user_id
        self.db_connection = self._get_db_connection()
        self.business_data = self._load_business_data()
        
    def _get_db_connection(self):
        """Get database connection with RealDictCursor for easier data access"""
        return psycopg2.connect(
            os.getenv('DATABASE_URL'),
            cursor_factory=psycopg2.extras.RealDictCursor
        )
    
    def _load_business_data(self):
        """Load business information and settings"""
        cur = self.db_connection.cursor()
        
        # Get business basic info
        cur.execute("""
            SELECT id, name, email, created_at
            FROM businesses 
            WHERE id = %s
        """, (self.business_id,))
        
        business = cur.fetchone()
        if not business:
            raise ValueError(f"Business {self.business_id} not found")
        
        # Get business settings
        cur.execute("""
            SELECT setting_key, setting_value
            FROM business_settings
            WHERE business_id = %s
        """, (self.business_id,))
        
        settings = {row['setting_key']: row['setting_value'] for row in cur.fetchall()}
        
        cur.close()
        
        return {
            'info': dict(business),
            'settings': settings
        }
    
    def get_available_agents(self) -> List[str]:
        """
        Get list of agent types this business/user has access to.
        
        Returns:
            List of agent type strings (e.g., ['marketing', 'customer_service'])
        """
        cur = self.db_connection.cursor()
        
        if self.user_id:
            # Regular user - get their specific agent access
            cur.execute("""
                SELECT DISTINCT ua.agent_type 
                FROM user_agents ua
                WHERE ua.user_id = %s AND ua.is_enabled = true
                ORDER BY ua.agent_type
            """, (self.user_id,))
        else:
            # Admin mode - get all agents for this business
            cur.execute("""
                SELECT DISTINCT ua.agent_type 
                FROM user_agents ua
                JOIN users u ON ua.user_id = u.id
                WHERE u.business_id = %s AND ua.is_enabled = true
                ORDER BY ua.agent_type
            """, (self.business_id,))
        
        agents = [row['agent_type'] for row in cur.fetchall()]
        cur.close()
        
        return agents
    
    def get_agent_instance(self, agent_type: str):
        """
        Create personalized agent instance for this business.
        
        Args:
            agent_type: Type of agent ('marketing', 'customer_service', etc.)
            
        Returns:
            Agent instance configured for this business
        """
        if agent_type not in self.get_available_agents():
            raise ValueError(f"Agent '{agent_type}' not available for this business")
        
        if agent_type == 'marketing':
            return self._create_marketing_agent()
        elif agent_type == 'customer_service':
            return self._create_customer_service_agent()
        elif agent_type == 'analytics':
            return self._create_analytics_agent()
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
    
    def _create_marketing_agent(self):
        """Create marketing agent with business-specific Facebook credentials"""
        try:
            from agents.marketing_agent.tools import FacebookMarketingTools
            return FacebookMarketingTools(self.business_id)
        except Exception as e:
            raise Exception(f"Failed to create marketing agent: {str(e)}")
    
    def _create_customer_service_agent(self):
        """Create customer service agent with business-specific knowledge base"""
        try:
            from agents.customer_service_agent.tools import CustomerServiceTools
            return CustomerServiceTools(
                business_id=self.business_id,
                business_name=self.business_data['info']['name']
            )
        except Exception as e:
            raise Exception(f"Failed to create customer service agent: {str(e)}")
    
    def _create_analytics_agent(self):
        """Create analytics agent with business-specific data access"""
        # TODO: Implement when analytics agent is ready
        raise NotImplementedError("Analytics agent not yet implemented")
    
    def process_message(self, agent_type: str, user_message: str, conversation_id: str = None) -> Dict[str, Any]:
        """
        Process user message with specified agent type.
        
        Args:
            agent_type: Which agent to use
            user_message: User's message
            conversation_id: Optional conversation ID for context
            
        Returns:
            Dict with response and metadata
        """
        try:
            # Get or create conversation
            if not conversation_id:
                conversation_id = self._create_conversation(agent_type)
            
            # Load conversation history
            conversation_history = self._load_conversation_history(conversation_id)
            
            # Get agent instance
            agent = self.get_agent_instance(agent_type)
            
            # Process with AI (will implement OpenAI integration next)
            response = self._process_with_ai(agent, agent_type, user_message, conversation_history)
            
            # Save conversation update
            self._save_conversation_message(conversation_id, user_message, response)
            
            return {
                'success': True,
                'response': response,
                'conversation_id': conversation_id,
                'agent_type': agent_type,
                'business_name': self.business_data['info']['name']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'agent_type': agent_type
            }
    
    def _create_conversation(self, agent_type: str) -> str:
        """Create new conversation record"""
        conversation_id = str(uuid.uuid4())
        
        cur = self.db_connection.cursor()
        cur.execute("""
            INSERT INTO agent_conversations 
            (id, business_id, user_id, agent_type, message_history, session_data)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            conversation_id,
            self.business_id,
            self.user_id,
            agent_type,
            json.dumps([]),
            json.dumps({})
        ))
        
        self.db_connection.commit()
        cur.close()
        
        return conversation_id
    
    def _load_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Load conversation history from database"""
        cur = self.db_connection.cursor()
        cur.execute("""
            SELECT message_history
            FROM agent_conversations
            WHERE id = %s AND business_id = %s
        """, (conversation_id, self.business_id))
        
        result = cur.fetchone()
        cur.close()
        
        if result and result['message_history']:
            return json.loads(result['message_history'])
        return []
    
    def _save_conversation_message(self, conversation_id: str, user_message: str, ai_response: str):
        """Save message exchange to conversation history"""
        cur = self.db_connection.cursor()
        
        # Get current history
        history = self._load_conversation_history(conversation_id)
        
        # Add new messages
        history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        history.append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update database
        cur.execute("""
            UPDATE agent_conversations 
            SET message_history = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND business_id = %s
        """, (json.dumps(history), conversation_id, self.business_id))
        
        self.db_connection.commit()
        cur.close()
    
    def _process_with_ai(self, agent, agent_type: str, user_message: str, conversation_history: List[Dict]) -> str:
        """
        Process message with AI and agent tools.
        
        This is where we'll integrate OpenAI GPT with tool calling.
        For now, return a placeholder response.
        """
        # TODO: Implement OpenAI integration
        business_name = self.business_data['info']['name']
        
        if agent_type == 'marketing':
            return f"Hello! I'm the marketing assistant for {business_name}. I can help you with Facebook posting, page management, and marketing analytics. What would you like to do today?"
        elif agent_type == 'customer_service':
            return f"Hi! I'm the customer service assistant for {business_name}. I have access to your knowledge base and can help answer customer questions. How can I assist you?"
        else:
            return f"Hello! I'm your {agent_type} assistant for {business_name}. How can I help you today?"
    
    def execute_tool(self, agent_type: str, tool_name: str, parameters: Dict, conversation_id: str = None) -> Dict[str, Any]:
        """
        Execute agent tool with business context.
        
        Args:
            agent_type: Which agent's tool to use
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            conversation_id: Optional conversation context
            
        Returns:
            Tool execution result
        """
        try:
            agent = self.get_agent_instance(agent_type)
            
            # Execute the tool
            if hasattr(agent, tool_name):
                tool_method = getattr(agent, tool_name)
                result = tool_method(**parameters)
            else:
                raise ValueError(f"Tool '{tool_name}' not found on {agent_type} agent")
            
            # Log tool execution
            if conversation_id:
                self._log_tool_execution(conversation_id, tool_name, parameters, result)
            
            return {
                'success': True,
                'result': result,
                'tool_name': tool_name,
                'agent_type': agent_type
            }
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'tool_name': tool_name,
                'agent_type': agent_type
            }
            
            # Log failed execution
            if conversation_id:
                self._log_tool_execution(conversation_id, tool_name, parameters, error_result, success=False)
            
            return error_result
    
    def _log_tool_execution(self, conversation_id: str, tool_name: str, parameters: Dict, result: Dict, success: bool = True):
        """Log tool execution for debugging and audit"""
        cur = self.db_connection.cursor()
        cur.execute("""
            INSERT INTO agent_tool_executions 
            (conversation_id, tool_name, parameters, result, success, error_message)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            conversation_id,
            tool_name,
            json.dumps(parameters),
            json.dumps(result),
            success,
            result.get('error') if not success else None
        ))
        
        self.db_connection.commit()
        cur.close()
    
    def get_conversation_list(self, agent_type: str = None) -> List[Dict]:
        """Get list of conversations for this business/user"""
        cur = self.db_connection.cursor()
        
        query = """
            SELECT id, agent_type, created_at, updated_at
            FROM agent_conversations
            WHERE business_id = %s
        """
        params = [self.business_id]
        
        if self.user_id:
            query += " AND user_id = %s"
            params.append(self.user_id)
        
        if agent_type:
            query += " AND agent_type = %s"
            params.append(agent_type)
        
        query += " ORDER BY updated_at DESC"
        
        cur.execute(query, params)
        conversations = cur.fetchall()
        cur.close()
        
        return [dict(conv) for conv in conversations]
    
    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'db_connection'):
            self.db_connection.close()


def create_business_agent_manager(business_id: str, user_id: str = None) -> BusinessAgentManager:
    """
    Factory function to create BusinessAgentManager instances.
    
    Args:
        business_id: UUID of the business
        user_id: Optional UUID of the user (for access control)
        
    Returns:
        Configured BusinessAgentManager instance
    """
    return BusinessAgentManager(business_id, user_id)
