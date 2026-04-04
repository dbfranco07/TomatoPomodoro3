// ── Bootstrap ──────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  const loggedIn = await checkAuth();
  if (loggedIn) {
    initApp();
  }
});

function initApp() {
  initTasks();
  initNotes();
  fetchTasks();
  fetchNotes();
  loadAISettings();
}
