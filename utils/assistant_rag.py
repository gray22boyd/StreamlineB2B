import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI
from utils.supa import SupabaseClient
from dotenv import load_dotenv

load_dotenv()

class AssistantRAG:
    """RAG system for the Streamline Automation assistant"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.table_name = "assistant_knowledge_base"
        self.conversation_memory = {}  # Store conversation history by session_id
        self.pending_leads = {}  # Track users in lead capture flow
        
    def embed_query(self, query: str) -> list:
        """Generate embedding for a user query"""
        embeddings = self.client.embeddings.create(
            input=query,
            model="text-embedding-3-small"  # Using small model (1536 dims) for compatibility
        )
        return embeddings.data[0].embedding
    
    def retrieve_context(self, query: str, limit: int = 5) -> list:
        """Retrieve relevant context from knowledge base using vector similarity"""
        embedding = self.embed_query(query)
        
        supabase = SupabaseClient(customer_schema="public")
        try:
            # Use pgvector's <=> operator for cosine distance
            supabase.cur.execute(f"""
                SELECT text_content, chunk_type, similarity
                FROM (
                    SELECT 
                        text_content,
                        chunk_type,
                        1 - (embedding <=> %s::vector) as similarity
                    FROM {self.table_name}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                ) sub
                WHERE similarity > 0.5
                ORDER BY similarity DESC
            """, (embedding, embedding, limit))
            
            results = supabase.cur.fetchall()
            supabase.close()
            return results
        except Exception as e:
            print(f"Error retrieving context: {e}")
            supabase.close()
            return []
    
    def detect_interest(self, query: str) -> bool:
        """Detect if user is expressing interest in services"""
        interest_phrases = [
            'interested', 'get started', 'sign up', 'contact', 'reach out',
            'talk to someone', 'speak to', 'demo', 'consultation', 'meeting',
            'how do i', 'want to learn more', 'pricing', 'quote', 'proposal'
        ]
        query_lower = query.lower()
        return any(phrase in query_lower for phrase in interest_phrases)
    
    def send_lead_email(self, name: str, email: str, business_type: str, initial_query: str = None):
        """Send email notification for new lead"""
        try:
            sender_email = os.getenv('GMAIL_EMAIL', 'grayson@streamlineautomationco.com')
            sender_password = os.getenv('GMAIL_APP_PASSWORD')
            
            if not sender_password:
                print("Warning: GMAIL_APP_PASSWORD not set, skipping email")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = sender_email  # Send to yourself
            msg['Subject'] = f'🎯 New Lead: {name} - {business_type}'
            
            body = f"""
New lead from the AI Assistant!

📧 Email: {email}
👤 Name: {name}
🏢 Business Type: {business_type}
💬 Initial Query: {initial_query or 'N/A'}

---
This lead was captured automatically by your AI assistant.
Login to your admin dashboard to view all leads and conversation history.
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email via Gmail SMTP
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            print(f"✅ Lead email sent for {name}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending lead email: {e}")
            return False
    
    def generate_response(self, query: str, session_id: str = None) -> dict:
        """Generate response using RAG"""
        
        # Check if user is in lead capture flow
        if session_id and session_id in self.pending_leads:
            return self.handle_lead_capture(query, session_id)
        
        # Check if user is expressing interest
        if self.detect_interest(query) and session_id:
            self.pending_leads[session_id] = {
                'step': 'name',
                'initial_query': query
            }
            return {
                "success": True,
                "response": "That's great! I'd love to connect you with our team. To get started, could you please share your name?",
                "sources_found": False,
                "collecting_lead": True
            }
        
        # Retrieve relevant context
        context_results = self.retrieve_context(query)
        
        # Build context string
        if context_results:
            context = "\n\n".join([
                f"[{result['chunk_type']}] {result['text_content']}"
                for result in context_results
            ])
        else:
            context = "No specific information found."
        
        # Get conversation history
        conversation_history = []
        if session_id and session_id in self.conversation_memory:
            conversation_history = self.conversation_memory[session_id][-6:]  # Last 3 exchanges
        
        # Build messages for GPT
        system_prompt = """You are a helpful assistant for Streamline Automation, a company that builds custom AI agents and automation solutions.

Use the provided context to answer user questions accurately. If the context doesn't contain the answer, politely say:
"I don't have that information right now. For specific questions, please email support@streamlineautomation.co and our team will assist you."

Be friendly, professional, and concise. Focus on helping potential clients understand what Streamline Automation does and how it can help them.

Context:
{context}"""
        
        messages = [
            {"role": "system", "content": system_prompt.format(context=context)}
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        # Generate response
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            
            # Update conversation memory
            if session_id:
                if session_id not in self.conversation_memory:
                    self.conversation_memory[session_id] = []
                self.conversation_memory[session_id].append({"role": "user", "content": query})
                self.conversation_memory[session_id].append({"role": "assistant", "content": assistant_message})
                
                # Keep only last 10 messages
                if len(self.conversation_memory[session_id]) > 10:
                    self.conversation_memory[session_id] = self.conversation_memory[session_id][-10:]
            
            return {
                "success": True,
                "response": assistant_message,
                "sources_found": len(context_results) > 0
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "success": False,
                "response": "I'm having trouble processing your request right now. Please try again or email support@streamlineautomation.co",
                "error": str(e)
            }
    
    def handle_lead_capture(self, query: str, session_id: str) -> dict:
        """Handle the conversational lead capture flow"""
        lead_data = self.pending_leads[session_id]
        
        if lead_data['step'] == 'name':
            # Store name and ask for email
            lead_data['name'] = query
            lead_data['step'] = 'email'
            return {
                "success": True,
                "response": f"Nice to meet you, {query}! What's your email address?",
                "sources_found": False,
                "collecting_lead": True
            }
        
        elif lead_data['step'] == 'email':
            # Validate email and ask for business type
            if '@' not in query or '.' not in query:
                return {
                    "success": True,
                    "response": "That doesn't look like a valid email. Could you please provide your email address?",
                    "sources_found": False,
                    "collecting_lead": True
                }
            lead_data['email'] = query
            lead_data['step'] = 'business_type'
            return {
                "success": True,
                "response": "Perfect! And what type of business do you run? (e.g., e-commerce, tech startup, professional services, etc.)",
                "sources_found": False,
                "collecting_lead": True
            }
        
        elif lead_data['step'] == 'business_type':
            # Store business type and save lead
            lead_data['business_type'] = query
            
            # Save to database with business_type in notes field
            result = self.save_lead(
                name=lead_data['name'],
                email=lead_data['email'],
                business_type=lead_data['business_type'],
                initial_query=lead_data.get('initial_query'),
                session_id=session_id
            )
            
            # Send email notification
            self.send_lead_email(
                name=lead_data['name'],
                email=lead_data['email'],
                business_type=lead_data['business_type'],
                initial_query=lead_data.get('initial_query')
            )
            
            # Clear pending lead
            del self.pending_leads[session_id]
            
            return {
                "success": True,
                "response": f"Thank you! We've received your information and someone from our team will reach out to you at {lead_data['email']} shortly. Is there anything else I can help you with in the meantime?",
                "sources_found": False,
                "lead_captured": True
            }
        
        return {
            "success": False,
            "response": "Something went wrong. Please try again.",
            "sources_found": False
        }
    
    def save_lead(self, name: str, email: str, business_type: str = None, initial_query: str = None, session_id: str = None):
        """Save lead information to database"""
        supabase = SupabaseClient(customer_schema="public")
        
        try:
            # Get conversation history if available
            conversation_history = None
            if session_id and session_id in self.conversation_memory:
                conversation_history = str(self.conversation_memory[session_id])
            
            # Store business type in notes field
            notes = f"Business Type: {business_type}" if business_type else None
            
            supabase.cur.execute("""
                INSERT INTO assistant_leads 
                (name, email, initial_query, conversation_history, notes, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                RETURNING id
            """, (name, email, initial_query, conversation_history, notes))
            
            lead_id = supabase.cur.fetchone()['id']
            supabase.commit()
            supabase.close()
            
            return {"success": True, "lead_id": lead_id}
            
        except Exception as e:
            print(f"Error saving lead: {e}")
            supabase.rollback()
            supabase.close()
            return {"success": False, "error": str(e)}


def main():
    """Test the assistant RAG system"""
    assistant = AssistantRAG()
    
    # Test query
    response = assistant.generate_response(
        "What does Streamline Automation do?",
        session_id="test_session"
    )
    
    print("Response:", response['response'])
    print("Sources found:", response['sources_found'])


if __name__ == "__main__":
    main()

