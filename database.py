"""
database.py  (v2 - Enhanced)
-----------------------------
SQLite database operations:
  - students, attendance, subjects, settings tables
  - attendance percentage, department stats, student profiles
  - late marking, bulk import, subject-wise filtering
"""

import sqlite3
import streamlit as st
import libsql
import os
from datetime import datetime, date

DB_DIR = os.path.join(os.path.dirname(__file__), "database")
DB_PATH = os.path.join(DB_DIR, "attendance.db")


def get_connection():
    conn = libsql.connect(
        database=st.secrets["TURSO_DATABASE_URL"],
        auth_token=st.secrets["TURSO_AUTH_TOKEN"],
    )
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id   TEXT PRIMARY KEY,
            name         TEXT NOT NULL,
            department   TEXT,
            email        TEXT,
            image_path   TEXT NOT NULL,
            registered_on TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id   TEXT NOT NULL,
            name         TEXT NOT NULL,
            date         TEXT NOT NULL,
            time         TEXT NOT NULL,
            subject      TEXT DEFAULT 'General',
            status       TEXT NOT NULL DEFAULT 'Present',
            is_late      INTEGER DEFAULT 0,
            confidence   REAL,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            UNIQUE (student_id, date, subject)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Seed default subjects
    default_subjects = ["General", "Mathematics", "Physics", "Chemistry",
                        "Computer Science", "English", "Lab"]
    for s in default_subjects:
        cur.execute("INSERT OR IGNORE INTO subjects (name) VALUES (?)", (s,))

    # Seed default settings
    import hashlib
    default_hash = hashlib.sha256("admin123".encode()).hexdigest()
    defaults = [
        ("admin_username", "admin"),
        ("admin_password_hash", default_hash),
        ("late_threshold", "09:30"),
        ("recognition_threshold", "0.40"),
    ]
    for k, v in defaults:
        cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

    # Backward compat: add columns if missing
    try:
        cur.execute("ALTER TABLE attendance ADD COLUMN subject TEXT DEFAULT 'General'")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE attendance ADD COLUMN is_late INTEGER DEFAULT 0")
    except Exception:
        pass

    conn.commit()
    conn.close()


# ------------------------------------------------------------------
# Settings
# ------------------------------------------------------------------

def get_setting(key, default=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else default


def set_setting(key, value):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()


# ------------------------------------------------------------------
# Subjects
# ------------------------------------------------------------------

def get_subjects():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM subjects ORDER BY name")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows


def add_subject(name):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def delete_subject(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM subjects WHERE name = ?", (name,))
    conn.commit()
    conn.close()


# ------------------------------------------------------------------
# Student CRUD
# ------------------------------------------------------------------

def add_student(student_id, name, department, email, image_path):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO students (student_id, name, department, email, image_path, registered_on)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (student_id, name, department, email, image_path,
          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_all_students():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT student_id, name, department, email, image_path, registered_on FROM students ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows


def student_exists(student_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM students WHERE student_id = ?", (student_id,))
    result = cur.fetchone()
    conn.close()
    return result is not None


def delete_student(student_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    cur.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()


def bulk_add_students(records):
    """records = list of (student_id, name, department, email, image_path) tuples"""
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    added = 0
    skipped = 0
    for r in records:
        try:
            cur.execute("""
                INSERT INTO students (student_id, name, department, email, image_path, registered_on)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (*r, now))
            added += 1
        except sqlite3.IntegrityError:
            skipped += 1
    conn.commit()
    conn.close()
    return added, skipped


# ------------------------------------------------------------------
# Attendance
# ------------------------------------------------------------------

def _is_late(time_str):
    threshold = get_setting("late_threshold", "09:30")
    return time_str > threshold


def mark_attendance(student_id, name, subject="General", confidence=None):
    today = date.today().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")
    late = 1 if _is_late(now_time) else 0
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO attendance (student_id, name, date, time, subject, status, is_late, confidence)
            VALUES (?, ?, ?, ?, ?, 'Present', ?, ?)
        """, (student_id, name, today, now_time, subject, late, confidence))
        conn.commit()
        marked = True
    except sqlite3.IntegrityError:
        marked = False
    finally:
        conn.close()
    return marked, late


def already_marked_today(student_id, subject="General"):
    today = date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM attendance WHERE student_id=? AND date=? AND subject=?",
                (student_id, today, subject))
    result = cur.fetchone()
    conn.close()
    return result is not None


def get_attendance_by_date(target_date=None, subject=None):
    target_date = target_date or date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    cur = conn.cursor()
    if subject and subject != "All":
        cur.execute("""
            SELECT student_id, name, date, time, subject, status, is_late, confidence
            FROM attendance WHERE date=? AND subject=? ORDER BY time
        """, (target_date, subject))
    else:
        cur.execute("""
            SELECT student_id, name, date, time, subject, status, is_late, confidence
            FROM attendance WHERE date=? ORDER BY time
        """, (target_date,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_attendance_range(start_date, end_date, subject=None):
    conn = get_connection()
    cur = conn.cursor()
    if subject and subject != "All":
        cur.execute("""
            SELECT student_id, name, date, time, subject, status, is_late, confidence
            FROM attendance WHERE date BETWEEN ? AND ? AND subject=?
            ORDER BY date, time
        """, (start_date, end_date, subject))
    else:
        cur.execute("""
            SELECT student_id, name, date, time, subject, status, is_late, confidence
            FROM attendance WHERE date BETWEEN ? AND ?
            ORDER BY date, time
        """, (start_date, end_date))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_student_attendance(student_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT date, time, subject, status, is_late, confidence
        FROM attendance WHERE student_id=? ORDER BY date DESC
    """, (student_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_attendance_percentage(student_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM attendance WHERE student_id=?", (student_id,))
    present = cur.fetchone()[0]
    # Count working days since registration
    cur.execute("SELECT registered_on FROM students WHERE student_id=?", (student_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return 0, 0, 0
    return present, present, round((present / max(present, 1)) * 100, 1)


def get_department_stats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.department, COUNT(DISTINCT s.student_id) as total,
               COUNT(DISTINCT a.student_id) as present_today
        FROM students s
        LEFT JOIN attendance a ON s.student_id = a.student_id
            AND a.date = date('now')
        GROUP BY s.department
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_today_stats():
    conn = get_connection()
    cur = conn.cursor()
    today = date.today().strftime("%Y-%m-%d")
    cur.execute("SELECT COUNT(*) FROM students")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT student_id) FROM attendance WHERE date=?", (today,))
    present = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND is_late=1", (today,))
    late = cur.fetchone()[0]
    conn.close()
    return total, present, max(0, total - present), late


def get_weekly_trend():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT date, COUNT(DISTINCT student_id) as count
        FROM attendance
        WHERE date >= date('now', '-6 days')
        GROUP BY date ORDER BY date
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


# ------------------------------------------------------------------
# Activity Log
# ------------------------------------------------------------------

def _ensure_log_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            actor     TEXT NOT NULL,
            action    TEXT NOT NULL,
            details   TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_activity(actor, action, details=""):
    _ensure_log_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO activity_log (timestamp, actor, action, details)
        VALUES (?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), actor, action, details))
    conn.commit()
    conn.close()


def get_activity_log(limit=100):
    _ensure_log_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT timestamp, actor, action, details
        FROM activity_log ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


# ------------------------------------------------------------------
# Timetable
# ------------------------------------------------------------------

def _ensure_timetable_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS timetable (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            day        TEXT NOT NULL,
            time_slot  TEXT NOT NULL,
            subject    TEXT NOT NULL,
            teacher    TEXT,
            room       TEXT,
            UNIQUE(day, time_slot, subject)
        )
    """)
    conn.commit()
    conn.close()


def add_timetable_entry(day, time_slot, subject, teacher="", room=""):
    _ensure_timetable_table()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO timetable (day, time_slot, subject, teacher, room)
            VALUES (?, ?, ?, ?, ?)
        """, (day, time_slot, subject, teacher, room))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_timetable():
    _ensure_timetable_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, day, time_slot, subject, teacher, room
        FROM timetable ORDER BY
        CASE day
            WHEN 'Monday'    THEN 1 WHEN 'Tuesday'   THEN 2
            WHEN 'Wednesday' THEN 3 WHEN 'Thursday'  THEN 4
            WHEN 'Friday'    THEN 5 WHEN 'Saturday'  THEN 6
        END, time_slot
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_timetable_entry(entry_id):
    _ensure_timetable_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM timetable WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()


# ------------------------------------------------------------------
# Absent Students (registered but not marked today)
# ------------------------------------------------------------------

def get_absent_students(target_date=None, subject=None):
    target_date = target_date or date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    cur = conn.cursor()
    if subject and subject != "All":
        cur.execute("""
            SELECT s.student_id, s.name, s.department, s.email
            FROM students s
            WHERE s.student_id NOT IN (
                SELECT a.student_id FROM attendance a
                WHERE a.date=? AND a.subject=?
            ) ORDER BY s.name
        """, (target_date, subject))
    else:
        cur.execute("""
            SELECT s.student_id, s.name, s.department, s.email
            FROM students s
            WHERE s.student_id NOT IN (
                SELECT DISTINCT a.student_id FROM attendance a WHERE a.date=?
            ) ORDER BY s.name
        """, (target_date,))
    rows = cur.fetchall()
    conn.close()
    return rows


def mark_manual_attendance(student_id, name, subject="General", status="Present", note="Manual"):
    today = date.today().strftime("%Y-%m-%d")
    now_t = datetime.now().strftime("%H:%M:%S")
    late  = 1 if now_t > get_setting("late_threshold","09:30") + ":00" else 0
    conn  = get_connection()
    cur   = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO attendance (student_id, name, date, time, subject, status, is_late, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1.0)
        """, (student_id, name, today, now_t, subject, status, late))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Update existing
        cur.execute("""
            UPDATE attendance SET status=?, time=?, is_late=?
            WHERE student_id=? AND date=? AND subject=?
        """, (status, now_t, late, student_id, today, subject))
        conn.commit()
        return True
    finally:
        conn.close()


# ------------------------------------------------------------------
# Low Attendance & Class Summary helpers
# ------------------------------------------------------------------

def get_all_student_attendance_summary():
    """Returns list of (student_id, name, dept, total_present, last_seen)."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT s.student_id, s.name, s.department,
               COUNT(a.id) as present_days,
               MAX(a.date) as last_seen
        FROM students s
        LEFT JOIN attendance a ON s.student_id = a.student_id
        GROUP BY s.student_id
        ORDER BY present_days DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_subject_summary():
    """Per-subject: total records, unique students, late count."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT subject,
               COUNT(*) as total,
               COUNT(DISTINCT student_id) as students,
               SUM(is_late) as late_count,
               MAX(date) as last_class
        FROM attendance
        GROUP BY subject
        ORDER BY total DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_daily_counts_for_month(year, month):
    """Returns dict {date_str: count} for the given month."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT date, COUNT(DISTINCT student_id) as cnt
        FROM attendance
        WHERE strftime('%Y', date)=? AND strftime('%m', date)=?
        GROUP BY date
    """, (str(year), f"{month:02d}"))
    rows = cur.fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def get_today_timetable():
    """Return timetable entries for today's day name."""
    day_name = date.today().strftime("%A")
    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.execute("""
            SELECT time_slot, subject, teacher, room
            FROM timetable WHERE day=? ORDER BY time_slot
        """, (day_name,))
        rows = cur.fetchall()
    except Exception:
        rows = []
    conn.close()
    return rows


def get_weekly_comparison():
    """This week vs last week attendance counts."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT
            SUM(CASE WHEN date >= date('now','-6 days') THEN 1 ELSE 0 END) as this_week,
            SUM(CASE WHEN date >= date('now','-13 days') AND date < date('now','-6 days') THEN 1 ELSE 0 END) as last_week
        FROM attendance
    """)
    row = cur.fetchone()
    conn.close()
    return (row[0] or 0, row[1] or 0)