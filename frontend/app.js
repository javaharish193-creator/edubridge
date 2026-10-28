// EduBridge Client Application — HP Design System Edition
const API_BASE = window.location.origin + '/api/v1';

let currentRole = 'admin';
let currentToken = '';
let currentUser = null;
let currentSelectedSubjectId = null;
let currentSelectedAssignmentId = null;
let currentActiveLiveClassId = null;
let currentGradeLevel = 8;
let currentQuizData = null;

// Preset demo accounts
const DEMO_ACCOUNTS = {
  admin: { phone: '9876543210', pass: 'Admin@123', name: 'Harish Kumar D', role: 'SUPER_ADMIN' },
  teacher: { phone: '9876543211', pass: 'Teacher@123', name: 'Priya Sundaram', role: 'TEACHER' },
  student4: { phone: '9876543220', pass: 'Student@123', name: 'Kavya Ramesh', role: 'STUDENT', grade: 4 },
  student8: { phone: '9876543221', pass: 'Student@123', name: 'Aarav Kumar', role: 'STUDENT', grade: 8 },
  student10: { phone: '9876543222', pass: 'Student@123', name: 'Diya Sharma', role: 'STUDENT', grade: 10 }
};

// --- INITIALIZATION ---
window.addEventListener('DOMContentLoaded', async () => {
  const tomorrow = new Date(Date.now() + 86400000 * 3).toISOString().slice(0, 16);
  if (document.getElementById('asgnDueDateInput')) document.getElementById('asgnDueDateInput').value = tomorrow;
  if (document.getElementById('liveStartTimeInput')) document.getElementById('liveStartTimeInput').value = new Date(Date.now() + 3600000).toISOString().slice(0, 16);

  await switchRole('admin');
});

// --- ROLE SWITCHING ---
async function switchRole(roleKey) {
  currentRole = roleKey;
  const acc = DEMO_ACCOUNTS[roleKey];
  
  // Highlight HP switcher buttons
  ['admin', 'teacher', 'student4', 'student8', 'student10'].forEach(k => {
    const btn = document.getElementById(`roleBtn-${k}`);
    if (btn) {
      if (k === roleKey) {
        btn.className = "px-2 py-0.5 rounded text-[11px] uppercase transition bg-hp-primary text-white font-bold";
      } else {
        btn.className = "px-2 py-0.5 rounded text-[11px] uppercase transition text-slate-400 hover:text-white font-medium";
      }
    }
  });

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone_number: acc.phone, password: acc.pass })
    });
    if (!res.ok) throw new Error('Login failed');
    const data = await res.json();
    currentToken = data.access_token;
    currentUser = data.user;

    // Update Header
    document.getElementById('userAvatar').innerText = currentUser.full_name.charAt(0);
    document.getElementById('userNameLabel').innerText = currentUser.full_name;
    document.getElementById('userRoleLabel').innerText = currentUser.role;

    if (currentUser.role === 'STUDENT') {
      currentGradeLevel = currentUser.student ? currentUser.student.grade_level : 8;
      document.getElementById('adminView').classList.add('hidden');
      document.getElementById('studentView').classList.remove('hidden');
      applyStudentTierStyling(currentGradeLevel);
      await loadStudentDashboard();
    } else {
      document.getElementById('studentView').classList.add('hidden');
      document.getElementById('adminView').classList.remove('hidden');
      await loadAdminDashboard();
    }

    showToast(`Active Session: ${currentUser.full_name} (${currentUser.role})`, 'success');
  } catch (err) {
    showToast(`Authentication error: ${err.message}`, 'error');
  }
}

// --- STUDENT MULTI-TIER THEMES (HP Design Style) ---
function applyStudentTierStyling(grade) {
  const badge = document.getElementById('tierBadge');
  const title = document.getElementById('studentWelcomeTitle');
  const subtitle = document.getElementById('studentClassSubtitle');

  title.innerText = `Welcome Back, ${currentUser.full_name}!`;
  subtitle.innerText = `Class ${grade}-${currentUser.student.section} • Roll: ${currentUser.student.roll_number} • Academic Year 2026-2027`;

  if (grade <= 5) {
    badge.innerText = 'Primary Tier (Classes 3-5)';
  } else if (grade <= 8) {
    badge.innerText = 'Middle School Tier (Classes 6-8)';
  } else {
    badge.innerText = 'Senior Secondary Tier (Classes 9-12)';
  }
}

// --- ADMIN TABS NAVIGATION ---
function switchAdminTab(tabKey) {
  document.querySelectorAll('.admin-tab').forEach(b => {
    if (b.dataset.tab === tabKey) {
      b.className = "admin-tab active-tab px-5 py-2 rounded-hp-pill text-xs font-semibold uppercase tracking-[0.5px] bg-hp-ink text-white transition";
    } else {
      b.className = "admin-tab px-5 py-2 rounded-hp-pill text-xs font-semibold uppercase tracking-[0.5px] text-hp-charcoal hover:bg-hp-cloud transition";
    }
  });

  document.querySelectorAll('.admin-tab-pane').forEach(p => p.classList.add('hidden'));
  const target = document.getElementById(`adminTab-${tabKey}`);
  if (target) target.classList.remove('hidden');

  if (tabKey === 'classes') loadAdminClasses();
  if (tabKey === 'students') loadAdminStudents();
  if (tabKey === 'content') loadAdminContentHub();
  if (tabKey === 'assignments') loadAdminAssignments();
  if (tabKey === 'live') loadAdminLiveClasses();
}

// --- ADMIN DASHBOARD OVERVIEW ---
async function loadAdminDashboard() {
  try {
    const res = await fetch(`${API_BASE}/admin/stats`, {
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    if (!res.ok) return;
    const stats = await res.json();
    document.getElementById('statStudents').innerText = stats.total_students;
    document.getElementById('statClasses').innerText = stats.total_classes;
    document.getElementById('statPendingReviews').innerText = stats.pending_submissions;
    document.getElementById('statLiveToday').innerText = stats.live_classes_today;

    const list = document.getElementById('recentSubmissionsList');
    if (!stats.recent_submissions || stats.recent_submissions.length === 0) {
      list.innerHTML = '<p class="text-xs text-hp-graphite py-4 text-center">No recent submissions recorded.</p>';
    } else {
      list.innerHTML = stats.recent_submissions.map(r => `
        <div class="flex items-center justify-between p-3.5 rounded-hp-btn bg-hp-cloud border border-hp-fog">
          <div>
            <p class="text-xs font-bold text-hp-ink">${r.student_name} <span class="text-hp-graphite font-normal">(${r.roll_number})</span></p>
            <p class="text-[11px] text-hp-charcoal mt-0.5">${r.assignment_title}</p>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-hp-btn uppercase tracking-wider ${r.status === 'GRADED' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">${r.status}</span>
            <span class="text-[11px] text-hp-graphite">${new Date(r.submitted_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error(err);
  }
}

// --- ADMIN CLASSES ---
async function loadAdminClasses() {
  const res = await fetch(`${API_BASE}/admin/classes`, { headers: { 'Authorization': `Bearer ${currentToken}` } });
  if (!res.ok) return;
  const classes = await res.json();
  const tbody = document.getElementById('classesTableBody');
  tbody.innerHTML = classes.map(c => `
    <tr class="hover:bg-hp-cloud/60 transition">
      <td class="p-4 font-semibold text-hp-ink">Class ${c.grade_level}-${c.section}</td>
      <td class="p-4 text-hp-charcoal">${c.academic_year}</td>
      <td class="p-4">
        <span class="text-[10px] font-bold px-2 py-0.5 rounded-hp-btn uppercase tracking-wider bg-hp-cloud border border-hp-fog text-hp-ink">
          ${c.grade_level <= 5 ? 'Primary (3-5)' : c.grade_level <= 8 ? 'Middle (6-8)' : 'High (9-12)'}
        </span>
      </td>
      <td class="p-4 font-semibold text-hp-ink">${c.student_count} Enrolled</td>
      <td class="p-4">
        <button onclick="filterStudentsByClass('${c.id}')" class="text-xs text-hp-primary hover:underline font-bold uppercase tracking-wider">View Roster</button>
      </td>
    </tr>
  `).join('');

  // Populate selects
  const classOpts = classes.map(c => `<option value="${c.id}">Class ${c.grade_level}-${c.section} (${c.academic_year})</option>`).join('');
  const select1 = document.getElementById('studentClassFilter');
  if (select1) select1.innerHTML = `<option value="">All Classes</option>${classOpts}`;
  const select2 = document.getElementById('importTargetClassSelect');
  if (select2) select2.innerHTML = classOpts;
  const select3 = document.getElementById('asgnClassSelect');
  if (select3) { select3.innerHTML = classOpts; loadSubjectsForAsgnSelect(); }
  const select4 = document.getElementById('liveClassSelect');
  if (select4) { select4.innerHTML = classOpts; loadSubjectsForLiveSelect(); }
}

async function executeCreateClass() {
  const grade = parseInt(document.getElementById('inputClassGrade').value);
  const section = document.getElementById('inputClassSection').value.trim();
  const year = document.getElementById('inputClassYear').value.trim();

  const res = await fetch(`${API_BASE}/admin/classes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
    body: JSON.stringify({ grade_level: grade, section: section, academic_year: year })
  });

  if (!res.ok) {
    const err = await res.json();
    showToast(err.error?.message || 'Failed to create class', 'error');
    return;
  }
  closeModal('createClassModal');
  showToast(`Class ${grade}-${section} created in PostgreSQL!`, 'success');
  loadAdminClasses();
}

// --- ADMIN STUDENTS ---
async function loadAdminStudents() {
  const search = document.getElementById('studentSearchInput')?.value || '';
  const classId = document.getElementById('studentClassFilter')?.value || '';

  const params = new URLSearchParams({ page: '1', page_size: '50' });
  if (search) params.append('search', search);
  if (classId) params.append('class_id', classId);

  const res = await fetch(`${API_BASE}/admin/students?${params.toString()}`, { headers: { 'Authorization': `Bearer ${currentToken}` } });
  if (!res.ok) return;
  const data = await res.json();
  const tbody = document.getElementById('studentsTableBody');
  tbody.innerHTML = data.items.map(s => `
    <tr class="hover:bg-hp-cloud/60 transition">
      <td class="p-4 font-mono text-xs font-bold text-hp-primary">${s.roll_number}</td>
      <td class="p-4 font-semibold text-hp-ink">${s.full_name}</td>
      <td class="p-4 text-hp-charcoal">Class ${s.grade_level}-${s.section}</td>
      <td class="p-4 font-mono text-xs text-hp-graphite">${s.phone_number}</td>
      <td class="p-4 text-xs text-hp-charcoal">${s.guardian_name || '—'} (${s.guardian_phone || '—'})</td>
      <td class="p-4">
        <span class="text-[10px] font-bold px-2 py-0.5 rounded-hp-btn uppercase tracking-wider ${s.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}">
          ${s.is_active ? 'Active' : 'Inactive'}
        </span>
      </td>
      <td class="p-4">
        <button onclick="viewStudentActivity('${s.id}', '${s.full_name}')" class="text-xs text-hp-primary hover:underline font-bold uppercase tracking-wider">Activity</button>
      </td>
    </tr>
  `).join('');
}

function filterStudentsByClass(classId) {
  switchAdminTab('students');
  const sel = document.getElementById('studentClassFilter');
  if (sel) {
    sel.value = classId;
    loadAdminStudents();
  }
}

async function viewStudentActivity(studentId, name) {
  const res = await fetch(`${API_BASE}/admin/students/${studentId}/activity`, { headers: { 'Authorization': `Bearer ${currentToken}` } });
  if (!res.ok) return;
  const act = await res.json();
  alert(`Activity Record for ${name}:\n• Cohort: ${act.class_name}\n• Avg Score: ${act.average_score}%\n• Attendance: ${act.attendance_percentage}%\n• Homework: ${act.submitted_assignments}/${act.total_assignments} submitted`);
}

function downloadSampleCsv() {
  const csvContent = "data:text/csv;charset=utf-8,roll_number,full_name,phone_number,guardian_name,guardian_phone\n08A11,Manoj V,9876543231,Vasanth M,9876543293\n08A12,Sneha R,9876543232,Ravi K,9876543294";
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "edubridge_student_sample.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

async function executeCsvImport() {
  const classId = document.getElementById('importTargetClassSelect').value;
  const fileInput = document.getElementById('importCsvFileInput');
  if (!fileInput.files[0]) {
    showToast('Please select a CSV file to import', 'error');
    return;
  }

  const formData = new FormData();
  formData.append('class_id', classId);
  formData.append('file', fileInput.files[0]);

  const res = await fetch(`${API_BASE}/admin/students/import`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${currentToken}` },
    body: formData
  });

  if (!res.ok) {
    showToast('Failed to import CSV', 'error');
    return;
  }
  const result = await res.json();
  closeModal('importCsvModal');
  showToast(`Imported ${result.imported_count} students to PostgreSQL! (${result.skipped_count} skipped)`, 'success');
  loadAdminStudents();
}

// --- ADMIN CONTENT HUB ---
async function loadAdminContentHub() {
  const res = await fetch(`${API_BASE}/admin/subjects`, { headers: { 'Authorization': `Bearer ${currentToken}` } });
  if (!res.ok) return;
  const subjects = await res.json();
  document.getElementById('subjectCountBadge').innerText = subjects.length;
  
  const container = document.getElementById('contentSubjectList');
  container.innerHTML = subjects.map(s => `
    <div onclick="selectContentSubject('${s.id}', '${s.name}', '${s.code}')" class="p-3.5 rounded-hp-btn border transition cursor-pointer flex items-center justify-between ${currentSelectedSubjectId === s.id ? 'bg-hp-cloud border-hp-primary' : 'bg-white border-hp-hairline hover:border-hp-steel'}">
      <div>
        <h5 class="text-xs font-bold text-hp-ink">${s.name}</h5>
        <p class="text-[11px] text-hp-graphite font-mono">${s.code} • ${s.chapter_count} Chapters</p>
      </div>
      <i class="fa-solid fa-chevron-right text-xs text-hp-steel"></i>
    </div>
  `).join('');

  if (subjects.length > 0 && !currentSelectedSubjectId) {
    selectContentSubject(subjects[0].id, subjects[0].name, subjects[0].code);
  }
}

async function selectContentSubject(subjectId, name, code) {
  currentSelectedSubjectId = subjectId;
  document.getElementById('contentSelectedSubjectTitle').innerText = `${name} (${code})`;
  document.getElementById('contentSelectedSubjectSub').innerText = "Chapters, curriculum topics, and secured revision notes";
  document.getElementById('btnGenerateQuizTop').classList.remove('hidden');

  const res = await fetch(`${API_BASE}/content/subjects/${subjectId}/materials`, { headers: { 'Authorization': `Bearer ${currentToken}` } });
  if (!res.ok) return;
  const tree = await res.json();

  const treeContainer = document.getElementById('contentChapterTree');
  if (tree.chapters.length === 0) {
    treeContainer.innerHTML = '<p class="text-xs text-hp-graphite py-8 text-center">No chapters created yet. Click "Add Chapter" above.</p>';
    return;
  }

  treeContainer.innerHTML = tree.chapters.map(c => `
    <div class="p-5 rounded-hp-card border border-hp-hairline bg-hp-cloud/60 space-y-3">
      <div class="flex items-center justify-between">
        <h5 class="text-xs font-bold uppercase tracking-wider text-hp-primary flex items-center gap-2">
          <i class="fa-solid fa-folder-open"></i> ${c.title}
        </h5>
        <div class="flex items-center gap-2">
          <button onclick="generateQuizForChapter('${c.id}', '${c.title}')" class="btn-hp-outline py-1 px-3 text-[11px]">
            <i class="fa-solid fa-wand-magic-sparkles text-amber-500"></i> AI Quiz
          </button>
        </div>
      </div>
      <div class="space-y-2 pl-4 border-l-2 border-hp-primary/40">
        ${c.materials.length === 0 ? '<p class="text-xs text-hp-graphite italic">No study files uploaded for this chapter yet.</p>' : ''}
        ${c.materials.map(m => `
          <div class="flex items-center justify-between p-3 rounded-hp-btn bg-white border border-hp-hairline text-xs">
            <div class="flex items-center gap-2.5">
              <i class="fa-solid ${m.material_type === 'PDF_NOTES' ? 'fa-file-pdf text-red-600' : 'fa-video text-blue-600'}"></i>
              <span class="font-medium text-hp-ink">${m.title}</span>
            </div>
            <div class="flex items-center gap-4">
              <a href="${m.download_url}" target="_blank" class="text-xs text-hp-primary hover:underline font-bold uppercase tracking-wider flex items-center gap-1">
                <i class="fa-solid fa-arrow-up-right-from-square"></i> Open (15m Link)
              </a>
              <button onclick="deleteMaterial('${m.id}')" class="text-hp-graphite hover:text-red-600 text-xs"><i class="fa-solid fa-trash-can"></i></button>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `).join('');
}

async function deleteMaterial(materialId) {
  if (!confirm('Are you sure you want to remove this study material?')) return;
  const res = await fetch(`${API_BASE}/admin/materials/${materialId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${currentToken}` }
  });
  if (res.ok) {
    showToast('Material deleted successfully', 'success');
    if (currentSelectedSubjectId) selectContentSubject(currentSelectedSubjectId, '', '');
  }
}

// --- ADMIN ASSIGNMENTS & REVIEW QUEUE ---
async function loadAdminAssignments() {
  const res = await fetch(`${API_BASE}/assignments/list?page=1&page_size=50`, { headers: { 'Authorization': `Bearer ${currentToken}` } });
  if (!res.ok) return;
  const data = await res.json();
  const container = document.getElementById('adminAssignmentList');

  if (data.items.length === 0) {
    container.innerHTML = '<p class="text-xs text-hp-graphite py-6 text-center">No assignments posted yet.</p>';
    return;
  }

  container.innerHTML = data.items.map(a => `
    <div onclick="openReviewQueue('${a.id}')" class="p-4 rounded-hp-btn border transition cursor-pointer ${currentSelectedAssignmentId === a.id ? 'bg-hp-cloud border-hp-primary' : 'bg-white border-hp-hairline hover:border-hp-steel'}">
      <div class="flex items-start justify-between">
        <div>
          <span class="text-[11px] font-bold text-hp-primary uppercase tracking-wider">${a.subject_name}</span>
          <h5 class="text-xs font-bold text-hp-ink mt-0.5">${a.title}</h5>
        </div>
        <span class="text-[10px] font-bold px-2 py-0.5 rounded-hp-btn uppercase tracking-wider ${a.answer_key_url ? 'bg-emerald-100 text-emerald-800' : 'bg-hp-fog text-hp-charcoal'}">
          ${a.answer_key_url ? 'Key Published' : 'Key Hidden'}
        </span>
      </div>
      <div class="flex items-center justify-between text-xs text-hp-graphite mt-3 pt-2 border-t border-hp-hairline">
        <span>Due: ${new Date(a.due_date).toLocaleDateString()}</span>
        <span class="font-bold text-hp-primary">${a.submitted_count}/${a.total_students} Submitted</span>
      </div>
    </div>
  `).join('');

  if (data.items.length > 0 && !currentSelectedAssignmentId) {
    openReviewQueue(data.items[0].id);
  }
}

async function openReviewQueue(assignmentId) {
  currentSelectedAssignmentId = assignmentId;
  document.getElementById('emptyReviewQueueNotice').classList.add('hidden');
  document.getElementById('activeReviewQueuePanel').classList.remove('hidden');

  const res = await fetch(`${API_BASE}/admin/assignments/${assignmentId}/submissions`, { headers: { 'Authorization': `Bearer ${currentToken}` } });
  if (!res.ok) return;
  const queue = await res.json();

  document.getElementById('queueAssignmentTitle').innerText = queue.assignment.title;
  document.getElementById('queueAssignmentMeta').innerText = `Max Marks: ${queue.assignment.max_marks} • Due: ${new Date(queue.assignment.due_date).toLocaleString()} • ${queue.total} Students in Cohort`;
  
  const btnPub = document.getElementById('btnPublishKey');
  if (queue.assignment.answer_key_published) {
    btnPub.innerText = 'Key Published ✓';
    btnPub.className = "btn-hp-ink bg-hp-steel text-white cursor-not-allowed text-xs";
    btnPub.disabled = true;
  } else {
    btnPub.innerText = 'Publish Key Now';
    btnPub.className = "btn-hp-primary text-xs";
    btnPub.disabled = false;
  }

  const tbody = document.getElementById('queueSubmissionsTbody');
  tbody.innerHTML = queue.items.map(item => `
    <tr class="hover:bg-hp-cloud/60 transition">
      <td class="p-3 font-mono font-bold text-hp-primary">${item.roll_number}</td>
      <td class="p-3 font-semibold text-hp-ink">${item.student_name}</td>
      <td class="p-3">
        <span class="text-[10px] font-bold px-2 py-0.5 rounded-hp-btn uppercase tracking-wider ${item.status === 'GRADED' ? 'bg-emerald-100 text-emerald-800' : item.status === 'SUBMITTED' ? 'bg-blue-100 text-blue-800' : item.status === 'OVERDUE' ? 'bg-red-100 text-red-800' : 'bg-hp-cloud text-hp-graphite'}">
          ${item.status}
        </span>
      </td>
      <td class="p-3 font-medium text-hp-charcoal">
        ${item.files.length > 0 ? `<span class="text-hp-primary font-bold">${item.files.length} file(s)</span>` : '<span class="text-hp-steel">—</span>'}
      </td>
      <td class="p-3 font-bold text-hp-ink">
        ${item.marks_awarded !== null ? `${item.marks_awarded}/${queue.assignment.max_marks}` : '—'}
      </td>
      <td class="p-3">
        ${item.submission_id ? `
          <button onclick='openGradingWorkbench(${JSON.stringify(item)}, ${queue.assignment.max_marks})' class="btn-hp-outline py-1 px-3 text-[11px]">
            ${item.status === 'GRADED' ? 'Edit Grade' : 'Grade Work'}
          </button>
        ` : '<span class="text-hp-steel text-[11px]">No submit</span>'}
      </td>
    </tr>
  `).join('');
}

let activeGradingItem = null;
let activeGradingMaxMarks = 100;

function openGradingWorkbench(item, maxMarks) {
  activeGradingItem = item;
  activeGradingMaxMarks = maxMarks;

  const bench = document.getElementById('gradingWorkbench');
  bench.classList.remove('hidden');

  document.getElementById('gradingStudentHeader').innerText = `Grading: ${item.student_name} (Roll ${item.roll_number})`;
  document.getElementById('gradingStudentNotes').innerText = item.student_notes ? `Student Notes: "${item.student_notes}"` : 'No additional student notes.';
  document.getElementById('gradingMaxMarksSpan').innerText = maxMarks;
  document.getElementById('inputMarksAwarded').value = item.marks_awarded || '';
  document.getElementById('inputFeedbackRemarks').value = item.feedback_remarks || '';
  document.getElementById('checkRequestResubmit').checked = (item.status === 'RESUBMISSION_REQUESTED');

  const filesContainer = document.getElementById('gradingFilesList');
  filesContainer.innerHTML = item.files.map(f => `
    <a href="${f.url}" target="_blank" class="px-3 py-1.5 bg-white border border-hp-steel rounded-hp-btn text-xs font-semibold text-hp-primary hover:underline flex items-center gap-1.5">
      <i class="fa-solid fa-file-arrow-down text-red-600"></i> ${f.name}
    </a>
  `).join('');
}

function closeGradingWorkbench() {
  document.getElementById('gradingWorkbench').classList.add('hidden');
}

// AI Model 3: Teacher Auto-Grading Assistant
async function triggerAIGradingAssist() {
  if (!activeGradingItem) return;
  showToast('AI Grade Assistant analyzing submission...', 'info');

  try {
    const res = await fetch(`${API_BASE}/ai/grading/assist`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
      body: JSON.stringify({
        assignment_title: document.getElementById('queueAssignmentTitle').innerText,
        question_instructions: "Evaluate completeness and adherence to rubric",
        student_notes: activeGradingItem.student_notes || "All answers attached in file",
        max_marks: activeGradingMaxMarks,
        submitted_files: activeGradingItem.files.map(f => f.name)
      })
    });
    if (!res.ok) throw new Error('AI Assist failed');
    const aiResp = await res.json();

    document.getElementById('inputMarksAwarded').value = aiResp.suggested_marks;
    document.getElementById('inputFeedbackRemarks').value = aiResp.feedback_remarks;
    showToast(`AI Evaluation: Proposing ${aiResp.suggested_marks}/${aiResp.max_marks} marks`, 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function submitGradingDecision() {
  if (!activeGradingItem) return;
  const marks = parseFloat(document.getElementById('inputMarksAwarded').value);
  const remarks = document.getElementById('inputFeedbackRemarks').value.trim();
  const resubmit = document.getElementById('checkRequestResubmit').checked;

  const res = await fetch(`${API_BASE}/admin/submissions/${activeGradingItem.submission_id}/grade`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
    body: JSON.stringify({
      marks_awarded: isNaN(marks) ? null : marks,
      feedback_remarks: remarks,
      request_resubmission: resubmit
    })
  });

  if (!res.ok) {
    const err = await res.json();
    showToast(err.error?.message || 'Grading failed', 'error');
    return;
  }
  showToast('Submission graded and saved to PostgreSQL!', 'success');
  closeGradingWorkbench();
  openReviewQueue(currentSelectedAssignmentId);
}

async function publishAnswerKeyNow() {
  if (!currentSelectedAssignmentId) return;
  const res = await fetch(`${API_BASE}/admin/assignments/${currentSelectedAssignmentId}/publish-answer-key`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
    body: JSON.stringify({ force: true })
  });

  if (!res.ok) {
    const err = await res.json();
    showToast(err.error?.message || 'Failed to publish key', 'error');
    return;
  }
  showToast('Answer key published to student portal!', 'success');
  openReviewQueue(currentSelectedAssignmentId);
}

// --- ADMIN LIVE CLASSES & ATTENDANCE ---
async function loadAdminLiveClasses() {
  const res = await fetch(`${API_BASE}/live/upcoming?include_completed=true`, { headers: { 'Authorization': `Bearer ${currentToken}` } });
  if (!res.ok) return;
  const classes = await res.json();
  const container = document.getElementById('adminLiveClassesList');

  if (classes.length === 0) {
    container.innerHTML = '<p class="text-xs text-hp-graphite py-6 text-center">No live sessions scheduled.</p>';
    return;
  }

  container.innerHTML = classes.map(c => `
    <div class="p-5 rounded-hp-card border border-hp-hairline bg-white flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-[10px] font-bold px-2 py-0.5 rounded-hp-btn uppercase tracking-wider ${c.status === 'IN_PROGRESS' ? 'bg-red-100 text-red-700 animate-pulse' : c.status === 'COMPLETED' ? 'bg-hp-fog text-hp-charcoal' : 'bg-emerald-100 text-emerald-800'}">
            ${c.status}
          </span>
          <span class="text-xs font-bold text-hp-graphite uppercase tracking-wider">${c.subject_name}</span>
        </div>
        <h5 class="text-base font-semibold text-hp-ink mt-1">${c.title}</h5>
        <p class="text-xs text-hp-graphite font-mono mt-0.5">Room: ${c.meeting_room_id} • Duration: ${c.duration_minutes}m</p>
      </div>

      <div class="flex items-center gap-2.5">
        <button onclick="viewClassAttendance('${c.id}', '${c.meeting_room_id}')" class="btn-hp-outline text-xs">
          Attendance Log
        </button>
        ${c.status === 'IN_PROGRESS' || c.status === 'SCHEDULED' ? `
          <button onclick="enterLiveClassroom('${c.id}', '${c.title}')" class="btn-hp-primary text-xs">
            <i class="fa-solid fa-headset"></i> Launch Room
          </button>
        ` : ''}
      </div>
    </div>
  `).join('');
}

let activeAttendanceClassId = null;

async function viewClassAttendance(classId, room) {
  activeAttendanceClassId = classId;
  const res = await fetch(`${API_BASE}/live/${classId}/attendance`, { headers: { 'Authorization': `Bearer ${currentToken}` } });
  if (!res.ok) return;
  const rep = await res.json();

  document.getElementById('btnDownloadCsv').classList.remove('hidden');
  const container = document.getElementById('attendanceReportContainer');

  container.innerHTML = `
    <div class="space-y-4 text-left">
      <div class="grid grid-cols-3 gap-2 text-center pb-3 border-b border-hp-hairline">
        <div>
          <p class="text-[10px] text-hp-graphite uppercase font-bold tracking-wider">Enrolled</p>
          <p class="text-base font-bold text-hp-ink mt-0.5">${rep.summary.enrolled}</p>
        </div>
        <div>
          <p class="text-[10px] text-emerald-600 uppercase font-bold tracking-wider">Attended</p>
          <p class="text-base font-bold text-emerald-600 mt-0.5">${rep.summary.attended}</p>
        </div>
        <div>
          <p class="text-[10px] text-hp-primary uppercase font-bold tracking-wider">Avg Mins</p>
          <p class="text-base font-bold text-hp-primary mt-0.5">${rep.summary.average_minutes}m</p>
        </div>
      </div>

      <div class="space-y-2 max-h-[320px] overflow-y-auto custom-scrollbar text-xs">
        ${rep.items.map(st => `
          <div class="p-3 rounded-hp-btn bg-hp-cloud border border-hp-fog flex items-center justify-between">
            <div>
              <p class="font-bold text-hp-ink">${st.student_name} <span class="font-mono text-hp-graphite">(${st.roll_number})</span></p>
              <p class="text-[11px] text-hp-charcoal">${st.present ? `Duration: ${st.duration_minutes}m • ${st.reconnects} reconnects` : 'Absent'}</p>
            </div>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-hp-btn uppercase tracking-wider ${st.present ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}">
              ${st.present ? 'Present' : 'Absent'}
            </span>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

function downloadCurrentAttendanceCSV() {
  if (!activeAttendanceClassId) return;
  window.open(`${API_BASE}/live/${activeAttendanceClassId}/attendance.csv?token=${currentToken}`, '_blank');
}

// --- STUDENT DASHBOARD VIEW ---
async function loadStudentDashboard() {
  try {
    const res = await fetch(`${API_BASE}/student/dashboard`, { headers: { 'Authorization': `Bearer ${currentToken}` } });
    if (!res.ok) return;
    const dash = await res.json();

    document.getElementById('stStatSubjects').innerText = dash.stats.total_subjects;
    document.getElementById('stStatPending').innerText = dash.stats.pending_homework;
    document.getElementById('stStatCompleted').innerText = dash.stats.completed_homework;
    document.getElementById('stStatLive').innerText = dash.stats.upcoming_live_count;

    // Live alert banner
    const liveAlert = document.getElementById('studentLiveClassAlert');
    if (dash.upcoming_live_classes.length > 0 && dash.upcoming_live_classes[0].status === 'IN_PROGRESS') {
      const live = dash.upcoming_live_classes[0];
      liveAlert.classList.remove('hidden');
      liveAlert.innerHTML = `
        <div class="hp-card p-5 bg-hp-ink text-white border-none flex items-center justify-between">
          <div class="flex items-center gap-3">
            <span class="hp-chevron-slash-sm bg-hp-bloom-coral"></span>
            <div>
              <h4 class="font-medium text-sm text-white">LIVE SESSION ACTIVE: ${live.title}</h4>
              <p class="text-xs text-slate-400">${live.subject_name} • Duration ${live.duration_minutes} minutes</p>
            </div>
          </div>
          <button onclick="enterLiveClassroom('${live.id}', '${live.title}')" class="btn-hp-primary">
            Join Class
          </button>
        </div>
      `;
    } else {
      liveAlert.classList.add('hidden');
    }

    // Subjects Grid
    const subGrid = document.getElementById('studentSubjectsGrid');
    subGrid.innerHTML = dash.subjects.map(s => `
      <div onclick="openStudentSubjectMaterials('${s.id}', '${s.name}')" class="hp-card p-5 cursor-pointer hover:border-hp-primary transition group">
        <div class="flex items-center justify-between mb-3">
          <div class="w-10 h-10 rounded-hp-btn bg-hp-cloud border border-hp-fog text-hp-primary flex items-center justify-center text-base">
            <i class="fa-solid fa-book-bookmark"></i>
          </div>
          <span class="text-[11px] font-mono font-bold px-2 py-0.5 rounded-hp-btn bg-hp-cloud text-hp-graphite uppercase tracking-wider">${s.code}</span>
        </div>
        <h4 class="font-semibold text-base text-hp-ink">${s.name}</h4>
        <p class="text-xs text-hp-graphite mt-1">${s.materials_count} Study Documents Available</p>
      </div>
    `).join('');

    // Assignments List
    const asgnList = document.getElementById('studentAssignmentsList');
    const allAssignments = [...dash.pending_assignments];
    if (allAssignments.length === 0) {
      asgnList.innerHTML = '<p class="text-xs text-hp-graphite py-6 text-center">No assignments pending! You are completely up to date.</p>';
    } else {
      asgnList.innerHTML = allAssignments.map(a => `
        <div class="hp-card p-5 space-y-3">
          <div class="flex items-start justify-between">
            <div>
              <span class="text-[11px] font-bold text-hp-primary uppercase tracking-wider">${a.subject_name}</span>
              <h4 class="font-semibold text-sm text-hp-ink mt-0.5">${a.title}</h4>
            </div>
            <span class="text-[10px] font-bold px-2.5 py-0.5 rounded-hp-btn uppercase tracking-wider ${a.status === 'GRADED' ? 'bg-emerald-100 text-emerald-800' : a.status === 'SUBMITTED' ? 'bg-blue-100 text-blue-800' : 'bg-amber-100 text-amber-800'}">
              ${a.status}
            </span>
          </div>

          <div class="flex items-center justify-between text-xs text-hp-graphite pt-3 border-t border-hp-hairline">
            <span>Due: ${new Date(a.due_date).toLocaleDateString()}</span>
            <div>
              ${a.status === 'PENDING' || a.status === 'RESUBMISSION_REQUESTED' ? `
                <button onclick="openSubmitHomeworkModal('${a.id}', '${a.title}')" class="btn-hp-primary py-1 px-3 text-xs">
                  Submit Work
                </button>
              ` : `
                <button onclick="viewMySubmissionResult('${a.id}')" class="text-xs text-hp-primary font-bold hover:underline uppercase tracking-wider">
                  View Result
                </button>
              `}
            </div>
          </div>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error(err);
  }
}

async function openStudentSubjectMaterials(subjectId, subjectName) {
  const drawer = document.getElementById('studentSubjectMaterialsDrawer');
  drawer.classList.remove('hidden');
  document.getElementById('drawerSubjectTitle').innerText = `${subjectName} — Syllabus & Revision Notes`;

  const res = await fetch(`${API_BASE}/content/subjects/${subjectId}/materials`, { headers: { 'Authorization': `Bearer ${currentToken}` } });
  if (!res.ok) return;
  const tree = await res.json();

  const container = document.getElementById('drawerChaptersContainer');
  container.innerHTML = tree.chapters.map(c => `
    <div class="p-4 rounded-hp-btn bg-hp-cloud border border-hp-fog space-y-2">
      <div class="flex items-center justify-between">
        <h5 class="text-xs font-bold uppercase tracking-wider text-hp-ink">${c.title}</h5>
        <button onclick="generateQuizForChapter('${c.id}', '${c.title}')" class="btn-hp-outline py-1 px-2.5 text-[10px]">
          <i class="fa-solid fa-wand-magic-sparkles text-amber-500"></i> AI Quiz
        </button>
      </div>
      <div class="space-y-1.5 pl-3 border-l-2 border-hp-primary/40">
        ${c.materials.map(m => `
          <a href="${m.download_url}" target="_blank" class="flex items-center justify-between text-xs text-hp-primary hover:underline py-1">
            <span><i class="fa-solid fa-file-pdf text-red-600 mr-2"></i> ${m.title}</span>
            <span class="text-[10px] text-hp-graphite font-semibold uppercase">Open (15m)</span>
          </a>
        `).join('')}
      </div>
    </div>
  `).join('');
}

function closeStudentDrawer() {
  document.getElementById('studentSubjectMaterialsDrawer').classList.add('hidden');
}

// --- LIVE CLASSROOM (JITSI MEET EMBED) ---
async function enterLiveClassroom(liveId, title) {
  try {
    const res = await fetch(`${API_BASE}/live/${liveId}/join`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    if (!res.ok) {
      const err = await res.json();
      showToast(err.error?.message || 'Cannot join class', 'error');
      return;
    }
    const data = await res.json();
    currentActiveLiveClassId = liveId;

    document.getElementById('classroomTitle').innerText = title;
    document.getElementById('classroomMeta').innerText = `Room: ${data.room} • Authenticated as ${data.display_name} (${data.is_moderator ? 'Teacher' : 'Student'})`;

    const jitsiUrl = `https://${data.domain}/${data.room}#userInfo.displayName="${encodeURIComponent(data.display_name)}"&config.startWithAudioMuted=${data.start_muted}&config.startWithVideoMuted=${data.start_muted}`;
    document.getElementById('jitsiFrame').src = jitsiUrl;
    document.getElementById('liveClassroomModal').classList.remove('hidden');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function leaveLiveClassroom() {
  if (currentActiveLiveClassId) {
    try {
      await fetch(`${API_BASE}/live/${currentActiveLiveClassId}/leave`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${currentToken}` }
      });
    } catch (e) {
      console.error(e);
    }
  }
  document.getElementById('jitsiFrame').src = '';
  document.getElementById('liveClassroomModal').classList.add('hidden');
  showToast('You have exited the live classroom.', 'info');
}

// --- AI MODEL 1: SYLLABUS DOUBT SOLVER ---
function openDoubtModal() {
  openModal('doubtModal');
}

async function askAIDoubt() {
  const question = document.getElementById('inputDoubtQuestion').value.trim();
  if (!question) {
    showToast('Please type your question or doubt first', 'error');
    return;
  }

  const btn = document.getElementById('btnSubmitDoubt');
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Reasoning & Formulating Steps...';
  btn.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/ai/doubt/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
      body: JSON.stringify({ question: question, subject_id: currentSelectedSubjectId })
    });
    if (!res.ok) throw new Error('AI Doubt Solver error');
    const data = await res.json();

    document.getElementById('aiDoubtResultBox').classList.remove('hidden');
    document.getElementById('aiDoubtTierTag').innerText = data.grade_tier;
    document.getElementById('aiDoubtAnswerText').innerText = data.answer;

    document.getElementById('aiDoubtStepsList').innerHTML = data.step_by_step.map(s => `
      <div class="flex items-start gap-2">
        <span class="hp-chevron-slash-sm w-1.5 h-3 bg-hp-primary mt-1"></span>
        <span class="text-hp-ink font-medium">${s}</span>
      </div>
    `).join('');

    document.getElementById('aiDoubtTakeawaysList').innerHTML = data.key_takeaways.map(t => `
      <div class="flex items-start gap-2">
        <i class="fa-solid fa-check text-emerald-600 text-xs mt-1"></i>
        <span class="text-hp-charcoal">${t}</span>
      </div>
    `).join('');

    document.getElementById('aiDoubtPracticeText').innerText = data.practice_question || 'Review textbook exercises on this section.';
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Solve Doubt with AI';
    btn.disabled = false;
  }
}

// --- AI MODEL 2: SOCRATIC HOMEWORK HINTS ---
async function triggerSocraticHintForAssignment() {
  const asgnTitle = document.getElementById('submitModalTitle').innerText;
  const notes = document.getElementById('inputSubmitNotes').value;

  try {
    const res = await fetch(`${API_BASE}/ai/homework/hint`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
      body: JSON.stringify({
        assignment_id: activeSubmittingAssignmentId,
        question_text: asgnTitle,
        student_attempt: notes
      })
    });
    if (!res.ok) throw new Error('Hint error');
    const hint = await res.json();
    alert(`💡 Socratic Hint from AI Teacher:\n\n${hint.guiding_hint}\n\nConcept to Review: ${hint.clarifying_concept}\n\nThink About: ${hint.socratic_question}`);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// --- AI MODEL 4: CHAPTER QUIZ GENERATOR ---
async function generateQuizForChapter(chapterId, title) {
  openModal('quizModal');
  document.getElementById('quizModalTitle').innerText = `Revision Quiz: ${title}`;
  const body = document.getElementById('quizContentBody');
  body.innerHTML = `
    <div class="py-16 text-center text-hp-graphite">
      <i class="fa-solid fa-spinner fa-spin text-2xl text-hp-primary mb-2"></i>
      <p class="text-xs font-semibold">Generating adaptive questions from chapter curriculum...</p>
    </div>
  `;

  try {
    const res = await fetch(`${API_BASE}/ai/quiz/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
      body: JSON.stringify({ chapter_id: chapterId, num_questions: 4 })
    });
    if (!res.ok) throw new Error('Quiz generation failed');
    currentQuizData = await res.json();
    renderQuizQuestions(currentQuizData);
  } catch (err) {
    body.innerHTML = `<p class="text-xs text-red-600 py-6 text-center">${err.message}</p>`;
  }
}

function renderQuizQuestions(data) {
  const body = document.getElementById('quizContentBody');
  body.innerHTML = `
    <div class="space-y-6">
      ${data.questions.map((q, idx) => `
        <div class="p-5 rounded-hp-card bg-hp-cloud border border-hp-fog space-y-3">
          <p class="text-xs font-bold text-hp-ink">${idx + 1}. ${q.question}</p>
          <div class="space-y-2">
            ${q.options.map((opt, oIdx) => `
              <button onclick="checkQuizAnswer(${idx}, ${oIdx})" id="qOpt-${idx}-${oIdx}" class="w-full text-left p-3 rounded-hp-btn border border-hp-steel bg-white text-xs hover:border-hp-primary transition">
                <span class="font-bold mr-2 text-hp-primary">${String.fromCharCode(65 + oIdx)}.</span> ${opt}
              </button>
            `).join('')}
          </div>
          <div id="qExplain-${idx}" class="hidden p-3 rounded-hp-btn bg-white border border-hp-hairline text-xs"></div>
        </div>
      `).join('')}
    </div>
  `;
}

function checkQuizAnswer(qIdx, selectedIdx) {
  const q = currentQuizData.questions[qIdx];
  const explainBox = document.getElementById(`qExplain-${qIdx}`);
  explainBox.classList.remove('hidden');

  for (let i = 0; i < q.options.length; i++) {
    const btn = document.getElementById(`qOpt-${qIdx}-${i}`);
    if (i === q.correct_option_index) {
      btn.className = "w-full text-left p-3 rounded-hp-btn border border-emerald-600 bg-emerald-50 text-emerald-900 text-xs font-bold";
    } else if (i === selectedIdx) {
      btn.className = "w-full text-left p-3 rounded-hp-btn border border-red-600 bg-red-50 text-red-900 text-xs font-bold";
    }
  }

  explainBox.innerHTML = `
    <p class="font-bold text-hp-primary">${selectedIdx === q.correct_option_index ? '🎉 Correct Answer!' : '❌ Incorrect'}</p>
    <p class="text-[11px] text-hp-charcoal mt-1">${q.explanation}</p>
  `;
}

// --- STUDENT HOMEWORK SUBMISSION ---
let activeSubmittingAssignmentId = null;

function openSubmitHomeworkModal(assignmentId, title) {
  activeSubmittingAssignmentId = assignmentId;
  document.getElementById('submitModalTitle').innerText = title;
  openModal('submitHomeworkModal');
}

async function executeSubmitHomework() {
  if (!activeSubmittingAssignmentId) return;
  const notes = document.getElementById('inputSubmitNotes').value.trim();
  const fileInput = document.getElementById('inputSubmitFiles');

  if (!fileInput.files || fileInput.files.length === 0) {
    showToast('Please attach at least one page or PDF file', 'error');
    return;
  }

  const formData = new FormData();
  formData.append('notes', notes);
  for (let i = 0; i < fileInput.files.length; i++) {
    formData.append('files', fileInput.files[i]);
  }

  const res = await fetch(`${API_BASE}/assignments/${activeSubmittingAssignmentId}/submit`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${currentToken}` },
    body: formData
  });

  if (!res.ok) {
    const err = await res.json();
    showToast(err.error?.message || 'Submission failed', 'error');
    return;
  }

  closeModal('submitHomeworkModal');
  showToast('Homework submitted successfully to PostgreSQL!', 'success');
  loadStudentDashboard();
}

async function viewMySubmissionResult(assignmentId) {
  const res = await fetch(`${API_BASE}/assignments/${assignmentId}/my-submission`, { headers: { 'Authorization': `Bearer ${currentToken}` } });
  if (!res.ok) return;
  const sub = await res.json();

  let msg = `Submission Result:\n• Status: ${sub.status}\n• Marks: ${sub.marks_awarded !== null ? `${sub.marks_awarded}/${sub.max_marks}` : 'Under Review'}\n• Remarks: ${sub.feedback_remarks || 'None yet'}`;
  if (sub.answer_key_url) {
    msg += `\n\nAnswer Key is published! Opening solution in new window...`;
    window.open(sub.answer_key_url, '_blank');
  }
  alert(msg);
}

// --- HELPERS & MODAL MANAGEMENT ---
function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('hidden');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('hidden');
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  const bg = type === 'success' ? 'bg-hp-ink text-white border-l-4 border-hp-primary' : type === 'error' ? 'bg-hp-bloom-deep text-white' : 'bg-hp-ink text-white';
  const icon = type === 'success' ? 'fa-circle-check text-emerald-400' : type === 'error' ? 'fa-circle-xmark text-white' : 'fa-circle-info text-hp-primary-bright';

  toast.className = `px-5 py-3 rounded-hp-btn shadow-floating-modal flex items-center gap-3 text-xs font-semibold ${bg} pointer-events-auto transform transition duration-300 ease-out translate-y-2 opacity-0`;
  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  }, 10);

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
