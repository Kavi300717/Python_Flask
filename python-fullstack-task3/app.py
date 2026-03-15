import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_in_production'

DATABASE = 'database.db'

# ─── Database Helper ──────────────────────────────────────────────────────────

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
            password TEXT    NOT NULL
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
    db.commit()
    db.close()

# ─── Auth Routes ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        hashed   = generate_password_hash(password)
        try:
            db = get_db()
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
            db.commit()
            db.close()
            flash('Account created! Please log in.', 'success')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        db   = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        db.close()
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            flash(f'Welcome back, {username}!', 'success')
            return redirect('/dashboard')
        flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    db    = get_db()
    count = db.execute("SELECT COUNT(*) as cnt FROM students").fetchone()['cnt']
    db.close()
    return render_template('dashboard.html', username=session['user'], count=count)

# ─── CRUD Routes ──────────────────────────────────────────────────────────────

@app.route('/students')
def students():
    if 'user' not in session:
        return redirect('/login')
    db   = get_db()
    data = db.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    db.close()
    return render_template('students.html', students=data)

@app.route('/add-student', methods=['GET', 'POST'])
def add_student():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        name   = request.form['name'].strip()
        email  = request.form['email'].strip()
        course = request.form['course'].strip()
        if not name or not email or not course:
            flash('All fields are required.', 'error')
            return render_template('add_student.html')
        db = get_db()
        db.execute("INSERT INTO students (name, email, course) VALUES (?, ?, ?)", (name, email, course))
        db.commit()
        db.close()
        flash(f'Student "{name}" added successfully!', 'success')
        return redirect('/students')
    return render_template('add_student.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if 'user' not in session:
        return redirect('/login')
    db      = get_db()
    student = db.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()
    if not student:
        db.close()
        flash('Student not found.', 'error')
        return redirect('/students')
    if request.method == 'POST':
        name   = request.form['name'].strip()
        email  = request.form['email'].strip()
        course = request.form['course'].strip()
        db.execute(
            "UPDATE students SET name=?, email=?, course=? WHERE id=?",
            (name, email, course, id)
        )
        db.commit()
        db.close()
        flash('Student updated successfully!', 'success')
        return redirect('/students')
    db.close()
    return render_template('edit_student.html', student=student)

@app.route('/delete/<int:id>')
def delete_student(id):
    if 'user' not in session:
        return redirect('/login')
    db = get_db()
    db.execute("DELETE FROM students WHERE id=?", (id,))
    db.commit()
    db.close()
    flash('Student deleted.', 'info')
    return redirect('/students')

# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
