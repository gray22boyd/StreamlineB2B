#!/usr/bin/env python3
"""
Load Streamline Automation knowledge base into the database with embeddings.
Run this once to populate the assistant's knowledge base.
"""

import os
from openai import OpenAI
from utils.supa import SupabaseClient
from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_BASE = """# Streamline Automation — Knowledge Base

## Company Overview

Streamline Automation builds **custom AI agents** designed around the unique problems of each business.

- We do not sell generic chatbots or pre-packaged agents.
- Each solution is tailored to the client's workflows, tools, and challenges.
- Our goal is to reduce repetitive work, improve efficiency, and help businesses scale through automation.

---

## Services

### Custom AI Agents

- **Customer Support Agents**: Answer company FAQs, handle support tickets, escalate issues.
- **Marketing Agents**: Automate ad campaigns, reporting, and analytics.
- **Operations Agents**: Manage scheduling, order tracking, and repetitive workflows.
- **Research Agents**: Collect and analyze industry-specific data.
- **Other Custom Agents**: Built for unique business challenges identified during consultation.

### Workflow Automation

- Automates repetitive manual tasks.
- Reduces human error.
- Saves time and increases efficiency.

### Integrations

- Connects with CRMs, spreadsheets, Google Workspace, Slack, cloud platforms, and APIs.
- Works with the tools a business already uses.

---

## Pricing

- Pricing is **customized for each client**.
- There is no fixed cost because every agent is unique.
- Pricing depends on:
    - Type of agent.
    - Level of customization.
    - Complexity of integrations.
- An exact proposal is provided after a discovery call and project scoping.

---

## FAQs

**Q: What does Streamline Automation do?**

A: We build custom AI agents and automation systems designed specifically for each business's problems.

**Q: Do you provide pre-built agents?**

A: No. Every agent is customized to fit the client's workflows, tools, and challenges.

**Q: What types of agents can you build?**

A: We can build customer support agents, marketing agents, operations agents, research agents, and other specialized agents depending on your needs.

**Q: How do you determine what kind of agent we need?**

A: We start with a discovery process, analyzing your workflows and pain points. Then we propose an agent that directly solves those problems.

**Q: Can you integrate with our existing tools?**

A: Yes. We build custom integrations for CRMs, spreadsheets, Google Workspace, Slack, APIs, and other business systems.

**Q: Do I need technical expertise to use your agents?**

A: No. We handle the setup and technical details. Your team only needs to interact with the agent through simple interfaces.

**Q: How does pricing work?**

A: Pricing depends on the type of agent, level of customization, and integrations required. We provide a tailored proposal after consultation.

**Q: How long does it take to build an agent?**

A: Simple projects may take days. More complex, fully customized solutions typically take several weeks.

**Q: Can you update or expand agents after launch?**

A: Yes. Agents can be continuously updated and improved as your business grows.

**Q: Do you offer ongoing support and maintenance?**

A: Yes. We provide optional support packages for monitoring, updates, and improvements.

**Q: What industries do you serve?**

A: We work with a wide range of industries including technology, e-commerce, professional services, and startups.

**Q: Do your agents use company-specific data?**

A: Yes. We train and configure each agent on your documents, FAQs, and workflows so it reflects your business knowledge.

**Q: Is my company's data secure?**

A: Yes. All data used for training and integration is handled securely, and we follow industry best practices for data privacy.

**Q: Can you build multiple agents for different departments?**

A: Yes. Many clients use different agents for support, marketing, operations, and research. They can work independently or together.

**Q: What if we're not sure what we need?**

A: That's fine. During the consultation, we'll help identify where automation or an agent can bring the most value.

---

## Fallback Policy

If a user asks a question that is not covered in this documentation, the chatbot should respond with:

> "I don't have that information right now. For specific questions, please email support@streamlineautomation.co and our team will assist you."

---

## Contact Information

- 📧 Email: support@streamlineautomation.co
"""


def chunk_knowledge_base(text: str, chunk_size: int = 200, overlap: int = 50) -> list:
    """Split knowledge base into overlapping chunks with metadata"""
    chunks = []
    
    # Split by major sections
    sections = text.split('---')
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Determine chunk type
        chunk_type = "general"
        if "##" in section:
            if "FAQ" in section:
                chunk_type = "faq"
            elif "Service" in section:
                chunk_type = "services"
            elif "Pricing" in section:
                chunk_type = "pricing"
            elif "Overview" in section:
                chunk_type = "overview"
            elif "Contact" in section:
                chunk_type = "contact"
        
        # Further split long sections by words
        words = section.split()
        if len(words) <= chunk_size:
            chunks.append({
                "text": section,
                "chunk_type": chunk_type
            })
        else:
            # Create overlapping chunks
            start = 0
            while start < len(words):
                end = min(start + chunk_size, len(words))
                chunk_text = " ".join(words[start:end])
                chunks.append({
                    "text": chunk_text,
                    "chunk_type": chunk_type
                })
                if end == len(words):
                    break
                start = start + chunk_size - overlap
    
    return chunks


def embed_chunks(chunks: list) -> list:
    """Generate embeddings for chunks"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    texts = [chunk['text'] for chunk in chunks]
    
    embeddings_response = client.embeddings.create(
        input=texts,
        model="text-embedding-3-small"  # Using small model (1536 dims) for compatibility
    )
    
    for i, chunk in enumerate(chunks):
        chunk['embedding'] = embeddings_response.data[i].embedding
    
    return chunks


def upload_to_database(chunks: list):
    """Upload chunks and embeddings to database"""
    supabase = SupabaseClient(customer_schema="public")
    
    try:
        # Clear existing data
        print("Clearing existing knowledge base...")
        supabase.cur.execute("DELETE FROM assistant_knowledge_base")
        
        # Insert new chunks
        print(f"Uploading {len(chunks)} chunks...")
        for i, chunk in enumerate(chunks):
            # Convert embedding list to pgvector format
            embedding_str = '[' + ','.join(str(x) for x in chunk['embedding']) + ']'
            
            supabase.cur.execute("""
                INSERT INTO assistant_knowledge_base 
                (text_content, chunk_type, embedding, chunk_index, created_at)
                VALUES (%s, %s, %s::vector, %s, NOW())
            """, (
                chunk['text'],
                chunk['chunk_type'],
                embedding_str,
                i
            ))
            
            if (i + 1) % 10 == 0:
                print(f"  Uploaded {i + 1}/{len(chunks)} chunks...")
        
        supabase.commit()
        print("✅ Successfully uploaded knowledge base!")
        
    except Exception as e:
        print(f"❌ Error uploading to database: {e}")
        supabase.rollback()
    finally:
        supabase.close()


def main():
    print("🚀 Loading Streamline Automation Knowledge Base...")
    print("=" * 60)
    
    # Step 1: Chunk the knowledge base
    print("\n1. Chunking knowledge base...")
    chunks = chunk_knowledge_base(KNOWLEDGE_BASE)
    print(f"   Created {len(chunks)} chunks")
    
    # Step 2: Generate embeddings
    print("\n2. Generating embeddings...")
    chunks_with_embeddings = embed_chunks(chunks)
    print(f"   Generated embeddings for {len(chunks_with_embeddings)} chunks")
    
    # Step 3: Upload to database
    print("\n3. Uploading to database...")
    upload_to_database(chunks_with_embeddings)
    
    print("\n" + "=" * 60)
    print("✨ Knowledge base loaded successfully!")


if __name__ == "__main__":
    main()

