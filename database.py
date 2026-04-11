import sqlite3

def connect():
    return sqlite3.connect("hostel.db")


def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prn TEXT,
        email TEXT,
        password TEXT,
        role TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_prn TEXT,
        room_no TEXT,
        category TEXT,
        description TEXT,
        status TEXT,
        worker TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()


def seed_data():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    if count == 0:
        for i in range(1, 51):
            prn = f"100{i:03}"
            cursor.execute(
                "INSERT INTO users (prn, password, role) VALUES (?, ?, ?)",
                (prn, prn, "student")
            )

        cursor.execute(
            "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
            ("admin@college.com", "admin@college.com", "admin")
        )

    conn.commit()
    conn.close()