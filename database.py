import sqlite3
import hashlib

DB_NAME = "hospital.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'patient'
        )
    """)

    # Appointments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            username TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            department TEXT NOT NULL,
            doctor TEXT NOT NULL,
            token INTEGER NOT NULL,
            counter_number INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Waiting',
            appointment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Default admin account
    cursor.execute("""
        INSERT OR IGNORE INTO users
        (username, password, role)
        VALUES (?, ?, ?)
    """, ("admin", hash_password("admin123"), "admin"))

    conn.commit()
    conn.close()


def register_user(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, 'patient')
        """, (username, hash_password(password)))

        conn.commit()
        conn.close()
        return True

    except sqlite3.IntegrityError:
        return False


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role FROM users
        WHERE username = ? AND password = ?
    """, (username, hash_password(password)))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None