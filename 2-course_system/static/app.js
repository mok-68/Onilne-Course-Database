// ============================================================
//  app.js  —  ตรรกะหน้าเว็บ (ทำให้เสร็จแล้ว ★ นิสิตไม่ต้องแก้)
//  ปรับช่องค้นหา/ฟอร์มได้ที่ตัวแปร ENTITIES ด้านล่าง
// ============================================================
// ★ ตัวอย่าง dropdown ที่อ่านข้อมูลจากฐานข้อมูล: ฟอร์ม "การลงทะเบียน" ช่อง course_id
//   แสดง title แต่ส่งค่าเป็น course_id (อ่านรายการจาก /api/courses)
//   ช่อง FK อื่น ๆ ทำแบบเดียวกันได้ — เปลี่ยน "type": "number" เป็น select + optionsFrom
const ENTITIES = {

  "learners": {
    "label": "ผู้เรียน",
    "api": "/api/learners",
    "idKey": "learner_id",
    "search": [
      {
        "key": "name",
        "label": "ชื่อ",
        "type": "text"
      },
      {
        "key": "email",
        "label": "อีเมล",
        "type": "text"
      }
    ],
    "form": [
      {
        "key": "name",
        "label": "ชื่อ",
        "type": "text"
      },
      {
        "key": "email",
        "label": "อีเมล",
        "type": "text"
      },
      {
        "key": "join_date",
        "label": "วันที่สมัคร",
        "type": "date"
      }
    ]
  },

  "courses": {
    "label": "คอร์ส",
    "api": "/api/courses",
    "idKey": "course_id",
    "search": [
      {
        "key": "title",
        "label": "ชื่อคอร์ส",
        "type": "text"
      },
      {
        "key": "category",
        "label": "หมวดหมู่",
        "type": "select",
        "placeholder": "-- กรุณาเลือกหมวดหมู่ --",
        "optionsFrom": {
          "api": "/api/courses",
          "value": "course_id",
          "label": "category"
        }
      }
    ],
    "form": [
      {
        "key": "title",
        "label": "ชื่อคอร์ส",
        "type": "text"
      },
      {
        "key": "category",
        "label": "หมวดหมู่",
        "type": "select",
        "placeholder": "-- กรุณาเลือกหมวดหมู่ --",
        "optionsFrom": {
          "api": "/api/courses",
          "value": "course_id",
          "label": "category"
        }
      },
      {
        "key": "price",
        "label": "ราคา",
        "type": "number"
      },
      {
        "key": "prerequisite_id",
        "label": "วิชาที่ต้องเรียนก่อน",
        "type": "select",
        "placeholder": "ไม่มี",
        "allowEmpty": true,
        "optionsFrom": {
          "api": "/api/courses",
          "value": "course_id",
          "label": "title"
        }
      }
    ]
  },
  
  "enrollments": 
  {
    "label": "การลงทะเบียน",
    "api": "/api/enrollments",
    "idKey": "enroll_id",
    "search": [
      {
        "key": "learner_id",
        "label": "ชื่อผู้เรียน",
        "type": "select",
        "optionsFrom": {
          "api": "/api/learners",
          "value" : "learner_id",
          "label" : "name"
        }
      },
      {
        "key": "course_id",
        "label": "รหัสคอร์ส",
        "type": "number"
      },
      {
        "key": "status",
        "label": "สถานะ",
        "type": "select",
        "options": [
          "",
          "studying",
          "completed",
          "cancelled"
        ]
      }
    ],
    "form": [
      {
        "key": "learner_id",
        "label": "ชื่อผู้เรียน",
        "type": "select" ,
        "optionsFrom": {
          "api": "/api/learners",
          "value" : "learner_id",
          "label" : "name"
        }
      },
      {
        "key": "course_id",
        "label": "คอร์ส",
        "type": "select",
        "optionsFrom": {
          "api": "/api/courses",
          "value": "course_id",
          "label": "title"
        }
      },
      {
        "key": "enroll_date",
        "label": "วันที่ลงทะเบียน",
        "type": "date"
      },
      {
        "key": "status",
        "label": "สถานะ",
        "type": "select",
        "options": [
          "studying",
          "completed",
          "cancelled"
        ]
      }
    ]
  },
// Certificate 
  "certificate" : {
    "label": "ใบรับรอง",
    "api": "/api/certificate",
    "idKey": "cer_id",
    "search": [
      {
        "key": "learner_id",
        "label": "ผู้เรียน",
        "type": "select",
        "optionsFrom": {
          "api": "/api/learners",
          "value": "learner_id",
          "label": "name"
        }
      },
      {
        "key"   : "name",
        "label" : "ชื่อผู้เรียน",
        "type"  : "text"
      },
      {
        "key"   : "category",
        "label" : "ประเภทคอร์ส",
        "type"  : "text"
      }
    ],
    "form": [
      {
        "key": "learner_id",
        "label": "ผู้เรียน",
        "type": "select",
        "optionsFrom": {
          "api": "/api/learners",
          "value": "learner_id",
          "label": "name"
        }
      },
      {
        "key": "course_id",
        "label": "คอร์ส",
        "type": "select",
        "optionsFrom": {
          "api": "/api/courses",
          "value": "course_id",
          "label": "title"
        }
      },
      {
        "key": "issue_date",
        "label": "วันที่ออกใบรับรอง",
        "type": "date"
      }
    ]

  }




  



  
};

let current = Object.keys(ENTITIES)[0];
let editingId = null;
const $ = (s) => document.querySelector(s);
function setStatus(el, msg, cls = "") { el.className = "status " + cls; el.textContent = msg; }
async function api(url, opts) { const res = await fetch(url, opts); return res.json(); }

function fieldHtml(f, prefix, value = "") {
  if (f.type === "heading") return '<div class="form-section">' + f.label + '</div>';
  let input;
  if (f.type === "select") {
    // options เป็นข้อความ "a" หรือ {value, label} ก็ได้
    input = '<select id="' + prefix + f.key + '">' +
      f.options.map(o => {
        const v = typeof o === "object" ? o.value : o;
        const t = typeof o === "object" ? o.label : (o || "ทั้งหมด");
        return '<option value="' + v + '"' + (String(v) === String(value ?? "") ? " selected" : "") + '>' + t + '</option>';
      }).join("") + '</select>';
  } else { input = '<input id="' + prefix + f.key + '" type="' + f.type + '" value="' + (value ?? "") + '">'; }
  return '<div class="field"><label>' + f.label + '</label>' + input + '</div>';
}
// ช่อง select ที่มี optionsFrom → ดึงตัวเลือกจาก API (เช่น รายชื่อหมวดหมู่จากฐานข้อมูล)
async function loadOptions(fields, forSearch) {
  for (const f of fields.filter(f => f.optionsFrom)) {
    const src = f.optionsFrom, r = await api(src.api);
    f.options = r.ok ? (r.data || []).map(row => ({ value: row[src.value], label: row[src.label] }))
                     : [{ value: "", label: (r.todo ? "🚧 " : "⚠️ ") + r.error }];
    if (forSearch && r.ok) f.options.unshift({ value: "", label: "ทั้งหมด" });
    else if (f.allowEmpty && r.ok) f.options.unshift({ value: "", label: "ไม่มี" });
  }
}
// ช่องในฟอร์มที่ใช้อยู่ตอนนี้ (ช่อง editOnly แสดงเฉพาะตอนแก้ไข)
function formFields() { return ENTITIES[current].form.filter(f => !f.editOnly || editingId !== null); }
async function buildSearch() {
  const cfg = ENTITIES[current];
  await loadOptions(cfg.search, true);
  if (cfg !== ENTITIES[current]) return;   // ผู้ใช้เปลี่ยนแท็บระหว่างรอ
  $("#searchTitle").textContent = cfg.label;
  $("#searchFields").innerHTML = cfg.search.map(f => fieldHtml(f, "s_")).join("");
}
async function doSearch() {
  const cfg = ENTITIES[current];
  const params = new URLSearchParams();
  cfg.search.forEach(f => { const v = $("#s_" + f.key).value; if (v) params.append(f.key, v); });
  setStatus($("#status"), "กำลังค้นหา...");
  renderTable(await api(cfg.api + "?" + params.toString()));
}
function renderTable(r) {
  const head = $("#tableHead"), body = $("#tableBody"), st = $("#status");
  head.innerHTML = ""; body.innerHTML = "";
  if (!r.ok) { setStatus(st, (r.todo ? "🚧 " : "⚠️ ") + r.error, r.todo ? "todo" : "err"); return; }
  const rows = r.data || [];
  if (rows.length === 0) { setStatus(st, "ไม่พบข้อมูล"); return; }
  setStatus(st, "พบ " + rows.length + " รายการ");
  const cols = Object.keys(rows[0]);
  head.innerHTML = cols.map(c => "<th>" + c + "</th>").join("") + "<th>จัดการ</th>";
  body.innerHTML = rows.map(row => {
    const id = row[ENTITIES[current].idKey];
    return "<tr>" + cols.map(c => "<td>" + (row[c] ?? "—") + "</td>").join("") +
      '<td><button class="btn sm" onclick="editRow(' + id + ')">แก้ไข</button> ' +
      '<button class="btn sm del" onclick="deleteRow(' + id + ')">ลบ</button></td></tr>';
  }).join("");
}
async function openForm(title, data = {}) {
  await loadOptions(formFields(), false);
  $("#modalTitle").textContent = title;
  $("#formFields").innerHTML = formFields().map(f => fieldHtml(f, "f_", data[f.key])).join("");
  $("#modal").classList.remove("hidden");
}
function collectForm() { const d = {}; formFields().filter(f => f.key).forEach(f => d[f.key] = $("#f_" + f.key).value); return d; }
async function editRow(id) {
  const cfg = ENTITIES[current];
  const r = await api(cfg.api + "/" + id);
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  editingId = id; openForm("แก้ไขข้อมูล", r.data);
}
async function deleteRow(id) {
  if (!confirm("ยืนยันการลบ?")) return;
  const r = await api(ENTITIES[current].api + "/" + id, { method: "DELETE" });
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  doSearch();
}
async function save() {
  const cfg = ENTITIES[current], data = collectForm();
  const opts = { method: editingId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) };
  const r = await api(editingId ? cfg.api + "/" + editingId : cfg.api, opts);
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  $("#modal").classList.add("hidden"); doSearch();
}
document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
  t.classList.add("active"); current = t.dataset.entity;
  buildSearch(); $("#tableHead").innerHTML = ""; $("#tableBody").innerHTML = "";
  setStatus($("#status"), 'กด "ค้นหา" เพื่อแสดงข้อมูล');
}));
$("#btnSearch").onclick = doSearch;
$("#btnClear").onclick = () => buildSearch();
$("#btnAdd").onclick = () => { editingId = null; openForm("เพิ่มข้อมูลใหม่"); };
$("#btnSave").onclick = save;
$("#btnCancel").onclick = () => $("#modal").classList.add("hidden");
buildSearch();
setStatus($("#status"), 'กด "ค้นหา" เพื่อแสดงข้อมูล');