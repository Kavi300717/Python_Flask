# Python Full Stack – Task 3
## Database-Driven CRUD Application with Flask (Authenticated Users Only)

---

## Project Structure

```
python-fullstack-task3/
├── app.py
├── database.db          (auto-created on first run)
├── README.md
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── students.html
│   ├── add_student.html
│   └── edit_student.html
└── static/
    └── style.css
```

---

## Setup & Run

```bash
# 1. Install dependencies
pip install flask werkzeug

# 2. Run the app
python app.py

# 3. Open browser
http://127.0.0.1:5000
```

---

## CRUD Flow Explained

### Authentication Gate
Every CRUD route checks `if 'user' not in session` before doing anything.
If the check fails, the user is redirected to `/login`. This enforces
session-based access control on all protected pages.

### CREATE – Add a Student
- **Route:** `POST /add-student`
- The form submits name, email, course via HTTP POST.
- Flask reads `request.form`, validates fields are non-empty, then executes:
  ```sql
  INSERT INTO students (name, email, course) VALUES (?, ?, ?)
  ```
- Uses parameterised queries to prevent SQL injection.
- After insert → `db.commit()` → redirect to `/students`.

### READ – View All Students
- **Route:** `GET /students`
- Executes `SELECT * FROM students ORDER BY id DESC`.
- Passes result list to `students.html` via Jinja2 `{{ students }}`.
- Template loops with `{% for s in students %}` to render each row.

### UPDATE – Edit a Student
- **Route:** `GET /edit/<id>` (load form) + `POST /edit/<id>` (save)
- On GET: fetches the student row by id, pre-fills the form.
- On POST: executes:
  ```sql
  UPDATE students SET name=?, email=?, course=? WHERE id=?
  ```
- Then commits and redirects back to `/students`.

### DELETE – Remove a Student
- **Route:** `GET /delete/<id>`
- Executes `DELETE FROM students WHERE id=?`, commits, redirects.
- JavaScript `confirm()` dialog on the frontend prevents accidental deletion.

---

## Security Rules Implemented

| Rule | Implementation |
|------|---------------|
| Only logged-in users access CRUD | `if 'user' not in session` guard on every route |
| Direct URL access redirects to login | `return redirect('/login')` |
| No plain-text passwords | `generate_password_hash` / `check_password_hash` (Werkzeug) |
| Session-based access control | `app.secret_key` + Flask `session` dictionary |
| SQL injection prevention | Parameterised queries (`?` placeholders) |

---

## Database Schema

```sql
-- Task-2 table (authentication)
CREATE TABLE users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT    UNIQUE NOT NULL,
    password TEXT    NOT NULL        -- bcrypt hash via Werkzeug
);

-- Task-3 table (CRUD data)
CREATE TABLE students (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name   TEXT NOT NULL,
    email  TEXT NOT NULL,
    course TEXT NOT NULL
);
```

---

## Tech Stack

- **Backend:** Python 3 + Flask
- **Database:** SQLite (via built-in `sqlite3` module)
- **Auth:** Flask Sessions + Werkzeug password hashing
- **Frontend:** HTML5 + CSS3 (Jinja2 templates)
