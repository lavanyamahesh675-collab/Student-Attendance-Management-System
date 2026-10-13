import os
import re
from datetime import date, datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

import db_adapter
import sqlite3

# ---------------------------------------------------------
# DATABASE CONNECTION HELPER (Supports MySQL & Free Cloud Fallback)
# ---------------------------------------------------------
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME'],
            port=app.config['DB_PORT']
        )
        return conn
    except Exception as err:
        app.logger.info(f"MySQL not available ({err}), activating 100% Free Cloud Database...")
        db_path = os.path.join(os.path.dirname(__file__), 'attendance.db')
        db_adapter.init_sqlite_db(db_path)
        raw_conn = sqlite3.connect(db_path)
        raw_conn.row_factory = sqlite3.Row
        return db_adapter.SQLiteConnWrapper(raw_conn)


# ---------------------------------------------------------
# AUTHENTICATION & ROLE-BASED ACCESS DECORATORS
# ---------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first to access the system.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first to access the system.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Unauthorized access! Admin privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------------------------
# VALIDATION HELPERS
# ---------------------------------------------------------
def is_valid_email(email):
    regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(regex, email) is not None

# ---------------------------------------------------------
# LOGIN & LOGOUT ROUTES
# ---------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Server-side validation
        if not email or not password:
            flash('Both Email and Password are required.', 'danger')
            return render_template('login.html')

        if not is_valid_email(email):
            flash('Invalid email format.', 'danger')
            return render_template('login.html')

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed! Ensure MySQL service is running.', 'danger')
            return render_template('login.html')

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user:
                # Check password with Werkzeug hash or plain fallback
                is_valid_pwd = False
                try:
                    if check_password_hash(user['password'], password):
                        is_valid_pwd = True
                except Exception:
                    pass

                if not is_valid_pwd and user['password'] == password:
                    is_valid_pwd = True

                if is_valid_pwd:
                    session['user_id'] = user['user_id']
                    session['user_name'] = user['name']
                    session['user_email'] = user['email']
                    session['role'] = user['role']
                    flash(f"Welcome back, {user['name']}!", 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid password. Please try again.', 'danger')
            else:
                flash('No account found with this email address.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

# ---------------------------------------------------------
# DASHBOARD ROUTE
# ---------------------------------------------------------
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    if not conn:
        flash('Failed to connect to MySQL database.', 'danger')
        return render_template('dashboard.html', stats={}, recent_attendance=[], active_page='dashboard')

    cursor = conn.cursor(dictionary=True)
    try:
        # Total Students Count
        cursor.execute("SELECT COUNT(*) AS count FROM students")
        total_students = cursor.fetchone()['count']

        # Total Faculty Count
        cursor.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'faculty'")
        total_faculty = cursor.fetchone()['count']

        # Total Subjects Count
        cursor.execute("SELECT COUNT(*) AS count FROM subjects")
        total_subjects = cursor.fetchone()['count']

        # Today's Attendance Count
        today_str = date.today().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) AS count FROM attendance WHERE attendance_date = %s", (today_str,))
        today_attendance_count = cursor.fetchone()['count']

        # Recent Attendance Log
        cursor.execute("""
            SELECT a.attendance_date, a.status, s.roll_number, s.name AS student_name,
                   s.department, s.year, s.section, sub.subject_name, sub.subject_code
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            JOIN subjects sub ON a.subject_id = sub.subject_id
            ORDER BY a.attendance_id DESC
            LIMIT 8
        """)
        recent_attendance = cursor.fetchall()

        stats = {
            'total_students': total_students,
            'total_faculty': total_faculty,
            'total_subjects': total_subjects,
            'today_attendance_count': today_attendance_count
        }

        return render_template('dashboard.html', stats=stats, recent_attendance=recent_attendance, active_page='dashboard')
    finally:
        cursor.close()
        conn.close()

# ---------------------------------------------------------
# STUDENT MANAGEMENT (CRUD)
# ---------------------------------------------------------
@app.route('/students')
@login_required
def list_students():
    dept = request.args.get('dept', '').strip()
    sec = request.args.get('section', '').strip()

    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'danger')
        return render_template('students/list.html', students=[], active_page='students')

    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM students WHERE 1=1"
        params = []
        if dept:
            query += " AND department = %s"
            params.append(dept)
        if sec:
            query += " AND section = %s"
            params.append(sec)

        query += " ORDER BY roll_number ASC"
        cursor.execute(query, tuple(params))
        students = cursor.fetchall()

        return render_template('students/list.html', students=students, selected_dept=dept, selected_section=sec, active_page='students')
    finally:
        cursor.close()
        conn.close()

@app.route('/students/add', methods=['GET', 'POST'])
@admin_required
def add_student():
    if request.method == 'POST':
        roll_number = request.form.get('roll_number', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        department = request.form.get('department', '').strip()
        year = request.form.get('year', '').strip()
        section = request.form.get('section', '').strip()
        batch = request.form.get('batch', '').strip()

        # Server-side validation
        if not roll_number or not name or not email or not department or not year or not section:
            flash('All required fields (Roll Number, Name, Email, Dept, Year, Section) must be filled.', 'danger')
            return render_template('students/add.html', active_page='students')

        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('students/add.html', active_page='students')

        try:
            year_int = int(year)
            if year_int < 1 or year_int > 4:
                flash('Year must be between 1 and 4.', 'danger')
                return render_template('students/add.html', active_page='students')
        except ValueError:
            flash('Invalid year format.', 'danger')
            return render_template('students/add.html', active_page='students')

        conn = get_db_connection()
        if not conn:
            flash('Database connection failure.', 'danger')
            return render_template('students/add.html', active_page='students')

        cursor = conn.cursor(dictionary=True)
        try:
            # Check duplicate roll number or email
            cursor.execute("SELECT * FROM students WHERE roll_number = %s OR email = %s", (roll_number, email))
            existing = cursor.fetchone()
            if existing:
                if existing['roll_number'] == roll_number:
                    flash(f'Roll number "{roll_number}" is already registered.', 'danger')
                else:
                    flash(f'Email address "{email}" is already in use by another student.', 'danger')
                return render_template('students/add.html', active_page='students')

            cursor.execute("""
                INSERT INTO students (roll_number, name, email, phone, department, year, section, batch)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (roll_number, name, email, phone, department, year_int, section, batch))
            conn.commit()

            flash(f'Student "{name}" ({roll_number}) added successfully!', 'success')
            return redirect(url_for('list_students'))
        except mysql.connector.Error as err:
            flash(f'Database Error: {err}', 'danger')
            return render_template('students/add.html', active_page='students')
        finally:
            cursor.close()
            conn.close()

    return render_template('students/add.html', active_page='students')

@app.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
@admin_required
def edit_student(student_id):
    conn = get_db_connection()
    if not conn:
        flash('Database error.', 'danger')
        return redirect(url_for('list_students'))

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        if not student:
            flash('Student not found.', 'danger')
            return redirect(url_for('list_students'))

        if request.method == 'POST':
            roll_number = request.form.get('roll_number', '').strip()
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            department = request.form.get('department', '').strip()
            year = request.form.get('year', '').strip()
            section = request.form.get('section', '').strip()
            batch = request.form.get('batch', '').strip()

            if not roll_number or not name or not email or not department or not year or not section:
                flash('Please fill in all mandatory fields.', 'danger')
                return render_template('students/edit.html', student=student, active_page='students')

            # Check uniqueness for updated roll or email
            cursor.execute("SELECT * FROM students WHERE (roll_number = %s OR email = %s) AND student_id != %s", (roll_number, email, student_id))
            duplicate = cursor.fetchone()
            if duplicate:
                flash('Roll number or Email is already used by another student.', 'danger')
                return render_template('students/edit.html', student=student, active_page='students')

            cursor.execute("""
                UPDATE students
                SET roll_number = %s, name = %s, email = %s, phone = %s,
                    department = %s, year = %s, section = %s, batch = %s
                WHERE student_id = %s
            """, (roll_number, name, email, phone, department, int(year), section, batch, student_id))
            conn.commit()

            flash(f'Student "{name}" updated successfully.', 'success')
            return redirect(url_for('list_students'))

        return render_template('students/edit.html', student=student, active_page='students')
    finally:
        cursor.close()
        conn.close()

@app.route('/students/delete/<int:student_id>')
@admin_required
def delete_student(student_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
            conn.commit()
            flash('Student record deleted successfully.', 'success')
        except mysql.connector.Error as err:
            flash(f'Delete failed: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('list_students'))

# ---------------------------------------------------------
# FACULTY MANAGEMENT (CRUD)
# ---------------------------------------------------------
@app.route('/faculty')
@admin_required
def list_faculty():
    conn = get_db_connection()
    if not conn:
        flash('Database error.', 'danger')
        return render_template('faculty/list.html', faculty_list=[], active_page='faculty')

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT u.user_id, u.name, u.email, u.role,
                   GROUP_CONCAT(sub.subject_name) AS assigned_subjects
            FROM users u
            LEFT JOIN subjects sub ON u.user_id = sub.faculty_id
            GROUP BY u.user_id, u.name, u.email, u.role
            ORDER BY u.user_id ASC
        """)
        faculty_list = cursor.fetchall()
        return render_template('faculty/list.html', faculty_list=faculty_list, active_page='faculty')
    finally:
        cursor.close()
        conn.close()

@app.route('/faculty/add', methods=['GET', 'POST'])
@admin_required
def add_faculty():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'faculty').strip()

        if not name or not email or not password:
            flash('Name, Email and Password are required.', 'danger')
            return render_template('faculty/add.html', active_page='faculty')

        if not is_valid_email(email):
            flash('Invalid email format.', 'danger')
            return render_template('faculty/add.html', active_page='faculty')

        conn = get_db_connection()
        if not conn:
            flash('Database error.', 'danger')
            return render_template('faculty/add.html', active_page='faculty')

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash(f'Email address "{email}" is already registered.', 'danger')
                return render_template('faculty/add.html', active_page='faculty')

            pwd_hash = generate_password_hash(password)
            cursor.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                           (name, email, pwd_hash, role))
            conn.commit()

            flash(f'Faculty account for "{name}" created successfully.', 'success')
            return redirect(url_for('list_faculty'))
        finally:
            cursor.close()
            conn.close()

    return render_template('faculty/add.html', active_page='faculty')

@app.route('/faculty/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_faculty(user_id):
    conn = get_db_connection()
    if not conn:
        flash('Database error.', 'danger')
        return redirect(url_for('list_faculty'))

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        faculty = cursor.fetchone()
        if not faculty:
            flash('Faculty user not found.', 'danger')
            return redirect(url_for('list_faculty'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            role = request.form.get('role', 'faculty').strip()

            if not name or not email:
                flash('Name and Email are required.', 'danger')
                return render_template('faculty/edit.html', faculty=faculty, active_page='faculty')

            cursor.execute("SELECT * FROM users WHERE email = %s AND user_id != %s", (email, user_id))
            if cursor.fetchone():
                flash(f'Email "{email}" is already in use.', 'danger')
                return render_template('faculty/edit.html', faculty=faculty, active_page='faculty')

            if password:
                pwd_hash = generate_password_hash(password)
                cursor.execute("UPDATE users SET name = %s, email = %s, password = %s, role = %s WHERE user_id = %s",
                               (name, email, pwd_hash, role, user_id))
            else:
                cursor.execute("UPDATE users SET name = %s, email = %s, role = %s WHERE user_id = %s",
                               (name, email, role, user_id))
            conn.commit()

            flash(f'Faculty member "{name}" updated successfully.', 'success')
            return redirect(url_for('list_faculty'))

        return render_template('faculty/edit.html', faculty=faculty, active_page='faculty')
    finally:
        cursor.close()
        conn.close()

@app.route('/faculty/delete/<int:user_id>')
@admin_required
def delete_faculty(user_id):
    if user_id == session.get('user_id'):
        flash('You cannot delete your own logged-in admin account.', 'danger')
        return redirect(url_for('list_faculty'))

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            conn.commit()
            flash('Faculty account deleted successfully.', 'success')
        except mysql.connector.Error as err:
            flash(f'Delete failed: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('list_faculty'))

# ---------------------------------------------------------
# SUBJECT MANAGEMENT (CRUD)
# ---------------------------------------------------------
@app.route('/subjects')
@login_required
def list_subjects():
    conn = get_db_connection()
    if not conn:
        flash('Database error.', 'danger')
        return render_template('subjects/list.html', subjects=[], active_page='subjects')

    cursor = conn.cursor(dictionary=True)
    try:
        # Show all subjects or filter by logged-in faculty
        if session.get('role') == 'faculty':
            cursor.execute("""
                SELECT sub.*, u.name AS faculty_name
                FROM subjects sub
                LEFT JOIN users u ON sub.faculty_id = u.user_id
                WHERE sub.faculty_id = %s OR sub.faculty_id IS NULL
                ORDER BY sub.subject_code ASC
            """, (session.get('user_id'),))
        else:
            cursor.execute("""
                SELECT sub.*, u.name AS faculty_name
                FROM subjects sub
                LEFT JOIN users u ON sub.faculty_id = u.user_id
                ORDER BY sub.subject_code ASC
            """)
        subjects = cursor.fetchall()
        return render_template('subjects/list.html', subjects=subjects, active_page='subjects')
    finally:
        cursor.close()
        conn.close()

@app.route('/subjects/add', methods=['GET', 'POST'])
@admin_required
def add_subject():
    conn = get_db_connection()
    if not conn:
        flash('Database error.', 'danger')
        return redirect(url_for('list_subjects'))

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id, name, email FROM users WHERE role = 'faculty' ORDER BY name ASC")
        faculty_members = cursor.fetchall()

        if request.method == 'POST':
            code = request.form.get('subject_code', '').strip()
            name = request.form.get('subject_name', '').strip()
            semester = request.form.get('semester', '').strip()
            faculty_id = request.form.get('faculty_id', '').strip()

            if not code or not name or not semester:
                flash('Subject Code, Subject Name, and Semester are mandatory.', 'danger')
                return render_template('subjects/add.html', faculty_members=faculty_members, active_page='subjects')

            # Validate subject code uniqueness
            cursor.execute("SELECT * FROM subjects WHERE subject_code = %s", (code,))
            if cursor.fetchone():
                flash(f'Subject Code "{code}" already exists.', 'danger')
                return render_template('subjects/add.html', faculty_members=faculty_members, active_page='subjects')

            fac_id = int(faculty_id) if faculty_id else None

            cursor.execute("""
                INSERT INTO subjects (subject_code, subject_name, semester, faculty_id)
                VALUES (%s, %s, %s, %s)
            """, (code, name, int(semester), fac_id))
            conn.commit()

            flash(f'Subject "{name}" ({code}) created successfully.', 'success')
            return redirect(url_for('list_subjects'))

        return render_template('subjects/add.html', faculty_members=faculty_members, active_page='subjects')
    finally:
        cursor.close()
        conn.close()

@app.route('/subjects/edit/<int:subject_id>', methods=['GET', 'POST'])
@admin_required
def edit_subject(subject_id):
    conn = get_db_connection()
    if not conn:
        flash('Database error.', 'danger')
        return redirect(url_for('list_subjects'))

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM subjects WHERE subject_id = %s", (subject_id,))
        subject = cursor.fetchone()
        if not subject:
            flash('Subject not found.', 'danger')
            return redirect(url_for('list_subjects'))

        cursor.execute("SELECT user_id, name, email FROM users WHERE role = 'faculty' ORDER BY name ASC")
        faculty_members = cursor.fetchall()

        if request.method == 'POST':
            code = request.form.get('subject_code', '').strip()
            name = request.form.get('subject_name', '').strip()
            semester = request.form.get('semester', '').strip()
            faculty_id = request.form.get('faculty_id', '').strip()

            if not code or not name or not semester:
                flash('Mandatory fields missing.', 'danger')
                return render_template('subjects/edit.html', subject=subject, faculty_members=faculty_members, active_page='subjects')

            cursor.execute("SELECT * FROM subjects WHERE subject_code = %s AND subject_id != %s", (code, subject_id))
            if cursor.fetchone():
                flash(f'Subject Code "{code}" is already in use.', 'danger')
                return render_template('subjects/edit.html', subject=subject, faculty_members=faculty_members, active_page='subjects')

            fac_id = int(faculty_id) if faculty_id else None

            cursor.execute("""
                UPDATE subjects
                SET subject_code = %s, subject_name = %s, semester = %s, faculty_id = %s
                WHERE subject_id = %s
            """, (code, name, int(semester), fac_id, subject_id))
            conn.commit()

            flash(f'Subject "{name}" updated successfully.', 'success')
            return redirect(url_for('list_subjects'))

        return render_template('subjects/edit.html', subject=subject, faculty_members=faculty_members, active_page='subjects')
    finally:
        cursor.close()
        conn.close()

@app.route('/subjects/delete/<int:subject_id>')
@admin_required
def delete_subject(subject_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM subjects WHERE subject_id = %s", (subject_id,))
            conn.commit()
            flash('Subject deleted successfully.', 'success')
        except mysql.connector.Error as err:
            flash(f'Delete failed: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('list_subjects'))

# ---------------------------------------------------------
# ATTENDANCE MARKING & EDITING
# ---------------------------------------------------------
@app.route('/attendance/mark', methods=['GET'])
@login_required
def mark_attendance():
    conn = get_db_connection()
    if not conn:
        flash('Database error.', 'danger')
        return render_template('attendance/mark.html', subjects=[], active_page='mark_attendance')

    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch available subjects
        if session.get('role') == 'faculty':
            cursor.execute("SELECT * FROM subjects WHERE faculty_id = %s OR faculty_id IS NULL ORDER BY subject_name ASC", (session.get('user_id'),))
        else:
            cursor.execute("SELECT * FROM subjects ORDER BY subject_name ASC")
        subjects = cursor.fetchall()

        selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        selected_subject_id = request.args.get('subject_id', type=int)
        selected_dept = request.args.get('department', 'CSM')
        selected_year = request.args.get('year', 2, type=int)
        selected_section = request.args.get('section', 'A')

        students = []
        existing_attendance = {}

        if selected_subject_id:
            cursor.execute("""
                SELECT * FROM students
                WHERE department = %s AND year = %s AND section = %s
                ORDER BY roll_number ASC
            """, (selected_dept, selected_year, selected_section))
            students = cursor.fetchall()

            # Check if attendance is already recorded for this subject, date & students
            cursor.execute("""
                SELECT student_id, status FROM attendance
                WHERE subject_id = %s AND attendance_date = %s
            """, (selected_subject_id, selected_date))
            records = cursor.fetchall()
            for r in records:
                existing_attendance[r['student_id']] = r['status']

        return render_template(
            'attendance/mark.html',
            subjects=subjects,
            students=students,
            existing_attendance=existing_attendance,
            selected_date=selected_date,
            selected_subject_id=selected_subject_id,
            selected_dept=selected_dept,
            selected_year=selected_year,
            selected_section=selected_section,
            active_page='mark_attendance'
        )
    finally:
        cursor.close()
        conn.close()

@app.route('/attendance/save', methods=['POST'])
@login_required
def save_attendance():
    attendance_date = request.form.get('attendance_date')
    subject_id = request.form.get('subject_id', type=int)

    if not attendance_date or not subject_id:
        flash('Missing attendance date or subject selection.', 'danger')
        return redirect(url_for('mark_attendance'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('mark_attendance'))

    cursor = conn.cursor()
    try:
        saved_count = 0
        for key, value in request.form.items():
            if key.startswith('status_'):
                student_id = int(key.split('_')[1])
                status = value  # 'Present' or 'Absent'

                # Use ON DUPLICATE KEY UPDATE to ensure idempotent saving without errors
                cursor.execute("""
                    INSERT INTO attendance (student_id, subject_id, attendance_date, status)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE status = VALUES(status)
                """, (student_id, subject_id, attendance_date, status))
                saved_count += 1

        conn.commit()
        flash(f'Attendance recorded successfully for {saved_count} student(s) on {attendance_date}.', 'success')
    except mysql.connector.Error as err:
        flash(f'Error saving attendance: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('mark_attendance', date=attendance_date, subject_id=subject_id))

@app.route('/attendance/edit', methods=['GET'])
@login_required
def edit_attendance():
    conn = get_db_connection()
    if not conn:
        flash('Database error.', 'danger')
        return render_template('attendance/edit.html', subjects=[], active_page='edit_attendance')

    cursor = conn.cursor(dictionary=True)
    try:
        if session.get('role') == 'faculty':
            cursor.execute("SELECT * FROM subjects WHERE faculty_id = %s OR faculty_id IS NULL ORDER BY subject_name ASC", (session.get('user_id'),))
        else:
            cursor.execute("SELECT * FROM subjects ORDER BY subject_name ASC")
        subjects = cursor.fetchall()

        selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        selected_subject_id = request.args.get('subject_id', type=int)

        attendance_records = []
        if selected_date and selected_subject_id:
            cursor.execute("""
                SELECT a.attendance_id, a.student_id, a.status, s.roll_number, s.name AS student_name,
                       s.department, s.year, s.section
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.subject_id = %s AND a.attendance_date = %s
                ORDER BY s.roll_number ASC
            """, (selected_subject_id, selected_date))
            attendance_records = cursor.fetchall()

        return render_template(
            'attendance/edit.html',
            subjects=subjects,
            attendance_records=attendance_records,
            selected_date=selected_date,
            selected_subject_id=selected_subject_id,
            active_page='edit_attendance'
        )
    finally:
        cursor.close()
        conn.close()

@app.route('/attendance/update', methods=['POST'])
@login_required
def update_attendance():
    attendance_date = request.form.get('attendance_date')
    subject_id = request.form.get('subject_id', type=int)

    if not attendance_date or not subject_id:
        flash('Missing parameters.', 'danger')
        return redirect(url_for('edit_attendance'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('edit_attendance'))

    cursor = conn.cursor()
    try:
        updated_count = 0
        for key, value in request.form.items():
            if key.startswith('status_'):
                student_id = int(key.split('_')[1])
                status = value  # 'Present' or 'Absent'

                cursor.execute("""
                    UPDATE attendance
                    SET status = %s
                    WHERE student_id = %s AND subject_id = %s AND attendance_date = %s
                """, (status, student_id, subject_id, attendance_date))
                updated_count += 1

        conn.commit()
        flash(f'Updated attendance records for {updated_count} student(s).', 'success')
    except mysql.connector.Error as err:
        flash(f'Error updating attendance: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('edit_attendance', date=attendance_date, subject_id=subject_id))

# ---------------------------------------------------------
# ATTENDANCE REPORTS & PERCENTAGE CALCULATION
# Demonstrates SQL Aggregate Functions (COUNT, SUM, GROUP BY, JOIN)
# ---------------------------------------------------------
@app.route('/attendance/report')
@login_required
def attendance_report():
    conn = get_db_connection()
    if not conn:
        flash('Database error.', 'danger')
        return render_template('attendance/report.html', report_data=[], subjects=[], active_page='report')

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM subjects ORDER BY subject_name ASC")
        subjects = cursor.fetchall()

        selected_subject_id = request.args.get('subject_id', type=int)
        selected_dept = request.args.get('department', '').strip()
        selected_year = request.args.get('year', type=int)
        selected_section = request.args.get('section', '').strip()
        from_date = request.args.get('from_date', '').strip()
        to_date = request.args.get('to_date', '').strip()

        # SQL Aggregate Query using COUNT(), SUM(), GROUP BY, and JOIN
        query = """
            SELECT 
                s.student_id,
                s.roll_number,
                s.name AS student_name,
                s.department,
                s.year,
                s.section,
                sub.subject_name,
                COUNT(a.attendance_id) AS total_classes,
                SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_count,
                SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS absent_count
            FROM students s
            JOIN attendance a ON s.student_id = a.student_id
            JOIN subjects sub ON a.subject_id = sub.subject_id
            WHERE 1=1
        """
        params = []

        if selected_subject_id:
            query += " AND a.subject_id = %s"
            params.append(selected_subject_id)

        if selected_dept:
            query += " AND s.department = %s"
            params.append(selected_dept)

        if selected_year:
            query += " AND s.year = %s"
            params.append(selected_year)

        if selected_section:
            query += " AND s.section = %s"
            params.append(selected_section)

        if from_date:
            query += " AND a.attendance_date >= %s"
            params.append(from_date)

        if to_date:
            query += " AND a.attendance_date <= %s"
            params.append(to_date)

        query += """
            GROUP BY s.student_id, s.roll_number, s.name, s.department, s.year, s.section, sub.subject_id, sub.subject_name
            ORDER BY s.roll_number ASC
        """

        cursor.execute(query, tuple(params))
        raw_rows = cursor.fetchall()

        # Calculate exact percentage for each aggregated row
        report_data = []
        for row in raw_rows:
            total = row['total_classes'] or 0
            present = int(row['present_count'] or 0)
            absent = int(row['absent_count'] or 0)
            pct = (present / total * 100.0) if total > 0 else 0.0

            report_data.append({
                'student_id': row['student_id'],
                'roll_number': row['roll_number'],
                'student_name': row['student_name'],
                'department': row['department'],
                'year': row['year'],
                'section': row['section'],
                'subject_name': row['subject_name'],
                'total_classes': total,
                'present_count': present,
                'absent_count': absent,
                'percentage': pct
            })

        return render_template(
            'attendance/report.html',
            report_data=report_data,
            subjects=subjects,
            selected_subject_id=selected_subject_id,
            selected_dept=selected_dept,
            selected_year=selected_year,
            selected_section=selected_section,
            from_date=from_date,
            to_date=to_date,
            active_page='report'
        )
    finally:
        cursor.close()
        conn.close()

# ---------------------------------------------------------
# DATABASE INITIALIZER ROUTE (FOR CLOUD DEPLOYMENT)
# ---------------------------------------------------------
@app.route('/init-mysql')
def init_mysql():
    pwd = request.args.get('pwd', '')
    if not pwd:
        return "Please provide password in query string, e.g. /init-mysql?pwd=YOUR_PASSWORD", 400
    
    app.config['DB_PASSWORD'] = pwd
    conn = get_db_connection()
    if not conn:
        try:
            conn_root = mysql.connector.connect(
                host=app.config['DB_HOST'],
                user=app.config['DB_USER'],
                password=pwd,
                port=app.config['DB_PORT']
            )
            cursor = conn_root.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{app.config['DB_NAME']}`")
            conn_root.commit()
            cursor.close()
            conn_root.close()
            conn = get_db_connection()
        except Exception as e:
            return f"Failed to connect to MySQL on {app.config['DB_HOST']}: {e}", 500

    if not conn:
        return "Could not connect to database.", 500

    cursor = conn.cursor()
    try:
        sql_file = os.path.join(os.path.dirname(__file__), 'database', 'attendance_db.sql')
        if os.path.exists(sql_file):
            with open(sql_file, 'r') as f:
                statements = f.read().split(';')
            for stmt in statements:
                s = stmt.strip()
                if s and not s.lower().startswith('create database') and not s.lower().startswith('use '):
                    try:
                        cursor.execute(s)
                    except Exception:
                        pass
            conn.commit()
        return "Database initialized successfully! <a href='/login'>Go to Login</a>"
    finally:
        cursor.close()
        conn.close()

# ---------------------------------------------------------
# RUN FLASK APPLICATION SERVER
# ---------------------------------------------------------
if __name__ == '__main__':
    print("Starting Student Attendance Management System Flask Server...")
    print("Access application at: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
