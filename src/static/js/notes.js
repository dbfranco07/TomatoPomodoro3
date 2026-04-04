// ── Notes ─────────────────────────────────────────────────────────────────
const notesArea = document.getElementById('notes-area');
const notesStatus = document.getElementById('notes-status');
let notesSaveTimer = null;

async function fetchNotes() {
  const res = await apiFetch('/notes');
  if (!res) return;
  const data = await res.json();
  notesArea.value = data.content;
}

async function saveNotes() {
  notesStatus.textContent = 'Saving\u2026';
  await apiFetch('/notes', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content: notesArea.value })
  });
  notesStatus.textContent = 'Saved';
  setTimeout(() => { notesStatus.textContent = ''; }, 2000);
}

function initNotes() {
  notesArea.addEventListener('input', () => {
    clearTimeout(notesSaveTimer);
    notesStatus.textContent = '';
    notesSaveTimer = setTimeout(saveNotes, 800);
  });
}
