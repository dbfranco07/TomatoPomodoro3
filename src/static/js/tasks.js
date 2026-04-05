// ── Todo list ──────────────────────────────────────────────────────────────
const taskList = document.getElementById('task-list');

async function fetchTasks() {
  const res = await apiFetch('/tasks');
  if (!res) return;
  const tasks = await res.json();
  renderTasks(tasks);
}

function renderTasks(tasks) {
  taskList.innerHTML = '';
  tasks.forEach(t => taskList.appendChild(buildTaskEl(t)));
}

function buildTaskEl(task) {
  const li = document.createElement('li');
  li.dataset.id = task.id;
  li.className = 'task-item flex items-center gap-2 bg-stone-50 dark:bg-stone-700 border border-stone-200 dark:border-stone-600 rounded-lg px-3 py-2 select-none';

  // Drag handle
  const handle = document.createElement('span');
  handle.className = 'text-stone-300 dark:text-stone-500 cursor-grab text-lg leading-none pr-1';
  handle.innerHTML = '&#x2261;';
  li.appendChild(handle);

  // Checkbox
  const cb = document.createElement('input');
  cb.type = 'checkbox';
  cb.checked = task.checked;
  cb.className = 'w-4 h-4 accent-red-500 cursor-pointer shrink-0';
  cb.onchange = () => toggleTask(task.id, cb.checked, textSpan);
  li.appendChild(cb);

  // Text
  const textSpan = document.createElement('span');
  textSpan.textContent = task.text;
  textSpan.className = 'flex-1 text-stone-700 dark:text-stone-200 text-sm' + (task.checked ? ' line-through !text-stone-400' : '');
  li.appendChild(textSpan);

  // Delete button with inline confirmation
  const delWrap = document.createElement('div');
  delWrap.className = 'flex items-center gap-1 ml-1';

  const del = document.createElement('button');
  del.innerHTML = '&times;';
  del.className = 'text-stone-300 hover:text-red-500 font-bold text-lg leading-none transition';
  del.onclick = () => showDeleteConfirm(delWrap, del, task.id);
  delWrap.appendChild(del);

  li.appendChild(delWrap);

  return li;
}

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
  const el = buildTaskEl(task);
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
}

function showDeleteConfirm(wrap, delBtn, taskId) {
  // Already showing confirm? ignore
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

  // Auto-dismiss after 3 seconds
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
  const el = taskList.querySelector(`[data-id="${id}"]`);
  if (el) {
    el.classList.add('task-exit');
    el.addEventListener('animationend', () => el.remove(), { once: true });
  }
}

function initTasks() {
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
