// ── Todo list ──────────────────────────────────────────────────────────────
const taskList = document.getElementById('task-list');
let allTasks = [];
let subtasksExpanded = true; // global expand/collapse for subtasks

async function fetchTasks() {
  const res = await apiFetch('/tasks');
  if (!res) return;
  allTasks = await res.json();
  renderTasks(allTasks);
}

// ── Rendering ──────────────────────────────────────────────────────────────

function renderTasks(tasks) {
  taskList.innerHTML = '';
  const parentTasks = tasks.filter(t => !t.parent_id);
  parentTasks.forEach(t => {
    taskList.appendChild(buildTaskEl(t, false));
    // Render subtasks
    const subtasks = tasks.filter(s => s.parent_id === t.id);
    subtasks.forEach(s => {
      const subEl = buildTaskEl(s, true);
      if (!subtasksExpanded) subEl.classList.add('hidden');
      subEl.classList.add('subtask-item');
      taskList.appendChild(subEl);
    });
  });
}

function buildTaskEl(task, isSubtask) {
  const li = document.createElement('li');
  li.dataset.id = task.id;
  if (task.parent_id) li.dataset.parentId = task.parent_id;
  li.className = 'task-item flex flex-col bg-stone-50 dark:bg-stone-700 border border-stone-200 dark:border-stone-600 rounded-lg select-none'
    + (isSubtask ? ' ml-8 border-l-2 border-l-red-300 dark:border-l-red-700' : '');

  // Main row
  const row = document.createElement('div');
  row.className = 'flex items-center gap-2 px-3 py-2';

  // Drag handle
  const handle = document.createElement('span');
  handle.className = 'text-stone-300 dark:text-stone-500 cursor-grab text-lg leading-none pr-1';
  handle.innerHTML = '&#x2261;';
  row.appendChild(handle);

  // Checkbox
  const cb = document.createElement('input');
  cb.type = 'checkbox';
  cb.checked = task.checked;
  cb.className = 'w-4 h-4 accent-red-500 cursor-pointer shrink-0';
  cb.onchange = () => toggleTask(task.id, cb.checked, textSpan);
  row.appendChild(cb);

  // Text
  const textSpan = document.createElement('span');
  textSpan.textContent = task.text;
  textSpan.className = 'flex-1 text-stone-700 dark:text-stone-200 text-sm cursor-pointer'
    + (task.checked ? ' line-through !text-stone-400' : '');
  row.appendChild(textSpan);

  // Details indicator (shows a small icon if details exist)
  if (task.details) {
    const detailsIcon = document.createElement('span');
    detailsIcon.className = 'text-stone-400 dark:text-stone-500 text-xs';
    detailsIcon.title = 'Has details (double-click to view)';
    detailsIcon.innerHTML = '&#9998;';
    row.appendChild(detailsIcon);
  }

  // Add subtask button (only for parent tasks)
  if (!isSubtask) {
    const addSubBtn = document.createElement('button');
    addSubBtn.title = 'Add subtask';
    addSubBtn.innerHTML = '+sub';
    addSubBtn.className = 'text-stone-400 hover:text-red-500 text-xs font-medium transition';
    addSubBtn.onclick = (e) => { e.stopPropagation(); showAddSubtaskInput(task.id, li); };
    row.appendChild(addSubBtn);
  }

  // Delete button with inline confirmation
  const delWrap = document.createElement('div');
  delWrap.className = 'flex items-center gap-1 ml-1';

  const del = document.createElement('button');
  del.innerHTML = '&times;';
  del.className = 'text-stone-300 hover:text-red-500 font-bold text-lg leading-none transition';
  del.onclick = (e) => { e.stopPropagation(); showDeleteConfirm(delWrap, del, task.id); };
  delWrap.appendChild(del);

  row.appendChild(delWrap);
  li.appendChild(row);

  // Details panel (hidden by default, shown on double-click)
  const detailsPanel = document.createElement('div');
  detailsPanel.className = 'task-details hidden px-3 pb-3';
  detailsPanel.dataset.taskId = task.id;

  const detailsTextarea = document.createElement('textarea');
  detailsTextarea.placeholder = 'Add details...';
  detailsTextarea.value = task.details || '';
  detailsTextarea.className = 'w-full h-20 resize-y border border-stone-200 dark:border-stone-600 dark:bg-stone-600 rounded-lg px-3 py-2 text-stone-700 dark:text-stone-200 text-sm focus:outline-none focus:ring-2 focus:ring-red-400';

  let detailsSaveTimeout;
  detailsTextarea.oninput = () => {
    clearTimeout(detailsSaveTimeout);
    detailsSaveTimeout = setTimeout(() => {
      saveTaskDetails(task.id, detailsTextarea.value);
    }, 800);
  };

  detailsPanel.appendChild(detailsTextarea);
  li.appendChild(detailsPanel);

  // Double-click to toggle details
  row.addEventListener('dblclick', (e) => {
    e.preventDefault();
    detailsPanel.classList.toggle('hidden');
    if (!detailsPanel.classList.contains('hidden')) {
      detailsTextarea.focus();
    }
  });

  return li;
}

// ── Subtask input ──────────────────────────────────────────────────────────

function showAddSubtaskInput(parentId, parentEl) {
  // Check if already showing
  if (parentEl.querySelector('.subtask-input-wrap')) return;

  const wrap = document.createElement('div');
  wrap.className = 'subtask-input-wrap flex gap-2 px-3 pb-2 ml-6';

  const input = document.createElement('input');
  input.type = 'text';
  input.placeholder = 'Subtask name...';
  input.className = 'border border-stone-300 dark:border-stone-600 dark:bg-stone-600 rounded-lg px-2 py-1 flex-1 text-stone-800 dark:text-stone-100 text-sm focus:outline-none focus:ring-2 focus:ring-red-400';

  const okBtn = document.createElement('button');
  okBtn.textContent = 'Add';
  okBtn.className = 'bg-red-500 hover:bg-red-600 text-white text-xs font-semibold px-3 py-1 rounded-lg transition';
  okBtn.onclick = () => addSubtask(parentId, input.value.trim(), wrap);

  const cancelBtn = document.createElement('button');
  cancelBtn.textContent = 'Cancel';
  cancelBtn.className = 'bg-stone-200 dark:bg-stone-600 hover:bg-stone-300 dark:hover:bg-stone-500 text-stone-600 dark:text-stone-300 text-xs font-semibold px-3 py-1 rounded-lg transition';
  cancelBtn.onclick = () => wrap.remove();

  input.onkeydown = (e) => {
    if (e.key === 'Enter') okBtn.click();
    if (e.key === 'Escape') wrap.remove();
  };

  wrap.appendChild(input);
  wrap.appendChild(okBtn);
  wrap.appendChild(cancelBtn);
  parentEl.appendChild(wrap);
  input.focus();
}

async function addSubtask(parentId, text, inputWrap) {
  if (!text) return;
  const res = await apiFetch('/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, parent_id: parentId })
  });
  if (!res) return;
  const task = await res.json();
  allTasks.push(task);
  inputWrap.remove();

  // Insert subtask element after the parent and its existing subtasks
  const parentEl = taskList.querySelector(`[data-id="${parentId}"]`);
  let insertAfter = parentEl;
  let next = parentEl.nextElementSibling;
  while (next && next.dataset.parentId === parentId) {
    insertAfter = next;
    next = next.nextElementSibling;
  }

  const subEl = buildTaskEl(task, true);
  subEl.classList.add('subtask-item', 'task-enter');
  if (!subtasksExpanded) subEl.classList.add('hidden');
  insertAfter.after(subEl);
}

// ── Task actions ───────────────────────────────────────────────────────────

async function addTask() {
  const input = document.getElementById('new-task-input');
  const text = input.value.trim();
  if (!text) return;
  const res = await apiFetch('/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  if (!res) return;
  const task = await res.json();
  allTasks.push(task);
  const el = buildTaskEl(task, false);
  el.classList.add('task-enter');
  taskList.appendChild(el);
  input.value = '';
}

async function toggleTask(id, checked, textSpan) {
  await apiFetch(`/tasks/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ checked })
  });
  if (checked) {
    textSpan.classList.add('line-through', '!text-stone-400');
    textSpan.classList.remove('text-stone-700', 'dark:text-stone-200');
  } else {
    textSpan.classList.remove('line-through', '!text-stone-400');
    textSpan.classList.add('text-stone-700', 'dark:text-stone-200');
  }
  // Update local state
  const t = allTasks.find(t => t.id === id);
  if (t) t.checked = checked;
}

async function saveTaskDetails(id, details) {
  await apiFetch(`/tasks/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ details })
  });
  // Update local state
  const t = allTasks.find(t => t.id === id);
  if (t) t.details = details;
}

function showDeleteConfirm(wrap, delBtn, taskId) {
  if (wrap.dataset.confirming) return;
  wrap.dataset.confirming = 'true';

  delBtn.classList.add('hidden');

  const yes = document.createElement('button');
  yes.textContent = 'Delete?';
  yes.className = 'text-red-500 text-xs font-semibold hover:text-red-700 transition';
  yes.onclick = (e) => { e.stopPropagation(); deleteTask(taskId); };

  const no = document.createElement('button');
  no.textContent = 'No';
  no.className = 'text-stone-400 text-xs font-medium hover:text-stone-600 transition';
  no.onclick = (e) => {
    e.stopPropagation();
    yes.remove();
    no.remove();
    delBtn.classList.remove('hidden');
    delete wrap.dataset.confirming;
  };

  wrap.appendChild(yes);
  wrap.appendChild(no);

  setTimeout(() => {
    if (wrap.dataset.confirming) {
      yes.remove();
      no.remove();
      delBtn.classList.remove('hidden');
      delete wrap.dataset.confirming;
    }
  }, 3000);
}

async function deleteTask(id) {
  await apiFetch(`/tasks/${id}`, { method: 'DELETE' });

  // Remove from local state (task + its subtasks)
  const subtaskIds = allTasks.filter(t => t.parent_id === id).map(t => t.id);
  allTasks = allTasks.filter(t => t.id !== id && t.parent_id !== id);

  // Animate out the task element
  const el = taskList.querySelector(`[data-id="${id}"]`);
  if (el) {
    el.classList.add('task-exit');
    el.addEventListener('animationend', () => el.remove(), { once: true });
  }

  // Also remove subtask elements
  subtaskIds.forEach(sid => {
    const subEl = taskList.querySelector(`[data-id="${sid}"]`);
    if (subEl) {
      subEl.classList.add('task-exit');
      subEl.addEventListener('animationend', () => subEl.remove(), { once: true });
    }
  });
}

// ── Expand / Collapse subtasks toggle ──────────────────────────────────────

function toggleSubtasksExpanded() {
  subtasksExpanded = !subtasksExpanded;
  const subtaskEls = taskList.querySelectorAll('.subtask-item');
  subtaskEls.forEach(el => {
    el.classList.toggle('hidden', !subtasksExpanded);
  });

  // Update button text
  const btn = document.getElementById('toggle-subtasks-btn');
  if (btn) {
    btn.textContent = subtasksExpanded ? 'Collapse subtasks' : 'Expand subtasks';
  }

  // Update chevron
  const chevron = document.getElementById('subtasks-chevron');
  if (chevron) {
    chevron.classList.toggle('collapsed', !subtasksExpanded);
  }

  localStorage.setItem('subtasks-expanded', subtasksExpanded ? '1' : '0');
}

function restoreSubtasksState() {
  const stored = localStorage.getItem('subtasks-expanded');
  if (stored !== null) {
    subtasksExpanded = stored === '1';
  }
  const btn = document.getElementById('toggle-subtasks-btn');
  if (btn) {
    btn.textContent = subtasksExpanded ? 'Collapse subtasks' : 'Expand subtasks';
  }
  const chevron = document.getElementById('subtasks-chevron');
  if (chevron) {
    chevron.classList.toggle('collapsed', !subtasksExpanded);
  }
}

// ── Init ───────────────────────────────────────────────────────────────────

function initTasks() {
  restoreSubtasksState();
  Sortable.create(taskList, {
    animation: 150,
    ghostClass: 'sortable-ghost',
    dragClass: 'sortable-drag',
    onEnd: async () => {
      const ids = [...taskList.querySelectorAll('[data-id]')].map(el => el.dataset.id);
      await apiFetch('/tasks/reorder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids })
      });
    }
  });
}
