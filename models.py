from database import connect
from datetime import datetime


# ---------------- BASE CLASS ----------------
class User:
    def __init__(self, password):
        self.password = password

    def change_password(self, new_password, identifier):
        conn = connect()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET password=? WHERE prn=? OR email=?",
            (new_password, identifier, identifier)
        )

        conn.commit()
        conn.close()


# ---------------- STUDENT CLASS ----------------
class Student(User):
    def __init__(self, prn, password):
        super().__init__(password)
        self.prn = prn

    def register(self):
        conn = connect()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (prn, password, role) VALUES (?, ?, ?)",
            (self.prn, self.password, "student")
        )

        conn.commit()
        conn.close()

    def login(self):
        conn = connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE prn=? AND password=? AND role='student'",
            (self.prn, self.password)
        )

        user = cursor.fetchone()
        conn.close()
        return user

    def file_complaint(self, room, category, description):
        conn = connect()
        cursor = conn.cursor()

        # 📅 Add current date & time
        date = datetime.now().strftime("%Y-%m-%d %H:%M")

        cursor.execute("""
        INSERT INTO complaints 
        (student_prn, room_no, category, description, status, worker, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (self.prn, room, category, description, "Pending", "Not Assigned", date))

        conn.commit()
        conn.close()

    def view_complaints(self):
        conn = connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM complaints WHERE student_prn=?",
            (self.prn,)
        )

        data = cursor.fetchall()
        conn.close()
        return data


# ---------------- ADMIN CLASS ----------------
class Admin(User):
    def __init__(self, email, password):
        super().__init__(password)
        self.email = email

    def register(self):
        conn = connect()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
            (self.email, self.password, "admin")
        )

        conn.commit()
        conn.close()

    def login(self):
        conn = connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=? AND role='admin'",
            (self.email, self.password)
        )

        admin = cursor.fetchone()
        conn.close()
        return admin

    def view_complaints(self):
        conn = connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM complaints")
        data = cursor.fetchall()

        conn.close()
        return data

    def update_status(self, comp_id, status, worker):
        conn = connect()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE complaints 
        SET status=?, worker=? 
        WHERE id=?
        """, (status, worker, comp_id))

        conn.commit()
        conn.close()