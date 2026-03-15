# UserBase — User Management Web Application
**Maincrafts Technology · Python Full Stack Internship · Task 1 (with Auth)**

---

## Features

| Feature | Details |
|---|---|
| 🔐 Register | Username, email, hashed password, validation |
| 🔑 Login | Username or email + password, session-based |
| 🚪 Logout | Clears session with farewell flash message |
| 🛡 Protected routes | `@login_required` decorator on all dashboard routes |
| 👥 Add users | Name, email, phone, department |
| 📋 View users | Table with stats bar (total, assigned, departments) |
| 🗑 Delete users | With confirmation prompt |
| ⚡ Flash messages | Success / error / info feedback on every action |
| 💪 Password strength | Live meter on register page |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+ · Flask · Werkzeug |
| Frontend | HTML5 · CSS3 · Jinja2 |
| Database | SQLite3 |
| Security | `werkzeug.security` (pbkdf2:sha256 hashing) · Flask sessions |

---

## Project Structure

```
python-fullstack-task1/
├── app.py                  ← Flask routes + auth logic
├── database.db             ← SQLite (auth_users + users tables)
├── README.md
├── templates/
│   ├── login.html          ← Sign-in page (split layout)
│   ├── register.html       ← Sign-up page + password strength
│   └── index.html          ← Protected dashboard
└── static/
    └── style.css           ← Complete design system
```

---

## How to Run

```bash
# 1. Install dependencies
pip install flask werkzeug

# 2. Start the server
cd python-fullstack-task1
python app.py

# 3. Open browser
http://127.0.0.1:5000/
```

### Demo Account
| Field | Value |
|---|---|
| Username | `admin` |
| Password | `admin123` |

---

## Authentication Flow

```
/register  →  Validate form  →  Hash password  →  Save to auth_users  →  Redirect /login
/login     →  Lookup user    →  check_password_hash  →  Set session   →  Redirect /
/          →  @login_required checks session  →  Render dashboard OR redirect /login
/logout    →  session.clear()  →  Flash message  →  Redirect /login
```

---

## Database Schema

```sql
-- Registered accounts
CREATE TABLE auth_users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT NOT NULL UNIQUE,
    email      TEXT NOT NULL UNIQUE,
    password   TEXT NOT NULL,           -- pbkdf2:sha256 hash
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Managed user records
CREATE TABLE users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL,
    phone      TEXT,
    department TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

*Maincrafts Technology · hr@maincrafts.com · www.maincrafts.com*
