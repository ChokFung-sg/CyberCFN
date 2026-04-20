import sqlite3
import os

# ================= DATABASE PATH (MUST MATCH app.py) =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "database.db")

# Create connection
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ================= USER TABLE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    username TEXT,
    points INTEGER DEFAULT 0,
    role TEXT DEFAULT 'user'
)
""")

# ================= PROGRESS SYSTEM =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course TEXT NOT NULL,
    day INTEGER NOT NULL,
    UNIQUE(user_id, course)
)
""")

# ================= ACHIEVEMENTS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS achievement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    unlocked INTEGER DEFAULT 0
)
""")

# ================= FRIENDS SYSTEM =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS friends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    friend_username TEXT NOT NULL
)
""")

# ================= COMMIT & CLOSE =================
conn.commit()
conn.close()

print("✅ DATABASE INITIALIZED SUCCESSFULLY")