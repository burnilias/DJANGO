# LMS (Learning Management System) - Setup Guide

## Overview

Full-featured LMS with role-based authentication:
- **Admin**: Manages all users and courses
- **Teacher**: Creates/edits/deletes their own courses with lessons
- **Student**: Browses/joins courses, tracks progress, earns certificates
- **Student of the Month**: Automatically awarded to student with most completed courses each month

## Database Setup

1. Run the main database setup first:
```sql
-- In phpMyAdmin, run setup_database.sql
```

2. Then run the LMS tables setup:
```sql
-- In phpMyAdmin, run setup_lms_tables.sql
```

## User Credentials (from setup_database.sql)

| Email | Password | Role |
|-------|----------|------|
| admin@emsi.edu | EmsiAdmin!2026 | Admin |
| teacher@emsi.edu | EmsiTeach!2026 | Teacher |
| student@emsi.edu | EmsiLearn!2026 | Student |

## Features by Role

### Admin
- View/manage all courses
- View all enrollments
- View all certificates issued
- Calculate/reset Student of the Month
- Access at: `/dashboard/admin/courses/`

### Teacher
- Dashboard with course stats
- Create/edit/delete their own courses
- Add/edit/delete lessons within courses
- View enrollments for their courses
- Access at: `/dashboard/teacher/`

### Student
- Browse all published courses
- Enroll in courses
- View enrolled courses with progress tracking
- Mark lessons as complete
- Earn certificate at 100% completion
- View certificates in "My Certificates" section
- View Student of the Month on dashboard
- Access at: `/dashboard/student/`

## Student of the Month

- Automatically calculated based on completed courses per month
- Admin can manually trigger calculation at: `/dashboard/admin/student-of-month/`
- Displayed prominently on student dashboard

## Certificate System

- Generated automatically when student completes 100% of a course
- Viewable in "My Certificates" section
- Printable format
- Unique certificate number

## URL Routes

### Admin LMS Routes
- `/dashboard/admin/courses/` - All courses management
- `/dashboard/admin/enrollments/` - All enrollments
- `/dashboard/admin/certificates/` - All certificates
- `/dashboard/admin/student-of-month/` - Student of the Month

### Teacher Routes
- `/dashboard/teacher/` - Teacher dashboard
- `/dashboard/teacher/courses/` - My courses
- `/dashboard/teacher/courses/create/` - Create course
- `/dashboard/teacher/courses/<id>/lessons/` - Manage lessons

### Student Routes
- `/dashboard/student/courses/` - Browse courses
- `/dashboard/student/my-courses/` - My enrolled courses
- `/dashboard/student/certificates/` - My certificates

## Running the Application

```bash
python manage.py runserver 8000
```

Then access:
- Login: http://127.0.0.1:8000/
- Student Dashboard: http://127.0.0.1:8000/dashboard/student/
- Teacher Dashboard: http://127.0.0.1:8000/dashboard/teacher/
- Admin Dashboard: http://127.0.0.1:8000/dashboard/admin/

## File Structure

```
templates/
├── admin/
│   └── courses/
│       ├── list.html
│       ├── edit.html
│       └── student_of_month.html
├── teacher/
│   ├── base_teacher.html
│   ├── dashboard.html
│   ├── profile.html
│   └── courses/
│       ├── list.html
│       ├── create.html
│       ├── edit.html
│       ├── lessons.html
│       └── enrollments.html
│   └── lessons/
│       ├── create.html
│       └── edit.html
└── student/
    └── courses/
        ├── browse.html
        ├── my_courses.html
        └── learn.html
    └── certificates/
        ├── list.html
        └── view.html
```

## API Endpoints

- `POST /api/auth/api/courses/<id>/enroll/` - Enroll in course
- `POST /api/auth/api/lessons/<id>/complete/` - Mark lesson complete
- `GET /api/auth/api/courses/<id>/progress/` - Get progress
- `GET /api/auth/api/student-of-month/` - Get current SOM
