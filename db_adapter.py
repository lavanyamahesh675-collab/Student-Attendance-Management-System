import os
import sqlite3

class SQLiteCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query, params=None):
        # Translate MySQL syntax to SQLite syntax
        q = query.replace('%s', '?')
        # Translate MySQL GROUP_CONCAT SEPARATOR to SQLite syntax
        q = q.replace("SEPARATOR ', '", ", ', '").replace("SEPARATOR ','", ", ','")
        # Translate ON DUPLICATE KEY UPDATE to SQLite ON CONFLICT
        if 'ON DUPLICATE KEY UPDATE' in q:
            q = q.replace('ON DUPLICATE KEY UPDATE status = VALUES(status)',
                          'ON CONFLICT(student_id, subject_id, attendance_date) DO UPDATE SET status = excluded.status')
        if params is not None:
            return self.cursor.execute(q, params)
        return self.cursor.execute(q)

    def fetchone(self):
        row = self.cursor.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self):
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    def close(self):
        self.cursor.close()

class SQLiteConnWrapper:
    def __init__(self, conn):
        self.conn = conn

    def cursor(self, dictionary=False):
        return SQLiteCursorWrapper(self.conn.cursor())

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

def init_sqlite_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_number TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        department TEXT NOT NULL,
        year INTEGER NOT NULL,
        section TEXT NOT NULL,
        batch TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS subjects (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT UNIQUE NOT NULL,
        subject_name TEXT NOT NULL,
        semester INTEGER NOT NULL,
        faculty_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (faculty_id) REFERENCES users(user_id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS attendance (
        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        attendance_date TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
        UNIQUE (student_id, subject_id, attendance_date)
    );
    """)

    admin_hash = 'pbkdf2:sha256:1000000$QF1DwkXjiHWkgPca$fabf72e5e60398401a24c6722fa9e36e311b77ff1098f6ef392f445d53cbd834'
    faculty_hash = 'pbkdf2:sha256:1000000$9udbeR1Pr1VHgwZb$033c464ecd2e4cd9021291d76bb3f2eb689519d72ddff075cdec89f15935c075'

    # Seed users if not present
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO users (user_id, name, email, password, role) VALUES
        (1, 'System Administrator', 'admin@attendance.com', ?, 'admin'),
        (2, 'Dr. Ramesh Verma', 'faculty@attendance.com', ?, 'faculty'),
        (3, 'Prof. Sunita Sharma', 'prof.sharma@attendance.com', ?, 'faculty')
        """, (admin_hash, faculty_hash, faculty_hash))
    else:
        # Ensure password hashes are always valid and working for demo logins
        cursor.execute("UPDATE users SET password = ? WHERE email = 'admin@attendance.com'", (admin_hash,))
        cursor.execute("UPDATE users SET password = ? WHERE email = 'faculty@attendance.com'", (faculty_hash,))
        cursor.execute("UPDATE users SET password = ? WHERE email = 'prof.sharma@attendance.com'", (faculty_hash,))

    # Seed students if not present
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO students (student_id, roll_number, name, email, phone, department, year, section, batch) VALUES
        (1, '101', 'Ravi Kumar', 'ravi.kumar@college.edu', '9876543210', 'CSM', 2, 'A', '2023-2027'),
        (2, '102', 'Anu Sharma', 'anu.sharma@college.edu', '9876543211', 'CSM', 2, 'A', '2023-2027'),
        (3, '103', 'Rahul Verma', 'rahul.verma@college.edu', '9876543212', 'CSM', 2, 'A', '2023-2027'),
        (4, '104', 'Priya Patel', 'priya.patel@college.edu', '9876543213', 'CSE', 2, 'A', '2023-2027'),
        (5, '105', 'Amit Singh', 'amit.singh@college.edu', '9876543214', 'CSE', 2, 'A', '2023-2027'),
        (6, '106', 'Sneha Reddy', 'sneha.reddy@college.edu', '9876543215', 'CSE', 2, 'B', '2023-2027'),
        (7, '107', 'Vikram Rao', 'vikram.rao@college.edu', '9876543216', 'ECE', 2, 'A', '2023-2027'),
        (8, '108', 'Pooja Gupta', 'pooja.gupta@college.edu', '9876543217', 'ECE', 2, 'A', '2023-2027'),
        (9, '109', 'Karthik Nair', 'karthik.nair@college.edu', '9876543218', 'CSM', 2, 'B', '2023-2027'),
        (10, '110', 'Ananya Roy', 'ananya.roy@college.edu', '9876543219', 'CSM', 2, 'B', '2023-2027')
        """)

    # Seed subjects if not present
    cursor.execute("SELECT COUNT(*) FROM subjects")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO subjects (subject_id, subject_code, subject_name, semester, faculty_id) VALUES
        (1, 'CS301', 'Database Management Systems', 4, 2),
        (2, 'CS302', 'Java Programming', 4, 3),
        (3, 'CS303', 'Operating Systems', 4, 2),
        (4, 'CS304', 'Computer Networks', 4, 3)
        """)

    # Seed attendance records if not present
    cursor.execute("SELECT COUNT(*) FROM attendance")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO attendance (student_id, subject_id, attendance_date, status) VALUES
        (1, 1, '2026-09-20', 'Present'),
        (2, 1, '2026-09-20', 'Present'),
        (3, 1, '2026-09-20', 'Absent'),
        (1, 1, '2026-09-21', 'Present'),
        (2, 1, '2026-09-21', 'Absent'),
        (3, 1, '2026-09-21', 'Absent'),
        (1, 1, '2026-09-22', 'Present'),
        (2, 1, '2026-09-22', 'Present'),
        (3, 1, '2026-09-22', 'Present'),
        (1, 1, '2026-09-23', 'Present'),
        (2, 1, '2026-09-23', 'Present'),
        (3, 1, '2026-09-23', 'Absent'),
        (1, 1, '2026-09-24', 'Present'),
        (2, 1, '2026-09-24', 'Absent'),
        (3, 1, '2026-09-24', 'Absent'),
        (4, 2, '2026-09-20', 'Present'),
        (5, 2, '2026-09-20', 'Present'),
        (4, 2, '2026-09-21', 'Present'),
        (5, 2, '2026-09-21', 'Absent'),
        (4, 2, '2026-09-22', 'Present'),
        (5, 2, '2026-09-22', 'Present')
        """)

    conn.commit()
    conn.close()
