import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, session, flash, jsonify

app = Flask(__name__)
app.secret_key = 'dev_secret_key_change_in_production'

DATABASE = 'database.db'

# ─── DB Helper ────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            role     TEXT    NOT NULL DEFAULT 'user'
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            name   TEXT NOT NULL,
            email  TEXT NOT NULL,
            course TEXT NOT NULL
        )
    ''')
    # Seed a default admin if none exists
    existing = db.execute("SELECT * FROM users WHERE role='admin'").fetchone()
    if not existing:
        from werkzeug.security import generate_password_hash
        db.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', generate_password_hash('admin123'), 'admin')
        )
    db.commit()
    db.close()

# ─── Decorators ───────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session or session.get('role') != 'admin':
            flash('Access denied. Admins only.', 'error')
            return redirect('/dashboard')
        return f(*args, **kwargs)
    return wrapper

# ─── Auth ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect('/dashboard' if 'user' in session else '/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        from werkzeug.security import generate_password_hash
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')
        try:
            db = get_db()
            db.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, 'user')",
                (username, generate_password_hash(password))
            )
            db.commit()
            db.close()
            flash('Account created! Please log in.', 'success')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Username already taken.', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        from werkzeug.security import check_password_hash
        username = request.form['username'].strip()
        password = request.form['password']
        db   = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        db.close()
        if user and check_password_hash(user['password'], password):
            session['user'] = user['username']
            session['role'] = user['role']
            session['uid']  = user['id']
            flash(f"Welcome, {user['username']}! You are logged in as {user['role']}.", 'success')
            return redirect('/admin' if user['role'] == 'admin' else '/dashboard')
        flash('Invalid credentials.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect('/login')

# ─── User Dashboard ───────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    db    = get_db()
    count = db.execute("SELECT COUNT(*) as c FROM students").fetchone()['c']
    db.close()
    return render_template('dashboard.html', count=count)

# ─── Students (Read only for normal users) ────────────────────────────────────

@app.route('/students')
@login_required
def students():
    db   = get_db()
    data = db.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    db.close()
    return render_template('students.html', students=data)

@app.route('/add-student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        name   = request.form['name'].strip()
        email  = request.form['email'].strip()
        course = request.form['course'].strip()
        if not name or not email or not course:
            flash('All fields are required.', 'error')
            return render_template('add_student.html')
        db = get_db()
        db.execute("INSERT INTO students (name,email,course) VALUES (?,?,?)", (name, email, course))
        db.commit()
        db.close()
        flash(f'Student "{name}" added!', 'success')
        return redirect('/students')
    return render_template('add_student.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    db      = get_db()
    student = db.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    if not student:
        db.close()
        flash('Student not found.', 'error')
        return redirect('/students')
    if request.method == 'POST':
        name   = request.form['name'].strip()
        email  = request.form['email'].strip()
        course = request.form['course'].strip()
        db.execute("UPDATE students SET name=?,email=?,course=? WHERE id=?", (name, email, course, id))
        db.commit()
        db.close()
        flash('Student updated!', 'success')
        return redirect('/students')
    db.close()
    return render_template('edit_student.html', student=student)

@app.route('/delete/<int:id>')
@admin_required          # Only admins can delete
def delete_student(id):
    db = get_db()
    db.execute("DELETE FROM students WHERE id=?", (id,))
    db.commit()
    db.close()
    flash('Student deleted.', 'info')
    return redirect('/students')

# ─── Admin Panel ──────────────────────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    db           = get_db()
    users        = db.execute("SELECT id, username, role FROM users ORDER BY id").fetchall()
    students     = db.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    total_users  = len(users)
    total_students = len(students)
    db.close()
    return render_template('admin.html',
                           users=users,
                           students=students,
                           total_users=total_users,
                           total_students=total_students)

@app.route('/admin/delete-student/<int:id>')
@admin_required
def admin_delete_student(id):
    db = get_db()
    db.execute("DELETE FROM students WHERE id=?", (id,))
    db.commit()
    db.close()
    flash('Student deleted from admin panel.', 'info')
    return redirect('/admin')

@app.route('/admin/promote/<int:id>')
@admin_required
def promote_user(id):
    db = get_db()
    db.execute("UPDATE users SET role='admin' WHERE id=?", (id,))
    db.commit()
    db.close()
    flash('User promoted to admin.', 'success')
    return redirect('/admin')

@app.route('/admin/demote/<int:id>')
@admin_required
def demote_user(id):
    if id == session.get('uid'):
        flash("You cannot demote yourself.", 'error')
        return redirect('/admin')
    db = get_db()
    db.execute("UPDATE users SET role='user' WHERE id=?", (id,))
    db.commit()
    db.close()
    flash('User demoted to normal user.', 'info')
    return redirect('/admin')

# ─── REST API ─────────────────────────────────────────────────────────────────

@app.route('/api/students', methods=['GET'])
def api_get_students():
    db       = get_db()
    students = db.execute("SELECT * FROM students").fetchall()
    db.close()
    return jsonify([dict(row) for row in students]), 200

@app.route('/api/students/<int:id>', methods=['GET'])
def api_get_student(id):
    db      = get_db()
    student = db.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    db.close()
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(dict(student)), 200

@app.route('/api/students', methods=['POST'])
def api_add_student():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    name   = data.get('name', '').strip()
    email  = data.get('email', '').strip()
    course = data.get('course', '').strip()
    if not name or not email or not course:
        return jsonify({"error": "name, email, and course are required"}), 400
    db = get_db()
    cur = db.execute("INSERT INTO students (name,email,course) VALUES (?,?,?)", (name, email, course))
    db.commit()
    new_id = cur.lastrowid
    db.close()
    return jsonify({"message": "Student added successfully", "id": new_id}), 201

@app.route('/api/students/<int:id>', methods=['PUT'])
def api_update_student(id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    db      = get_db()
    student = db.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    if not student:
        db.close()
        return jsonify({"error": "Student not found"}), 404
    name   = data.get('name',   student['name'])
    email  = data.get('email',  student['email'])
    course = data.get('course', student['course'])
    db.execute("UPDATE students SET name=?,email=?,course=? WHERE id=?", (name, email, course, id))
    db.commit()
    db.close()
    return jsonify({"message": "Student updated successfully"}), 200

@app.route('/api/students/<int:id>', methods=['DELETE'])
def api_delete_student(id):
    db      = get_db()
    student = db.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    if not student:
        db.close()
        return jsonify({"error": "Student not found"}), 404
    db.execute("DELETE FROM students WHERE id=?", (id,))
    db.commit()
    db.close()
    return jsonify({"message": "Student deleted successfully"}), 200

# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
