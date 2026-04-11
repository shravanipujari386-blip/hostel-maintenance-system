from flask import flash
from flask import Flask, render_template, request, redirect, session
from database import create_tables, seed_data
from models import Student, Admin

app = Flask(__name__)
app.secret_key = "secret123"

# Initialize database
create_tables()
seed_data()


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        password = request.form.get("password")

        if role == "student":
            prn = request.form.get("prn")

            user = Student(prn, password)
            if user.login():
                session["user"] = prn
                session["role"] = "student"
                return redirect("/student")
            else:
                return "Invalid Student Login"

        elif role == "admin":
            email = request.form.get("email")

            admin = Admin(email, password)
            if admin.login():
                session["user"] = email
                session["role"] = "admin"
                return redirect("/admin")
            else:
                return "Invalid Admin Login"

    return render_template("login.html")


# ---------------- STUDENT DASHBOARD ----------------
@app.route("/student")
def student_dashboard():
    if "user" not in session or session["role"] != "student":
        return redirect("/")
    return render_template("student_dashboard.html")


# ---------------- FILE COMPLAINT ----------------
@app.route("/complaint", methods=["GET", "POST"])
def complaint():
    if request.method == "POST":
        room = request.form["room"]
        category = request.form["category"]
        desc = request.form["desc"]

        student = Student(session["user"], "")
        student.file_complaint(room, category, desc)

        flash("✅ Complaint submitted successfully!")

        return redirect("/student")

    return render_template("complaint.html")


# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin_dashboard():
    if "user" not in session or session["role"] != "admin":
        return redirect("/")

    admin = Admin(session["user"], "")
    data = admin.view_complaints()

    # Count status
    pending = sum(1 for row in data if row[5] == "Pending")
    progress = sum(1 for row in data if row[5] == "In Progress")
    completed = sum(1 for row in data if row[5] == "Completed")

    return render_template(
        "admin_dashboard.html",
        data=data,
        pending=pending,
        progress=progress,
        completed=completed
    )


# ---------------- UPDATE STATUS ----------------
@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    if "user" not in session or session["role"] != "admin":
        return redirect("/")

    status = request.form["status"]
    worker = request.form["worker"]

    admin = Admin(session["user"], "")
    admin.update_status(id, status, worker)

    return redirect("/admin")

@app.route("/my_complaints")
def my_complaints():
    if "user" not in session:
        return redirect("/")

    filter_status = request.args.get("status")

    student = Student(session["user"], "")
    data = student.view_complaints()

    if filter_status and filter_status != "All":
        data = [row for row in data if row[5] == filter_status]

    return render_template("status.html", data=data)

# ---------------- CHANGE PASSWORD ----------------
@app.route("/change_password", methods=["POST"])
def change_password():
    if "user" not in session:
        return redirect("/")

    new_pass = request.form["new_pass"]
    identifier = session["user"]

    if session["role"] == "student":
        user = Student(identifier, "")
    else:
        user = Admin(identifier, "")

    user.change_password(new_pass, identifier)

    return redirect("/")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)