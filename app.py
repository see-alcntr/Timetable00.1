from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secretkey123"

# ---------------- DATABASE PATH (RENDER SAFE) ----------------
DB_PATH = os.path.join(os.getcwd(), "database.db")

# ---------------- INIT DB ----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        subject TEXT,
        day TEXT,
        time TEXT,
        color TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")

        return "Invalid login"

    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return "Missing fields", 400

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # check duplicate
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        if c.fetchone():
            conn.close()
            return "User already exists"

        c.execute("INSERT INTO users(username, password, role) VALUES (?, ?, ?)",
                  (username, password, "student"))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM schedules WHERE user_id=?", (session["user_id"],))
    data = c.fetchall()

    conn.close()

    return render_template("dashboard.html", data=data)


# ---------------- ADD ----------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user_id" not in session:
        return redirect("/")

    if request.method == "POST":
        subject = request.form.get("subject")
        day = request.form.get("day")
        time = request.form.get("time")
        color = request.form.get("color")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("""
        INSERT INTO schedules(user_id, subject, day, time, color)
        VALUES (?, ?, ?, ?, ?)
        """, (session["user_id"], subject, day, time, color))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add.html")


# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("DELETE FROM schedules WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RENDER FIX ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
