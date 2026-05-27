import re

with open("d:/buildtrack/static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add currentProjectId
html = html.replace(
    "let allProjects = [];\nlet allWorkers = [];",
    "let allProjects = [];\nlet allWorkers = [];\nlet currentProjectId = null;"
)

# 2. Add material-modal HTML before <div class="toast"
material_modal = """
<!-- Material modal -->
<div class="modal-overlay" id="material-modal">
  <div class="modal">
    <div class="modal-head">
      <div class="modal-title">Add material</div>
      <button class="modal-close" onclick="closeModal('material-modal')">✕</button>
    </div>
    <div class="form-group"><label class="form-label">Material Name *</label><input id="mm-name" placeholder="e.g. Cement, TMT Bars"/></div>
    <div class="form-grid">
      <div class="form-group"><label class="form-label">Category</label><input id="mm-cat" placeholder="e.g. Core, Finishing"/></div>
      <div class="form-group"><label class="form-label">Unit</label><input id="mm-unit" placeholder="e.g. bags, tons, sqft"/></div>
      <div class="form-group"><label class="form-label">Total Quantity</label><input id="mm-qty" type="number" placeholder="0"/></div>
      <div class="form-group"><label class="form-label">Price / Unit</label><input id="mm-price" type="number" placeholder="0"/></div>
    </div>
    <div class="modal-actions">
      <button class="btn" onclick="closeModal('material-modal')">Cancel</button>
      <button class="btn btn-primary" onclick="saveMaterial()">Add material</button>
    </div>
  </div>
</div>
"""
inputs = """
<input type="file" id="pd-scan-input" style="display:none" accept=".jpg,.jpeg,.png,.pdf" onchange="scanBillProject(this)"/>
<input type="file" id="pd-doc-input" style="display:none" accept=".pdf,.jpg,.jpeg,.png" onchange="uploadDocProject(this)"/>
"""
html = html.replace('<div class="toast" id="toast"></div>', material_modal + '\n<div class="toast" id="toast"></div>\n' + inputs)

# 3. Update Project Details buttons
html = html.replace(
    '<div style="padding:1rem;font-weight:600;border-bottom:1px solid var(--border)">Project Expenses</div>',
    '<div style="padding:1rem;font-weight:600;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center">Project Expenses<div><button class="btn btn-sm" onclick="document.getElementById(\'pd-scan-input\').click()"><i class="ti ti-scan"></i> Scan Bill</button> <button class="btn btn-sm" onclick="openBillModal()">+ Bill</button></div></div>'
)
html = html.replace(
    '<div style="padding:1rem;font-weight:600;border-bottom:1px solid var(--border)">Assigned Workers</div>',
    '<div style="padding:1rem;font-weight:600;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center">Assigned Workers<button class="btn btn-sm" onclick="openWorkerModal()">+ Worker</button></div>'
)
html = html.replace(
    '<div style="padding:1rem;font-weight:600;border-bottom:1px solid var(--border)">Documents (PDFs/Contracts)</div>',
    '<div style="padding:1rem;font-weight:600;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center">Documents (PDFs/Contracts)<button class="btn btn-sm" onclick="document.getElementById(\'pd-doc-input\').click()">Upload</button></div>'
)
html = html.replace(
    '<div style="padding:1rem;font-weight:600;border-bottom:1px solid var(--border)">Materials</div>',
    '<div style="padding:1rem;font-weight:600;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center">Materials<button class="btn btn-sm" onclick="openMaterialModal()">+ Material</button></div>'
)

# 4. Update showScreen
html = html.replace(
    "if (map[name] !== undefined) items[map[name]].classList.add('active');",
    "if (name !== 'project-details') currentProjectId = null;\n  if (map[name] !== undefined) items[map[name]].classList.add('active');"
)

# 5. Update openBillModal
html = html.replace(
    "document.getElementById('bm-date').value=new Date().toISOString().split('T')[0];\n  openModal('bill-modal');",
    "document.getElementById('bm-date').value=new Date().toISOString().split('T')[0];\n  if (currentProjectId) { const s = document.getElementById('bm-project'); if(!s.innerHTML.includes('<option value=\"'+currentProjectId+'\"')) populateProjectDropdown(); s.value = currentProjectId; }\n  openModal('bill-modal');"
)

# 6. Update saveBill
html = html.replace(
    "if (res?.ok) { closeModal('bill-modal'); loadBills(); toast('Bill saved'); }",
    "if (res?.ok) { closeModal('bill-modal'); loadBills(); if(currentProjectId) showProjectDetails(currentProjectId); toast('Bill saved'); }"
)

# 7. Update openWorkerModal
html = html.replace(
    "function openWorkerModal() { document.getElementById('wm-name').value=''; document.getElementById('wm-role').value=''; openModal('worker-modal'); }",
    "function openWorkerModal() { document.getElementById('wm-name').value=''; document.getElementById('wm-role').value=''; if(currentProjectId) { document.getElementById('wm-project').value = currentProjectId; } openModal('worker-modal'); }"
)

# 8. Update saveWorker
html = html.replace(
    "if (res?.ok) { closeModal('worker-modal'); loadLabour(); toast('Worker added'); }",
    "if (res?.ok) { closeModal('worker-modal'); loadLabour(); if(currentProjectId) showProjectDetails(currentProjectId); toast('Worker added'); }"
)

# 9. Update showProjectDetails
html = html.replace(
    "async function showProjectDetails(id) {\n  const p = allProjects.find(x => x.id === id);",
    "async function showProjectDetails(id) {\n  currentProjectId = id;\n  const p = allProjects.find(x => x.id === id);"
)

# 10. Add new functions at the end of the file
new_funcs = """
async function scanBillProject(input) {
  if (!currentProjectId) return;
  const file = input.files[0]; if (!file) return;
  toast('Scanning bill via OCR...');
  const fd = new FormData(); 
  fd.append('file', file);
  fd.append('project_id', currentProjectId);
  const res = await apiFetch('/api/ocr/process-and-save', { method:'POST', body: fd, form: true });
  input.value = '';
  if (res?.ok) { showProjectDetails(currentProjectId); toast('Bill scanned and saved!'); }
  else {
    try { const data = await res.json(); toast('Scanning failed: ' + (data.detail||'')); }
    catch { toast('Scanning failed.'); }
  }
}

async function uploadDocProject(input) {
  if (!currentProjectId) return;
  const file = input.files[0]; if (!file) return;
  toast('Uploading...');
  const fd = new FormData(); 
  fd.append('file', file);
  fd.append('project_id', currentProjectId);
  const res = await apiFetch('/api/uploads/', { method:'POST', body: fd, form: true });
  input.value = '';
  if (res?.ok) { showProjectDetails(currentProjectId); toast('Document uploaded!'); }
  else toast('Upload failed.');
}

function openMaterialModal() {
  document.getElementById('mm-name').value='';
  document.getElementById('mm-cat').value='';
  document.getElementById('mm-unit').value='';
  document.getElementById('mm-qty').value='';
  document.getElementById('mm-price').value='';
  openModal('material-modal');
}

async function saveMaterial() {
  if (!currentProjectId) return;
  const body = {
    name: document.getElementById('mm-name').value.trim(),
    category: document.getElementById('mm-cat').value.trim(),
    unit: document.getElementById('mm-unit').value.trim(),
    total_quantity: parseFloat(document.getElementById('mm-qty').value)||0,
    unit_price: parseFloat(document.getElementById('mm-price').value)||0,
    project_id: currentProjectId
  };
  if (!body.name) return toast('Name is required');
  const res = await apiFetch('/api/materials/', { method:'POST', body: JSON.stringify(body) });
  if (res?.ok) { closeModal('material-modal'); showProjectDetails(currentProjectId); toast('Material added'); }
  else toast('Error adding material');
}
</script>
"""
html = html.replace("</script>", new_funcs)

with open("d:/buildtrack/static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
