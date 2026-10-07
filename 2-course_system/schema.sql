-- Active: 1791274003397@@127.0.0.1@3306@onile_course
-- ============================================================
--  1. CREATE TABLES (โครงสร้างตารางสมบูรณ์)
-- ============================================================
-- ============================================================
--  0. DROP TABLES (ลบตารางเก่าเรียงตาม FK Dependency)
-- ============================================================




DROP TABLE IF EXISTS progress;
DROP TABLE IF EXISTS enrollment;
DROP TABLE IF EXISTS lesson;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS learner;

CREATE TABLE learner (
    learner_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    join_date DATE NOT NULL
);

CREATE TABLE course (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    prerequisite_id INT NULL,
    FOREIGN KEY (prerequisite_id) REFERENCES course(course_id) ON DELETE SET NULL
);

CREATE TABLE lesson (
    lesson_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    seq_no INT NOT NULL,
    duration_min INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE
);

CREATE TABLE enrollment (
    enroll_id INT AUTO_INCREMENT PRIMARY KEY,
    learner_id INT NOT NULL,
    course_id INT NOT NULL,
    enroll_date DATE NOT NULL,
    status ENUM('studying', 'completed') NOT NULL DEFAULT 'studying',
    FOREIGN KEY (learner_id) REFERENCES learner(learner_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE,
    UNIQUE (learner_id, course_id) -- 1 คนลงคอร์สเดิมซ้ำไม่ได้
);

CREATE TABLE progress (
    learner_id INT NOT NULL,
    lesson_id INT NOT NULL,
    watched BOOLEAN NOT NULL DEFAULT FALSE,
    completed_date DATETIME NULL,
    PRIMARY KEY (learner_id, lesson_id),
    FOREIGN KEY (learner_id) REFERENCES learner(learner_id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lesson(lesson_id) ON DELETE CASCADE
);


-- ============================================================
--  SAMPLE DATA INSERT (8 Learners & Full Course Network)
-- ============================================================

-- 1. เพิ่มผู้เรียน (Learners) - 8 คน
INSERT INTO learner (name, email, join_date) VALUES
('Sompong Jaidee', 'sompong.j@example.com', '2026-01-05'),
('Kanya Rattana', 'kanya.r@example.com', '2026-01-10'),
('Nattapong Dev', 'nattapong.d@example.com', '2026-01-12'),
('Preeya Chaitai', 'preeya.c@example.com', '2026-01-20'),
('Chaiwat Tech', 'chaiwat.t@example.com', '2026-01-25'),
('Wipa Sukjai', 'wipa.s@example.com', '2026-02-01'),
('Thanakorn Code', 'thanakorn.c@example.com', '2026-02-03'),
('Apinya Learn', 'apinya.l@example.com', '2026-02-05');

-- 2. เพิ่มคอร์สเรียน (Courses)
-- คอร์ส 1 & 4 & 5: ไม่ต้องมีวิชาก่อนหน้า
-- คอร์ส 2: ต้องผ่าน คอร์ส 1
-- คอร์ส 3: ต้องผ่าน คอร์ส 2
INSERT INTO course (course_id, title, category, price, prerequisite_id) VALUES
(1, 'Python for Beginners', 'Programming', 1000.00, NULL),
(2, 'Data Structure & Algorithms with Python', 'Programming', 1800.00, 1),
(3, 'Applied Machine Learning', 'Data Science', 2900.00, 2),
(4, 'UI/UX Design Fundamentals', 'Design', 1200.00, NULL),
(5, 'Database Systems & SQL Essentials', 'Database', 1500.00, NULL);

-- 3. เพิ่มบทเรียน (Lessons)
INSERT INTO lesson (course_id, title, seq_no, duration_min) VALUES
-- Python for Beginners (Course 1)
(1, 'Python Setup & Basic Syntax', 1, 25),
(1, 'Control Structures & Loops', 2, 40),
-- Data Structure & Algorithms (Course 2)
(2, 'Lists, Stacks, and Queues', 1, 50),
(2, 'Binary Trees & Recursion', 2, 60),
-- Applied Machine Learning (Course 3)
(3, 'Supervised Learning & Regression', 1, 90),
-- UI/UX Design (Course 4)
(4, 'Wireframing & Prototyping in Figma', 1, 45),
-- Database Systems (Course 5)
(5, 'Relational Database & ER-Diagram', 1, 35),
(5, 'SQL Queries & Joins', 2, 55);

-- 4. การลงทะเบียน (Enrollment) - 8 ตัวอย่าง
INSERT INTO enrollment (learner_id, course_id, enroll_date, status) VALUES
(1, 1, '2026-01-06', 'completed'), -- Sompong เรียน Python จบแล้ว
(1, 2, '2026-01-20', 'studying'),  -- Sompong ต่อ Data Structure
(2, 4, '2026-01-11', 'studying'),  -- Kanya เรียน UI/UX
(3, 1, '2026-01-15', 'completed'), -- Nattapong เรียน Python จบแล้ว
(3, 2, '2026-01-28', 'completed'), -- Nattapong เรียน Data Struct จบแล้ว
(3, 3, '2026-02-02', 'studying')  -- Nattapong ขึ้น