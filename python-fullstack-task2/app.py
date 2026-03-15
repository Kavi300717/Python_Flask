from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re

app = Flask(__name__)
app.secret_key = 'maincrafts-secret-key-change-in-production'

DATABASE = 'database.db'


# ─── DB Helpers ───────────────────────────────────────────────────────────────

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS auth_users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT NOT NULL UNIQUE,
            email       TEXT NOT NULL UNIQUE,
            password    TEXT NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT NOT NULL,
            phone       TEXT,
            department  TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# ─── Auth Decorator ───────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ─── Auth Routes ─────────────────────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        confirm  = request.form['confirm_password']

        errors = []
        if len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email):
            errors.append('Enter a valid email address.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')

        if not errors:
            conn = get_db_connection()
            existing = conn.execute(
                'SELECT id FROM auth_users WHERE username=? OR email=?',
                (username, email)
            ).fetchone()
            if existing:
                errors.append('Username or email already registered.')
            else:
                hashed = generate_password_hash(password)
                conn.execute(
                    'INSERT INTO auth_users (username, email, password) VALUES (?, ?, ?)',
                    (username, email, hashed)
                )
                conn.commit()
                conn.close()
                flash('Account created! Please log in.', 'success')
                return redirect(url_for('login'))
            conn.close()

        for err in errors:
            flash(err, 'error')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        identifier = request.form['identifier'].strip()
        password   = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM auth_users WHERE username=? OR email=?',
            (identifier, identifier)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id']  = user['id']
            session['username'] = user['username']
            flash(f"Welcome back, {user['username']}!", 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username/email or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}! You have been logged out.', 'info')
    return redirect(url_for('login'))


# ─── Main App Routes ──────────────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    conn = get_db_connection()

    if request.method == 'POST':
        name       = request.form['name'].strip()
        email      = request.form['email'].strip()
        phone      = request.form.get('phone', '').strip()
        department = request.form.get('department', '').strip()

        if name and email:
            conn.execute(
                'INSERT INTO users (name, email, phone, department) VALUES (?, ?, ?, ?)',
                (name, email, phone, department)
            )
            conn.commit()
            flash(f'User "{name}" added successfully!', 'success')

        conn.close()
        return redirect(url_for('index'))

    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', users=users)


@app.route('/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT name FROM users WHERE id=?', (user_id,)).fetchone()
    if user:
        conn.execute('DELETE FROM users WHERE id=?', (user_id,))
        conn.commit()
        flash(f'User "{user["name"]}" deleted.', 'info')
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    print("✅ Database ready")
    print("🚀 Server starting at http://127.0.0.1:5000/")
    app.run(debug=True)
