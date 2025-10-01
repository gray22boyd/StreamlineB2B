from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import psycopg2
import psycopg2.extras
import bcrypt
import os
from dotenv import load_dotenv
from pathlib import Path
from authlib.integrations.flask_client import OAuth
from agent_registry import build_registry
from utils.assistant_rag import AssistantRAG

# Load env from project root and frontend directory to support different run contexts
project_root_env = Path(__file__).resolve().parent.parent / '.env'
frontend_env = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=project_root_env, override=False)
load_dotenv(dotenv_path=frontend_env, override=False)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-later')

# Build agent registry (supports remote MCP via env)
REGISTRY = build_registry()

# Initialize assistant RAG system
assistant_rag = AssistantRAG()

oauth = OAuth(app)
oauth.register(
    name='facebook',
    client_id=os.getenv('FACEBOOK_CLIENT_ID'),
    client_secret=os.getenv('FACEBOOK_CLIENT_SECRET'),
    access_token_url='https://graph.facebook.com/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    api_base_url='https://graph.facebook.com/',
    client_kwargs={'scope': 'email'}
)


def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        os.getenv('DATABASE_URL'),
        cursor_factory=psycopg2.extras.RealDictCursor
    )


def hash_password(password):
    """Hash a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, hashed):
    """Verify a password"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def get_user_by_email(email):
    """Get user from database by email"""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT u.*, b.name as business_name, array_agg(ua.agent_type) as agents
        FROM users u
        LEFT JOIN businesses b ON u.business_id = b.id
        LEFT JOIN user_agents ua ON u.id = ua.user_id AND ua.is_enabled = true
        WHERE u.email = %s AND u.is_active = true
        GROUP BY u.id, b.id, b.name
    """, (email,))

    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


def create_user(email, password, name, business_id, company=None):
    """Create a new user"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        password_hash = hash_password(password)

        cur.execute("""
            INSERT INTO users (email, password_hash, name, business_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (email, password_hash, name, business_id))

        user_id = cur.fetchone()['id']

        # Assign default agents (marketing)
        cur.execute("""
            INSERT INTO user_agents (user_id, agent_type)
            VALUES (%s, 'marketing')
        """, (user_id,))

        conn.commit()
        cur.close()
        conn.close()
        return True

    except psycopg2.IntegrityError:
        conn.rollback()
        cur.close()
        conn.close()
        return False  # Email already exists


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        password = request.form['password']

        user = get_user_by_email(email)

        if user and verify_password(password, user['password_hash']):
            # Check if user is super admin
            is_super_admin = user.get('is_super_admin', False)
            
            session['user'] = {
                'id': str(user['id']),
                'email': user['email'],
                'name': user['name'],
                'business_id': str(user['business_id']) if user['business_id'] else None,
                'business_name': user.get('business_name', 'Admin'),
                'role': user['role'],
                'is_super_admin': is_super_admin,
                'agents': user['agents'] if user['agents'] and user['agents'][0] else []
            }
            
            # Redirect super admin to admin dashboard, regular users to chat
            if is_super_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('chat'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')

@app.route('/login/facebook')
def login_facebook():
    redirect_uri = url_for('facebook_callback', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)

@app.route('/auth/facebook/callback')
def facebook_callback():
    try:
        token = oauth.facebook.authorize_access_token()
        resp = oauth.facebook.get('me?fields=id,name,email')
        profile = resp.json()
    except Exception:
        flash('Facebook login failed. Please try again.', 'error')
        return redirect(url_for('login'))

    email = (profile.get('email') or '').lower().strip()
    if not email:
        flash('Your Facebook account has no email. Please use email/password or contact admin.', 'error')
        return redirect(url_for('login'))

    user = get_user_by_email(email)
    if not user:
        flash('No account found for this Facebook email. Contact your administrator.', 'error')
        return redirect(url_for('login'))

    is_super_admin = user.get('is_super_admin', False)
    session['user'] = {
        'id': str(user['id']),
        'email': user['email'],
        'name': user['name'],
        'business_id': str(user['business_id']) if user['business_id'] else None,
        'business_name': user.get('business_name', 'Admin'),
        'role': user['role'],
        'is_super_admin': is_super_admin,
        'agents': user['agents'] if user['agents'] and user['agents'][0] else []
    }

    return redirect(url_for('admin_dashboard' if is_super_admin else 'chat'))


# Registration removed - admin creates accounts directly in database

def admin_required(f):
    """Decorator to require super admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or not session['user'].get('is_super_admin', False):
            flash('Admin access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/admin')
@admin_required
def admin_dashboard():
    """Super admin dashboard"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get business overview
    cur.execute("""
        SELECT b.*, COUNT(u.id) as user_count
        FROM businesses b
        LEFT JOIN users u ON b.id = u.business_id AND u.is_active = true
        GROUP BY b.id, b.name, b.email, b.created_at
        ORDER BY b.name
    """)
    businesses = cur.fetchall()
    
    # Get total user count
    cur.execute("SELECT COUNT(*) as total_users FROM users WHERE is_active = true AND is_super_admin = false")
    user_stats = cur.fetchone()
    
    # Get recent activity (last 10 logins)
    cur.execute("""
        SELECT u.name, u.email, b.name as business_name, u.created_at
        FROM users u
        LEFT JOIN businesses b ON u.business_id = b.id
        WHERE u.is_active = true AND u.is_super_admin = false
        ORDER BY u.created_at DESC
        LIMIT 10
    """)
    recent_users = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         businesses=businesses,
                         user_stats=user_stats,
                         recent_users=recent_users,
                         user=session['user'])


@app.route('/admin/businesses')
@admin_required
def admin_businesses():
    """Manage businesses"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT b.*, COUNT(u.id) as user_count,
               COUNT(ua.id) as agent_count
        FROM businesses b
        LEFT JOIN users u ON b.id = u.business_id AND u.is_active = true
        LEFT JOIN user_agents ua ON u.id = ua.user_id AND ua.is_enabled = true
        GROUP BY b.id, b.name, b.email, b.created_at
        ORDER BY b.name
    """)
    businesses = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin_businesses.html', 
                         businesses=businesses,
                         user=session['user'])


@app.route('/admin/users')
@admin_required
def admin_users():
    """Manage users"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT u.*, b.name as business_name, array_agg(ua.agent_type) as agents
        FROM users u
        LEFT JOIN businesses b ON u.business_id = b.id
        LEFT JOIN user_agents ua ON u.id = ua.user_id AND ua.is_enabled = true
        WHERE u.is_super_admin = false
        GROUP BY u.id, b.name
        ORDER BY u.created_at DESC
    """)
    users = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin_users.html', 
                         users=users,
                         user=session['user'])


@app.route('/admin/switch-business/<business_id>')
@admin_required
def switch_business(business_id):
    """Switch business context for admin"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get business info
    cur.execute("SELECT * FROM businesses WHERE id = %s", (business_id,))
    business = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if business:
        # Update session with business context
        session['admin_business_context'] = {
            'business_id': str(business['id']),
            'business_name': business['name']
        }
        flash(f'Switched to {business["name"]} context', 'success')
        return redirect(url_for('chat'))
    else:
        flash('Business not found', 'error')
        return redirect(url_for('admin_dashboard'))


@app.route('/chat')
def chat():
    """Chat interface with AI agents"""
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template('chat.html', user=session['user'])


@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    """User profile page"""
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template('profile.html', user=session['user'])


@app.route('/privacy')
def privacy():
    """Privacy Policy"""
    return render_template('privacy.html')


@app.route('/terms')
def terms():
    """Terms of Service"""
    return render_template('terms.html')


# --------- API: Assistant Chat (Public) ----------
@app.route('/api/assistant/chat', methods=['POST'])
def assistant_chat():
    """Public assistant endpoint for website visitors"""
    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()
    session_id = data.get('session_id')
    
    if not message:
        return jsonify({"error": "Empty message"}), 400
    
    try:
        result = assistant_rag.generate_response(message, session_id=session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "response": "I'm having trouble right now. Please email support@streamlineautomation.co"
        }), 500


@app.route('/api/assistant/lead', methods=['POST'])
def assistant_lead():
    """Capture lead information from assistant conversation"""
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    initial_query = data.get('initial_query')
    session_id = data.get('session_id')
    
    if not name or not email:
        return jsonify({"error": "Name and email required"}), 400
    
    # Basic email validation
    if '@' not in email or '.' not in email:
        return jsonify({"error": "Invalid email"}), 400
    
    try:
        result = assistant_rag.save_lead(name, email, initial_query, session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Admin endpoint to view captured leads
@app.route('/admin/assistant-leads')
@admin_required
def admin_assistant_leads():
    """View captured assistant leads"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, name, email, initial_query, created_at, contacted, notes
        FROM assistant_leads
        ORDER BY created_at DESC
        LIMIT 100
    """)
    leads = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin_assistant_leads.html', 
                         leads=leads,
                         user=session['user'])


# --------- API: Chat → MCP tools ----------
@app.route('/api/chat', methods=['POST'])
def api_chat():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    agent = (data.get('agent') or 'marketing').strip()
    message = (data.get('message') or '').strip()
    if not message:
        return jsonify({"error": "Empty message"}), 400

    # Determine business_id: admin override > user business
    business_id = None
    if session['user'].get('is_super_admin') and session.get('admin_business_context'):
        business_id = session['admin_business_context'].get('business_id')
    if not business_id:
        business_id = session['user'].get('business_id')
    if not business_id:
        return jsonify({"error": "No business selected/assigned"}), 400

    adapter = REGISTRY.get(agent)
    if not adapter:
        return jsonify({"error": f"Unknown agent '{agent}'"}), 400

    try:
        lower = message.lower()

        if lower.startswith('/list_pages'):
            result = adapter.call_tool('list_pages', {"business_id": business_id})
            if result.get('success'):
                pages = result.get('pages', [])
                if not pages:
                    return jsonify({"text": "No pages found."})
                lines = [f"- {p.get('name')} (ID: {p.get('id')})" for p in pages]
                return jsonify({"text": "Pages:\n" + "\n".join(lines)})
            return jsonify({"text": f"Error: {result.get('error') or 'unknown'}"})

        if lower.startswith('/post_text '):
            text_msg = message[len('/post_text '):].strip()
            if not text_msg:
                return jsonify({"text": "Usage: /post_text <message>"})
            result = adapter.call_tool('post_text', {"business_id": business_id, "message": text_msg})
            return jsonify({"text": result.get('message') or result.get('error') or 'Done'})

        if lower.startswith('/post_image '):
            payload = message[len('/post_image '):]
            if '|' not in payload:
                return jsonify({"text": "Usage: /post_image <image_url> | <caption>"})
            image_url, caption = [x.strip() for x in payload.split('|', 1)]
            if not image_url or not caption:
                return jsonify({"text": "Usage: /post_image <image_url> | <caption>"})
            result = adapter.call_tool('post_image', {"business_id": business_id, "caption": caption, "image_url": image_url})
            return jsonify({"text": result.get('message') or result.get('error') or 'Done'})

        # Help
        return jsonify({"text": "Commands:\n- /list_pages\n- /post_text <message>\n- /post_image <image_url> | <caption>"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Production-ready configuration
    import os
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print(f"Starting Flask app on port {port} with debug={debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)