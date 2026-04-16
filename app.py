from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"


# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prn TEXT,
        email TEXT,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_prn TEXT,
        room_no TEXT,
        category TEXT,
        description TEXT,
        status TEXT,
        worker TEXT,
        phone TEXT,
        date TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_prn TEXT,
        message TEXT,
        reply TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS timetable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT,
        breakfast TEXT,
        lunch TEXT,
        dinner TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------- ADD TEST USERS ----------------
def add_test_users():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM users")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (prn, password, role) VALUES (?, ?, ?)", ("123", "123", "student"))
        cur.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", ("admin@college.com", "admin", "admin"))

    conn.commit()
    conn.close()


init_db()
add_test_users()


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE prn=? AND password=? AND role='student'", (username, password))
        student = cur.fetchone()

        if student:
            session["student"] = username
            return redirect("/student_dashboard")

        cur.execute("SELECT * FROM users WHERE email=? AND password=? AND role='admin'", (username, password))
        admin = cur.fetchone()

        if admin:
            session["admin"] = username
            return redirect("/admin_dashboard")

        return "Invalid Login"

    return render_template("login.html")


# ---------------- STUDENT ----------------
@app.route("/student_dashboard")
def student_dashboard():
    if "student" in session:
        return render_template("student_dashboard.html")
    return redirect("/")


@app.route("/file_complaint")
def file_complaint():
    if "student" not in session:
        return redirect("/")
    return render_template("file_complaint.html")


@app.route("/complaint_form/<category>", methods=["GET", "POST"])
def complaint_form(category):
    if "student" not in session:
        return redirect("/")

    if request.method == "POST":
        room = request.form["room"]
        description = request.form["description"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO complaints (student_prn, room_no, category, description, status, worker, phone, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (session["student"], room, category, description, "Pending", "Not Assigned", "-", "-"))

        conn.commit()
        conn.close()

        return redirect("/view_status")

    return render_template("complaint_form.html", category=category)


@app.route("/view_status")
def view_status():
    if "student" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM complaints WHERE student_prn=?", (session["student"],))
    complaints = cur.fetchall()

    conn.close()

    return render_template("view_status.html", complaints=complaints)


@app.route("/view_timetable")
def view_timetable():
    if "student" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM timetable")
    data = cur.fetchall()

    conn.close()

    return render_template("view_timetable.html", data=data)


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if "student" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    if request.method == "POST":
        msg = request.form["message"]
        cur.execute("INSERT INTO feedback (student_prn, message, reply) VALUES (?, ?, ?)",
                    (session["student"], msg, "No reply"))
        conn.commit()

    conn.close()
    return render_template("feedback.html")


@app.route("/emergency")
def emergency():
    if "student" not in session:
        return redirect("/")
    return render_template("emergency.html")


# ---------------- ADMIN ----------------
@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/")
    

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM complaints")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'")
    pending = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM complaints WHERE status='Completed'")
    completed = cur.fetchone()[0]

    conn.close()

    return render_template("admin_dashboard.html", total=total, pending=pending, completed=completed)


# ✅ MATCHED WITH YOUR BUTTONS
@app.route("/view_complaints")
def view_complaints():
    return redirect("/admin_view_complaints")


@app.route("/pending_complaints")
def pending_complaints():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM complaints WHERE status='Pending'")
    complaints = cur.fetchall()

    conn.close()
    return render_template("admin_view_complaints.html", complaints=complaints)


@app.route("/resolved_complaints")
def resolved_complaints():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM complaints WHERE status='Completed'")
    complaints = cur.fetchall()

    conn.close()
    return render_template("admin_view_complaints.html", complaints=complaints)


@app.route("/view_feedback")
def view_feedback():
    return redirect("/admin_feedback")


@app.route("/delete_timetable/<int:id>")
def delete_timetable(id):
    if "admin" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM timetable WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/admin_timetable")


# ---------------- EXISTING ----------------
@app.route("/admin_view_complaints")
def admin_view_complaints():
    if "admin" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM complaints")
    complaints = cur.fetchall()

    conn.close()

    return render_template("admin_view_complaints.html", complaints=complaints)


@app.route("/admin_feedback")
def admin_feedback():
    if "admin" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM feedback")
    data = cur.fetchall()

    conn.close()

    return render_template("admin_feedback.html", data=data)
@app.route("/admin_timetable", methods=["GET", "POST"])
def admin_timetable():
    if "admin" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    if request.method == "POST":
        day = request.form["day"]
        breakfast = request.form["breakfast"]
        lunch = request.form["lunch"]
        dinner = request.form["dinner"]

        # check if day already exists
        cur.execute("SELECT * FROM timetable WHERE day=?", (day,))
        existing = cur.fetchone()

        if existing:
            cur.execute("""
            UPDATE timetable
            SET breakfast=?, lunch=?, dinner=?
            WHERE day=?
            """, (breakfast, lunch, dinner, day))
        else:
            cur.execute("""
            INSERT INTO timetable (day, breakfast, lunch, dinner)
            VALUES (?, ?, ?, ?)
            """, (day, breakfast, lunch, dinner))

        conn.commit()

    cur.execute("SELECT * FROM timetable")
    data = cur.fetchall()

    conn.close()

    return render_template("admin_timetable.html", data=data)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
    