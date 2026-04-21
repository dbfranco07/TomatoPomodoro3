// ── Document Picture-in-Picture ────────────────────────────────────────────
// Requires Chromium 116+ / Edge 116+. The PiP button is hidden on
// unsupported browsers. The PiP window shares the same JS execution context
// so togglePause() / stopSession() from timer.js work directly.

let pipWindow = null;
let pipSyncInterval = null;

function initPip() {
  const btn = document.getElementById('btn-pip');
  if (!btn) return;
  if (!('documentPictureInPicture' in window)) {
    btn.classList.add('hidden');
  }
}

async function togglePip() {
  if (pipWindow && !pipWindow.closed) {
    pipWindow.close();
    return;
  }
  await openPip();
}

async function openPip() {
  pipWindow = await window.documentPictureInPicture.requestWindow({
    width: 320,
    height: 510,
  });

  // Copy all <style> elements from the main document into the PiP doc
  document.querySelectorAll('style').forEach(s => {
    const clone = pipWindow.document.createElement('style');
    clone.textContent = s.textContent;
    pipWindow.document.head.appendChild(clone);
  });

  // Mirror dark mode
  if (document.documentElement.classList.contains('dark')) {
    pipWindow.document.documentElement.classList.add('dark');
  }

  pipWindow.document.body.style.cssText =
    "font-family:'Segoe UI',sans-serif; margin:0; padding:12px; box-sizing:border-box;";
  pipWindow.document.body.className =
    'bg-stone-100 dark:bg-stone-900 min-h-screen';

  pipWindow.document.body.innerHTML = `
    <div id="pip-timer-card"
      class="bg-white dark:bg-stone-800 rounded-2xl shadow p-5 flex flex-col items-center gap-3 mb-3">
      <div id="pip-badge"
        class="text-xs font-semibold uppercase tracking-widest px-3 py-1 rounded-full
               bg-stone-100 text-stone-500">
        Stopped
      </div>
      <div id="pip-time"
        class="text-5xl font-bold text-stone-800 dark:text-stone-100"
        style="font-variant-numeric:tabular-nums;">
        --:--
      </div>
      <div id="pip-session" class="text-xs text-stone-500 dark:text-stone-400">Session: 0</div>
      <div class="flex gap-2 mt-1">
        <button id="pip-pause-btn"
          class="hidden bg-amber-500 hover:bg-amber-600 text-white font-semibold text-sm
                 px-4 py-2 rounded-lg transition">
          Pause
        </button>
        <button id="pip-stop-btn"
          class="bg-stone-200 dark:bg-stone-600 hover:bg-stone-300 dark:hover:bg-stone-500
                 text-stone-700 dark:text-stone-200 font-semibold text-sm
                 px-4 py-2 rounded-lg transition">
          Stop
        </button>
      </div>
    </div>

    <div class="bg-white dark:bg-stone-800 rounded-2xl shadow p-4 flex flex-col gap-2">
      <div class="text-xs font-semibold text-stone-500 dark:text-stone-400 uppercase tracking-widest">
        Quick Notes
      </div>
      <textarea id="pip-notes"
        placeholder="Jot notes here…"
        class="w-full resize-none border border-stone-200 dark:border-stone-600
               dark:bg-stone-700 rounded-lg px-3 py-2 text-stone-700 dark:text-stone-200
               text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
        style="height:148px;"></textarea>
    </div>
  `;

  // Wire controls back to main-window timer functions
  const pauseBtn = pipWindow.document.getElementById('pip-pause-btn');
  const stopBtn  = pipWindow.document.getElementById('pip-stop-btn');
  pauseBtn.onclick = () => { togglePause(); syncPipDisplay(); };
  stopBtn.onclick  = () => { stopSession(); syncPipDisplay(); };

  // Notes textarea two-way sync
  const mainNotes = document.getElementById('notes-area');
  const pipNotes  = pipWindow.document.getElementById('pip-notes');
  pipNotes.value  = mainNotes.value;

  pipNotes.addEventListener('input', () => {
    if (mainNotes.value !== pipNotes.value) {
      mainNotes.value = pipNotes.value;
      mainNotes.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });

  mainNotes.addEventListener('input', () => {
    if (pipNotes && pipNotes.value !== mainNotes.value) {
      pipNotes.value = mainNotes.value;
    }
  });

  // Keep the PiP timer display in sync
  syncPipDisplay();
  pipSyncInterval = setInterval(syncPipDisplay, 500);

  pipWindow.addEventListener('pagehide', () => {
    clearInterval(pipSyncInterval);
    pipSyncInterval = null;
    pipWindow = null;
    _updatePipBtn();
  });

  _updatePipBtn();
}

function syncPipDisplay() {
  if (!pipWindow || pipWindow.closed) return;

  const pd = pipWindow.document;
  const pipTime    = pd.getElementById('pip-time');
  const pipBadge   = pd.getElementById('pip-badge');
  const pipSession = pd.getElementById('pip-session');
  const pipPause   = pd.getElementById('pip-pause-btn');
  if (!pipTime) return;

  pipTime.textContent    = document.getElementById('timer-display').textContent;
  pipSession.textContent = document.getElementById('session-display').textContent;

  const mainBadge = document.getElementById('status-badge');
  pipBadge.textContent = mainBadge.textContent;
  pipBadge.className   = mainBadge.className;

  const mainPause = document.getElementById('btn-pause');
  if (!mainPause.classList.contains('hidden')) {
    pipPause.classList.remove('hidden');
    pipPause.textContent = mainPause.textContent;
  } else {
    pipPause.classList.add('hidden');
  }

  // Mirror dark-mode changes
  const isDark = document.documentElement.classList.contains('dark');
  pd.documentElement.classList.toggle('dark', isDark);
}

function _updatePipBtn() {
  const btn = document.getElementById('btn-pip');
  if (!btn) return;
  btn.textContent = (pipWindow && !pipWindow.closed) ? 'Close PiP' : 'PiP';
}
