# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล  ★★★ นิสิตเขียน SQL ในไฟล์นี้ ★★★
#  มองหาคำว่า  # TODO  ทุกฟังก์ชัน — ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
# ============================================================
import mysql.connector
import config
from datetime import date


def get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD,
        database=config.DB_NAME, port=config.DB_PORT)


def run_query(sql, params=None):
    """รัน SELECT คืนผลเป็น list ของ dict"""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute(sql, params or ()); rows = cur.fetchall()
    cur.close(); conn.close(); return rows


def run_command(sql, params=None):
    """รัน INSERT / UPDATE / DELETE แล้ว commit"""
    conn = get_connection(); cur = conn.cursor()
    cur.execute(sql, params or ()); conn.commit()
    out = {"new_id": cur.lastrowid, "affected": cur.rowcount}
    cur.close(); conn.close(); return out


def blank_to_none(value):
    """ช่องที่ไม่ได้กรอกในฟอร์มจะส่งมาเป็น "" — แปลงเป็น None (= NULL ใน SQL)
    ใช้กับคอลัมน์ที่ว่างได้ เช่น return_date, paid_date  เพราะ MySQL ไม่รับ '' เป็น DATE"""
    return None if value in ("", None) else value


def _todo(name):
    raise NotImplementedError(f"TODO: ยังไม่ได้เขียนฟังก์ชัน {name} ใน db.py")


# ---------- ผู้เรียน (learner) ----------
def search_learners(filters):
    """ค้นหา ผู้เรียน ตามเงื่อนไข (name, email)
    คำใบ้: เริ่มจาก sql = "SELECT * FROM learner WHERE 1=1"
    แล้วต่อเงื่อนไขเฉพาะ filter ที่มีค่า (ข้อความใช้ LIKE %s, อื่น ๆ ใช้ = %s)"""
    sql =(
        """
        select * from learner where 1 = 1
        """
    )
    params = []
    if filters.get("learner_id"):
        sql += " and learner_id like %s"
        params.append("%" + filters["learner_id"] + "%")
    if filters.get("name"):
        sql += " and name like %s"
        params.append("%" + filters["name"] + "%")
    if filters.get("email"):
        sql += " and email like %s"
        params.append("%" + filters["email"] + "%")
    if filters.get("join_date"):
        sql += " and join_date like %s"
        params.append("%" + filters["join_date"] + "%")
    return run_query(sql,params)
    
    # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
    _todo("search_learners")


def get_learner(learner_id):
    """ดึง ผู้เรียน 1 รายการตาม learner_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    sql = ("SELECT * FROM learner WHERE learner_id = %s")
    params = (learner_id,)
    rows = run_query(sql, params)
    return rows[0] if rows else None


def create_learner(data):
    """เพิ่ม ผู้เรียน ใหม่ — data มีคีย์: name, email, join_date"""
    sql = ("INSERT INTO learner (name, email, join_date) VALUES (%s,%s,%s)")
    params = (  data["name"],
                data["email"],
                data["join_date"]     
    )
    return run_command(sql,params)
    
def update_learner(learner_id, data):
    """แก้ไข ผู้เรียน ตาม learner_id"""
    sql = ("UPDATE learner SET name = %s, email = %s, join_date = %s WHERE learner_id=%s")
    params = (
        data["name"],
        data["email"],
        data["join_date"],
        learner_id,
    )
    return run_command(sql,params)
    # TODO: UPDATE learner SET ... WHERE learner_id=%s
    _todo("update_learner")


def delete_learner(learner_id):
    """ลบ ผู้เรียน — ลบไม่ได้ถ้ามีการลงทะเบียนที่กำลังเรียน/เรียนจบแล้ว"""
    if has_blocking_enrollment("learner_id", learner_id):
        raise ValueError("ลบไม่ได้: ผู้เรียนคนนี้มีการลงทะเบียนที่กำลังเรียนหรือเรียนจบแล้ว")
    return run_command("DELETE FROM learner WHERE learner_id=%s", (learner_id,))

# ---------- คอร์ส (course) ----------
def search_courses(filters):
    """ค้นหา คอร์ส ตามเงื่อนไข (title, category)
    ต้องแสดงคอลัมน์: course_id, title, category, price, prerequisite_id, learner_count (จำนวนผู้เรียน)
    คำใบ้:
      - learner_count ไม่ได้เก็บเป็นคอลัมน์ → นับจากตาราง enrollment ตอน SELECT
        วิธีที่ 1: LEFT JOIN enrollment แล้ว GROUP BY คอร์ส + COUNT(e.enroll_id)
                   (ใช้ COUNT(คอลัมน์) ไม่ใช่ COUNT(*) — คอร์สที่ไม่มีผู้เรียนจะได้ 0)
        วิธีที่ 2: subquery ใน SELECT: (SELECT COUNT(*) FROM enrollment e WHERE e.course_id = c.course_id)
      - title/category ใช้ LIKE %s"""
    sql = (
        """
            SELECT c.course_id, 
                c.title, 
                c.category, 
                c.price, 
                c.prerequisite_id,
                COUNT(e.learner_id) AS learner_count
            FROM course c
            LEFT JOIN enrollment e ON c.course_id = e.course_id
            WHERE 1 = 1
        """
      )
    params = []
    if filters.get("title"):
        sql += " AND c.title LIKE %s"
        params.append("%" + filters["title"] + "%")
    if filters.get("category"):
        sql += " AND c.category LIKE %s"
        params.append("%" + filters["category"] + "%")
    sql += """
            GROUP BY c.course_id, c.title, c.category, c.price, c.prerequisite_id
            """
    return run_query(sql, params)
    # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
    _todo("search_courses")


def get_course(course_id):
    """ดึง คอร์ส 1 รายการตาม course_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    # TODO: SELECT * FROM course WHERE course_id = %s แล้วคืนแถวเดียว
    sql =("select * from course where course_id =%s")
    params = (course_id,)
    
    rows = run_query(sql, params)
    return rows[0] if rows else None


def create_course(data):
    """เพิ่ม คอร์ส ใหม่ — data มีคีย์: title, category, price, prerequisite_id"""
    # TODO: INSERT INTO course (...) VALUES (%s, ...)
    if float(data.get("price", 0)) < 0:
        raise ValueError("ราคาไม่สามารถติดลบได้")

    sql = ("INSERT INTO course (title, category, price, prerequisite_id) VALUES (%s, %s, %s, %s)")
    params = (data.get("title"),
              data.get("category"),
              data.get("price"),
              blank_to_none(data.get("prerequisite_id"))
    )
    return run_command(sql , params)
    


def update_course(course_id, data):
    """แก้ไข คอร์ส ตาม course_id"""
    # TODO: UPDATE course SET ... WHERE course_id=%s
    sql =("UPDATE course SET title = %s, category = %s, price = %s, prerequisite_id = %s WHERE course_id=%s")
    params = (
        data["title"],
        data["category"],
        data["price"],
        blank_to_none(data["prerequisite_id"]),
        course_id,
    )
    return run_command(sql, params)


def delete_course(course_id):
    """ลบ คอร์ส — ลบไม่ได้ถ้ามีการลงทะเบียนที่กำลังเรียน/เรียนจบแล้ว"""
    if has_blocking_enrollment("course_id", course_id):
        raise ValueError("ลบไม่ได้: คอร์สนี้มีการลงทะเบียนที่กำลังเรียนหรือเรียนจบแล้ว")
    return run_command("DELETE FROM course WHERE course_id=%s", (course_id,))

# ---------- การลงทะเบียน (enrollment) ----------
def search_enrollments(filters):
    """ค้นหา การลงทะเบียน — JOIN แสดงชื่อผู้เรียน + ชื่อคอร์ส (แทนโชว์แต่เลข id)"""
    sql = """
        SELECT e.enroll_id,
               e.learner_id,
               l.name  AS learner_name,
               e.course_id,
               c.title AS course_title,
               e.enroll_date,
               e.status,
               e.completed_date,
               CASE
                   WHEN e.status = 'completed' THEN CONCAT(DATEDIFF(e.completed_date, e.enroll_date), ' วัน')
                   WHEN e.status = 'cancelled' THEN 'ยกเลิกแล้ว'
                   ELSE 'ยังเรียนไม่เสร็จ'
               END AS 'ระยะเวลาเรียน'
        FROM enrollment e
        JOIN learner l ON l.learner_id = e.learner_id
        JOIN course  c ON c.course_id  = e.course_id
        WHERE 1 = 1
    """
    params = []
    if filters.get("learner_id"):
        sql += " AND e.learner_id = %s"
        params.append(filters["learner_id"])
    if filters.get("course_id"):
        sql += " AND e.course_id = %s"
        params.append(filters["course_id"])
    if filters.get("status"):
        sql += " AND e.status = %s"
        params.append(filters["status"])

    return run_query(sql, params)


def get_enrollment(enroll_id):
    """ดึง การลงทะเบียน 1 รายการตาม enroll_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    # TODO: SELECT * FROM enrollment WHERE enroll_id = %s แล้วคืนแถวเดียว
    sql = ("SELECT * FROM enrollment WHERE enroll_id = %s")
    params = (
        enroll_id,
    )
    rows = run_query(sql, params)
    return rows[0] if rows else None

def check_can_enroll(learner_id, course_id, enroll_id=None):
    """ตรวจก่อนบันทึกการลงทะเบียน — ถ้าไม่ผ่านให้ raise ValueError("ข้อความ")
    (หน้าเว็บจะแสดงข้อความนั้นเป็น alert ให้ผู้ใช้เห็น และไม่บันทึกข้อมูล)
    1) ห้ามลงทะเบียนซ้ำ: ผู้เรียนคนเดิม + คอร์สเดิม มีอยู่แล้ว
       → SELECT COUNT(*) AS n FROM enrollment
         WHERE learner_id = %s AND course_id = %s AND enroll_id <> %s
       ★ ตอนเพิ่มใหม่ enroll_id เป็น None → ส่ง 0 แทน (enroll_id or 0)
    2) ถ้าคอร์สมีวิชาที่ต้องเรียนก่อน (prerequisite_id ไม่เป็น NULL)
       → ผู้เรียนต้องมี enrollment ของวิชานั้นที่ status = 'completed' แล้ว
         (หา prerequisite_id จากตาราง course ก่อน แล้วตรวจด้วย EXISTS หรือ COUNT)
    ตัวอย่าง: raise ValueError("ต้องเรียนวิชาที่ต้องเรียนก่อนให้จบก่อน")"""
    eid = enroll_id or 0
    dup = run_query(
        "SELECT COUNT(*) AS n FROM enrollment WHERE learner_id = %s AND course_id = %s AND enroll_id <> %s",
        (learner_id, course_id, eid))
    if dup and dup[0]["n"] > 0:
        raise ValueError("ผู้เรียนคนนี้ลงทะเบียนคอร์สนี้แล้ว")

    pre = run_query("SELECT prerequisite_id FROM course WHERE course_id = %s", (course_id,))
    prereq = pre[0]["prerequisite_id"] if pre else None
    if prereq is not None:
        done = run_query(
            "SELECT COUNT(*) AS n FROM enrollment WHERE learner_id = %s AND course_id = %s AND status = 'completed'",
            (learner_id, prereq))
        if not done or done[0]["n"] == 0:
            raise ValueError("ต้องเรียนวิชาที่ต้องเรียนก่อนให้จบก่อน")
    
def check_course_complete(learner_id, course_id):
    """ตรวจว่าผู้เรียนดูครบทุกบทของคอร์สแล้วหรือยัง — ยังไม่ครบจะ raise ValueError
    (ใช้ก่อนเปลี่ยนสถานะ enrollment เป็น 'completed' เพื่อกันเรียนจบทั้งที่ดูไม่ครบ)"""
    
    total = run_query("SELECT COUNT(*) AS n FROM lesson WHERE course_id = %s", (course_id,))
    done = run_query(
        "SELECT COUNT(*) AS n FROM progress p "
        "JOIN lesson l ON p.lesson_id = l.lesson_id "
        "WHERE p.learner_id = %s AND l.course_id = %s AND p.watched = TRUE",
        (learner_id, course_id))
    
    if not done or not total or done[0]["n"] < total[0]["n"]:
        n_done = done[0]["n"] if done else 0
        n_total = total[0]["n"] if total else 0
        raise ValueError(f"ยังดูบทเรียนไม่ครบ (ดูแล้ว {n_done}/{n_total} บท) จึงยังไม่สามารถเรียนจบคอร์สนี้ได้")
    
def validate_enrollment_input(enroll_date, status, completed_date):
    if blank_to_none(enroll_date) is None:
        raise ValueError("กรุณากรอกวันที่ลงทะเบียน")
    if status == "completed" and completed_date and str(enroll_date) > str(completed_date):
        raise ValueError("วันที่ลงทะเบียนต้องไม่หลังวันที่เรียนจบ")
    
def create_enrollment(data):
    """เพิ่ม การลงทะเบียน ใหม่ — data มีคีย์: learner_id, course_id, enroll_date, status"""
    check_can_enroll(data["learner_id"], data["course_id"])
   
    
    status = data.get("status") or "studying"
    completed_date = date.today().isoformat() if status == "completed" else None
    if status == "completed":
        check_course_complete(data["learner_id"], data["course_id"])
    validate_enrollment_input(data["enroll_date"], status, completed_date)
    sql = "INSERT INTO enrollment (learner_id, course_id, enroll_date, status, completed_date) VALUES (%s, %s, %s, %s, %s)"
    params = (data["learner_id"], data["course_id"], data["enroll_date"], status, completed_date)
    return run_command(sql, params)


def update_enrollment(enroll_id, data):
    """แก้ไข การลงทะเบียน ตาม enroll_id — การลงทะเบียนที่เรียนจบแล้วเปลี่ยนสถานะกลับไม่ได้"""
    
    old = get_enrollment(enroll_id)
    if not old:
        raise ValueError("ไม่พบข้อมูลการลงทะเบียน")

    
    if str(data.get("learner_id")) != str(old["learner_id"]) or str(data.get("course_id")) != str(old["course_id"]):
        check_can_enroll(data["learner_id"], data["course_id"], enroll_id)

    new_status = data.get("status") or "studying"
    if old["status"] == "completed" and new_status != "completed":
        raise ValueError("แก้ไม่ได้: การลงทะเบียนที่เรียนจบแล้วเปลี่ยนสถานะกลับไม่ได้")

    if new_status == "completed":
        if old["status"] == "completed":
            completed_date = old.get("completed_date")
        else:
            completed_date = date.today().isoformat()
    else:
        completed_date = None

    validate_enrollment_input(data["enroll_date"], new_status, completed_date)

    if new_status == "completed" and old["status"] != "completed":
        check_course_complete(data["learner_id"], data["course_id"])
        exist = run_query(
            "SELECT COUNT(*) AS n FROM certificate WHERE learner_id = %s AND course_id = %s",
            (data["learner_id"], data["course_id"]))
        if exist and exist[0]["n"] > 0:
            raise ValueError("ผู้เรียนมีใบรับรองของคอร์สนี้แล้ว")
        run_command(
            "INSERT INTO certificate (learner_id, course_id) VALUES (%s, %s)",
            (data["learner_id"], data["course_id"]))

    sql = "UPDATE enrollment SET learner_id = %s, course_id = %s, enroll_date = %s, status = %s, completed_date = %s WHERE enroll_id = %s"
    params = (data["learner_id"], data["course_id"], data["enroll_date"], new_status, completed_date, enroll_id)
    return run_command(sql, params)

def has_blocking_enrollment(column, _id):
    """คอลัมน์ที่อนุญาตมีแค่ learner_id / course_id (เป็นค่าคงที่ในโค้ด ไม่ใช่ input)"""
    if column not in ("learner_id", "course_id"):
        raise ValueError("คอลัมน์ไม่ถูกต้อง")
    rows = run_query(
        "SELECT COUNT(*) AS n FROM enrollment "
        f"WHERE {column} = %s AND status IN ('studying', 'completed')",
        (_id,))
    return bool(rows and rows[0]["n"])

def delete_enrollment(enroll_id):
    """ลบ การลงทะเบียน ตาม enroll_id — ลบได้เฉพาะสถานะ 'cancelled'
    ถ้ายัง 'studying' หรือ 'completed' อยู่ จะ raise ValueError ให้หน้าเว็บเตือน
    (หน้าเว็บแสดงข้อความนี้เป็น alert และไม่ลบข้อมูล)"""
    row = get_enrollment(enroll_id)
    if not row:
        raise ValueError("ไม่พบข้อมูลการลงทะเบียน")
    if row["status"] != "cancelled":
        raise ValueError("ลบไม่ได้: การลงทะเบียนที่กำลังเรียนอยู่หรือเรียนจบแล้วต้องยกเลิก (cancelled) ก่อน")

    sql = "DELETE FROM enrollment WHERE enroll_id = %s"
    return run_command(sql, (enroll_id,))

# ---------- certificate ----------
def search_certificate(filters):
    """ค้นหาใบรับรอง  แสดงชื่อผู้เรียน ชื่อคอร์ส ไม่เก็บชื่อซ้ำในตาราง"""
    sql = """
        SELECT ce.cer_id,
               ce.learner_id,
               l.name           AS learner_name,
               ce.course_id,
               c.title       AS course_title,
               ce.issue_date
        FROM certificate ce
        JOIN learner l ON l.learner_id = ce.learner_id
        JOIN course  c ON c.course_id  = ce.course_id
        WHERE 1 = 1
    """
    params = []
    if filters.get("learner_id"):
        sql += " AND ce.learner_id = %s"
        params.append(filters["learner_id"])
    if filters.get("name"):
            sql += " AND l.name LIKE %s"
            params.append("%"+filters["name"]+"%")
    if filters.get("category"):
        sql += " AND c.category LIKE %s"
        params.append("%" + filters["category"] + "%")
    
    return run_query(sql, params)


def get_certificate(cer_id):
    """ดึงใบรับรอง 1 รายการตาม cer_id """
    sql = "SELECT * FROM certificate WHERE cer_id = %s"
    rows = run_query(sql, (cer_id,))
    return rows[0] if rows else None


def create_certificate(data):
    """ออกใบรับรองใหม่ — ต้องเรียนคอร์สนั้นจบแล้วเท่านั้น"""
    done = run_query(
        "SELECT COUNT(*) AS n FROM enrollment WHERE learner_id = %s AND course_id = %s AND status = 'completed'",
        (data["learner_id"], data["course_id"]))
    if not done or done[0]["n"] == 0:
        raise ValueError("ผู้เรียนยังเรียนคอร์สนี้ไม่จบ จึงออกใบรับรองไม่ได้")

    exist = run_query(
        "SELECT COUNT(*) AS n FROM certificate WHERE learner_id = %s AND course_id = %s",
        (data["learner_id"], data["course_id"]))
    if exist and exist[0]["n"] > 0:
        raise ValueError("ผู้เรียนคนนี้มีใบรับรองของคอร์สนี้แล้ว")

    issue_date = data.get("issue_date")
    if issue_date in ("", None):
        sql = "INSERT INTO certificate (learner_id, course_id) VALUES (%s, %s)"
        params = (data["learner_id"], data["course_id"])
    else:
        sql = "INSERT INTO certificate (learner_id, course_id, issue_date) VALUES (%s, %s, %s)"
        params = (data["learner_id"], data["course_id"], issue_date)
    return run_command(sql, params)


def update_certificate(cer_id, data):
    """แก้ไขใบรับรองตาม cer_id"""
    sql = "UPDATE certificate SET learner_id = %s, course_id = %s, issue_date = %s WHERE cer_id = %s"
    params = (data["learner_id"], data["course_id"], data["issue_date"], cer_id)
    return run_command(sql, params)


def delete_certificate(cer_id):
    """ลบใบรับรองตาม cer_id"""
    sql = "DELETE FROM certificate WHERE cer_id = %s"
    return run_command(sql, (cer_id,))


# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
#  ★ ชื่อคอลัมน์ใน SELECT จะกลายเป็นหัวตารางบนเว็บ — ใช้ AS 'ชื่อภาษาไทย' ได้
# ============================================================
def report_summary():
    sql = """
        SELECT
            (SELECT COUNT(*) FROM learner)     AS 'ผู้เรียน',
            (SELECT COUNT(*) FROM course)      AS 'คอร์ส',
            (SELECT COUNT(*) FROM enrollment)  AS 'การลงทะเบียน',
            (SELECT COUNT(*) FROM lesson)      AS 'บทเรียน',
            (SELECT COUNT(*) FROM certificate) AS 'ใบรับรองที่ออกแล้ว',
            IFNULL((SELECT SUM(c.price)
                    FROM enrollment e
                    INNER JOIN course c ON c.course_id = e.course_id
                    WHERE e.status = 'completed'), 0) AS 'รายได้รวม (บาท)'
    """
    return run_query(sql)[0]

def report_popular_courses():
    sql = """
        SELECT c.course_id AS 'รหัสคอร์ส',
               c.title     AS 'ชื่อคอร์ส',
               c.category  AS 'หมวดหมู่',
               COUNT(e.enroll_id) AS 'จำนวนผู้ลงทะเบียน'
        FROM course c
        INNER JOIN enrollment e ON e.course_id = c.course_id
        GROUP BY c.course_id, c.title, c.category
        ORDER BY COUNT(e.enroll_id) DESC, c.title ASC
        LIMIT 5
    """
    return run_query(sql)


def report_completion_rate():
    sql = """
        SELECT c.course_id AS 'รหัสคอร์ส',
               c.title     AS 'ชื่อคอร์ส',
               COUNT(e.enroll_id) AS 'ผู้ลงทะเบียนทั้งหมด',
               SUM(CASE WHEN e.status = 'completed' THEN 1 ELSE 0 END) AS 'เรียนจบ',
               ROUND(100 * SUM(CASE WHEN e.status = 'completed' THEN 1 ELSE 0 END)
                     / NULLIF(COUNT(e.enroll_id), 0), 1) AS 'อัตราการเรียนจบ (%)'
        FROM course c
        LEFT JOIN enrollment e ON e.course_id = c.course_id
        GROUP BY c.course_id, c.title
        ORDER BY c.course_id
    """
    return run_query(sql)


def report_course_prerequisites():
    sql = """
        SELECT c.course_id AS 'รหัสคอร์ส',
               c.title     AS 'ชื่อคอร์ส',
               c.category  AS 'หมวดหมู่',
               COALESCE(pre.title, 'ไม่มี') AS 'วิชาที่ต้องเรียนก่อน'
        FROM course c
        LEFT JOIN course pre ON pre.course_id = c.prerequisite_id
        ORDER BY c.course_id
    """
    return run_query(sql)


def report_learner_progress():
    sql = """
        SELECT l.learner_id AS 'รหัสผู้เรียน',
               l.name       AS 'ชื่อผู้เรียน',
               COUNT(e.enroll_id) AS 'ลงทะเบียน (คอร์ส)',
               SUM(CASE WHEN e.status = 'completed' THEN 1 ELSE 0 END) AS 'เรียนจบ',
               SUM(CASE WHEN e.status = 'studying'  THEN 1 ELSE 0 END) AS 'กำลังเรียน',
               (SELECT COUNT(*) FROM certificate ce
                WHERE ce.learner_id = l.learner_id) AS 'ใบรับรอง'
        FROM learner l
        LEFT JOIN enrollment e ON e.learner_id = l.learner_id
        GROUP BY l.learner_id, l.name
        ORDER BY l.learner_id
    """
    return run_query(sql)


def report_revenue_by_category():
    sql = """
        SELECT c.category AS 'หมวดหมู่',
               COUNT(DISTINCT c.course_id) AS 'จำนวนคอร์ส',
               COUNT(CASE WHEN e.status = 'completed' THEN 1 END) AS 'ลงทะเบียนที่เรียนจบ',
               IFNULL(SUM(CASE WHEN e.status = 'completed' THEN c.price END), 0) AS 'รายได้ (บาท)'
        FROM course c
        LEFT JOIN enrollment e ON e.course_id = c.course_id
        GROUP BY c.category
        ORDER BY IFNULL(SUM(CASE WHEN e.status = 'completed' THEN c.price END), 0) DESC,
                 c.category ASC
    """
    return run_query(sql)


def report_learners_without_enrollment():
    sql = """
        SELECT l.learner_id AS 'รหัสผู้เรียน',
               l.name       AS 'ชื่อผู้เรียน',
               l.email      AS 'อีเมล',
               l.join_date  AS 'วันที่สมัคร'
        FROM learner 
        WHERE NOT EXISTS (SELECT 1 FROM enrollment e WHERE e.learner_id = l.learner_id)
        ORDER BY l.learner_id
    """
    return run_query(sql)


def report_pending_lessons():
    sql = """
        SELECT l.name        AS 'ชื่อผู้เรียน',
               c.title       AS 'คอร์ส',
               le.sec_no     AS 'บทที่',
               le.title      AS 'บทเรียนที่ยังไม่ดู',
               le.duration_min AS 'ความยาว (นาที)'
        FROM enrollment e
        INNER JOIN learner l  ON l.learner_id  = e.learner_id
        INNER JOIN course  c  ON c.course_id   = e.course_id
        INNER JOIN lesson  le ON le.course_id  = e.course_id
        LEFT JOIN progress p  ON p.learner_id  = e.learner_id
                             AND p.lesson_id   = le.lesson_id
                             AND p.watched      = TRUE
        WHERE e.status = 'studying' AND p.lesson_id IS NULL
        ORDER BY l.name, c.title, le.sec_no
    """
    return run_query(sql)


def _learner_name(learner_id):
    rows = run_query("SELECT name FROM learner WHERE learner_id = %s", (learner_id,))
    return rows[0]["name"] if rows else None


def _course_title(course_id):
    rows = run_query("SELECT title FROM course WHERE course_id = %s", (course_id,))
    return rows[0]["title"] if rows else None


def _count(sql, params=()):
    rows = run_query(sql, params)
    return rows[0]["n"] if rows else 0


def _result(action, allowed, message, steps=None, warnings=None):
    return {
        "action": action,
        "allowed": allowed,
        "message": message,
        "steps": steps or [],
        "warnings": warnings or [],
    }


def simulate(action, params):
    p = params or {}

    def to_int(key):
        try:
            return int(p.get(key))
        except (TypeError, ValueError):
            return None

    if action == "enroll":
        learner_id, course_id = to_int("learner_id"), to_int("course_id")
        if learner_id is None or course_id is None:
            return _result(action, False, "กรุณาเลือกผู้เรียนและคอร์สให้ครบ")
        learner, course = _learner_name(learner_id), _course_title(course_id)
        if learner is None:
            return _result(action, False, f"ไม่พบผู้เรียนรหัส {learner_id}")
        if course is None:
            return _result(action, False, f"ไม่พบคอร์สรหัส {course_id}")
        try:
            check_can_enroll(learner_id, course_id)
        except ValueError as e:
            return _result(action, False, str(e), ["ระบบจะไม่บันทึกข้อมูลใด ๆ"])
        warnings = []
        pre = run_query("SELECT prerequisite_id FROM course WHERE course_id = %s", (course_id,))
        if pre and pre[0]["prerequisite_id"]:
            warnings.append("คอร์สนี้บังคับวิชาก่อน '" + _course_title(pre[0]["prerequisite_id"]) +
                            "' — ตรวจแล้วว่าผู้เรียนผ่านมาแล้ว")
        total = _count("SELECT COUNT(*) AS n FROM enrollment WHERE course_id = %s", (course_id,))
        return _result(action, True, f"ลงทะเบียนได้: {learner} → {course}",
                       ["เพิ่มแถวในตาราง enrollment 1 แถว (status = 'studying', completed_date = NULL)",
                        f"learner_count ของ '{course}' เพิ่มจาก {total} เป็น {total + 1}"],
                       warnings)

    if action == "complete":
        learner_id, course_id = to_int("learner_id"), to_int("course_id")
        if learner_id is None or course_id is None:
            return _result(action, False, "กรุณาเลือกผู้เรียนและคอร์สให้ครบ")
        learner, course = _learner_name(learner_id), _course_title(course_id)
        if learner is None or course is None:
            return _result(action, False, "ไม่พบผู้เรียนหรือคอร์สที่เลือก")
        rows = run_query(
            "SELECT status FROM enrollment WHERE learner_id = %s AND course_id = %s "
            "ORDER BY enroll_id DESC LIMIT 1", (learner_id, course_id))
        if not rows:
            return _result(action, False, f"{learner} ยังไม่ลงทะเบียนคอร์ส '{course}'")
        if rows[0]["status"] == "completed":
            return _result(action, False, f"{learner} เรียนจบ '{course}' ไปแล้ว")
        try:
            check_course_complete(learner_id, course_id)
        except ValueError as e:
            return _result(action, False, str(e), ["สถานะยังคงเป็น 'studying'"])
        cert = _count("SELECT COUNT(*) AS n FROM certificate WHERE learner_id = %s AND course_id = %s",
                      (learner_id, course_id))
        if cert:
            return _result(action, False, "ผู้เรียนมีใบรับรองของคอร์สนี้แล้ว ระบบจึงไม่ยอมเปลี่ยนสถานะ")
        return _result(action, True, f"เปลี่ยนเป็นเรียนจบได้: {learner} → {course}",
                       ["enrollment.status → 'completed'",
                        "enrollment.completed_date → วันที่ปัจจุบัน",
                        "ออกใบรับรอง (certificate) ให้อัตโนมัติ 1 ใบ"])

    if action == "delete_learner":
        learner_id = to_int("learner_id")
        learner = _learner_name(learner_id) if learner_id is not None else None
        if learner is None:
            return _result(action, False, "ไม่พบผู้เรียนที่เลือก")
        blocked = _count("SELECT COUNT(*) AS n FROM enrollment WHERE learner_id = %s "
                         "AND status IN ('studying','completed')", (learner_id,))
        if blocked:
            return _result(action, False,
                           f"ลบไม่ได้: {learner} มีการลงทะเบียนที่กำลังเรียน/เรียนจบอยู่ {blocked} รายการ",
                           ["ต้องยกเลิก (cancelled) การลงทะเบียนเหล่านั้นก่อนจึงจะลบได้"])
        enrolls = _count("SELECT COUNT(*) AS n FROM enrollment WHERE learner_id = %s", (learner_id,))
        progress = _count("SELECT COUNT(*) AS n FROM progress WHERE learner_id = %s", (learner_id,))
        cert = _count("SELECT COUNT(*) AS n FROM certificate WHERE learner_id = %s", (learner_id,))
        warnings = []
        if enrolls or progress or cert:
            warnings.append("ข้อมูลของผู้เรียนคนนี้จะหายถาวร กู้คืนไม่ได้")
        return _result(action, True, f"ลบผู้เรียน '{learner}' ได้",
                       ["ลบผู้เรียน 1 แถว",
                        f"ลบการลงทะเบียนที่เหลือ (cancelled) {enrolls} แถว (ON DELETE CASCADE)",
                        f"ลบความคืบหน้าการดูบทเรียน {progress} แถว (ON DELETE CASCADE)",
                        f"ลบใบรับรอง {cert} ใบ (ON DELETE CASCADE)"],
                       warnings)

    if action == "delete_course":
        course_id = to_int("course_id")
        course = _course_title(course_id) if course_id is not None else None
        if course is None:
            return _result(action, False, "ไม่พบคอร์สที่เลือก")
        blocked = _count("SELECT COUNT(*) AS n FROM enrollment WHERE course_id = %s "
                         "AND status IN ('studying','completed')", (course_id,))
        if blocked:
            return _result(action, False,
                           f"ลบไม่ได้: คอร์ส '{course}' มีผู้ลงทะเบียนที่กำลังเรียน/เรียนจบอยู่ {blocked} รายการ")
        lessons = _count("SELECT COUNT(*) AS n FROM lesson WHERE course_id = %s", (course_id,))
        enrolls = _count("SELECT COUNT(*) AS n FROM enrollment WHERE course_id = %s", (course_id,))
        deps = run_query("SELECT title FROM course WHERE prerequisite_id = %s", (course_id,))
        warnings = []
        if deps:
            warnings.append("คอร์สที่ต้องเรียนก่อนหน้านี้: " +
                            ", ".join(d["title"] for d in deps) +
                            " → prerequisite_id จะถูกตั้งเป็น NULL")
        return _result(action, True, f"ลบคอร์ส '{course}' ได้",
                       ["ลบคอร์ส 1 แถว",
                        f"ลบบทเรียนทั้งหมด {lessons} บท (ON DELETE CASCADE)",
                        f"ลบการลงทะเบียนที่เหลือ {enrolls} แถว (ON DELETE CASCADE)",
                        "ความคืบหน้าของบทเรียนเหล่านั้นถูกลบตามไปด้วย"],
                       warnings)

    if action == "delete_enrollment":
        enroll_id = to_int("enroll_id")
        row = get_enrollment(enroll_id) if enroll_id is not None else None
        if not row:
            return _result(action, False, "ไม่พบการลงทะเบียนที่เลือก")
        if row["status"] != "cancelled":
            return _result(action, False,
                           f"ลบไม่ได้: สถานะเป็น {row['status']} ต้องยกเลิกก่อน",
                           ["ใช้การกระทำ 'ยกเลิกการลงทะเบียน' ก่อน แล้วจึงลบ"])
        return _result(action, True, f"ลบการลงทะเบียน #{enroll_id} ได้",
                       ["ลบแถวในตาราง enrollment 1 แถว"])

    if action == "cancel_enrollment":
        enroll_id = to_int("enroll_id")
        row = get_enrollment(enroll_id) if enroll_id is not None else None
        if not row:
            return _result(action, False, "ไม่พบการลงทะเบียนที่เลือก")
        if row["status"] == "completed":
            return _result(action, False, "ยกเลิกไม่ได้: เรียนจบแล้วเปลี่ยนสถานะกลับไม่ได้")
        if row["status"] == "cancelled":
            return _result(action, False, "การลงทะเบียนนี้ถูกยกเลิกอยู่แล้ว")
        return _result(action, True, f"ยกเลิกการลงทะเบียน #{enroll_id} ได้",
                       ["enrollment.status → 'cancelled'",
                        "enrollment.completed_date → NULL"],
                       ["ความคืบหน้าการดูบทเรียนยังอยู่ แต่ไม่ถูกนับรวมกับคอร์สนี้",
                        "ถ้าคอร์สนี้ถูกใช้เป็น prerequisite ผู้เรียนจะยังไม่ถือว่าผ่าน"])

    if action == "set_prerequisite":
        course_id, prereq_id = to_int("course_id"), to_int("prerequisite_id")
        course = _course_title(course_id) if course_id is not None else None
        if course is None:
            return _result(action, False, "ไม่พบคอร์สที่เลือก")
        if prereq_id in (None, 0):
            return _result(action, True, f"เอาวิชาที่ต้องเรียนก่อนของ '{course}' ออก",
                           ["course.prerequisite_id → NULL"])
        if prereq_id == course_id:
            return _result(action, False, "คอร์สอ้างตัวเองเป็นวิชาที่ต้องเรียนก่อนไม่ได้")
        prereq = _course_title(prereq_id)
        if prereq is None:
            return _result(action, False, "ไม่พบวิชาที่ต้องเรียนก่อนที่เลือก")
        seen, cur = set(), prereq_id
        while cur:
            if cur == course_id:
                return _result(action, False,
                               f"ตั้งไม่ได้: จะเกิดวงกลม prerequisite ระหว่าง '{course}' กับ '{prereq}'")
            if cur in seen:
                break
            seen.add(cur)
            nxt = run_query("SELECT prerequisite_id FROM course WHERE course_id = %s", (cur,))
            cur = nxt[0]["prerequisite_id"] if nxt else None
        affected = run_query(
            "SELECT l.name FROM enrollment e "
            "INNER JOIN learner l ON l.learner_id = e.learner_id "
            "WHERE e.course_id = %s AND e.status IN ('studying','completed') "
            "AND NOT EXISTS (SELECT 1 FROM enrollment pe WHERE pe.learner_id = e.learner_id "
            "AND pe.course_id = %s AND pe.status = 'completed')", (course_id, prereq_id))
        warnings = []
        if affected:
            warnings.append("ผู้เรียนที่ลงทะเบียนคอร์สนี้แล้วแต่ยังไม่ผ่านวิชาก่อน: " +
                            ", ".join(a["name"] for a in affected))
        warnings.append(f"ผู้เรียนใหม่จะลงทะเบียน '{course}' ไม่ได้จนกว่าจะเรียน '{prereq}' จบก่อน")
        return _result(action, True, f"ตั้ง '{course}' ให้ต้องเรียน '{prereq}' ก่อน",
                       [f"course.prerequisite_id → {prereq_id}"], warnings)

    return _result(action, False, f"ไม่รู้จักการกระทำ '{action}'")

# ============================================================
#  รายการรายงานที่แสดงบนหน้า /report  (เรียงตามลำดับที่แสดง)
#  ★ วิธีเพิ่มรายงานใหม่ (ไม่ต้องแก้ไฟล์อื่น):
#    1) เขียนฟังก์ชัน report_xxx() ด้านบน ให้ return run_query(sql)
#    2) เพิ่ม 1 บรรทัดในรายการนี้:  ("ชื่อใน-url", "หัวข้อที่แสดง", ชื่อฟังก์ชัน)
#  ★ รายการนี้ต้องอยู่ท้ายไฟล์ (หลังฟังก์ชันทั้งหมด) ไม่งั้น Python หาชื่อฟังก์ชันไม่เจอ
#  ★ ห้ามตั้งชื่อ url ว่า "summary" (ใช้แล้วสำหรับการ์ดสรุป)
# ============================================================
REPORTS = [
    ("popular-courses",     "คอร์สยอดนิยม (Most Enrolled)",              report_popular_courses),
    ("completion-rate",     "อัตราการเรียนจบต่อคอร์ส (Completion Rate)", report_completion_rate),
    ("prerequisites",       "คอร์สและวิชาที่ต้องเรียนก่อน (Self-Join)",  report_course_prerequisites),
    ("learner-progress",    "ความคืบหน้าของผู้เรียนแต่ละคน",              report_learner_progress),
    ("revenue-by-category", "รายได้ตามหมวดหมู่คอร์ส",                    report_revenue_by_category),
    ("no-enrollment",       "ผู้เรียนที่ยังไม่ลงทะเบียนคอร์สใดเลย",        report_learners_without_enrollment),
    ("pending-lessons",     "บทเรียนที่ยังดูไม่ครบ (เฉพาะกำลังเรียน)",     report_pending_lessons),
]
