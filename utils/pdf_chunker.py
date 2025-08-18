#!/usr/bin/env python3

from utils.supa import SupabaseClient

"""
Simple PDF Parser and Text Chunker
- Accepts a single PDF file path OR a directory containing PDFs
- Extracts text safely (skips pages with no text)
- Splits into overlapping word chunks
"""

import os
from pathlib import Path
import PyPDF2
from openai import OpenAI
import numpy as np
import supabase

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract all text from a PDF file."""
    text_parts = []
    with open(pdf_path, "rb") as fh:
        reader = PyPDF2.PdfReader(fh)
        for page in reader.pages:
            page_text = page.extract_text() or ""   # guard against None
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts).strip()


def chunk_text(text: str, chunk_size: int = 50, overlap: int = 10):
    """
    Split text into overlapping chunks of words.
    - chunk_size: number of WORDS per chunk
    - overlap: number of WORDS to overlap between adjacent chunks
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()
    chunks = []

    start = 0
    step = chunk_size - overlap
    n = len(words)

    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(" ".join(words[start:end]))
        if end == n:  # finished
            break
        start = start + step

    return [
        {"chunk_number": i + 1, "text": c}
        for i, c in enumerate(chunks)
    ]


def embed_chunks(chunks: list[dict]):
    """Embed chunks using OpenAI's API."""
    client = OpenAI()
    embeddings = client.embeddings.create(
        input=[chunk['text'] for chunk in chunks],
        model="text-embedding-3-large"
    )
    return embeddings

def process_pdf(pdf_path: Path):
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)
    return chunks, embeddings

def upload_to_supabase(pdf_path: Path, table_name: str):
    """Upload pdf chunks and embeddings to Supabase."""
    
    # Process PDF
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    if not chunks:
        print(f"No chunks to upload for {pdf_path}")
        return
    
    # Get embeddings for chunks
    embeddings = embed_chunks(chunks)
    
    # Connect to database
    supabase = SupabaseClient(customer_schema="Legends")
    
    try:
        # Insert chunks and embeddings into single table
        for i, chunk in enumerate(chunks):
            embedding_data = embeddings.data[i]
            supabase.cur.execute("""
                INSERT INTO {supabase.customer_schema}.{table_name}  
                (index, embedding, source_file, chunk_number, text_content, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                i,
                embedding_data.embedding,
                pdf_path.name,
                chunk['chunk_number'],
                chunk['text']
            ))
        
        supabase.commit()
        print(f"Successfully uploaded {len(chunks)} chunks and embeddings")
        
    except Exception as e:
        supabase.conn.rollback()
        print(f"Error uploading to database: {e}")
    finally:
        supabase.close()



def main():
    print("Starting PDF chunker")

    # Change this to your file OR directory
    target_path = Path(r"C:\Users\LukeH\Desktop\Python Project\StreamlineB2B\pdfs\Customer_Service Agent.pdf")

    try:
        pdf_file = target_path
    except Exception as e:
        print(f"Error: {e}")
        return

    if not pdf_file:
        print(f"No PDF files found in {target_path}")
        return

    print(f"Processing PDF file: {pdf_file.name}")
    
    # Extract text and create chunks
    text = extract_text_from_pdf(pdf_file)
    if not text:
        print(f"No text extracted from {pdf_file}")
        return
    
    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks")
    
    # Display chunks
    print("Uploading to Supabase...")
    

    upload_to_supabase(pdf_file)
    

    # Optionally upload to database
    # upload_to_supabase(pdf_file)

if __name__ == "__main__":
    main()
