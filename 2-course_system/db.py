# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล  ★★★ นิสิตเขียน SQL ในไฟล์นี้ ★★★
#  มองหาคำว่า  # TODO  ทุกฟังก์ชัน — ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
# ============================================================
import mysql.connector
import config


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
    return run_query(sql,params)
    # TODO: SELECT * FROM learner WHERE learner_id = %s แล้วคืนแถวเดียว
    _todo("get_learner")


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
    """ลบ ผู้เรียน ตาม learner_id"""
    sql = ("DELETE FROM learner WHERE learner_id=%s")
    params = (learner_id,)
    return run_command(sql,params)
    # TODO: DELETE FROM learner WHERE learner_id=%s
    _todo("delete_learner")

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
    return run_query(sql,params)
    _todo("get_course")


def create_course(data):
    """เพิ่ม คอร์ส ใหม่ — data มีคีย์: title, category, price, prerequisite_id"""
    # TODO: INSERT INTO course (...) VALUES (%s, ...)
    sql = ("INSERT INTO course (title, category, price, prerequisite_id) VALUES (%s, %s, %s, %s)")
    params = (data.get("title"),
              data.get("category"),
              data.get("price"),
              data.get("prerequisite_id")
              )
    return run_command(sql,params) 
    _todo("create_course")


def update_course(course_id, data):
    """แก้ไข คอร์ส ตาม course_id"""
    # TODO: UPDATE course SET ... WHERE course_id=%s
    sql =("UPDATE course SET title = %s, category = %s, price = %s, prerequisite_id = %s WHERE course_id=%s")
    params = (
        data["title"],
        data["category"],
        data["price"],
        data["prerequisite_id"],
        course_id,
    )
    return run_command(sql,params)
    _todo("update_course")


def delete_course(course_id):
    """ลบ คอร์ส ตาม course_id"""
    sql = ("DELETE FROM course WHERE course_id=%s")
    params = (course_id,)
    return run_command(sql,params)
    # TODO: DELETE FROM course WHERE course_id=%s
    _todo("delete_course")

# ---------- การลงทะเบียน (enrollment) ----------
def search_enrollments(filters):
    """ค้นหา การลงทะเบียน ตามเงื่อนไข (learner_id, course_id, status)
    คำใบ้: เริ่มจาก sql = "SELECT * FROM enrollment WHERE 1=1"
    แล้วต่อเงื่อนไขเฉพาะ filter ที่มีค่า (ข้อความใช้ LIKE %s, อื่น ๆ ใช้ = %s)"""
    sql = "SELECT * FROM enrollment WHERE 1 = 1"
    params = []
    if filters.get("learner_id"):
        sql += " AND learner_id = %s"
        params.append(filters["learner_id"])
    if filters.get("course_id"):
        sql += " AND course_id = %s"
        params.append(filters["course_id"])
    if filters.get("status"):
        sql += " AND status = %s"
        params.append(filters["status"])

    return run_query(sql,params)
    # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
    _todo("search_enrollments")


def get_enrollment(enroll_id):
    """ดึง การลงทะเบียน 1 รายการตาม enroll_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    # TODO: SELECT * FROM enrollment WHERE enroll_id = %s แล้วคืนแถวเดียว
    sql = ("SELECT * FROM enrollment WHERE enroll_id = %s")
    params = (
        enroll_id,
    )
    return run_query(sql , params)
    _todo("get_enrollment")


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

def create_enrollment(data):
    """เพิ่ม การลงทะเบียน ใหม่ — data มีคีย์: learner_id, course_id, enroll_date, status
    คำใบ้:
      1) เรียก check_can_enroll(data["learner_id"], data["course_id"]) ก่อน
      2) INSERT INTO enrollment (...) VALUES (%s, ...)"""
    check_can_enroll(data["learner_id"], data["course_id"])
    sql = "INSERT INTO enrollment (learner_id, course_id, enroll_date, status) VALUES (%s, %s, %s, %s)"
    params = (data["learner_id"], data["course_id"], data["enroll_date"], data.get("status") or "studying")
    return run_command(sql, params)


def update_enrollment(enroll_id, data):
    """แก้ไข การลงทะเบียน ตาม enroll_id
    คำใบ้:
      1) ถ้าเปลี่ยนผู้เรียนหรือคอร์ส (เทียบกับค่าเดิมจาก get_enrollment) →
         check_can_enroll(data["learner_id"], data["course_id"], enroll_id)
         (แก้แค่สถานะ เช่น studying → completed ไม่ต้องตรวจ)
      2) UPDATE enrollment SET ... WHERE enroll_id=%s"""
    old = get_enrollment(enroll_id)
    if not old:
        raise ValueError("ไม่พบข้อมูลการลงทะเบียน")
    old = old[0]
    if str(data.get("learner_id")) != str(old["learner_id"]) or str(data.get("course_id")) != str(old["course_id"]):
        check_can_enroll(data["learner_id"], data["course_id"], enroll_id)
    sql = "UPDATE enrollment SET learner_id = %s, course_id = %s, enroll_date = %s, status = %s WHERE enroll_id = %s"
    params = (data["learner_id"], data["course_id"], data["enroll_date"], data.get("status") or "studying", enroll_id)
    return run_command(sql, params)


def delete_enrollment(enroll_id):
    """ลบ การลงทะเบียน ตาม enroll_id"""
    sql = "DELETE FROM enrollment WHERE enroll_id = %s"
    return run_command(sql, (enroll_id,))


# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
#  ★ ชื่อคอลัมน์ใน SELECT จะกลายเป็นหัวตารางบนเว็บ — ใช้ AS 'ชื่อภาษาไทย' ได้
# ============================================================
def report_summary():
    """ตัวเลขสรุปบนการ์ด dashboard — คืน dict {ชื่อการ์ด: ตัวเลข}  (1 คีย์ = 1 การ์ด)
    ตอนนี้ยังไม่ได้เขียน SQL → คืนค่า None ทุกการ์ด หน้าเว็บจึงแสดง "—" รอไว้
    ★ งานของนิสิต: เขียน SQL ตามตัวอย่างด้านล่าง (1 คอลัมน์ใน SELECT = 1 การ์ด
      ชื่อหลัง AS = ข้อความใต้ตัวเลข) แล้วลบ return {...} ชุดล่างสุดทิ้ง
    ★ การ์ด "คิดเพิ่มเอง" 2 ใบ: ตั้งชื่อการ์ดใหม่ แล้วเขียน SQL เอง
    ★ ผลรวมเงินใช้ IFNULL(SUM(...), 0) — ถ้ายังไม่มีข้อมูล SUM จะได้ NULL"""
    # ---- ตัวอย่างเมื่อเขียน SQL แล้ว (เอา # ข้างหน้าออก แล้วเติมให้ครบทุกการ์ด) ----
    # sql = """SELECT
    #            (SELECT COUNT(*) FROM ...) AS 'ผู้เรียน',
    #            (SELECT ...)               AS 'คอร์ส',
    #            ...
    #          """
    # return run_query(sql)[0]      ← [0] = เอาแถวแรก (ผลมีแถวเดียว) ได้เป็น dict

    # TODO: ระหว่างที่ยังไม่ได้เขียน SQL คืนค่า None ให้การ์ดแสดง "—" รอไว้
    return {
        "ผู้เรียน":       None,   # (SELECT COUNT(*) FROM learner)
        "คอร์ส":          None,   # นับคอร์สทั้งหมด
        "การลงทะเบียน":   None,   # นับการลงทะเบียนทั้งหมด
        "บทเรียน":        None,   # นับบทเรียนทั้งหมด
        "คิดเพิ่มเอง 1":  None,   # ตั้งชื่อการ์ดใหม่ + เขียน SQL เอง
        "คิดเพิ่มเอง 2":  None,   # ตั้งชื่อการ์ดใหม่ + เขียน SQL เอง
    }

def report_popular_courses():
    """📈 คอร์สยอดนิยม (Most Enrolled)
    คำใบ้: JOIN enrollment→course, GROUP BY course, COUNT, ORDER BY DESC, LIMIT 5"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_popular_courses")

def report_completion_rate():
    """✅ อัตราการเรียนจบต่อคอร์ส (Completion Rate)
    คำใบ้: GROUP BY course, นับ completed เทียบทั้งหมด ด้วย SUM(CASE WHEN ...)"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_completion_rate")

def report_course_prerequisites():
    """🔗 คอร์สและวิชาที่ต้องเรียนก่อน (Self-Join)
    คำใบ้: self-join: course c LEFT JOIN course pre ON c.prerequisite_id = pre.course_id"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_course_prerequisites")

# ============================================================
#  รายการรายงานที่แสดงบนหน้า /report  (เรียงตามลำดับที่แสดง)
#  ★ วิธีเพิ่มรายงานใหม่ (ไม่ต้องแก้ไฟล์อื่น):
#    1) เขียนฟังก์ชัน report_xxx() ด้านบน ให้ return run_query(sql)
#    2) เพิ่ม 1 บรรทัดในรายการนี้:  ("ชื่อใน-url", "หัวข้อที่แสดง", ชื่อฟังก์ชัน)
#  ★ รายการนี้ต้องอยู่ท้ายไฟล์ (หลังฟังก์ชันทั้งหมด) ไม่งั้น Python หาชื่อฟังก์ชันไม่เจอ
#  ★ ห้ามตั้งชื่อ url ว่า "summary" (ใช้แล้วสำหรับการ์ดสรุป)
# ============================================================
REPORTS = [
    ("popular-courses", "📈 คอร์สยอดนิยม (Most Enrolled)",              report_popular_courses),
    ("completion-rate", "✅ อัตราการเรียนจบต่อคอร์ส (Completion Rate)", report_completion_rate),
    ("prerequisites",   "🔗 คอร์สและวิชาที่ต้องเรียนก่อน (Self-Join)",  report_course_prerequisites),
    # ("my-report", "📋 รายงานของฉัน", report_my_report),   ← ตัวอย่างการเพิ่มรายงานที่ 4
]
