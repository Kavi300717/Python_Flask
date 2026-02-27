# User Management Web Application
**Maincrafts Technology – Python Full Stack Internship | Task 1**

---

## Project Overview

A full-stack web application built with Python (Flask), HTML, CSS, and SQLite that allows users to:
- **Add** new user details via a web form
- **View** all users in a styled table
- **Delete** users from the database
- **Store** data permanently in a local SQLite database

---

## Tech Stack

| Layer      | Technology         |
|------------|--------------------|
| Backend    | Python 3.10+ + Flask |
| Frontend   | HTML5, CSS3        |
| Database   | SQLite3            |
| Tools      | VS Code, Browser   |

---

## Project Structure

```
python-fullstack-task1/
│
├── app.py              ← Flask backend (routes, DB logic)
├── database.db         ← SQLite database (auto-created on first run)
├── README.md           ← This file
│
├── templates/
│   └── index.html      ← HTML frontend template (Jinja2)
│
└── static/
    └── style.css       ← CSS styling
```

---

## How to Run

### 1. Install Python and Flask

Make sure Python 3.10+ is installed, then:

```bash
pip install flask
```

### 2. Run the App

```bash
cd python-fullstack-task1
python app.py
```

### 3. Open in Browser

```
http://127.0.0.1:5000/
```

The database is **automatically created** on first run — no separate setup needed!

---

## Features

- **Add User**: Form with Name, Email, Phone, and Department
- **View Users**: Styled table with all records
- **Delete User**: Remove any user with a confirmation prompt
- **Persistent Storage**: Data is saved in `database.db` across restarts
- **Responsive UI**: Works on desktop and mobile
- **Auto-initialize DB**: Database and table are created automatically

---

## Application Flow

```
User fills form → POST /
       ↓
Flask receives form data
       ↓
Data inserted into SQLite (users table)
       ↓
Redirect to GET /
       ↓
Flask fetches all users from DB
       ↓
Renders index.html with users list
       ↓
User sees updated table
```

---

## Database Schema

```sql
CREATE TABLE users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL,
    phone       TEXT,
    department  TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Learning Outcomes

After completing this task, you will understand:
- How Flask handles GET and POST requests
- How HTML forms send data to a Python backend
- How SQLite stores and retrieves data
- How Jinja2 templates render dynamic content
- How frontend, backend, and database work together

---

*Maincrafts Technology | hr@maincrafts.com | www.maincrafts.com*
