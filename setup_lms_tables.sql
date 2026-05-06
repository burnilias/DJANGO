-- ============================================================
-- LMS (Learning Management System) Tables Setup
-- Run this in phpMyAdmin after the main setup_database.sql
-- ============================================================

USE auth_db;

-- 1. Courses Table ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS `courses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `description` longtext NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `teacher_id` int(11) NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'draft',
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`id`),
  KEY `courses_teacher_id_fk` (`teacher_id`),
  CONSTRAINT `courses_teacher_id_fk` FOREIGN KEY (`teacher_id`) REFERENCES `accounts_customuser` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Lessons Table ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS `lessons` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `course_id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `content` longtext NOT NULL,
  `video_url` varchar(200) NOT NULL DEFAULT '',
  `order` int(10) unsigned NOT NULL DEFAULT 0,
  `duration_minutes` int(10) unsigned NOT NULL DEFAULT 0,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`id`),
  KEY `lessons_course_id_fk` (`course_id`),
  CONSTRAINT `lessons_course_id_fk` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Enrollments Table -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `enrollments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'active',
  `enrolled_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `completed_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `enrollments_student_course_unique` (`student_id`, `course_id`),
  KEY `enrollments_student_id_fk` (`student_id`),
  KEY `enrollments_course_id_fk` (`course_id`),
  CONSTRAINT `enrollments_student_id_fk` FOREIGN KEY (`student_id`) REFERENCES `accounts_customuser` (`id`) ON DELETE CASCADE,
  CONSTRAINT `enrollments_course_id_fk` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Progress Table --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `progress` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `enrollment_id` int(11) NOT NULL,
  `lesson_id` int(11) NOT NULL,
  `is_completed` tinyint(1) NOT NULL DEFAULT 0,
  `completed_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `progress_enrollment_lesson_unique` (`enrollment_id`, `lesson_id`),
  KEY `progress_enrollment_id_fk` (`enrollment_id`),
  KEY `progress_lesson_id_fk` (`lesson_id`),
  CONSTRAINT `progress_enrollment_id_fk` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`id`) ON DELETE CASCADE,
  CONSTRAINT `progress_lesson_id_fk` FOREIGN KEY (`lesson_id`) REFERENCES `lessons` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Certificates Table ----------------------------------------------------
CREATE TABLE IF NOT EXISTS `certificates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `enrollment_id` int(11) NOT NULL,
  `certificate_number` varchar(50) NOT NULL,
  `issued_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `pdf_file` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `certificates_enrollment_unique` (`enrollment_id`),
  UNIQUE KEY `certificates_number_unique` (`certificate_number`),
  KEY `certificates_enrollment_id_fk` (`enrollment_id`),
  CONSTRAINT `certificates_enrollment_id_fk` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Student of the Month Table ---------------------------------------------
CREATE TABLE IF NOT EXISTS `student_of_month` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) NOT NULL,
  `month` date NOT NULL,
  `courses_completed_count` int(10) unsigned NOT NULL DEFAULT 0,
  `awarded_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_of_month_month_unique` (`month`),
  KEY `student_of_month_student_id_fk` (`student_id`),
  CONSTRAINT `student_of_month_student_id_fk` FOREIGN KEY (`student_id`) REFERENCES `accounts_customuser` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Update Django Content Types and Permissions ---------------------------
INSERT IGNORE INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
  (9, 'accounts', 'course'),
  (10, 'accounts', 'lesson'),
  (11, 'accounts', 'enrollment'),
  (12, 'accounts', 'progress'),
  (13, 'accounts', 'certificate'),
  (14, 'accounts', 'studentofmonth');

-- 8. Add Permissions for LMS Models ----------------------------------------
INSERT IGNORE INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
  (33, 'Can add course', 9, 'add_course'),
  (34, 'Can change course', 9, 'change_course'),
  (35, 'Can delete course', 9, 'delete_course'),
  (36, 'Can view course', 9, 'view_course'),
  (37, 'Can add lesson', 10, 'add_lesson'),
  (38, 'Can change lesson', 10, 'change_lesson'),
  (39, 'Can delete lesson', 10, 'delete_lesson'),
  (40, 'Can view lesson', 10, 'view_lesson'),
  (41, 'Can add enrollment', 11, 'add_enrollment'),
  (42, 'Can change enrollment', 11, 'change_enrollment'),
  (43, 'Can delete enrollment', 11, 'delete_enrollment'),
  (44, 'Can view enrollment', 11, 'view_enrollment'),
  (45, 'Can add progress', 12, 'add_progress'),
  (46, 'Can change progress', 12, 'change_progress'),
  (47, 'Can delete progress', 12, 'delete_progress'),
  (48, 'Can view progress', 12, 'view_progress'),
  (49, 'Can add certificate', 13, 'add_certificate'),
  (50, 'Can change certificate', 13, 'change_certificate'),
  (51, 'Can delete certificate', 13, 'delete_certificate'),
  (52, 'Can view certificate', 13, 'view_certificate'),
  (53, 'Can add student of month', 14, 'add_studentofmonth'),
  (54, 'Can change student of month', 14, 'change_studentofmonth'),
  (55, 'Can delete student of month', 14, 'delete_studentofmonth'),
  (56, 'Can view student of month', 14, 'view_studentofmonth');

-- 9. Migration Records ------------------------------------------------------
INSERT IGNORE INTO `django_migrations` (`app`, `name`, `applied`) VALUES
  ('accounts', '0002_lms_models', NOW());

-- ============================================================
-- DONE! LMS Tables Created Successfully
-- ============================================================
