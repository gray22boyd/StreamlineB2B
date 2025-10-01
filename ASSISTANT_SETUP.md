# 🤖 Streamline Assistant Setup Guide

This guide will help you set up the AI Assistant widget on your website.

## ✅ What Was Implemented

### **1. Backend Components**
- ✅ `utils/assistant_rag.py` - RAG system with OpenAI embeddings & GPT
- ✅ `utils/assistant_kb_loader.py` - Knowledge base loader script
- ✅ `database/migrations/create_assistant_tables.sql` - Database schema
- ✅ API endpoints in `frontend/app.py`:
  - `/api/assistant/chat` - Public chat endpoint
  - `/api/assistant/lead` - Lead capture endpoint
  - `/admin/assistant-leads` - Admin view for leads

### **2. Frontend Components**
- ✅ `frontend/templates/assistant_widget.html` - Floating chat widget
- ✅ `frontend/templates/admin_assistant_leads.html` - Admin lead management
- ✅ Widget automatically included on all pages via `base.html`

### **3. Features**
- ✅ RAG-powered responses (accurate, no hallucinations)
- ✅ Conversation memory (context across messages)
- ✅ Lead capture after 3+ messages
- ✅ Fallback to email for out-of-scope questions
- ✅ Beautiful gradient purple/blue design
- ✅ Mobile responsive
- ✅ Admin dashboard to view captured leads

---

## 🚀 Setup Instructions

### **Step 1: Verify Environment Variables**

Make sure your `.env` file has these variables:

```bash
OPENAI_API_KEY=sk-...your-key...
DATABASE_URL=postgresql://...your-database-url...
```

### **Step 2: Create Database Tables**

Run the SQL migration to create the necessary tables:

```bash
# Using psql command line
psql $DATABASE_URL -f database/migrations/create_assistant_tables.sql

# OR using Python
python -c "
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
with open('database/migrations/create_assistant_tables.sql', 'r') as f:
    cur.execute(f.read())
conn.commit()
conn.close()
print('✅ Tables created!')
"
```

This creates:
- `assistant_knowledge_base` - Stores embedded knowledge chunks
- `assistant_leads` - Stores visitor contact information

### **Step 3: Load Knowledge Base**

Run the knowledge base loader to populate the database:

```bash
python utils/assistant_kb_loader.py
```

Expected output:
```
🚀 Loading Streamline Automation Knowledge Base...
============================================================

1. Chunking knowledge base...
   Created X chunks

2. Generating embeddings...
   Generated embeddings for X chunks

3. Uploading to database...
   Uploaded X/X chunks...
✅ Successfully uploaded knowledge base!
```

### **Step 4: Test the Assistant**

1. Start your Flask app:
   ```bash
   python frontend/app.py
   ```

2. Visit your homepage (e.g., `http://localhost:8000`)

3. Look for the **purple chat button** in the bottom right corner

4. Click it and ask: "What does Streamline Automation do?"

---

## 🧪 Testing Checklist

- [ ] Assistant button appears on all pages
- [ ] Click button opens chat window
- [ ] Can send messages and receive responses
- [ ] Responses are relevant to your knowledge base
- [ ] After 3+ messages, lead capture form appears
- [ ] Can submit name/email successfully
- [ ] Admin can view leads at `/admin/assistant-leads`

---

## 📊 Admin Features

### **Viewing Captured Leads**

1. Login as super admin
2. Go to **Admin Dashboard**
3. Click **💬 Assistant Leads** in sidebar or quick actions
4. View all captured leads with:
   - Name & email
   - Initial query
   - Date captured
   - Contact status

---

## 🎨 Customization Options

### **Change Widget Colors**

Edit `frontend/templates/assistant_widget.html`:

```css
/* Find this line: */
background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);

/* Change to your brand colors, e.g.: */
background:linear-gradient(135deg,#YOUR_COLOR_1 0%,#YOUR_COLOR_2 100%);
```

### **Change Widget Position**

In `assistant_widget.html`, find:
```css
#assistant-widget{position:fixed;bottom:20px;right:20px;}
```

Change to:
- Bottom left: `bottom:20px;left:20px;`
- Top right: `top:20px;right:20px;`

### **Update Knowledge Base**

To add/modify company information:

1. Edit the `KNOWLEDGE_BASE` string in `utils/assistant_kb_loader.py`
2. Run the loader again: `python utils/assistant_kb_loader.py`
3. The script will clear old data and upload the new content

### **Adjust Lead Capture Timing**

In `assistant_widget.html`, find:
```javascript
if(assistantMsgCount>=3&&!assistantLeadCaptured)
```

Change `3` to a different number to trigger after more/fewer messages.

---

## 🐛 Troubleshooting

### **Widget doesn't appear**
- Check browser console for JavaScript errors
- Verify `assistant_widget.html` is included in `base.html`
- Clear browser cache

### **"Error generating response"**
- Verify `OPENAI_API_KEY` is set correctly
- Check knowledge base was loaded: `SELECT COUNT(*) FROM assistant_knowledge_base;`
- Check Flask logs for detailed error messages

### **Database connection errors**
- Verify `DATABASE_URL` is correct
- Ensure `pgvector` extension is installed: `CREATE EXTENSION IF NOT EXISTS vector;`
- Check database user has necessary permissions

### **No responses from assistant**
- Verify knowledge base is loaded (Step 3)
- Check `assistant_knowledge_base` table has data
- Increase similarity threshold in `utils/assistant_rag.py` (line with `WHERE similarity > 0.7`)

---

## 📝 Knowledge Base Format

The knowledge base is stored in Markdown format with sections:

```markdown
## Company Overview
General information about the company

---

## Services
What you offer

---

## Pricing
Pricing information

---

## FAQs
Q: Question?
A: Answer.
```

Each section is automatically:
1. Chunked into smaller pieces
2. Embedded using OpenAI's `text-embedding-3-large`
3. Stored in PostgreSQL with pgvector
4. Retrieved using semantic similarity search

---

## 🔐 Security Notes

- Assistant endpoints are **public** (no authentication required)
- Lead data is stored securely in your database
- Conversation history is stored in memory (not persisted unless lead is captured)
- Admin leads page requires super admin authentication

---

## 🚀 Going to Production

1. **Set proper environment variables** in your production environment
2. **Enable HTTPS** for secure communication
3. **Add rate limiting** to prevent abuse:
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=lambda: request.remote_addr)
   
   @app.route('/api/assistant/chat', methods=['POST'])
   @limiter.limit("20 per minute")
   def assistant_chat():
       ...
   ```
4. **Monitor OpenAI usage** - each message costs ~$0.0001-0.0005
5. **Set up email notifications** for new leads

---

## 📧 Support

For questions or issues:
- Email: support@streamlineautomation.co
- Update knowledge base with new FAQs as needed

---

**Enjoy your new AI Assistant! 🎉**

