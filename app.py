from flask import Flask, render_template, request, redirect, session

import sqlite3

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        username TEXT,
        points INTEGER DEFAULT 0,
        role TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        friend_username TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

import os

DB_PATH = "database.db"

def get_db():
    return sqlite3.connect(DB_PATH)

app = Flask(__name__)
app.secret_key = "secretkey"

# ================= DATABASE =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = "database.db"

def get_db():
    return sqlite3.connect(DB_PATH)


# ================= HOME =================
@app.route("/")
def home():
    return render_template("hero.html")


# ================= AUTH (UNCHANGED) =================
@app.route("/auth", methods=["GET", "POST"])
def auth():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        action = request.form["action"]

        db = get_db()
        cursor = db.cursor()

        if action == "register":
            try:
                cursor.execute(
                    "INSERT INTO user (email, password, points, role) VALUES (?, ?, 0, 'user')",
                    (email, password)
                )
                db.commit()
                session["user_id"] = cursor.lastrowid
                return redirect("/create-username")
            except:
                return "Account exists"

        elif action == "login":
            user = cursor.execute(
                "SELECT id, username FROM user WHERE email=? AND password=?",
                (email, password)
            ).fetchone()

            if user:
                session["user_id"] = user[0]
                if user[1] is None:
                    return redirect("/create-username")
                return redirect("/dashboard")

            return "Invalid login"

    return render_template("auth.html")

@app.route("/welcome")
def welcome():
    if "user_id" not in session:
        return redirect("/auth")

    db = get_db()

    user = db.execute(
        "SELECT username FROM user WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    return render_template("welcome.html", user=user)


# ================= CREATE USERNAME =================
@app.route("/create-username", methods=["GET", "POST"])
def create_username():
    if "user_id" not in session:
        return redirect("/auth")

    if request.method == "POST":
        username = request.form["username"]

        db = get_db()
        db.execute(
            "UPDATE user SET username=? WHERE id=?",
            (username, session["user_id"])
        )
        db.commit()

        return redirect("/dashboard")

    return render_template("create_username.html")


# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/auth")

    db = get_db()
    user = db.execute(
        "SELECT username, points FROM user WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    return render_template("dashboard.html", user=user)


# ================= COURSES MAIN =================
@app.route("/courses")
def courses():
    return render_template("courses.html")


# ================= CRASH COURSE (FIXED) =================
@app.route("/crash-course")
def crash_course():
    return redirect("/course/cyber")


# ================= COURSE SYSTEM =================
@app.route("/course/<lang>")
def course(lang):
    return render_template("course.html", lang=lang)


# ================= LESSON SLIDES (CRASH) =================
@app.route("/crash/<int:day>/<int:slide>")
def crash_slide(day, slide):
    if "user_id" not in session:
        return redirect("/auth")

    lessons = {
        1: [
            "Cybersecurity protects systems and data.",
            "CIA Triad: Confidentiality, Integrity, Availability.",
            "Threats include phishing and malware."
        ],
        2: [
            "IP identifies devices.",
            "DNS converts names to IP.",
            "Ports handle communication."
        ],
        3: [
            "Encryption protects data.",
            "Firewalls block threats.",
            "Authentication verifies identity."
        ]
    }

    slides = lessons.get(day, [])

    if not slides:
        return "Lesson not found"

    if slide > len(slides):
        return redirect("/dashboard")

    return render_template(
        "crash_slide.html",
        content=slides[slide-1],
        day=day,
        slide=slide
    )


# ================= SIMULATOR =================
@app.route("/simulator", methods=["GET", "POST"])
def simulator():
    result = None

    if request.method == "POST":
        answer = request.form.get("answer", "")

        if answer.lower() == "phishing":
            result = "Correct"
        else:
            result = "Incorrect"

    return render_template("simulator.html", result=result)


# ================= FRIENDS =================
@app.route("/friends", methods=["GET", "POST"])
def friends():
    if "user_id" not in session:
        return redirect("/auth")

    db = get_db()

    if request.method == "POST":
        friend = request.form["friend"]

        db.execute(
            "INSERT INTO friends (user_id, friend_username) VALUES (?, ?)",
            (session["user_id"], friend)
        )
        db.commit()

    data = db.execute(
        "SELECT friend_username FROM friends WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()

    return render_template("friends.html", data=data)


# ================= PROFILE =================
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/auth")

    db = get_db()
    user = db.execute(
        "SELECT username, points FROM user WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    return render_template("profile.html", user=user)


# ================= LEADERBOARD =================
@app.route("/leaderboard")
def leaderboard():
    db = get_db()

    users = db.execute(
        "SELECT username, points FROM user ORDER BY points DESC"
    ).fetchall()

    return render_template("leaderboard.html", users=users)


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run()