-- ============================================================
--  schema.sql — ระบบคอร์สออนไลน์ (นิสิตออกแบบและเขียนเอง)
--  กติกา: ลงทะเบียน = M:N (learner × course), ความคืบหน้า = M:N (learner × lesson),
--         บทเรียน 1:M จาก course, คอร์สมี prerequisite อ้างถึง course เอง (self-reference)
-- ============================================================
CREATE TABLE learner (
    learner_id INT AUTO_INCREMENT PRIMARY KEY
    -- TODO: name, email, join_date
);
CREATE TABLE course (             -- prerequisite_id = self-reference -> course
    course_id INT AUTO_INCREMENT PRIMARY KEY
    -- TODO: title, category, price, prerequisite_id (FK -> course, NULL ได้)
);
CREATE TABLE lesson (             -- 1:M จาก course
    lesson_id INT AUTO_INCREMENT PRIMARY KEY
    -- TODO: course_id (FK), title, seq_no, duration_min
);
CREATE TABLE enrollment (         -- M:N: learner × course
    enroll_id INT AUTO_INCREMENT PRIMARY KEY
    -- TODO: learner_id (FK), course_id (FK), enroll_date, status ENUM('studying','completed')
    -- ★ ควรมี UNIQUE (learner_id, course_id) — 1 คนลงคอร์สเดิมได้ครั้งเดียว
);
CREATE TABLE progress (           -- M:N: learner × lesson
    -- TODO: learner_id (FK), lesson_id (FK), watched, completed_date ; PRIMARY KEY (learner_id, lesson_id)
    learner_id INT, lesson_id INT
);
-- TODO: INSERT ข้อมูลตัวอย่างทุกตาราง
--   ★ ควรมีคอร์สที่มี prerequisite อย่างน้อย 1 คอร์ส ไว้ทดสอบ "ต้องเรียนวิชาก่อนหน้าให้จบก่อน"
