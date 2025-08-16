from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import psycopg2.extras
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-later')


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
        SELECT u.*, array_agg(ua.agent_type) as agents
        FROM users u
        LEFT JOIN user_agents ua ON u.id = ua.user_id AND ua.is_enabled = true
        WHERE u.email = %s AND u.is_active = true
        GROUP BY u.id
    """, (email,))

    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


def create_user(email, password, name, company=None):
    """Create a new user"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        password_hash = hash_password(password)

        cur.execute("""
            INSERT INTO users (email, password_hash, name, company)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (email, password_hash, name, company))

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
            session['user'] = {
                'id': str(user['id']),
                'email': user['email'],
                'name': user['name'],
                'company': user['company'],
                'agents': user['agents'] if user['agents'][0] else []
            }
            return redirect(url_for('chat'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        password = request.form['password']
        name = request.form['name'].strip()
        company = request.form.get('company', '').strip()

        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
        elif create_user(email, password, name, company):
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email already exists', 'error')

    return render_template('register.html')


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


if __name__ == '__main__':
    app.run(debug=True, port=8000)