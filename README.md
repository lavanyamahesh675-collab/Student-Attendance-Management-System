# Student Attendance Management System

A full-stack, real-world web application built specifically for college DBMS laboratory projects and BTech viva presentations. Built using **HTML5, CSS3, Vanilla JavaScript**, **Python Flask**, and **MySQL**.

---

## 📌 1. Project Objective

The **Student Attendance Management System (SAMS)** allows college administrators and faculty members to efficiently track, manage, and calculate student attendance. 

Key Capabilities:
- Role-based Access Control (Admin and Faculty roles)
- Complete Student, Faculty, and Subject CRUD operations
- Subject-wise and section-wise daily attendance marking
- Attendance modification & editing
- Automated Attendance Percentage Calculation via SQL aggregate queries
- Low Attendance (< 75%) automated warning indicators
- Real-time client-side search and multi-criteria database filtering

---

## 🛠️ 2. Technology Stack

- **Frontend:** HTML5, CSS3, Vanilla JavaScript (No heavy frameworks used).
- **Backend:** Python 3.13, Flask 3.1.
- **Database:** MySQL 8.0 / MySQL Server (`mysql-connector-python`).
- **Security:** Werkzeug password hashing & Flask session management.

---

## 🗄️ 3. Database Architecture & Schema

**Database Name:** `attendance_db`

### Entity-Relationship Diagram (ERD) Overview & Relationships
```
        +-------------------+
        |       users       |  (Admin / Faculty)
        +-------------------+
        | PK | user_id      |
        +-------------------+
                  | 1
                  |
                  | N (assigned faculty)
                  v
        +-------------------+
        |     subjects      |
        +-------------------+
        | PK | subject_id   |
        | FK | faculty_id   |
        +-------------------+
                  | 1
                  |
                  | N
                  v
+---------------+  +--------------------+
|   students    |  |     attendance     |
+---------------+  +--------------------+
| PK|student_id |--+ N  | PK | attendance_id|
+---------------+ 1|    | FK | student_id   |
                   |    | FK | subject_id   |
                   +--->|    | attendance_date|
                        |    | status (P/A) |
                        +--------------------+
```

### Table Definitions:

1. **`users` Table:**
   - `user_id` (INT, PK, AUTO_INCREMENT)
   - `name` (VARCHAR(100), NOT NULL)
   - `email` (VARCHAR(100), UNIQUE, NOT NULL)
   - `password` (VARCHAR(255), NOT NULL) - Stores Werkzeug scrypt/pbkdf2 password hash
   - `role` (ENUM('admin', 'faculty'), NOT NULL)

2. **`students` Table:**
   - `student_id` (INT, PK, AUTO_INCREMENT)
   - `roll_number` (VARCHAR(30), UNIQUE, NOT NULL)
   - `name` (VARCHAR(100), NOT NULL)
   - `email` (VARCHAR(100), UNIQUE, NOT NULL)
   - `phone` (VARCHAR(15))
   - `department` (VARCHAR(50), NOT NULL)
   - `year` (INT, NOT NULL)
   - `section` (VARCHAR(10), NOT NULL)
   - `batch` (VARCHAR(30))

3. **`subjects` Table:**
   - `subject_id` (INT, PK, AUTO_INCREMENT)
   - `subject_code` (VARCHAR(30), UNIQUE, NOT NULL)
   - `subject_name` (VARCHAR(100), NOT NULL)
   - `semester` (INT, NOT NULL)
   - `faculty_id` (INT, FK -> `users.user_id`)

4. **`attendance` Table:**
   - `attendance_id` (INT, PK, AUTO_INCREMENT)
   - `student_id` (INT, FK -> `students.student_id`)
   - `subject_id` (INT, FK -> `subjects.subject_id`)
   - `attendance_date` (DATE, NOT NULL)
   - `status` (ENUM('Present', 'Absent'), NOT NULL)
   - **Constraint:** `UNIQUE KEY (student_id, subject_id, attendance_date)` ensures no duplicate attendance entry per student/subject per day.

---

## 🔑 4. Default Credentials (Demo Accounts)

| Role | Email | Password |
|---|---|---|
| **ADMIN** | `admin@attendance.com` | `admin123` |
| **FACULTY** | `faculty@attendance.com` | `faculty123` |

---

## 📁 5. Folder Structure

```
student_attendance_system/
│
├── app.py                      # Main Flask application & routes
├── config.py                   # MySQL connection configuration
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation & viva guide
│
├── database/
│   └── attendance_db.sql       # DDL & DML initialization script
│
├── templates/
│   ├── base.html               # Main sidebar layout & top bar
│   ├── login.html              # Login portal page
│   ├── dashboard.html          # Stats cards & quick actions
│   │
│   ├── students/
│   │   ├── list.html           # Students directory & search
│   │   ├── add.html            # Add student form
│   │   └── edit.html           # Edit student details
│   │
│   ├── faculty/
│   │   ├── list.html           # Faculty list & assignments
│   │   ├── add.html            # Add faculty user
│   │   └── edit.html           # Edit faculty details
│   │
│   ├── subjects/
│   │   ├── list.html           # Subjects curriculum list
│   │   ├── add.html            # Add subject form
│   │   └── edit.html           # Edit subject details
│   │
│   └── attendance/
│       ├── mark.html           # Mark daily student attendance
│       ├── edit.html           # Modify recorded attendance
│       └── report.html         # Percentage & low attendance report
│
└── static/
    ├── css/
    │   └── style.css           # Custom CSS with blurred background
    ├── js/
    │   └── validation.js       # Form validation & quick actions
    └── images/
        └── bg.png              # Blurred college campus background
```

---

## 🚀 6. How to Setup and Run

### Step 1: Install Dependencies
Open terminal/cmd in the project root:
```bash
pip install -r requirements.txt
```

### Step 2: Setup MySQL Database
Make sure your MySQL Server (XAMPP / MySQL Workbench / Command Line) is running.
Run the database import script in Python or MySQL CLI:

**Option A (Using Python auto-initializer):**
```bash
python -c "import mysql.connector, config; conn = mysql.connector.connect(host=config.Config.DB_HOST, user=config.Config.DB_USER, password=config.Config.DB_PASSWORD); cursor = conn.cursor(); [cursor.execute(stmt.strip()) for stmt in open('database/attendance_db.sql').read().split(';') if stmt.strip()]; conn.commit(); print('MySQL Database ready!')"
```

**Option B (Using MySQL Command Line):**
```bash
mysql -u root -p < database/attendance_db.sql
```

### Step 3: Configure Database Password
If your MySQL password is not `root`, edit `config.py`:
```python
DB_PASSWORD = "YOUR_MYSQL_PASSWORD"
```

### Step 4: Run Flask Web Server
```bash
python app.py
```
Open your browser and visit: **`http://127.0.0.1:5000`**

---

## 🧠 7. DBMS Concepts Demonstrated

1. **Relational Database Schema:** Clean 3rd Normal Form (3NF) relational tables.
2. **Primary & Foreign Keys:** Referential integrity with `ON DELETE CASCADE` and `ON DELETE SET NULL`.
3. **Candidate / Unique Keys:** `roll_number`, `subject_code`, `email`, and composite unique key `(student_id, subject_id, attendance_date)`.
4. **SQL Aggregate Functions:**
   - `COUNT(a.attendance_id)` for total classes
   - `SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END)` for present classes
5. **Complex Joins:** `INNER JOIN` and `LEFT JOIN` connecting `students`, `attendance`, `subjects`, and `users`.
6. **SQL Grouping & Filtering:** `GROUP BY` and `HAVING` / `WHERE` for department & semester aggregate reporting.
7. **Parameterized Queries:** Prevents SQL Injection by passing tuple parameters `cursor.execute(sql, (param1, param2))`.

---

## 🎓 8. BTech DBMS Lab Viva Questions & Answers

**Q1: What is Referential Integrity and how is it implemented in this project?**
> *Answer:* Referential Integrity ensures that relationships between tables remain consistent. In this project, foreign keys like `student_id` in the `attendance` table reference `student_id` in the `students` table with `ON DELETE CASCADE`. If a student is removed, their associated attendance records are automatically deleted to prevent orphan records.

**Q2: How is duplicate attendance entry prevented?**
> *Answer:* We enforced a composite `UNIQUE` constraint in MySQL: `UNIQUE KEY (student_id, subject_id, attendance_date)`. In addition, Flask handles backend updates using `ON DUPLICATE KEY UPDATE status = VALUES(status)`.

**Q3: How is the Attendance Percentage calculated?**
> *Answer:* It is computed dynamically from the database using SQL aggregate functions:
> $$\text{Attendance Percentage} = \frac{\text{Total Present Classes}}{\text{Total Classes Conducted}} \times 100$$
> Using `SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END)` divided by `COUNT(attendance_id)`.

**Q4: How does this project prevent SQL Injection attacks?**
> *Answer:* All database interactions strictly use parameterized queries (`cursor.execute(query, (val1, val2))`) instead of string interpolation, ensuring user inputs are safely escaped by the MySQL connector.

---
