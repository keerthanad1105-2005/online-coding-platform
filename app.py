from flask import Flask, render_template, request, redirect, session
import sqlite3
import subprocess
import os
from plagiarism import calculate_similarity

app = Flask(__name__)
app.secret_key = "secretkey"

# Create Database
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS submissions
                 (id INTEGER PRIMARY KEY, username TEXT, code TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/")
    return render_template("login.html")

# Home Page
@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect("/login")

    output = ""
    similarity = 0

    if request.method == "POST":
        code = request.form["code"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT code FROM submissions ORDER BY id DESC LIMIT 1")
        previous = c.fetchone()

        c.execute("INSERT INTO submissions (username, code) VALUES (?, ?)",
                  (session["user"], code))
        conn.commit()
        conn.close()

        # Execute Code
        try:
            with open("temp.py", "w") as f:
                f.write(code)

            result = subprocess.check_output(
                ["python", "temp.py"],
                stderr=subprocess.STDOUT,
                timeout=5
            )
            output = result.decode()

        except subprocess.TimeoutExpired:
            output = "Execution Timeout!"
        except Exception as e:
            output = str(e)

        if previous:
            similarity = calculate_similarity(previous[0], code)

        if os.path.exists("temp.py"):
            os.remove("temp.py")

    return render_template("index.html",
                           output=output,
                           similarity=similarity,
                           user=session["user"])

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)