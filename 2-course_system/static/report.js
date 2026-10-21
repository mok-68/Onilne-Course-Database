// ============================================================
//  report.js  —  ตรรกะหน้ารายงาน (ทำให้เสร็จแล้ว ★)
// ============================================================
const $ = (s) => document.querySelector(s);
async function api(url) { return (await fetch(url)).json(); }
function fillTable(tableSel, statusSel, r) {
  const t = $(tableSel), st = $(statusSel);
  const thead = t.querySelector("thead"), tbody = t.querySelector("tbody");
  thead.innerHTML = ""; tbody.innerHTML = "";
  if (!r.ok) { st.className = "status " + (r.todo ? "todo" : "err"); st.textContent = r.error; return; }
  const rows = r.data || [];
  if (!rows.length) { st.className = "status"; st.textContent = "ไม่มีข้อมูล"; return; }
  st.textContent = "";
  const cols = Object.keys(rows[0]);
  thead.innerHTML = "<tr>" + cols.map(c => "<th>" + c + "</th>").join("") + "</tr>";
  tbody.innerHTML = rows.map(row => "<tr>" + cols.map(c => "<td>" + (row[c] ?? "—") + "</td>").join("") + "</tr>").join("");
}
async function loadSummary() {
  // report_summary() คืน dict {ชื่อการ์ด: ตัวเลข} → 1 คีย์ = 1 การ์ด
  const r = await api("/api/reports/summary");
  const box = $("#summary");
  if (!r.ok) { box.innerHTML = '<div style="grid-column:1/-1" class="status ' + (r.todo ? "todo" : "err") + '">' + r.error + '</div>'; return; }
  box.innerHTML = Object.entries(r.data || {}).map(([label, num]) =>
    '<div class="metric"><div class="metric-num">' + (num ?? "—") + '</div><div class="metric-label">' + label + '</div></div>').join("");
}
async function loadAll() {
  loadSummary();
  // สร้างกล่องรายงานตามรายการ REPORTS ใน db.py
  const list = await api("/api/reports");
  for (const rep of (list.data || [])) {
    const id = "rep_" + rep.key.replace(/\W/g, "_");
    const sec = document.createElement("section");
    sec.className = "card";
    sec.innerHTML = '<h3>' + rep.title + '</h3><div id="' + id + '_status" class="status"></div>' +
      '<div class="table-wrap"><table id="' + id + '_table"><thead></thead><tbody></tbody></table></div>';
    $("#reports").appendChild(sec);
    fillTable("#" + id + "_table", "#" + id + "_status", await api("/api/reports/" + rep.key));
  }
}

const SIM_ACTIONS = {
  enroll: {
    label: "ลงทะเบียนคอร์ส",
    fields: [
      { key: "learner_id", label: "ผู้เรียน", source: "learners" },
      { key: "course_id", label: "คอร์ส", source: "courses" }
    ]
  },
  complete: {
    label: "เปลี่ยนสถานะเป็นเรียนจบ",
    fields: [
      { key: "learner_id", label: "ผู้เรียน", source: "learners" },
      { key: "course_id", label: "คอร์ส", source: "courses" }
    ]
  },
  cancel_enrollment: {
    label: "ยกเลิกการลงทะเบียน",
    fields: [{ key: "enroll_id", label: "การลงทะเบียน", source: "enrollments" }]
  },
  delete_enrollment: {
    label: "ลบการลงทะเบียน (เฉพาะที่ยกเลิกแล้ว)",
    fields: [{ key: "enroll_id", label: "การลงทะเบียน", source: "enrollments" }]
  },
  delete_learner: {
    label: "ลบผู้เรียน",
    fields: [{ key: "learner_id", label: "ผู้เรียน", source: "learners" }]
  },
  delete_course: {
    label: "ลบคอร์ส",
    fields: [{ key: "course_id", label: "คอร์ส", source: "courses" }]
  },
  set_prerequisite: {
    label: "ตั้งวิชาที่ต้องเรียนก่อน",
    fields: [
      { key: "course_id", label: "คอร์ส", source: "courses" },
      { key: "prerequisite_id", label: "วิชาที่ต้องเรียนก่อน (เว้นว่าง = เอาออก)", source: "courses", empty: "ไม่มี" }
    ]
  }
};

const SIM_OPTIONS = {};

async function loadSimOptions() {
  const learners = await api("/api/learners");
  const courses = await api("/api/courses");
  const enrolls = await api("/api/enrollments");
  SIM_OPTIONS.learners = (learners.data || []).map(r => ({ value: r.learner_id, label: r.name }));
  SIM_OPTIONS.courses = (courses.data || []).map(r => ({ value: r.course_id, label: r.title }));
  SIM_OPTIONS.enrollments = (enrolls.data || []).map(r => ({
    value: r.enroll_id,
    label: "#" + r.enroll_id + " " + r.learner_name + " → " + r.course_title + " (" + r.status + ")"
  }));
}

function buildSimForm() {
  const act = SIM_ACTIONS[$("#simAction").value];
  $("#simFields").innerHTML = act.fields.map(f => {
    const opts = (SIM_OPTIONS[f.source] || []).map(o =>
      '<option value="' + o.value + '">' + o.label + '</option>').join("");
    const head = f.empty ? '<option value="">' + f.empty + '</option>' : "";
    return '<div class="field"><label>' + f.label + '</label><select id="sim_' + f.key + '">' +
      head + opts + '</select></div>';
  }).join("");
}

async function runSimulation() {
  const action = $("#simAction").value;
  const params = {};
  SIM_ACTIONS[action].fields.forEach(f => { params[f.key] = $("#sim_" + f.key).value; });
  const st = $("#simStatus"), out = $("#simResult");
  st.className = "status"; st.textContent = "กำลังจำลอง..."; out.innerHTML = "";
  const res = await fetch("/api/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: action, params: params })
  });
  const r = await res.json();
  if (!r.ok) { st.className = "status err"; st.textContent = r.error; return; }
  const d = r.data;
  st.className = "status " + (d.allowed ? "ok" : "err");
  st.textContent = d.message;
  const block = (title, items, cls) => items.length
    ? '<div class="sim-block"><p class="sim-title ' + cls + '">' + title + '</p><ul>' +
      items.map(i => "<li>" + i + "</li>").join("") + "</ul></div>"
    : "";
  out.innerHTML = block("จะเกิดอะไรขึ้น", d.steps, "") + block("คำเตือน", d.warnings, "warn");
}

async function initSimulator() {
  await loadSimOptions();
  $("#simAction").innerHTML = Object.entries(SIM_ACTIONS)
    .map(([k, v]) => '<option value="' + k + '">' + v.label + '</option>').join("");
  $("#simAction").onchange = buildSimForm;
  $("#btnSim").onclick = runSimulation;
  buildSimForm();
}

loadAll();
initSimulator();
