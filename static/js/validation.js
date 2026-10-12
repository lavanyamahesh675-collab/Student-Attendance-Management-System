/**
 * Student Attendance Management System - Validation & UI JavaScript
 * Pure Vanilla JavaScript (No frameworks)
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-dismiss Flash Alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Helper: Display validation error message below input
    function showError(input, message) {
        const group = input.closest('.form-group');
        let errorSpan = group.querySelector('.error-text');
        if (!errorSpan) {
            errorSpan = document.createElement('span');
            errorSpan.className = 'error-text';
            group.appendChild(errorSpan);
        }
        errorSpan.textContent = message;
        input.style.borderColor = '#dc2626';
    }

    // Helper: Clear validation error
    function clearError(input) {
        const group = input.closest('.form-group');
        if (group) {
            const errorSpan = group.querySelector('.error-text');
            if (errorSpan) {
                errorSpan.textContent = '';
            }
            input.style.borderColor = '';
        }
    }

    // Helper: Email Regex check
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    // 1. LOGIN FORM VALIDATION
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            let isValid = true;
            const email = document.getElementById('email');
            const password = document.getElementById('password');

            clearError(email);
            clearError(password);

            if (!email.value.trim()) {
                showError(email, 'Email address is required');
                isValid = false;
            } else if (!isValidEmail(email.value.trim())) {
                showError(email, 'Please enter a valid email address');
                isValid = false;
            }

            if (!password.value.trim()) {
                showError(password, 'Password is required');
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // 2. STUDENT FORM VALIDATION (Add / Edit)
    const studentForm = document.getElementById('studentForm');
    if (studentForm) {
        studentForm.addEventListener('submit', function(e) {
            let isValid = true;

            const rollNumber = document.getElementById('roll_number');
            const name = document.getElementById('name');
            const email = document.getElementById('email');
            const phone = document.getElementById('phone');
            const department = document.getElementById('department');
            const year = document.getElementById('year');
            const section = document.getElementById('section');

            [rollNumber, name, email, phone, department, year, section].forEach(clearError);

            if (!rollNumber.value.trim()) {
                showError(rollNumber, 'Roll number is required');
                isValid = false;
            }

            if (!name.value.trim()) {
                showError(name, 'Student name is required');
                isValid = false;
            }

            if (!email.value.trim()) {
                showError(email, 'Email address is required');
                isValid = false;
            } else if (!isValidEmail(email.value.trim())) {
                showError(email, 'Enter a valid email address');
                isValid = false;
            }

            if (phone.value.trim() && !/^\d{10,15}$/.test(phone.value.trim())) {
                showError(phone, 'Phone number must contain 10-15 digits');
                isValid = false;
            }

            if (!department.value.trim()) {
                showError(department, 'Department is required');
                isValid = false;
            }

            if (!year.value || year.value < 1 || year.value > 4) {
                showError(year, 'Year must be between 1 and 4');
                isValid = false;
            }

            if (!section.value.trim()) {
                showError(section, 'Section is required');
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // 3. FACULTY FORM VALIDATION
    const facultyForm = document.getElementById('facultyForm');
    if (facultyForm) {
        facultyForm.addEventListener('submit', function(e) {
            let isValid = true;
            const name = document.getElementById('name');
            const email = document.getElementById('email');
            const password = document.getElementById('password');

            [name, email, password].forEach(el => el && clearError(el));

            if (!name.value.trim()) {
                showError(name, 'Faculty name is required');
                isValid = false;
            }

            if (!email.value.trim()) {
                showError(email, 'Email is required');
                isValid = false;
            } else if (!isValidEmail(email.value.trim())) {
                showError(email, 'Enter a valid email');
                isValid = false;
            }

            // Password required only for new faculty addition
            if (password && password.hasAttribute('required') && !password.value.trim()) {
                showError(password, 'Password is required');
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // 4. SUBJECT FORM VALIDATION
    const subjectForm = document.getElementById('subjectForm');
    if (subjectForm) {
        subjectForm.addEventListener('submit', function(e) {
            let isValid = true;
            const code = document.getElementById('subject_code');
            const name = document.getElementById('subject_name');
            const sem = document.getElementById('semester');

            [code, name, sem].forEach(clearError);

            if (!code.value.trim()) {
                showError(code, 'Subject code is required');
                isValid = false;
            }

            if (!name.value.trim()) {
                showError(name, 'Subject name is required');
                isValid = false;
            }

            if (!sem.value || sem.value < 1 || sem.value > 8) {
                showError(sem, 'Semester must be between 1 and 8');
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // 5. ATTENDANCE MARKING PAGE HANDLERS
    const markAllPresentBtn = document.getElementById('markAllPresentBtn');
    const markAllAbsentBtn = document.getElementById('markAllAbsentBtn');
    
    if (markAllPresentBtn) {
        markAllPresentBtn.addEventListener('click', function() {
            const presentRadios = document.querySelectorAll('input[type="radio"][value="Present"]');
            presentRadios.forEach(radio => radio.checked = true);
        });
    }

    if (markAllAbsentBtn) {
        markAllAbsentBtn.addEventListener('click', function() {
            const absentRadios = document.querySelectorAll('input[type="radio"][value="Absent"]');
            absentRadios.forEach(radio => radio.checked = true);
        });
    }

    const attendanceMarkForm = document.getElementById('attendanceMarkForm');
    if (attendanceMarkForm) {
        attendanceMarkForm.addEventListener('submit', function(e) {
            const studentRows = document.querySelectorAll('.student-attendance-row');
            let allMarked = true;

            studentRows.forEach(row => {
                const checked = row.querySelector('input[type="radio"]:checked');
                if (!checked) {
                    allMarked = false;
                    row.style.backgroundColor = '#fee2e2';
                } else {
                    row.style.backgroundColor = '';
                }
            });

            if (!allMarked) {
                e.preventDefault();
                alert('Please select attendance status (Present or Absent) for all listed students before submitting.');
            }
        });
    }

    // 6. CLIENT-SIDE SEARCH & FILTER FOR TABLES
    const searchInput = document.getElementById('tableSearchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const term = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('.custom-table tbody tr');

            tableRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(term)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});

// Confirmation dialog for delete actions
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this record? This action cannot be undone.');
}
