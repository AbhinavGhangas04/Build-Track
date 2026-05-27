import re

with open("d:/buildtrack/static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update Project Details buttons to add Attendance
html = html.replace(
    '<div style="padding:1rem;font-weight:600;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center">Assigned Workers<button class="btn btn-sm" onclick="openWorkerModal()">+ Worker</button></div>',
    '<div style="padding:1rem;font-weight:600;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center">Assigned Workers<div><button class="btn btn-sm" onclick="openAttModal()"><i class="ti ti-check"></i> Attendance</button> <button class="btn btn-sm" onclick="openWorkerModal()">+ Worker</button></div></div>'
)

# 2. Update openAttModal to filter by currentProjectId
old_att = """function openAttModal() {
  const form = document.getElementById('att-form');
  if (!allWorkers.length) { form.innerHTML = '<p style="color:var(--muted);font-size:13px">No workers found. Add workers first.</p>'; openModal('att-modal'); return; }
  form.innerHTML = allWorkers.map(w => `
    <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:0.5px solid var(--border)">
      <div style="font-size:13px;font-weight:500">${esc(w.name)} <span style="font-size:11px;color:var(--muted)">${esc(w.role||'')}</span></div>
      <select id="att-${w.id}" style="width:130px;font-size:12px;padding:5px 8px">
        <option value="present">Present</option>
        <option value="absent">Absent</option>
        <option value="holiday">Holiday/Leave</option>
      </select>
    </div>`).join('');
  openModal('att-modal');
}"""

new_att = """function openAttModal() {
  const form = document.getElementById('att-form');
  let workersToMark = allWorkers;
  if (currentProjectId) {
    workersToMark = allWorkers.filter(w => w.project_id === currentProjectId);
  }
  if (!workersToMark.length) { form.innerHTML = '<p style="color:var(--muted);font-size:13px">No workers found for this project.</p>'; openModal('att-modal'); return; }
  form.innerHTML = workersToMark.map(w => `
    <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:0.5px solid var(--border)">
      <div style="font-size:13px;font-weight:500">${esc(w.name)} <span style="font-size:11px;color:var(--muted)">${esc(w.role||'')}</span></div>
      <select id="att-${w.id}" style="width:130px;font-size:12px;padding:5px 8px">
        <option value="present">Present</option>
        <option value="absent">Absent</option>
        <option value="holiday">Holiday/Leave</option>
      </select>
    </div>`).join('');
  openModal('att-modal');
}"""

html = html.replace(old_att, new_att)

with open("d:/buildtrack/static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
