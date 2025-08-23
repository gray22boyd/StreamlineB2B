# StreamlineB2B

A comprehensive B2B automation platform that combines AI-powered customer service agents and marketing automation tools to streamline business operations.

## Features

- **AI Customer Service Agent**: Automated customer support with PDF document processing and RAG (Retrieval-Augmented Generation) capabilities
- **Marketing Automation**: Facebook Business integration for social media management
- **Database Integration**: PostgreSQL/Supabase backend for data persistence
- **MCP (Model Context Protocol) Support**: Modular agent architecture for extensibility

## Prerequisites

- Python 3.12 or higher
- PostgreSQL database (Supabase recommended)
- Facebook Business account (for marketing features)


## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd StreamlineB2B
   ```

2. **Create and activate venv**
   '''bash
   uv venv .venv
   .venv\Scripts\Activate.ps1


3. **Install dependencies**
   ```bash
   uv pip install -e .
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql://username:password@host:port/database
   FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
   FACEBOOK_BUSINESS_ID=your_business_id
   ```

5. **Test database connection**
   ```bash
   python test_db_connection.py
   ```

## Project Structure

```
StreamlineB2B/
├── agents/
│   ├── customer_service_agent/
│   │   ├── __init__.py
│   │   ├── mcp_server.py      # MCP server implementation
│   │   ├── schemas.py         # Data schemas
│   │   └── tools.py           # Customer service tools
│   └── marketing_agent/
│       ├── __init__.py
│       ├── schemas.py         # Marketing data schemas
│       └── tools.py           # Facebook marketing tools
├── utils/
│   └── pdf_chunker.py         # PDF processing and RAG utilities
├── pyproject.toml             # Project configuration
├── uv.lock                    # Dependency lock file
└── test_db_connection.py      # Database connection test
```

## 🔧 Usage

### Customer Service Agent

The customer service agent provides automated support using PDF document processing:

```python
from agents.customer_service_agent.tools import CustomerServiceTools

# Initialize customer service tools
cs_tools = CustomerServiceTools(business_id="your_business_id")

# Process customer inquiries
response = cs_tools.handle_inquiry("How do I reset my password?")
```

### Marketing Agent

The marketing agent handles Facebook Business operations:

```python
from agents.marketing_agent.tools import FacebookMarketingTools

# Initialize marketing tools
marketing_tools = FacebookMarketingTools(business_id="your_business_id")

# Post to Facebook page
marketing_tools.post_text("Hello from StreamlineB2B!")

# Get page insights
insights = marketing_tools.get_page_insights()
```

### PDF Processing

Process PDF documents for RAG-based customer service:

```python
from utils.pdf_chunker import PDFProcessor

# Initialize PDF processor
processor = PDFProcessor()

# Process a PDF file
processor.process_pdf("path/to/document.pdf")
```

## 📚 Dependencies

- **facebook-business**: Facebook Business API integration
- **fastmcp**: Model Context Protocol implementation
- **psycopg2-binary**: PostgreSQL database adapter
- **python-dotenv**: Environment variable management
- **PyPDF2**: PDF processing
- **PyMuPDF**: Advanced PDF text extraction
- **sentence-transformers**: Text embeddings for RAG
- **chromadb**: Vector database for document storage
- **spacy**: Natural language processing
- **langchain**: Text splitting and processing

## 🔌 MCP Integration

This project uses the Model Context Protocol (MCP) for modular agent architecture. Each agent can be deployed as an MCP server:

```bash
# Start customer service agent
python -m agents.customer_service_agent.mcp_server

# Start marketing agent
python -m agents.marketing_agent.mcp_server
```

## 🗄️ Database Schema

The application requires the following database tables:

- `marketing_tokens`: Stores Facebook API credentials
- `customer_inquiries`: Logs customer service interactions
- `document_embeddings`: Stores processed PDF embeddings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `docs/` directory
- Review the test files for usage examples

## 🔄 Version History

- **v0.1.0**: Initial release with basic customer service and marketing agents
