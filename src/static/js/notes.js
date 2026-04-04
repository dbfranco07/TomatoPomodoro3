// ── Notes ─────────────────────────────────────────────────────────────────
const notesArea = document.getElementById('notes-area');
const notesStatus = document.getElementById('notes-status');
const notesList = document.getElementById('notes-list');
const notesEmpty = document.getElementById('notes-empty');
const noteEditor = document.getElementById('note-editor');
const notePlaceholder = document.getElementById('note-placeholder');
const noteTitleInput = document.getElementById('note-title-input');
const notesSearch = document.getElementById('notes-search');

let notesSaveTimer = null;
let titleSaveTimer = null;
let currentNoteId = null;
let notesData = [];

async function fetchNotesList() {
  const res = await apiFetch('/notes');
  if (!res) return;
  const data = await res.json();
  notesData = data.notes;
  renderNotesList();
}

function renderNotesList() {
  notesList.innerHTML = '';
  const query = notesSearch.value.trim().toLowerCase();
  const filtered = query
    ? notesData.filter(n => n.title.toLowerCase().includes(query))
    : notesData;

  notesEmpty.classList.toggle('hidden', notesData.length > 0);

  filtered.forEach(note => {
    const item = document.createElement('div');
    const isActive = note.id === currentNoteId;
    item.className = `cursor-pointer px-3 py-2 rounded-lg text-sm truncate whitespace-nowrap flex-shrink-0 transition ${
      isActive
        ? 'bg-red-500 text-white font-semibold'
        : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
    }`;
    item.textContent = note.title;
    item.title = note.title;
    item.onclick = () => selectNote(note.id);
    notesList.appendChild(item);
  });
}

async function selectNote(noteId) {
  // Save current note before switching
  if (currentNoteId && notesSaveTimer) {
    clearTimeout(notesSaveTimer);
    await saveCurrentNote();
  }
  if (currentNoteId && titleSaveTimer) {
    clearTimeout(titleSaveTimer);
    await saveCurrentTitle();
  }

  const res = await apiFetch(`/notes/${noteId}`);
  if (!res) return;
  const note = await res.json();

  currentNoteId = note.id;
  noteTitleInput.value = note.title;
  notesArea.value = note.content;

  noteEditor.classList.remove('hidden');
  notePlaceholder.classList.add('hidden');
  renderNotesList();
}

async function promptCreateNote() {
  const title = prompt('Enter a name for your new note:');
  if (!title || !title.trim()) return;

  const res = await apiFetch('/notes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: title.trim() })
  });
  if (!res) return;
  const note = await res.json();

  // Add to list and select it
  notesData.unshift({ id: note.id, title: note.title, updated_at: new Date().toISOString() });
  renderNotesList();
  await selectNote(note.id);
}

async function saveCurrentNote() {
  if (!currentNoteId) return;
  notesStatus.textContent = 'Saving…';
  await apiFetch(`/notes/${currentNoteId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content: notesArea.value })
  });
  notesStatus.textContent = 'Saved';
  setTimeout(() => { notesStatus.textContent = ''; }, 2000);
}

async function saveCurrentTitle() {
  if (!currentNoteId) return;
  const newTitle = noteTitleInput.value.trim();
  if (!newTitle) return;

  await apiFetch(`/notes/${currentNoteId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: newTitle })
  });

  // Update local data
  const note = notesData.find(n => n.id === currentNoteId);
  if (note) note.title = newTitle;
  renderNotesList();
}

async function confirmDeleteNote() {
  if (!currentNoteId) return;
  const note = notesData.find(n => n.id === currentNoteId);
  if (!confirm(`Delete "${note ? note.title : 'this note'}"?`)) return;

  await apiFetch(`/notes/${currentNoteId}`, { method: 'DELETE' });

  // Remove from list
  notesData = notesData.filter(n => n.id !== currentNoteId);
  currentNoteId = null;
  notesArea.value = '';
  noteTitleInput.value = '';
  noteEditor.classList.add('hidden');
  notePlaceholder.classList.remove('hidden');
  renderNotesList();

  // Auto-select the first remaining note
  if (notesData.length > 0) {
    await selectNote(notesData[0].id);
  }
}

function initNotes() {
  notesArea.addEventListener('input', () => {
    clearTimeout(notesSaveTimer);
    notesStatus.textContent = '';
    notesSaveTimer = setTimeout(saveCurrentNote, 800);
  });

  noteTitleInput.addEventListener('input', () => {
    clearTimeout(titleSaveTimer);
    titleSaveTimer = setTimeout(saveCurrentTitle, 800);
  });

  notesSearch.addEventListener('input', () => {
    renderNotesList();
  });
}
