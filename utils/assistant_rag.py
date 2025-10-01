import os
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
        
    def embed_query(self, query: str) -> list:
        """Generate embedding for a user query"""
        embeddings = self.client.embeddings.create(
            input=query,
            model="text-embedding-3-small"  # Using small model (1536 dims) for compatibility
        )
        return embeddings.data[0].embedding
    
    def retrieve_context(self, query: str, limit: int = 3) -> list:
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
                WHERE similarity > 0.7
                ORDER BY similarity DESC
            """, (embedding, embedding, limit))
            
            results = supabase.cur.fetchall()
            supabase.close()
            return results
        except Exception as e:
            print(f"Error retrieving context: {e}")
            supabase.close()
            return []
    
    def generate_response(self, query: str, session_id: str = None) -> dict:
        """Generate response using RAG"""
        
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
    
    def save_lead(self, name: str, email: str, initial_query: str = None, session_id: str = None):
        """Save lead information to database"""
        supabase = SupabaseClient(customer_schema="public")
        
        try:
            # Get conversation history if available
            conversation_history = None
            if session_id and session_id in self.conversation_memory:
                conversation_history = str(self.conversation_memory[session_id])
            
            supabase.cur.execute("""
                INSERT INTO assistant_leads 
                (name, email, initial_query, conversation_history, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                RETURNING id
            """, (name, email, initial_query, conversation_history))
            
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

