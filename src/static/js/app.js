// ── Bootstrap ──────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initTasks();
  initNotes();
  fetchTasks();
  fetchNotes();
  loadAISettings();
});
