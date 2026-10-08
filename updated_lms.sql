-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: lms_db
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admins` (
  `admin_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `contact` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`admin_id`),
  UNIQUE KEY `email` (`email`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `admins_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admins`
--

LOCK TABLES `admins` WRITE;
/*!40000 ALTER TABLE `admins` DISABLE KEYS */;
INSERT INTO `admins` VALUES (1,8,'Muhammad','Khurram','923047698099','saleemkhurram420@gmail.com',0);
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attendance` (
  `attendance_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_course_id` int(11) NOT NULL,
  `course_schedule_id` int(11) NOT NULL,
  `attendance_date` date NOT NULL,
  `attendance_status` enum('Present','Absent') DEFAULT 'Absent',
  `student_id` int(11) DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`attendance_id`),
  UNIQUE KEY `uq_att` (`student_course_id`,`course_schedule_id`,`attendance_date`),
  KEY `student_course_id` (`student_course_id`),
  KEY `course_schedule_id` (`course_schedule_id`),
  KEY `fk_attendance_student` (`student_id`),
  KEY `idx_attendance_date` (`attendance_date`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`student_course_id`) REFERENCES `student_course` (`student_course_id`),
  CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`course_schedule_id`) REFERENCES `course_schedule` (`course_schedule_id`),
  CONSTRAINT `fk_attendance_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance`
--

LOCK TABLES `attendance` WRITE;
/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
INSERT INTO `attendance` VALUES (1,2,3,'2025-12-31','Absent',3,0),(2,3,4,'2025-12-31','Absent',4,0),(4,2,3,'2026-02-04','Present',3,0),(5,3,4,'2026-02-04','Present',4,0),(6,2,3,'2026-03-04','Present',3,0),(7,3,4,'2026-03-04','Present',4,0),(10,2,3,'2026-03-11','Absent',3,0),(11,3,4,'2026-03-11','Present',4,0),(12,2,3,'2026-03-13','Present',3,0),(13,3,4,'2026-03-19','Present',4,0),(14,2,3,'2026-09-17','Present',3,0),(15,1,4,'2026-09-16','Absent',2,0),(16,3,4,'2026-09-16','Absent',4,0),(17,1,4,'2026-09-17','Present',2,0),(18,3,4,'2026-09-17','Present',4,0),(19,4,2,'2026-09-18','Present',5,0),(20,4,2,'2026-09-17','Present',5,0),(21,1,1,'2026-10-06','Absent',2,0),(22,1,1,'2026-10-05','Present',2,0),(23,2,3,'2026-10-05','Absent',3,0),(24,2,3,'2026-10-08','Present',3,0),(25,4,2,'2026-10-08','Present',5,0);
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `complaint_suggestion`
--

DROP TABLE IF EXISTS `complaint_suggestion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `complaint_suggestion` (
  `complt_sugst_id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `image_name` varchar(255) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `is_status` enum('Pending','Solved','Rejected') NOT NULL DEFAULT 'Pending',
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`complt_sugst_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `complaint_suggestion_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complaint_suggestion`
--

LOCK TABLES `complaint_suggestion` WRITE;
/*!40000 ALTER TABLE `complaint_suggestion` DISABLE KEYS */;
INSERT INTO `complaint_suggestion` VALUES (1,'Result','check my result',NULL,3,'Solved',0),(2,'Finance_Department','Give my salary\r\n',NULL,4,'Solved',0),(3,'Exam_Department','Where is my shedule??',NULL,3,'Solved',0),(4,'Finance_Department','hy testing fastapi teacher routes',NULL,11,'Pending',0),(5,'Library','checking again teacher fastapi route ',NULL,11,'Pending',0),(6,'Exam_Department','checking the flash message',NULL,11,'Pending',0),(7,'Finance_Department','checking the fastapi student module ',NULL,3,'Pending',0),(8,'Result','checking apirouter',NULL,3,'Pending',0),(9,'Library','checking again apirouter\r\n',NULL,3,'Pending',0),(10,'Hostel','checking service type fastapi',NULL,3,'Pending',0),(11,'Library','checking the service fastapi new student route',NULL,10,'Pending',0),(12,'Exam_Department','checking teacher fastapi service based',NULL,4,'Pending',0),(13,'Exam_Department','chking the orm based fastapi',NULL,3,'Pending',0);
/*!40000 ALTER TABLE `complaint_suggestion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_attendance_log`
--

DROP TABLE IF EXISTS `course_attendance_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `course_attendance_log` (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `teacher_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `course_schedule_id` int(11) NOT NULL,
  `attendance_date` date NOT NULL,
  `total_students` int(11) DEFAULT 0,
  `total_present` int(11) DEFAULT 0,
  `total_absent` int(11) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  `semester` int(11) DEFAULT NULL,
  PRIMARY KEY (`log_id`),
  KEY `teacher_id` (`teacher_id`),
  KEY `course_id` (`course_id`),
  KEY `course_schedule_id` (`course_schedule_id`),
  CONSTRAINT `cal_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`teacher_id`),
  CONSTRAINT `cal_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`),
  CONSTRAINT `cal_ibfk_3` FOREIGN KEY (`course_schedule_id`) REFERENCES `course_schedule` (`course_schedule_id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_attendance_log`
--

LOCK TABLES `course_attendance_log` WRITE;
/*!40000 ALTER TABLE `course_attendance_log` DISABLE KEYS */;
INSERT INTO `course_attendance_log` VALUES (3,1,1,3,'2026-03-11',91,41,50,'2026-03-11 07:37:21',0,5),(4,1,1,4,'2026-03-11',1,1,0,'2026-03-11 07:37:26',0,5),(5,1,1,3,'2026-03-13',1,1,0,'2026-03-13 06:38:50',0,5),(6,1,1,4,'2026-03-19',1,1,0,'2026-03-19 05:57:07',0,5),(7,5,6,4,'2026-03-26',15,10,5,'2026-03-25 13:34:10',0,5),(8,1,1,4,'2026-09-16',2,0,2,'2026-09-17 17:59:38',0,5),(9,1,1,4,'2026-09-17',2,0,2,'2026-09-17 18:04:13',0,5),(10,1,1,2,'2026-09-18',1,1,0,'2026-09-17 18:08:00',0,5),(11,1,1,2,'2026-09-17',1,1,0,'2026-09-17 18:28:14',0,5),(12,1,1,1,'2026-10-06',1,0,1,'2026-10-05 15:07:04',0,5),(13,1,1,1,'2026-10-05',1,1,0,'2026-10-05 15:07:50',0,5),(14,1,1,3,'2026-10-05',1,0,1,'2026-10-05 15:08:01',0,5),(15,1,1,3,'2026-10-08',1,1,0,'2026-10-08 11:15:12',0,5),(16,1,1,2,'2026-10-08',1,1,0,'2026-10-08 11:15:27',0,5);
/*!40000 ALTER TABLE `course_attendance_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_schedule`
--

DROP TABLE IF EXISTS `course_schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `course_schedule` (
  `course_schedule_id` int(11) NOT NULL AUTO_INCREMENT,
  `day_of_week` enum('Monday','Tuesday','Wednesday','Thursday','Friday') DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `course_id` int(11) NOT NULL,
  `section_id` int(11) DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`course_schedule_id`),
  KEY `course_id` (`course_id`),
  KEY `section_id` (`section_id`),
  CONSTRAINT `course_schedule_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`),
  CONSTRAINT `course_schedule_ibfk_2` FOREIGN KEY (`section_id`) REFERENCES `sections` (`section_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_schedule`
--

LOCK TABLES `course_schedule` WRITE;
/*!40000 ALTER TABLE `course_schedule` DISABLE KEYS */;
INSERT INTO `course_schedule` VALUES (1,'Monday','09:00:00','11:00:00','Class Room',1,1,0),(2,'Thursday','11:00:00','17:36:00','BTF-8',1,2,0),(3,'Friday','15:00:00','17:00:00','B-Lab-1',1,3,0),(4,'Wednesday','11:00:00','03:00:00','Lab 02',1,4,0),(5,'Monday','18:25:00','20:25:00','BTF-10',3,3,0),(6,'Thursday','09:00:00','12:00:00','BTF-11',5,4,0),(7,'Friday','06:36:00','20:36:00','BTF-09',6,4,0),(8,'Thursday','06:35:00','18:35:00','BTF-11',2,3,0),(9,'Monday','10:00:00','12:00:00','Room 101',5,8,0),(10,'Tuesday','14:00:00','16:00:00','Room 102',6,9,0);
/*!40000 ALTER TABLE `course_schedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `courses` (
  `course_id` int(11) NOT NULL AUTO_INCREMENT,
  `course_name` varchar(100) NOT NULL,
  `course_type` varchar(50) NOT NULL,
  `program_id` int(11) NOT NULL,
  `credit_hours` int(11) DEFAULT NULL,
  `no_of_lectures` int(11) DEFAULT NULL,
  `assignments_enabled` tinyint(1) DEFAULT 1,
  `quizzes_enabled` tinyint(1) DEFAULT 1,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`course_id`),
  KEY `program_id` (`program_id`),
  CONSTRAINT `courses_ibfk_1` FOREIGN KEY (`program_id`) REFERENCES `programs` (`program_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
INSERT INTO `courses` VALUES (1,'Introduction to Computing','Regular',1,3,17,1,1,0),(2,'Programming Fundamentals','Regular',1,4,19,1,1,0),(3,'IT Infrastructure','Regular',2,3,12,1,1,0),(4,'Network Administration','Regular',2,3,19,1,1,0),(5,'Introduction to AI','Regular',3,3,22,1,1,0),(6,'Machine Learning','Regular',3,4,20,1,1,0);
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exams`
--

DROP TABLE IF EXISTS `exams`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `exams` (
  `exam_id` int(11) NOT NULL AUTO_INCREMENT,
  `program_id` int(11) NOT NULL,
  `exam_category` enum('Mid','Final') NOT NULL,
  `exam_date` date NOT NULL,
  `exam_semester` tinyint(3) unsigned NOT NULL CHECK (`exam_semester` between 1 and 8),
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `location` varchar(100) DEFAULT NULL,
  `mode` enum('Online','On Campus') NOT NULL,
  `status` enum('Concluded','Ongoing') NOT NULL DEFAULT 'Ongoing',
  `is_deleted` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`exam_id`),
  KEY `fk_exam_program` (`program_id`),
  CONSTRAINT `fk_exam_program` FOREIGN KEY (`program_id`) REFERENCES `programs` (`program_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exams`
--

LOCK TABLES `exams` WRITE;
/*!40000 ALTER TABLE `exams` DISABLE KEYS */;
INSERT INTO `exams` VALUES (1,1,'Mid','2026-09-30',5,'10:00:00','12:00:00','BTF-11','On Campus','Ongoing',0),(2,2,'Mid','2026-03-17',3,'11:30:00','12:33:00','B-Lab-11','Online','Concluded',0),(3,3,'Final','2026-03-27',3,'13:00:00','15:00:00','BTF-09','On Campus','Concluded',0),(4,4,'Final','2026-03-20',3,'17:37:00','19:37:00','Lahore','Online','Ongoing',0),(5,4,'Final','2026-03-26',4,'10:00:00','12:00:00','BTF-03','On Campus','Ongoing',0);
/*!40000 ALTER TABLE `exams` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fyp_groups`
--

DROP TABLE IF EXISTS `fyp_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fyp_groups` (
  `fyp_id` int(11) NOT NULL AUTO_INCREMENT,
  `project_title` text NOT NULL,
  `description` text DEFAULT NULL,
  `teacher_id` int(11) DEFAULT NULL,
  `student_id` int(11) NOT NULL,
  `status` enum('In Progress','Approved','Completed','Rejected') NOT NULL DEFAULT 'In Progress',
  `progress` int(11) DEFAULT 0,
  `last_submission` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`fyp_id`),
  KEY `teacher_id` (`teacher_id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `fyp_groups_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`teacher_id`),
  CONSTRAINT `fyp_groups_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fyp_groups`
--

LOCK TABLES `fyp_groups` WRITE;
/*!40000 ALTER TABLE `fyp_groups` DISABLE KEYS */;
INSERT INTO `fyp_groups` VALUES (1,'thte','aaaabscs',1,2,'Approved',40,'uploads/students_uploads/students_fyp_proposal/SID_2_20261008_160923_Attendance_Report.pdf','2026-01-27 06:49:29',0),(2,'Huzaifa Title pr','i am again checking the project ',1,3,'Completed',0,'uploads/students_uploads/students_fyp_proposal/SID_3_portfolio-cv.pdf','2026-01-27 08:44:04',0),(3,'Developing LMS -Python-Flask-SQL','I want to develop the LMS of my University but with python flask and sqlalchemy.',4,5,'Approved',0,'uploads/students_uploads/students_fyp_proposal/SID_5_COA_CCP_sol.pdf','2026-03-05 06:19:33',0),(5,'finally working admin supervisor','chkng admin',4,4,'Approved',10,'uploads/students_uploads/students_fyp_proposal/SID_4_Organizational_Structure_and_Design.pdf','2026-03-13 11:01:22',0),(6,'thte','',NULL,2,'In Progress',0,'uploads/students_uploads/students_fyp_proposal/SID_2_test2.jpg','2026-10-02 07:00:16',0),(7,'testing service type fyp api route update','checking the fastapi route submit proposal',3,7,'Approved',10,'uploads/students_uploads/students_fyp_proposal/SID_7_20261002_140309_fine_report.pdf','2026-10-02 08:53:35',0);
/*!40000 ALTER TABLE `fyp_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fyp_messages`
--

DROP TABLE IF EXISTS `fyp_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fyp_messages` (
  `message_id` int(11) NOT NULL AUTO_INCREMENT,
  `fyp_id` int(11) NOT NULL,
  `teacher_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `sender_role` enum('teacher','student') NOT NULL,
  `message` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`message_id`),
  KEY `fyp_id` (`fyp_id`),
  CONSTRAINT `fyp_messages_ibfk_1` FOREIGN KEY (`fyp_id`) REFERENCES `fyp_groups` (`fyp_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fyp_messages`
--

LOCK TABLES `fyp_messages` WRITE;
/*!40000 ALTER TABLE `fyp_messages` DISABLE KEYS */;
INSERT INTO `fyp_messages` VALUES (1,1,1,2,'teacher','hy','2026-02-24 11:21:54',0),(2,2,1,3,'teacher','hy','2026-02-24 11:22:04',0),(3,1,1,2,'student','ji','2026-03-13 09:45:29',0),(4,5,4,4,'student','hi guys','2026-03-13 11:11:25',0),(5,1,1,2,'teacher','checking fastapi send message route','2026-09-17 16:33:28',0),(6,2,1,3,'teacher','also you checking','2026-09-17 16:34:03',0),(7,1,1,2,'student','hy i am testing fastapi response','2026-09-23 11:00:55',0),(8,1,1,2,'student','checking apirouter','2026-09-27 13:16:49',0),(9,7,3,7,'student','hi i am testing the fyp send message service based fastapi','2026-10-02 09:03:38',0),(10,1,1,2,'teacher','hecking the tchr fastapi service based api','2026-10-05 15:19:55',0),(11,2,1,3,'teacher','you didn\'t reply i am checking the fastapi servie based api','2026-10-05 15:20:27',0),(12,1,1,2,'teacher','so you didn\'t ans','2026-10-06 08:49:44',0),(13,1,1,2,'teacher','again checking','2026-10-07 10:44:06',0),(14,2,1,3,'teacher','checking again','2026-10-07 10:44:16',0),(15,1,1,2,'student','i am checking the orm based fastapi','2026-10-08 11:08:57',0),(16,1,1,2,'teacher','ok it is working','2026-10-08 11:39:54',0);
/*!40000 ALTER TABLE `fyp_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notifications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sender_id` int(11) NOT NULL,
  `sender_role` enum('student','teacher','admin') NOT NULL,
  `receiver_id` int(11) DEFAULT NULL,
  `receiver_role` enum('student','teacher','admin') NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `related_course_id` int(11) DEFAULT NULL,
  `status` enum('Pending','Resolved','Rejected') DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `related_course_id` (`related_course_id`),
  KEY `sender_id` (`sender_id`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`related_course_id`) REFERENCES `courses` (`course_id`) ON DELETE SET NULL,
  CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (1,8,'admin',NULL,'student','Notification checking','checking the method of notification',1,'Rejected','2026-03-13 06:21:45',1),(2,8,'admin',NULL,'teacher','checking the teacher  notify','i am just checking it.',NULL,'Pending','2026-03-13 06:38:10',0),(3,8,'admin',5,'student','Assigning the Course','this course has been assigned to you kindly visit my office.',5,'Pending','2026-03-13 06:44:07',0),(4,8,'admin',8,'admin','hhhhhh','mjhvyufdzay',1,'Pending','2026-03-25 13:38:54',0),(5,3,'student',NULL,'admin','Improvement Subject Selected','Student 2 select course 1 for improvement',1,'Pending','2026-09-14 13:57:44',0),(6,3,'student',NULL,'admin','Improvement Subject Selected','Student 2 select course 1 for improvement',1,'Pending','2026-09-23 10:59:45',0),(7,3,'student',NULL,'admin','Improvement Subject Selected','Student 2 select course 1 for improvement',1,'Pending','2026-09-27 13:14:55',0),(8,3,'student',NULL,'admin','Improvement Subject Selected','Student 2 select course 1 for improvement',1,'Pending','2026-09-27 13:31:38',0),(9,3,'student',NULL,'admin','Improvement Subject Selected','Student 2 select course 1 for improvement',1,'Pending','2026-09-27 14:41:44',0),(10,3,'student',NULL,'admin','Improvement Subject Selected','Student 2 select course 1 for improvement',1,'Pending','2026-10-02 06:59:01',0),(11,3,'student',NULL,'admin','Improvement Subject Selected','Student 2 select course 1 for improvement',1,'Pending','2026-10-02 06:59:10',0),(12,3,'student',NULL,'admin','Improvement Subject Selected','Student 2 select course 1 for improvement',1,'Pending','2026-10-02 14:35:42',0),(13,3,'student',NULL,'admin','Improvement Subject Selected','Student 2 select course 1 for improvement',1,'Pending','2026-10-03 10:44:43',0),(14,3,'student',NULL,'admin','Improvement Subject Selected','Student 2 select course 1 for improvement',1,'Pending','2026-10-03 10:45:41',0),(15,3,'student',NULL,'admin','Improvement Subject Selected','Student 2 select course 1 for improvement',1,'Pending','2026-10-03 10:50:41',0),(16,3,'student',NULL,'admin','Improvement Subject Selected','Student 2 select course 1 for improvement',1,'Pending','2026-10-08 11:05:28',0),(17,3,'student',NULL,'admin','Improvement Subject Selected','Student 2 select course 1 for improvement',1,'Pending','2026-10-08 11:05:45',0),(18,3,'student',NULL,'admin','Improvement Subject Selected','Student 2 select course 1 for improvement',1,'Pending','2026-10-08 11:46:54',0);
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `programs`
--

DROP TABLE IF EXISTS `programs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `programs` (
  `program_id` int(11) NOT NULL AUTO_INCREMENT,
  `program_name` varchar(100) NOT NULL,
  `program_coordinator` varchar(100) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`program_id`),
  UNIQUE KEY `program_name` (`program_name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `programs`
--

LOCK TABLES `programs` WRITE;
/*!40000 ALTER TABLE `programs` DISABLE KEYS */;
INSERT INTO `programs` VALUES (1,'BS Computer Science','Zeeshan Haider',0),(2,'BS Information Technology','Ansar Muneer',0),(3,'BS Artificial Intelligence','Shakeeb Ali',0),(4,'BS Data Science','Zohair Haider',0);
/*!40000 ALTER TABLE `programs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sections`
--

DROP TABLE IF EXISTS `sections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sections` (
  `section_id` int(11) NOT NULL AUTO_INCREMENT,
  `course_id` int(11) NOT NULL,
  `section_name` varchar(50) NOT NULL,
  `program_id` int(11) NOT NULL,
  `semester` int(11) NOT NULL,
  `assignments_enabled` tinyint(1) DEFAULT 1,
  `quizzes_enabled` tinyint(1) DEFAULT 1,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`section_id`),
  KEY `course_id` (`course_id`),
  KEY `program_id` (`program_id`),
  CONSTRAINT `sections_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`),
  CONSTRAINT `sections_ibfk_2` FOREIGN KEY (`program_id`) REFERENCES `programs` (`program_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sections`
--

LOCK TABLES `sections` WRITE;
/*!40000 ALTER TABLE `sections` DISABLE KEYS */;
INSERT INTO `sections` VALUES (1,1,'Blue',1,5,1,1,0),(2,1,'Green',1,5,0,0,0),(3,1,'Red',1,5,1,1,0),(4,1,'Orange',1,5,1,1,0),(5,2,'Blue',1,5,1,1,0),(6,3,'Blue',2,5,1,1,0),(7,4,'Blue',2,5,1,1,0),(8,5,'Blue',3,5,1,1,0),(9,6,'Blue',4,5,1,1,0);
/*!40000 ALTER TABLE `sections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `semester`
--

DROP TABLE IF EXISTS `semester`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `semester` (
  `semester_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `year` year(4) NOT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`semester_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `semester`
--

LOCK TABLES `semester` WRITE;
/*!40000 ALTER TABLE `semester` DISABLE KEYS */;
INSERT INTO `semester` VALUES (1,'Fall',2026,'2026-04-05','2026-06-03','2026-03-19 10:21:52',1),(2,'Spring',2026,'2026-03-04','2026-04-03','2026-03-04 11:02:43',1),(3,'Spring',2026,'2026-01-03','2026-04-03','2026-03-19 10:22:20',0),(4,'Fall',2027,'2026-03-19','2026-10-25','2026-03-25 13:25:37',0);
/*!40000 ALTER TABLE `semester` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `semester_freeze_students`
--

DROP TABLE IF EXISTS `semester_freeze_students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `semester_freeze_students` (
  `freeze_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) NOT NULL,
  `semester` int(11) NOT NULL,
  `reason` text NOT NULL,
  `status` enum('Pending','Approved','Rejected') DEFAULT 'Pending',
  `applied_date` datetime DEFAULT current_timestamp(),
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`freeze_id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `semester_freeze_students_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `semester_freeze_students`
--

LOCK TABLES `semester_freeze_students` WRITE;
/*!40000 ALTER TABLE `semester_freeze_students` DISABLE KEYS */;
INSERT INTO `semester_freeze_students` VALUES (1,3,5,'I am checking the semester freeze routes and methods for admin','Approved','2026-03-05 13:36:02',0),(2,2,5,'checking the fastapi freeze request','Rejected','2026-09-23 16:00:25',0);
/*!40000 ALTER TABLE `semester_freeze_students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_course`
--

DROP TABLE IF EXISTS `student_course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `student_course` (
  `student_course_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`student_course_id`),
  UNIQUE KEY `unique_student_course` (`student_id`,`course_id`),
  KEY `student_id` (`student_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `student_course_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`),
  CONSTRAINT `student_course_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_course`
--

LOCK TABLES `student_course` WRITE;
/*!40000 ALTER TABLE `student_course` DISABLE KEYS */;
INSERT INTO `student_course` VALUES (1,2,1,0,'2026-03-16 08:16:08'),(2,3,1,0,'2026-03-16 08:16:08'),(3,4,1,0,'2026-03-16 08:16:08'),(4,5,1,0,'2026-03-16 08:16:08'),(5,7,3,0,'2026-03-16 08:16:08'),(6,9,4,0,'2026-03-19 10:25:35'),(7,2,2,0,'2026-03-25 13:31:14');
/*!40000 ALTER TABLE `student_course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_fail_subjects`
--

DROP TABLE IF EXISTS `student_fail_subjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `student_fail_subjects` (
  `student_fail_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `status` enum('Pending','Approved','Rejected') NOT NULL DEFAULT 'Pending',
  `create_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`student_fail_id`),
  KEY `student_id` (`student_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `student_fail_subjects_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`),
  CONSTRAINT `student_fail_subjects_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_fail_subjects`
--

LOCK TABLES `student_fail_subjects` WRITE;
/*!40000 ALTER TABLE `student_fail_subjects` DISABLE KEYS */;
/*!40000 ALTER TABLE `student_fail_subjects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_fees`
--

DROP TABLE IF EXISTS `student_fees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `student_fees` (
  `student_fees_id` int(11) NOT NULL AUTO_INCREMENT,
  `fee_amount` decimal(10,2) NOT NULL,
  `fee_status` enum('paid','due') DEFAULT 'due',
  `update_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `voucher_front_pic` varchar(255) DEFAULT NULL,
  `voucher_back_pic` varchar(255) DEFAULT NULL,
  `program_id` int(11) NOT NULL,
  `fee_month` varchar(20) DEFAULT NULL,
  `student_id` int(11) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`student_fees_id`),
  KEY `program_id` (`program_id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `student_fees_ibfk_1` FOREIGN KEY (`program_id`) REFERENCES `programs` (`program_id`),
  CONSTRAINT `student_fees_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_fees`
--

LOCK TABLES `student_fees` WRITE;
/*!40000 ALTER TABLE `student_fees` DISABLE KEYS */;
INSERT INTO `student_fees` VALUES (1,18708.00,'paid','2025-12-31 09:10:20','uploads/students_uploads/voucher_pics/student_4_front_contact.PNG','uploads/students_uploads/voucher_pics/student_4_back_prj.PNG',1,'December',4,0),(2,68102.00,'paid','2026-03-05 07:08:03','uploads/students_uploads/voucher_pics/student_2_front_dep_view.PNG','uploads/students_uploads/voucher_pics/student_2_back_students_view.PNG',1,'January',2,0),(3,18708.00,'due','2026-03-25 13:21:57',NULL,NULL,4,'December',5,0),(4,19644.00,'paid','2026-03-19 10:25:10',NULL,NULL,4,'December',9,0),(5,12000.00,'due','2026-03-25 13:22:22',NULL,NULL,3,'December',8,0),(6,12345.00,'due','2026-09-14 13:48:46','uploads/students_uploads/voucher_pics/student_2_front_Screenshot_2026-09-14_184408.png','uploads/students_uploads/voucher_pics/student_2_back_Screenshot_2026-09-14_184408.png',1,'February',2,0),(7,19000.00,'due','2026-09-23 10:58:42','uploads/students_uploads/voucher_pics/student_2_front_Screenshot_2026-09-16_175618.png','uploads/students_uploads/voucher_pics/student_2_back_Screenshot_2026-09-16_175806.png',1,'September',2,0),(8,12345.00,'due','2026-09-27 12:53:09','uploads/students_uploads/voucher_pics/student_2_front_map_visualization.png','uploads/students_uploads/voucher_pics/student_2_back_project_tree.png',1,'July',2,0),(9,30000.00,'due','2026-10-02 06:56:26','uploads/students_uploads/voucher_pics/student_2_front_test4.jpg','uploads/students_uploads/voucher_pics/student_2_back_test5.jpg',1,'October',2,0),(10,123455.00,'due','2026-10-02 14:05:21','uploads/students_uploads/voucher_pics/student_2_front_test8.jpg','uploads/students_uploads/voucher_pics/student_2_back_test6.jpg',1,'July',2,0),(11,30000.00,'due','2026-10-02 14:32:35','uploads/students_uploads/voucher_pics/student_2_front_map_visualization.png','uploads/students_uploads/voucher_pics/student_2_back_analyze_api_response.png',1,'August',2,0),(12,87655.00,'due','2026-10-03 10:13:26','uploads/students_uploads/voucher_pics/student_2_front_Screenshot_2026-09-14_190312.png','uploads/students_uploads/voucher_pics/student_2_back_Screenshot_2026-09-14_184408.png',1,'February',2,0),(13,1267.00,'due','2026-10-08 11:04:07','uploads/students_uploads/voucher_pics/student_2_front_Screenshot_2026-09-16_175618.png','uploads/students_uploads/voucher_pics/student_2_back_Screenshot_2026-09-16_175806.png',1,'February',2,0);
/*!40000 ALTER TABLE `student_fees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_improvement`
--

DROP TABLE IF EXISTS `student_improvement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `student_improvement` (
  `improvement_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `status` enum('Pending','Approved','Rejected') NOT NULL DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`improvement_id`),
  UNIQUE KEY `unique_student_improvement` (`student_id`),
  KEY `student_id` (`student_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `student_improvement_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`),
  CONSTRAINT `student_improvement_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_improvement`
--

LOCK TABLES `student_improvement` WRITE;
/*!40000 ALTER TABLE `student_improvement` DISABLE KEYS */;
INSERT INTO `student_improvement` VALUES (2,3,4,'Pending','2026-03-05 07:57:05',0);
/*!40000 ALTER TABLE `student_improvement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_result_marks`
--

DROP TABLE IF EXISTS `student_result_marks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `student_result_marks` (
  `marks_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_course_id` int(11) NOT NULL,
  `student_result_id` int(11) NOT NULL,
  `total_marks` int(11) DEFAULT 0,
  `student_grade` varchar(10) NOT NULL,
  `status` varchar(50) NOT NULL,
  `student_semester` int(11) DEFAULT NULL,
  `sessional_marks` int(11) DEFAULT 0,
  `mid_marks` int(11) DEFAULT 0,
  `final_marks` int(11) DEFAULT 0,
  `subject_gpa` decimal(3,2) DEFAULT 0.00,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`marks_id`),
  UNIQUE KEY `uq_scm` (`student_course_id`),
  KEY `student_course_id` (`student_course_id`),
  KEY `student_result_id` (`student_result_id`),
  CONSTRAINT `student_result_marks_ibfk_1` FOREIGN KEY (`student_course_id`) REFERENCES `student_course` (`student_course_id`),
  CONSTRAINT `student_result_marks_ibfk_2` FOREIGN KEY (`student_result_id`) REFERENCES `student_results` (`student_result_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_result_marks`
--

LOCK TABLES `student_result_marks` WRITE;
/*!40000 ALTER TABLE `student_result_marks` DISABLE KEYS */;
INSERT INTO `student_result_marks` VALUES (1,1,1,89,'A','Pass',5,18,28,43,4.00,0),(2,3,2,75,'B+','Pass',5,18,23,34,3.30,0),(3,2,3,80,'A-','Pass',5,12,23,45,3.70,0),(4,4,4,82,'A-','Pass',5,18,23,41,3.70,0);
/*!40000 ALTER TABLE `student_result_marks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_results`
--

DROP TABLE IF EXISTS `student_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `student_results` (
  `student_result_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) NOT NULL,
  `student_semester` int(11) NOT NULL,
  `overall_gpa` decimal(3,2) NOT NULL CHECK (`overall_gpa` between 0.00 and 4.00),
  `result_status` enum('Pass','Fail') NOT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`student_result_id`),
  UNIQUE KEY `unique_student_semester` (`student_id`,`student_semester`),
  KEY `student_id` (`student_id`),
  KEY `idx_student_semester` (`student_id`,`student_semester`),
  CONSTRAINT `student_results_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_results`
--

LOCK TABLES `student_results` WRITE;
/*!40000 ALTER TABLE `student_results` DISABLE KEYS */;
INSERT INTO `student_results` VALUES (1,2,5,4.00,'Pass',0,'2026-10-06 10:05:39'),(2,4,5,3.30,'Pass',0,'2026-10-07 10:39:35'),(3,3,5,3.70,'Pass',0,'2026-10-08 11:38:40'),(4,5,5,3.70,'Pass',0,'2026-10-08 11:39:19');
/*!40000 ALTER TABLE `student_results` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_section`
--

DROP TABLE IF EXISTS `student_section`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `student_section` (
  `student_section_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) NOT NULL,
  `section_id` int(11) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`student_section_id`),
  UNIQUE KEY `unique_student_section` (`student_id`,`section_id`),
  KEY `fk_ss_student` (`student_id`),
  KEY `fk_ss_section` (`section_id`),
  CONSTRAINT `fk_ss_section` FOREIGN KEY (`section_id`) REFERENCES `sections` (`section_id`),
  CONSTRAINT `fk_ss_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_section`
--

LOCK TABLES `student_section` WRITE;
/*!40000 ALTER TABLE `student_section` DISABLE KEYS */;
INSERT INTO `student_section` VALUES (1,2,1,0,'2026-03-16 08:16:08'),(2,3,3,0,'2026-03-16 08:16:08'),(3,4,4,0,'2026-03-16 08:16:08'),(4,5,2,0,'2026-03-16 08:16:08'),(5,9,5,0,'2026-03-19 10:25:35'),(6,2,4,0,'2026-03-25 13:31:14');
/*!40000 ALTER TABLE `student_section` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_submissions`
--

DROP TABLE IF EXISTS `student_submissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `student_submissions` (
  `submission_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) DEFAULT NULL,
  `course_id` int(11) DEFAULT NULL,
  `section_id` int(11) DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `submission_type` enum('assignment','quiz') DEFAULT NULL,
  `upload_date` datetime DEFAULT current_timestamp(),
  `submission_status` enum('Best','Average','Worst','Pending') DEFAULT 'Pending',
  `marks` int(11) DEFAULT NULL,
  `total_marks` int(11) DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`submission_id`),
  KEY `fk_sub_student` (`student_id`),
  KEY `fk_sub_course` (`course_id`),
  KEY `fk_sub_section` (`section_id`),
  CONSTRAINT `fk_sub_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`),
  CONSTRAINT `fk_sub_section` FOREIGN KEY (`section_id`) REFERENCES `sections` (`section_id`),
  CONSTRAINT `fk_sub_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_submissions`
--

LOCK TABLES `student_submissions` WRITE;
/*!40000 ALTER TABLE `student_submissions` DISABLE KEYS */;
INSERT INTO `student_submissions` VALUES (1,3,1,3,'uploads/students_uploads/students_assignments/SID3_20260204_120727_new_cover.docx','assignment','2026-02-04 12:07:27','Best',5,5,0),(2,3,1,3,'uploads/students_uploads/students_quizes/SID3_20260204_121554_Student_Management_System_Report_Project.docx','quiz','2026-02-04 12:15:54','Best',2,5,0),(4,4,1,4,'uploads/students_uploads/students_assignments/SID4_20260204_135820_add_view_st.PNG','assignment','2026-02-04 13:58:20','Best',3,5,0),(5,4,1,4,'uploads/students_uploads/students_quizes/SID4_20260204_135954_home_view.PNG','quiz','2026-02-04 13:59:54','Best',3,5,0),(7,2,1,1,'uploads/students_uploads/students_assignments/SID_2_20261008_161308_Python_AI_ML_Developer.pdf','assignment','2026-10-08 16:13:08','Worst',4,5,0),(8,2,1,1,'uploads/students_uploads/students_quizes/SID_2_20261008_161413_InfinityWave_internship_certificate.pdf','quiz','2026-10-08 16:14:13','Average',0,5,0);
/*!40000 ALTER TABLE `student_submissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `students` (
  `student_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `contact` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `last_qualification` varchar(100) DEFAULT NULL,
  `program_id` int(11) NOT NULL,
  `admission_session` varchar(50) DEFAULT NULL,
  `admission_date` date DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  `current_semester` int(11) DEFAULT 1,
  PRIMARY KEY (`student_id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `program_id` (`program_id`),
  CONSTRAINT `students_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `students_ibfk_2` FOREIGN KEY (`program_id`) REFERENCES `programs` (`program_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES (2,3,'Umair','Ullah','923150484043','ullahcentral123@gmail.com','FSC-PreMedical',1,'Fall-2023','2024-01-10',0,7),(3,5,'Muhammad','Huzaifa','923047698099','huzaifacentral123@gmail.com','ICS',1,'Fall-2023','2025-12-31',0,4),(4,6,'Muhammad','Hammad','923047698098','hammadcentral123@gmail.com','FSC-PreMedical',1,'Fall-2023','2025-12-31',0,3),(5,7,'Mubeen','khurram','923057698092','mubeenmuzaffar123@gmail.com','ICS',3,'Fall-2026','2026-03-04',1,3),(6,9,'Haris','Rizwan','03047698099','hariscentral123@gmail.com','Intermediate',4,'Spring 2026','2026-03-04',1,1),(7,10,'Aiman','Rizwan','923047698099','aiman123@gmail.com','FSC-Engrineering',4,'Spring 2026','2026-04-03',0,1),(8,15,'New ','student','923047698091','newstudent@gmail.com','Intermediate',3,'Spring 2026','2026-03-17',0,2),(9,16,'check','model','03047598091','model@gmail.com','Intermediate',2,'Fall-2026','2026-03-02',0,7),(10,17,'Checking','Model','923047698098','modal@gmail.com','FSC-Engrineering',4,'Spring 2026','2026-03-20',0,1),(11,23,'main fastapi','checking','3150484045','checkmain123@gmail.com',NULL,1,NULL,'2026-09-22',0,1);
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `summer_registration`
--

DROP TABLE IF EXISTS `summer_registration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `summer_registration` (
  `registration_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `summer_semesters_id` int(11) NOT NULL,
  `registration_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`registration_id`),
  KEY `fk_summer_student` (`student_id`),
  KEY `fk_summer_course` (`course_id`),
  KEY `fk_summer_semester` (`summer_semesters_id`),
  CONSTRAINT `fk_summer_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_summer_semester` FOREIGN KEY (`summer_semesters_id`) REFERENCES `summer_semesters` (`summer_semesters_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_summer_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `summer_registration`
--

LOCK TABLES `summer_registration` WRITE;
/*!40000 ALTER TABLE `summer_registration` DISABLE KEYS */;
INSERT INTO `summer_registration` VALUES (2,3,4,2,'2026-03-05 11:02:18',0);
/*!40000 ALTER TABLE `summer_registration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `summer_semesters`
--

DROP TABLE IF EXISTS `summer_semesters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `summer_semesters` (
  `summer_semesters_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `year` year(4) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `previous_semester_id` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('Open','Closed') NOT NULL DEFAULT 'Open',
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`summer_semesters_id`),
  KEY `previous_semester_id` (`previous_semester_id`),
  CONSTRAINT `summer_semesters_ibfk_1` FOREIGN KEY (`previous_semester_id`) REFERENCES `semester` (`semester_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `summer_semesters`
--

LOCK TABLES `summer_semesters` WRITE;
/*!40000 ALTER TABLE `summer_semesters` DISABLE KEYS */;
INSERT INTO `summer_semesters` VALUES (1,'Winter',2026,'2026-03-05','2026-03-06',1,'2026-03-05 10:22:54','Open',0),(2,'Summer',2026,'2026-04-05','2026-07-05',1,'2026-03-05 10:25:17','Open',0),(3,'Summer Back',2026,'2026-03-19','2026-03-28',1,'2026-03-19 10:26:54','Open',0);
/*!40000 ALTER TABLE `summer_semesters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_settings`
--

DROP TABLE IF EXISTS `system_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `system_settings` (
  `setting_key` varchar(50) NOT NULL,
  `setting_value` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`setting_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_settings`
--

LOCK TABLES `system_settings` WRITE;
/*!40000 ALTER TABLE `system_settings` DISABLE KEYS */;
INSERT INTO `system_settings` VALUES ('current_term','1','Fall 2026',0),('is_admission_open','1','Controls if the signup/admission page is accessible',0),('is_course_reg_open','1','Controls if students can register for new courses',0),('is_summer_app_open','1','Controls if summer semester applications are enabled',0);
/*!40000 ALTER TABLE `system_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher_course`
--

DROP TABLE IF EXISTS `teacher_course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `teacher_course` (
  `teacher_course_id` int(11) NOT NULL AUTO_INCREMENT,
  `teacher_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`teacher_course_id`),
  KEY `teacher_id` (`teacher_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `teacher_course_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`teacher_id`),
  CONSTRAINT `teacher_course_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher_course`
--

LOCK TABLES `teacher_course` WRITE;
/*!40000 ALTER TABLE `teacher_course` DISABLE KEYS */;
INSERT INTO `teacher_course` VALUES (1,1,1,0),(2,1,2,0),(3,3,5,0),(4,3,6,0),(8,4,1,0),(9,4,2,1),(10,4,6,0),(11,4,4,0),(12,1,4,0),(15,5,2,0),(16,5,3,0),(17,5,5,0),(18,5,6,0),(19,5,1,0);
/*!40000 ALTER TABLE `teacher_course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher_salary`
--

DROP TABLE IF EXISTS `teacher_salary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `teacher_salary` (
  `salary_id` int(11) NOT NULL AUTO_INCREMENT,
  `teacher_id` int(11) NOT NULL,
  `month` varchar(20) NOT NULL,
  `year` int(11) NOT NULL,
  `basic_salary` decimal(10,2) NOT NULL,
  `bonus` decimal(10,2) DEFAULT 0.00,
  `deductions` decimal(10,2) DEFAULT 0.00,
  `status` enum('Pending','Paid') DEFAULT 'Pending',
  `is_deleted` tinyint(4) DEFAULT 0,
  PRIMARY KEY (`salary_id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `teacher_salary_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`teacher_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher_salary`
--

LOCK TABLES `teacher_salary` WRITE;
/*!40000 ALTER TABLE `teacher_salary` DISABLE KEYS */;
INSERT INTO `teacher_salary` VALUES (1,4,'March',2026,35000.00,2500.00,500.00,'Paid',0),(2,1,'April',2026,45000.00,3500.00,1199.99,'Pending',0),(3,4,'January',2026,45000.00,5400.00,600.00,'Paid',0),(4,5,'March',2026,12000.00,1200.00,100.00,'Paid',0);
/*!40000 ALTER TABLE `teacher_salary` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teachers`
--

DROP TABLE IF EXISTS `teachers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `teachers` (
  `teacher_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `contact_num` varchar(100) NOT NULL,
  `qualification` varchar(100) DEFAULT NULL,
  `joining_date` date DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`teacher_id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `teachers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teachers`
--

LOCK TABLES `teachers` WRITE;
/*!40000 ALTER TABLE `teachers` DISABLE KEYS */;
INSERT INTO `teachers` VALUES (1,4,'sana','fatima','sanacentral123@gmail.com','923150484043','Graduation','2025-12-30',0),(2,11,'Asim','Bashir','asimcentral123@gmail.com','923100484042','Master','2026-03-08',0),(3,13,'Ali','Imran','alicentral123@gmal.com','0315048404','Master','2026-03-08',0),(4,14,'Muhammad','Bashir','bashir123@gmail.com','923094645444','Phd','2027-03-12',0),(5,18,'check','model','charlie123@gmail.com','0315048403','Bachelor','2026-03-26',0),(6,24,'main fastapi','checking teacher','checkmain1234@gmail.com','3150484047',NULL,'2026-09-22',0);
/*!40000 ALTER TABLE `teachers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role_id` int(11) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `users_role` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'teacher@gmail.com','scrypt:32768:8:1$CeJBgdFFe1vMPnvT$59f8ad1cc8447fea3e9a0a4d831b97466af81a408925874c04c7062c4475df9c3dba1c18da1491cd5c0b329db8395e13f18b6f9b70d96c1bf4967983f62a517f',1,0),(2,'student@gmail.com','54321',2,0),(3,'ullahcentral123@gmail.com','scrypt:32768:8:1$JEkgewgb59qRZgyG$73fb00c9a04e93661316654d0dd4ab5b8b2e949a91b3de9d9246f9c893ec058bd11de9fd46ed9d5b415612bff15bd0f0ef8e67af44f42ffff9518893f0598e8e',2,0),(4,'sanacentral123@gmail.com','scrypt:32768:8:1$BSgvJ8PrNjxHYiAI$9df115ab1c4032c07d4d43904fad3f5f880009af0447d3d405ad44c4cab04eae964f3acb6766f3dc1468bebc3d50648939ee9420f5448393471c86f331991f84',1,0),(5,'huzaifacentral123@gmail.com','scrypt:32768:8:1$I9n0FGjNKaqHRaC4$3e9a48dd81365bda10cf83a4ab1e1eab8c15ac930da13bc1742efef4f4ea57274842f7ab41d824c2c8f135c5f214071ac911d9dd1a334ff553388ab2d0369575',2,0),(6,'hammadcentral123@gmail.com','scrypt:32768:8:1$jfSOWTiPsrWqazKQ$221c31ec18f224255ea2dff9eaf531a035cf704e27918fa7e4364a89d54eeae8af42701c759ba68cd5e7f49c9cf5bb690e8768725f11e63fc7b848f0f2e3de0f',2,0),(7,'mubeenmuzaffar123@gmail.com','scrypt:32768:8:1$ZhqrixLR5MGq8CS2$163df37b57801281972e50959c569da0d91ce77390944d9c2e81729f9a8feab0e9eaa3502ff59bdc825898746268da597de329eeebc9049ff365302bcfb74634',2,0),(8,'saleemkhurram420@gmail.com','scrypt:32768:8:1$skIzf7LpmeXDV7We$46816137a770b3c6ca5f90f7a3c5e03d772807aada70e450473f15803ebf2c5793b04ca86e78101e5da1272c80919b4e8a49d2540aabc7bd51e84d68b91e5e70',3,0),(9,'hariscentral123@gmail.com','scrypt:32768:8:1$R3WyGmnp0WVq4Yr6$3f666a241ec267a81464d1b8ba5efc3937e99b14d0970339055853ed23fb6c024978199950cd6c93e3d97d00d8999db3d286b43a1bf47b30c66cc8f09b55471e',2,0),(10,'aiman123@gmail.com','scrypt:32768:8:1$PJ1jGH07LQQy1Udh$4e70a5911417ae9ff1600f6f983cdff21a871c43e3d1cc08a059f4f27360e1b380759343ede2194a2fc51b84e016a8b8d652241cc2716e3eb09cafff0191456a',2,0),(11,'asimcentral123@gmail.com','scrypt:32768:8:1$MBwastRJTqbfXmQh$ac8da53d58f6220339a71e69df1702b582f0555df9a026bdc1c48880fc280ee6f76b67adf2171bbd71941392d70e9a73dfc29d7c84370a86254c9c0321c60780',1,0),(13,'alicentral123@gmal.com','scrypt:32768:8:1$77fUepREXyaiaeNg$2bc7dd4044eaea25c2d2cc37032fa6d132f07f514d0fcae77e69db7d05a6600bfa2702c174b6396ccf790761ed0bcd0b78355ad087694c7bb0527270275d8992',1,0),(14,'bashir123@gmail.com','scrypt:32768:8:1$IQjPszk5IyxicfEQ$57ec53dbbf405f881f2bfda1422a9cc11f5df4fcae9cea10a3971e88abe7e410f625536e523fc4e8579e49bfeff5314645a10a16b1ee6d48cfa88be27d03d3ce',1,0),(15,'newstudent@gmail.com','scrypt:32768:8:1$t1ZpuexMy2VJZasa$abe1b7915e8dbc3483a747fdab5874b0359970788c0ec9315639df56247d51d0443028ec43224995ccc9f4fd6f8bfcbf3087aeca1e2e41315ae0eb6d733f199b',2,0),(16,'model@gmail.com','scrypt:32768:8:1$Jwac0CdYZADbDD8n$e504184fd726b1ff6154ea08bf54802e766cf7a52de6b929039f49d60f659bf234fb855b17f01dca25b71d8ba4cbfb15bdb9b5dc650ca9fa5bcc3b4def7afbe0',2,0),(17,'modal@gmail.com','scrypt:32768:8:1$fUbd5VadA7Yxwx4x$03db4ff565b8ca609d883aa9599cc9c0e41e27fc386cdaef3840fb3d0f3753c051e0237c6fef99c152b1663b5c89ded726d7f6d8f51eb3616024f2a6ab9da818',2,0),(18,'charlie123@gmail.com','scrypt:32768:8:1$PlvXsXHYOnsF8U4R$b8c4aacf90cff686e78b4b726e7eb7b790608004e394e0d32df14a1fc52a435669b7d8cf38ec43bdaf64b822621f69388df7e83be5bd3f4111348e5e7dce60af',1,0),(19,'maintest123@gmail.com','scrypt:32768:8:1$22ssNJOhIJ480XsM$6dfd8b7be10e7b65123f73a9769693869973853c303a0ddcb6510c2b9c03d4f73ee08f2096713187c38f0bd2529bb782e37027312f8f380f48042b9348f02dc2',2,0),(20,'maintest1234@gmail.com','scrypt:32768:8:1$wXTzyQri3VwOMmUS$b1ebd1b2df9c74ffd1360c2ca58545628d7a5a39c32f95d15bffcbcddc1a190ed4899b070bc307b8f58253b81276d3230eee0ada6e144963a806b70e460c27bd',1,0),(21,'maintest12345@gmail.com','scrypt:32768:8:1$dvrzfSqeoXNAIapF$914a4ea67abdbaff4e2bf10e242fc389835ba20498ccc9885d2be0d0471c8d5f6ed3f72992d1874407168996a6035383ca35ff7e774c9776d8b01204bc6c4335',1,0),(22,'mainfastapi123@gmail.com','scrypt:32768:8:1$aHqzrdhUmqyi7i7R$c5176def61f470d59251f681a2b159bceb3d3b7699ab353ab779d783ea9240b6024c25f35712163f36462d8c935444093b3f0d1543b060fae71ba4ea65c24b9e',1,0),(23,'checkmain123@gmail.com','scrypt:32768:8:1$nCD7F6c2aXZBoSmZ$0750f4aaf49cdfc87a3c1b8a411ed7ec86882823d190a545b506309e9e6353476a60041c1c2652ffc2db66c26ca8eba60537e2fa69bd56f58ac4f1546fcc6ac1',2,0),(24,'checkmain1234@gmail.com','scrypt:32768:8:1$My7suN14qRWpxRo7$6289f2e31b25e16454feb26472ca2fc0fee120edd6c18a60c91f461df33a29145b928d98abccdbb089159a1e789737f9a283da10cb1f1308be386c73e9e73e1f',1,0),(25,'checkmain12345@gmail.com','scrypt:32768:8:1$2ndtPEnmeKgMxWsk$e1c8de737699def8d98e84cd0495d0531bad5840cf93c61f27210d3f3ae8079f4695181927db03a43fe3cfe8dbbef96247c7ed09fa4678b3d53b9f2fdb0d45a4',3,0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_role`
--

DROP TABLE IF EXISTS `users_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users_role` (
  `role_id` int(11) NOT NULL AUTO_INCREMENT,
  `role_type` varchar(100) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`role_id`),
  UNIQUE KEY `role_type` (`role_type`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_role`
--

LOCK TABLES `users_role` WRITE;
/*!40000 ALTER TABLE `users_role` DISABLE KEYS */;
INSERT INTO `users_role` VALUES (1,'teacher',0),(2,'student',0),(3,'admin',0);
/*!40000 ALTER TABLE `users_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'lms_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-08 16:47:42
