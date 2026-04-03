// ── Timer state ────────────────────────────────────────────────────────────
let workSec = 0;
let breakSec = 0;
let timeLeft = 0;
let isWork = true;
let isRunning = false;
let sessionNo = 0;
let timerInterval = null;

const sound = document.getElementById('notif-sound');
const timerDisplay = document.getElementById('timer-display');
const statusBadge = document.getElementById('status-badge');
const sessionDisplay = document.getElementById('session-display');
const modal = document.getElementById('modal-overlay');
const modalTitle = document.getElementById('modal-title');
const modalMessage = document.getElementById('modal-message');

function fmtTime(sec) {
  const m = Math.floor(sec / 60).toString().padStart(2, '0');
  const s = (sec % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

function updateDisplay() {
  timerDisplay.textContent = timeLeft >= 0 ? fmtTime(timeLeft) : '--:--';
  sessionDisplay.textContent = `Session No.: ${sessionNo}`;
}

function setStatusBadge(text, color) {
  statusBadge.textContent = text;
  statusBadge.className = `text-sm font-semibold uppercase tracking-widest px-4 py-1 rounded-full ${color}`;
}

function startSession() {
  const wInput = parseFloat(document.getElementById('input-work').value);
  const bInput = parseFloat(document.getElementById('input-break').value);

  if (isNaN(wInput) || isNaN(bInput) || wInput <= 0 || bInput <= 0) {
    alert('Please enter valid work and break times (minutes > 0).');
    return;
  }

  workSec = Math.round(wInput * 60);
  breakSec = Math.round(bInput * 60);
  isWork = true;
  sessionNo = 0;
  timeLeft = workSec;
  isRunning = true;

  setStatusBadge('Working...', 'bg-red-100 text-red-600');
  updateDisplay();
  clearInterval(timerInterval);
  timerInterval = setInterval(tick, 1000);
}

function stopSession() {
  clearInterval(timerInterval);
  timerInterval = null;
  isRunning = false;
  isWork = true;
  sessionNo = 0;
  timeLeft = 0;
  setStatusBadge('Stopped', 'bg-stone-100 text-stone-500');
  timerDisplay.textContent = '--:--';
  sessionDisplay.textContent = 'Session No.: 0';
  sound.pause();
  sound.currentTime = 0;
  modal.classList.remove('active');
}

function tick() {
  if (!isRunning) return;
  timeLeft--;
  updateDisplay();
  if (timeLeft <= 0) {
    clearInterval(timerInterval);
    timerInterval = null;
    phaseComplete();
  }
}

function phaseComplete() {
  sound.currentTime = 0;
  sound.play().catch(() => {});

  if (isWork) {
    sessionNo++;
    updateDisplay();
    modalTitle.textContent = 'Pause Work!';
    modalMessage.textContent = `Work session #${sessionNo} complete! Time for a ${fmtTime(breakSec)} break.`;
  } else {
    modalTitle.textContent = 'Resume Work!';
    modalMessage.textContent = `Break over! Start your next work session (${fmtTime(workSec)}).`;
  }

  modal.classList.add('active');
}

function dismissModal() {
  sound.pause();
  sound.currentTime = 0;
  modal.classList.remove('active');

  // Switch phase
  isWork = !isWork;
  timeLeft = isWork ? workSec : breakSec;

  if (isWork) {
    setStatusBadge('Working...', 'bg-red-100 text-red-600');
  } else {
    setStatusBadge('On a Break...', 'bg-green-100 text-green-600');
  }

  updateDisplay();
  isRunning = true;
  timerInterval = setInterval(tick, 1000);
}
