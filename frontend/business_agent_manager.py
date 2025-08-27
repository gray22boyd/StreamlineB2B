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
import openai
from openai import OpenAI

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
        
        # Initialize OpenAI client with fallback handling
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            print("Warning: OPENAI_API_KEY not found in environment variables")
            # Create a dummy client for now to prevent crashes
            self.openai_client = None
        else:
            self.openai_client = OpenAI(api_key=openai_key)
        
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
            # Add project root to path to find agents module
            import sys
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            from agents.marketing_agent.tools import FacebookMarketingTools
            return FacebookMarketingTools(self.business_id)
        except Exception as e:
            raise Exception(f"Failed to create marketing agent: {str(e)}")
    
    def _create_customer_service_agent(self):
        """Create customer service agent with business-specific knowledge base"""
        try:
            # Add project root to path to find agents module
            import sys
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
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

            # Router pattern handles all tool routing dynamically

            # Process with AI
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
        # Handle null user_id for admin context
        user_id_val = self.user_id if self.user_id else '00000000-0000-0000-0000-000000000000'
        
        cur.execute("""
            INSERT INTO agent_conversations 
            (id, business_id, user_id, agent_type, message_history, session_data)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            conversation_id,
            self.business_id,
            user_id_val,
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
            # message_history may be stored as TEXT (JSON string) or JSONB (already a list)
            history = result['message_history']
            if isinstance(history, str):
                try:
                    return json.loads(history)
                except Exception:
                    return []
            if isinstance(history, list):
                return history
            # Unknown type
            return []
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
        Process message with AI and agent tools using OpenAI GPT.
        """
        # If OpenAI client is not available, use fallback
        if not self.openai_client:
            return self._get_fallback_response(agent_type, user_message)
            
        try:
            # Build system prompt based on agent type and business context
            system_prompt = self._build_system_prompt(agent_type)
            
            # Convert conversation history to OpenAI format
            messages = self._format_conversation_for_openai(conversation_history, system_prompt, user_message)
            
            # Get available tools for this agent
            tools = self._get_agent_tools_for_openai(agent_type)
            
            # Call OpenAI API
            print(f"🔧 OPENAI DEBUG: About to call OpenAI with {len(tools) if tools else 0} tools")
            if tools:
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                        temperature=0.7,
                        max_tokens=1000
                    )
                    print(f"🔧 OPENAI SUCCESS: Got response with {len(response.choices[0].message.tool_calls or [])} tool calls")
                except Exception as e:
                    print(f"🔧 OPENAI ERROR: {e}")
                    raise
            else:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
            
            # Process response and handle tool calls
            return self._process_openai_response(response, agent, agent_type)
            
        except Exception as e:
            # Fallback to simple response if OpenAI fails
            print(f"OpenAI error: {e}")
            return self._get_fallback_response(agent_type, user_message)
    
    def _build_system_prompt(self, agent_type: str) -> str:
        """Build system prompt based on agent type and business context"""
        business_name = self.business_data['info']['name']
        business_settings = self.business_data['settings']
        
        base_prompt = f"""You are an AI assistant for {business_name}, a business automation platform.
Be concise and direct. Prefer bullet points. Avoid fluff.

Business Context:
- Business Name: {business_name}
- You can access and use tools specific to this business
- Always maintain context about which business you're serving

"""
        
        if agent_type == 'marketing':
            return base_prompt + f"""Your Role: Marketing Assistant for {business_name}

Available tools:
- list_facebook_pages: Show Facebook pages and stats
- post_to_facebook: Post text to Facebook (requires message)
- post_image_to_facebook: Post image with caption (requires caption and image_url)

Use the 'route' function to:
- action="respond" for general questions, follow-ups, or explanations
- action="tool" when user wants to use a specific tool
- action="clarify" if required parameters are missing

Examples:
- "What can you do?" → respond
- "List my pages" → tool: list_facebook_pages
- "Post hello world" → tool: post_to_facebook with parameters {{"message": "hello world"}}
- "Post 'testing from web'" → tool: post_to_facebook with parameters {{"message": "testing from web"}}
- "please post 'abc' to page" → tool: post_to_facebook with parameters {{"message": "abc"}}
- "Post something" (no content) → clarify what to post

Extract quoted text as message content. Be concise and helpful."""

        elif agent_type == 'customer_service':
            return base_prompt + f"""Your Role: Customer Service Assistant
You specialize in:
- Answering customer questions using {business_name}'s knowledge base
- Providing helpful and accurate information
- Escalating complex issues when appropriate

You have access to {business_name}'s documents and knowledge base.
Always be helpful, professional, and accurate in your responses."""

        elif agent_type == 'analytics':
            return base_prompt + f"""Your Role: Analytics Assistant
You specialize in:
- Business data analysis and insights
- Performance metrics and KPIs
- Reporting and visualization recommendations
- Data-driven decision support

Help {business_name} understand their business performance and make data-driven decisions."""

        else:
            return base_prompt + f"You are a general business assistant for {business_name}."
    
    def _format_conversation_for_openai(self, conversation_history: List[Dict], system_prompt: str, user_message: str) -> List[Dict]:
        """Convert conversation history to OpenAI message format"""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (limit to last 10 messages for context)
        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _get_agent_tools_for_openai(self, agent_type: str) -> List[Dict]:
        """Get single router tool for dynamic tool selection"""
        # Build available tools list for this agent
        available_tools = []
        if agent_type == 'marketing':
            available_tools = [
                {"name": "list_facebook_pages", "description": "List Facebook pages with follower counts", "parameters": {}},
                {"name": "post_to_facebook", "description": "Post text to Facebook page", "parameters": {"message": "string (required)"}},
                {"name": "post_image_to_facebook", "description": "Post image with caption to Facebook", "parameters": {"caption": "string (required)", "image_url": "string (required)"}}
            ]
        
        # Single router tool that handles all intents
        return [{
            "type": "function",
            "function": {
                "name": "route",
                "description": f"Route user intent to appropriate action. Available tools: {[t['name'] for t in available_tools]}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["respond", "tool", "clarify"],
                            "description": "respond=answer directly, tool=use a tool, clarify=ask for missing info"
                        },
                        "message": {
                            "type": "string",
                            "description": "Required if action=respond or clarify. Direct response or clarification question."
                        },
                        "tool_name": {
                            "type": "string",
                            "enum": [t["name"] for t in available_tools],
                            "description": "Required if action=tool. Which tool to use."
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Required if action=tool. Parameters for the chosen tool."
                        }
                    },
                    "required": ["action"]
                }
            }
        }]
    
    def _process_openai_response(self, response, agent, agent_type: str) -> str:
        """Process OpenAI response using router pattern"""
        choice = response.choices[0]
        message = choice.message
        
        # Check if model called the router tool
        if message.tool_calls and message.tool_calls[0].function.name == "route":
            tool_call = message.tool_calls[0]
            
            try:
                # Parse router arguments
                if isinstance(tool_call.function.arguments, str):
                    args = json.loads(tool_call.function.arguments)
                else:
                    args = tool_call.function.arguments or {}
                
                action = args.get("action")
                
                if action == "respond":
                    return args.get("message", "I'm ready to help!")
                
                elif action == "clarify":
                    return args.get("message", "Could you provide more details?")
                
                elif action == "tool":
                    tool_name = args.get("tool_name")
                    parameters = args.get("parameters", {})
                    
                    # Execute the tool
                    result = self._execute_tool_by_name(agent, tool_name, parameters)
                    return self._format_tool_result(tool_name, result)
                
                else:
                    return "I didn't understand that action. How can I help you?"
                    
            except Exception as e:
                print(f"🔧 ROUTER ERROR: {e}")
                return "I had trouble processing that request. Could you try rephrasing?"
        
        # Return regular text response if no tool call
        return message.content or self._get_fallback_response(agent_type, "")
    
    def _execute_tool_by_name(self, agent, tool_name: str, parameters: dict):
        """Execute a tool by name with parameters"""
        try:
            if tool_name == "list_facebook_pages":
                return agent.list_pages()
            elif tool_name == "post_to_facebook":
                message = parameters.get('message')
                if not message:
                    return {"success": False, "error": "Message parameter required"}
                return agent.post_text(message)
            elif tool_name == "post_image_to_facebook":
                caption = parameters.get('caption')
                image_url = parameters.get('image_url')
                if not caption or not image_url:
                    return {"success": False, "error": "Caption and image_url parameters required"}
                return agent.post_image(caption, image_url)
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _format_tool_result(self, tool_name: str, result: dict) -> str:
        """Format tool results into concise user-friendly text"""
        if not isinstance(result, dict):
            return str(result)
        
        if not result.get('success', True):
            error = result.get('error', 'Unknown error')
            return f"Error: {error}"
        
        if tool_name == "list_facebook_pages":
            pages = result.get('pages', [])
            if not pages:
                return "No Facebook pages found."
            lines = [f"• {p['name']} ({p.get('followers', 0)} followers)" for p in pages]
            return "Facebook pages:\n" + "\n".join(lines)
        
        elif tool_name == "post_to_facebook":
            return f"✅ Posted to Facebook successfully"
        
        elif tool_name == "post_image_to_facebook":
            return f"✅ Posted image to Facebook successfully"
        
        else:
            return "✅ Task completed"
    
    def _get_fallback_response(self, agent_type: str, user_message: str) -> str:
        """Fallback response when OpenAI fails"""
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
# JSON fix applied Sun Aug 24 10:12:24 CDT 2025
