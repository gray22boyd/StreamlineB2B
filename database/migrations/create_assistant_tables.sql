-- Create assistant knowledge base table with vector embeddings
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS assistant_knowledge_base (
    id SERIAL PRIMARY KEY,
    text_content TEXT NOT NULL,
    chunk_type VARCHAR(50) NOT NULL,  -- 'faq', 'services', 'pricing', 'overview', 'contact', 'general'
    embedding vector(3072) NOT NULL,  -- text-embedding-3-large produces 3072 dimensions
    chunk_index INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for vector similarity search
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

-- Create index on email for quick lookups
CREATE INDEX IF NOT EXISTS assistant_leads_email_idx ON assistant_leads(email);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS assistant_leads_created_at_idx ON assistant_leads(created_at DESC);

