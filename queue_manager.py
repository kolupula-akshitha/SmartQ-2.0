import sqlite3
from database import get_connection


def book_token(name, username, phone, department, doctor):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT MAX(token) FROM appointments
        WHERE department = ? AND doctor = ?
        AND DATE(appointment_time) = DATE('now', 'localtime')
    """, (department, doctor))

    result = cursor.fetchone()[0]
    token = (result or 0) + 1

    counter = 1

    cursor.execute("""
        INSERT INTO appointments
        (patient_name, username, phone_number,
         department, doctor, token, counter_number)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, username, phone, department, doctor, token, counter))

    conn.commit()
    conn.close()

    return token


def get_queue():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT token, patient_name, department,
               doctor, status, counter_number
        FROM appointments
        WHERE status IN ('Waiting', 'Called')
        ORDER BY id
    """)

    data = cursor.fetchall()
    conn.close()

    return data


def get_patient_tokens(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT token, department, doctor,
               status, counter_number, appointment_time
        FROM appointments
        WHERE username = ?
        ORDER BY id DESC
    """, (username,))

    data = cursor.fetchall()
    conn.close()

    return data


def call_next_patient():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, token, patient_name, phone_number
        FROM appointments
        WHERE status = 'Waiting'
        ORDER BY id
        LIMIT 1
    """)

    patient = cursor.fetchone()

    if patient:
        cursor.execute("""
            UPDATE appointments
            SET status = 'Called'
            WHERE id = ?
        """, (patient[0],))

        conn.commit()

    conn.close()
    return patient


def get_waiting_count(token, department, doctor):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM appointments
        WHERE department = ? AND doctor = ?
        AND token < ? AND status = 'Waiting'
    """, (department, doctor, token))

    count = cursor.fetchone()[0]
    conn.close()

    return count

def get_token_details(token):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT token, patient_name, department,
               doctor, status, counter_number
        FROM appointments
        WHERE token = ?
        ORDER BY id DESC
        LIMIT 1
    """, (token,))

    result = cursor.fetchone()
    conn.close()

    return result