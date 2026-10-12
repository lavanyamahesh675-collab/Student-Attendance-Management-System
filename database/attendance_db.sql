-- =========================================================
-- Student Attendance Management System
-- Database Initialization Script for MySQL
-- Database: attendance_db
-- =========================================================

CREATE DATABASE IF NOT EXISTS attendance_db;
USE attendance_db;

-- ---------------------------------------------------------
-- Table 1: users (Stores Admin & Faculty user accounts)
-- ---------------------------------------------------------
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'faculty') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------
-- Table 2: students (Stores Student personal & academic details)
-- ---------------------------------------------------------
CREATE TABLE students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    roll_number VARCHAR(30) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    department VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    section VARCHAR(10) NOT NULL,
    batch VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_dept_sec (department, year, section)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------
-- Table 3: subjects (Stores Academic Subjects mapped to Faculty)
-- ---------------------------------------------------------
CREATE TABLE subjects (
    subject_id INT PRIMARY KEY AUTO_INCREMENT,
    subject_code VARCHAR(30) UNIQUE NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    semester INT NOT NULL,
    faculty_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------
-- Table 4: attendance (Stores Daily Subject Attendance Records)
-- ---------------------------------------------------------
CREATE TABLE attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('Present', 'Absent') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY unique_student_subject_date (student_id, subject_id, attendance_date),
    INDEX idx_attendance_date (attendance_date),
    INDEX idx_student_subject (student_id, subject_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- INSERT SAMPLE INITIAL DATA
-- Default Passwords: 
-- Admin: admin@attendance.com / admin123
-- Faculty: faculty@attendance.com / faculty123
-- =========================================================

-- 1. Insert Users (Admin & Faculty)
-- Note: Werkzeug pbkdf2:sha256 hash for 'admin123' and 'faculty123'
INSERT INTO users (user_id, name, email, password, role) VALUES
(1, 'System Administrator', 'admin@attendance.com', 'pbkdf2:sha256:1000000$FGZyL3oaDnU6sQso$21999b6e47d9833e11f0b74d047ad8c43a597783a28724c4c148d41669fd001c', 'admin'),
(2, 'Dr. Ramesh Verma', 'faculty@attendance.com', 'pbkdf2:sha256:1000000$0b9e9UcZvaVqAelD$6bf373df097ba82be016ab33a1b47ed718df084398a3290e1ee7b6e7054f1702', 'faculty'),
(3, 'Prof. Sunita Sharma', 'prof.sharma@attendance.com', 'pbkdf2:sha256:1000000$0b9e9UcZvaVqAelD$6bf373df097ba82be016ab33a1b47ed718df084398a3290e1ee7b6e7054f1702', 'faculty');

-- 2. Insert Students (At least 10 sample students)
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
(10, '110', 'Ananya Roy', 'ananya.roy@college.edu', '9876543219', 'CSM', 2, 'B', '2023-2027');

-- 3. Insert Subjects
INSERT INTO subjects (subject_id, subject_code, subject_name, semester, faculty_id) VALUES
(1, 'CS301', 'Database Management Systems', 4, 2),
(2, 'CS302', 'Java Programming', 4, 3),
(3, 'CS303', 'Operating Systems', 4, 2),
(4, 'CS304', 'Computer Networks', 4, 3);

-- 4. Insert Sample Attendance Records across multiple dates
-- DBMS (Subject ID 1) for CSM 2nd Year Sec A students (Ravi, Anu, Rahul)
INSERT INTO attendance (student_id, subject_id, attendance_date, status) VALUES
-- Date 1: 2026-09-20
(1, 1, '2026-09-20', 'Present'),
(2, 1, '2026-09-20', 'Present'),
(3, 1, '2026-09-20', 'Absent'),

-- Date 2: 2026-09-21
(1, 1, '2026-09-21', 'Present'),
(2, 1, '2026-09-21', 'Absent'),
(3, 1, '2026-09-21', 'Absent'),

-- Date 3: 2026-09-22
(1, 1, '2026-09-22', 'Present'),
(2, 1, '2026-09-22', 'Present'),
(3, 1, '2026-09-22', 'Present'),

-- Date 4: 2026-09-23
(1, 1, '2026-09-23', 'Present'),
(2, 1, '2026-09-23', 'Present'),
(3, 1, '2026-09-23', 'Absent'),

-- Date 5: 2026-09-24
(1, 1, '2026-09-24', 'Present'),
(2, 1, '2026-09-24', 'Absent'),
(3, 1, '2026-09-24', 'Absent'),

-- Java (Subject ID 2) for CSE 2nd Year Sec A students (Priya, Amit)
(4, 2, '2026-09-20', 'Present'),
(5, 2, '2026-09-20', 'Present'),
(4, 2, '2026-09-21', 'Present'),
(5, 2, '2026-09-21', 'Absent'),
(4, 2, '2026-09-22', 'Present'),
(5, 2, '2026-09-22', 'Present');
