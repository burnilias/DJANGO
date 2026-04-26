-- ============================================================
-- EMSI Student++ — Full Database Setup Script
-- Run this in phpMyAdmin (XAMPP) or mysql CLI
-- After running: start Django with  python manage.py runserver 8000
-- Then open  http://127.0.0.1:8000/  and log in
-- ============================================================

-- 1. Drop the old database entirely (avoids FK constraint errors)
DROP DATABASE IF EXISTS auth_db;

-- 2. Create a fresh database
CREATE DATABASE auth_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE auth_db;

-- 3. Django internal tables -----------------------------------------------

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co`
    FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm`
    FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id`
    FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. CustomUser table (the main user table) --------------------------------

CREATE TABLE `accounts_customuser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `role` varchar(20) NOT NULL,
  `status` varchar(20) NOT NULL,
  `phone` varchar(30) NOT NULL,
  `bio` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `accounts_customuser_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `customuser_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_customuser_groups_customuser_id_group_id_c074bdcb_uniq` (`customuser_id`,`group_id`),
  KEY `accounts_customuser_groups_group_id_86ba5f9e_fk_auth_group_id` (`group_id`),
  CONSTRAINT `accounts_customuser__customuser_id_bc55088e_fk_accounts_`
    FOREIGN KEY (`customuser_id`) REFERENCES `accounts_customuser` (`id`),
  CONSTRAINT `accounts_customuser_groups_group_id_86ba5f9e_fk_auth_group_id`
    FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `accounts_customuser_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `customuser_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_customuser_user_customuser_id_permission_9632a709_uniq` (`customuser_id`,`permission_id`),
  KEY `accounts_customuser__permission_id_aea3d0e5_fk_auth_perm` (`permission_id`),
  CONSTRAINT `accounts_customuser__customuser_id_0deaefae_fk_accounts_`
    FOREIGN KEY (`customuser_id`) REFERENCES `accounts_customuser` (`id`),
  CONSTRAINT `accounts_customuser__permission_id_aea3d0e5_fk_auth_perm`
    FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Django admin log -----------------------------------------------------

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_accounts_customuser_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co`
    FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_accounts_customuser_id`
    FOREIGN KEY (`user_id`) REFERENCES `accounts_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. DRF Token table ------------------------------------------------------

CREATE TABLE `authtoken_token` (
  `key` varchar(40) NOT NULL,
  `created` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`key`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `authtoken_token_user_id_35299eff_fk_accounts_customuser_id`
    FOREIGN KEY (`user_id`) REFERENCES `accounts_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Django session table -------------------------------------------------

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Django migration history (so Django knows the DB is up-to-date) -------

CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 9. SEED DATA — content types & permissions (Django internals)
-- ============================================================

INSERT INTO `django_content_type` (`id`,`app_label`,`model`) VALUES
  (1,'admin','logentry'),
  (2,'auth','permission'),
  (3,'auth','group'),
  (4,'contenttypes','contenttype'),
  (5,'sessions','session'),
  (6,'authtoken','token'),
  (7,'authtoken','tokenproxy'),
  (8,'accounts','customuser');

INSERT INTO `auth_permission` (`id`,`name`,`content_type_id`,`codename`) VALUES
  ( 1,'Can add log entry',1,'add_logentry'),
  ( 2,'Can change log entry',1,'change_logentry'),
  ( 3,'Can delete log entry',1,'delete_logentry'),
  ( 4,'Can view log entry',1,'view_logentry'),
  ( 5,'Can add permission',2,'add_permission'),
  ( 6,'Can change permission',2,'change_permission'),
  ( 7,'Can delete permission',2,'delete_permission'),
  ( 8,'Can view permission',2,'view_permission'),
  ( 9,'Can add group',3,'add_group'),
  (10,'Can change group',3,'change_group'),
  (11,'Can delete group',3,'delete_group'),
  (12,'Can view group',3,'view_group'),
  (13,'Can add content type',4,'add_contenttype'),
  (14,'Can change content type',4,'change_contenttype'),
  (15,'Can delete content type',4,'delete_contenttype'),
  (16,'Can view content type',4,'view_contenttype'),
  (17,'Can add session',5,'add_session'),
  (18,'Can change session',5,'change_session'),
  (19,'Can delete session',5,'delete_session'),
  (20,'Can view session',5,'view_session'),
  (21,'Can add Token',6,'add_token'),
  (22,'Can change Token',6,'change_token'),
  (23,'Can delete Token',6,'delete_token'),
  (24,'Can view Token',6,'view_token'),
  (25,'Can add Token',7,'add_tokenproxy'),
  (26,'Can change Token',7,'change_tokenproxy'),
  (27,'Can delete Token',7,'delete_tokenproxy'),
  (28,'Can view Token',7,'view_tokenproxy'),
  (29,'Can add custom user',8,'add_customuser'),
  (30,'Can change custom user',8,'change_customuser'),
  (31,'Can delete custom user',8,'delete_customuser'),
  (32,'Can view custom user',8,'view_customuser');

-- ============================================================
-- 10. SEED DATA — Demo users (passwords hashed with Django PBKDF2)
--     These passwords match what the login page expects:
--       admin@emsi.edu   / EmsiAdmin!2026
--       teacher@emsi.edu / EmsiTeach!2026
--       student@emsi.edu / EmsiLearn!2026
-- ============================================================

INSERT INTO `accounts_customuser`
  (`id`,`password`,`last_login`,`is_superuser`,`first_name`,`last_name`,
   `email`,`role`,`status`,`phone`,`bio`,`created_at`,`is_staff`,`is_active`)
VALUES
  (1,
   'pbkdf2_sha256$600000$J0Ur5oNDgewvu0VOkzJBOE$wv2gJFETNhIKQeZ72Q7myA9QmHNY3yM7Fg59GLG28nc=',
   NULL, 1, 'Admin', 'User',
   'admin@emsi.edu', 'admin', 'active', '', '',
   NOW(), 1, 1),

  (2,
   'pbkdf2_sha256$600000$LfOfFJma1XxauAwGAgNYDm$m8cIzd8hT5odKelzJhMtfl7RS4SyMaGdLOIRRHO9fHQ=',
   NULL, 0, 'Teacher', 'User',
   'teacher@emsi.edu', 'teacher', 'active', '', '',
   NOW(), 0, 1),

  (3,
   'pbkdf2_sha256$600000$NEwoBw8Hr5LeQrXHW7kR8Q$8PRyXT9a297RCh98oXLgTXnpL/fpeupNt3Q30elAht8=',
   NULL, 0, 'Student', 'User',
   'student@emsi.edu', 'student', 'active', '', '',
   NOW(), 0, 1);

-- ============================================================
-- 11. Migration records (so Django doesn't re-run migrations)
-- ============================================================

INSERT INTO `django_migrations` (`app`,`name`,`applied`) VALUES
  ('contenttypes','0001_initial',NOW()),
  ('contenttypes','0002_remove_content_type_name',NOW()),
  ('auth','0001_initial',NOW()),
  ('auth','0002_alter_permission_name_max_length',NOW()),
  ('auth','0003_alter_user_email_max_length',NOW()),
  ('auth','0004_alter_user_username_opts',NOW()),
  ('auth','0005_alter_user_last_login_null',NOW()),
  ('auth','0006_require_contenttypes_0002',NOW()),
  ('auth','0007_alter_validators_add_error_messages',NOW()),
  ('auth','0008_alter_user_username_max_length',NOW()),
  ('auth','0009_alter_user_last_name_max_length',NOW()),
  ('auth','0010_alter_group_name_max_length',NOW()),
  ('auth','0011_update_proxy_permissions',NOW()),
  ('auth','0012_alter_user_first_name_max_length',NOW()),
  ('accounts','0001_initial',NOW()),
  ('admin','0001_initial',NOW()),
  ('admin','0002_logentry_remove_auto_add',NOW()),
  ('admin','0003_logentry_add_action_flag_choices',NOW()),
  ('authtoken','0001_initial',NOW()),
  ('authtoken','0002_auto_20160226_1747',NOW()),
  ('authtoken','0003_tokenproxy',NOW()),
  ('authtoken','0004_alter_tokenproxy_options',NOW()),
  ('sessions','0001_initial',NOW());

-- ============================================================
-- DONE! Now run:
--   python manage.py runserver 8000
-- Open http://127.0.0.1:8000/ and log in with:
--   admin@emsi.edu   / EmsiAdmin!2026
--   teacher@emsi.edu / EmsiTeach!2026
--   student@emsi.edu / EmsiLearn!2026
-- ============================================================
