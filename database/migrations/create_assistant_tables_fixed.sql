-- Fixed version for Supabase with dimension limits
-- Uses text-embedding-3-small (1536 dimensions) instead

CREATE EXTENSION IF NOT EXISTS vector;

-- Create assistant knowledge base table with vector embeddings
CREATE TABLE IF NOT EXISTS assistant_knowledge_base (
    id SERIAL PRIMARY KEY,
    text_content TEXT NOT NULL,
    chunk_type VARCHAR(50) NOT NULL,
    embedding vector(1536) NOT NULL,
    chunk_index INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for vector similarity search (1536 dimensions works with ivfflat)
CREATE INDEX IF NOT EXISTS assistant_knowledge_embedding_idx 
ON assistant_knowledge_base USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create assistant leads table for capturing interested visitors
CREATE TABLE IF NOT EXISTS assistant_leads (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    initial_query TEXT,
    conversation_history TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    contacted BOOLEAN DEFAULT FALSE,
    notes TEXT
);

-- Create indexes
CREATE INDEX IF NOT EXISTS assistant_leads_email_idx ON assistant_leads(email);
CREATE INDEX IF NOT EXISTS assistant_leads_created_at_idx ON assistant_leads(created_at DESC);

