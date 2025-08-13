#!/usr/bin/env python3
"""
PDF RAG Processing Workflow for Customer Service Documentation
Reads PDFs, parses them, creates embeddings, and stores them in a vector database
"""

import os
import logging
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Core libraries
import PyPDF2
import fitz  # PyMuPDF - better for text extraction
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import pandas as pd

# Text processing
import spacy
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

# Optional: For better PDF handling
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False