// ── Timer state ────────────────────────────────────────────────────────────
let workSec = 0;
let breakSec = 0;
let timeLeft = 0;
let totalPhaseTime = 0;
let isWork = true;
let isRunning = false;
let isPaused = false;
let sessionNo = 0;
let timerInterval = null;

const sound = document.getElementById('notif-sound');
const timerDisplay = document.getElementById('timer-display');
const statusBadge = document.getElementById('status-badge');
const sessionDisplay = document.getElementById('session-display');
const modal = document.getElementById('modal-overlay');
const modalTitle = document.getElementById('modal-title');
const modalMessage = document.getElementById('modal-message');
const btnStart = document.getElementById('btn-start');
const btnPause = document.getElementById('btn-pause');
const timerPanel = document.getElementById('timer-panel');
const progressRing = document.getElementById('progress-ring');
const timerError = document.getElementById('timer-error');

const RING_CIRCUMFERENCE = 2 * Math.PI * 115; // r=115

function fmtTime(sec) {
  const m = Math.floor(sec / 60).toString().padStart(2, '0');
  const s = (sec % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

function updateDisplay() {
  timerDisplay.textContent = timeLeft >= 0 ? fmtTime(timeLeft) : '--:--';
  sessionDisplay.textContent = `Session: ${sessionNo}`;
}

function updateProgressRing() {
  if (!isRunning && !isPaused) {
    // Stopped: empty ring
    progressRing.style.strokeDashoffset = RING_CIRCUMFERENCE;
    progressRing.setAttribute('stroke', '#d6d3d1');
    return;
  }
  const progress = totalPhaseTime > 0 ? timeLeft / totalPhaseTime : 0;
  const offset = RING_CIRCUMFERENCE * (1 - progress);
  progressRing.style.strokeDashoffset = offset;
  progressRing.setAttribute('stroke', isWork ? '#ef4444' : '#22c55e');
}

function setTimerPanelState(state) {
  timerPanel.className = timerPanel.className.replace(/state-\w+/g, '').trim();
  timerPanel.classList.add(`state-${state}`);
}

function setStatusBadge(text, color) {
  statusBadge.textContent = text;
  statusBadge.className = `text-sm font-semibold uppercase tracking-widest px-4 py-1 rounded-full ${color}`;
}

function updateUrgentPulse() {
  if (isRunning && !isPaused && timeLeft <= 10 && timeLeft > 0) {
    timerDisplay.classList.add('timer-urgent');
  } else {
    timerDisplay.classList.remove('timer-urgent');
  }
}

function startSession() {
  const wInput = parseFloat(document.getElementById('input-work').value);
  const bInput = parseFloat(document.getElementById('input-break').value);

  if (isNaN(wInput) || isNaN(bInput) || wInput <= 0 || bInput <= 0) {
    timerError.textContent = 'Enter valid work and break times (> 0 min)';
    setTimeout(() => { timerError.textContent = ''; }, 3000);
    return;
  }
  timerError.textContent = '';

  workSec = Math.round(wInput * 60);
  breakSec = Math.round(bInput * 60);
  isWork = true;
  sessionNo = 0;
  timeLeft = workSec;
  totalPhaseTime = workSec;
  isRunning = true;
  isPaused = false;

  btnStart.classList.add('hidden');
  btnPause.classList.remove('hidden');
  btnPause.textContent = 'Pause';

  setStatusBadge('Working...', 'bg-red-100 text-red-600');
  setTimerPanelState('working');
  updateDisplay();
  updateProgressRing();
  clearInterval(timerInterval);
  timerInterval = setInterval(tick, 1000);
}

function stopSession() {
  clearInterval(timerInterval);
  timerInterval = null;
  isRunning = false;
  isPaused = false;
  isWork = true;
  sessionNo = 0;
  timeLeft = 0;
  totalPhaseTime = 0;

  btnStart.classList.remove('hidden');
  btnPause.classList.add('hidden');

  setStatusBadge('Stopped', 'bg-stone-100 text-stone-500');
  setTimerPanelState('stopped');
  timerDisplay.textContent = '--:--';
  timerDisplay.classList.remove('timer-urgent');
  sessionDisplay.textContent = 'Session: 0';
  updateProgressRing();
  sound.pause();
  sound.currentTime = 0;
  modal.classList.remove('active');
}

function togglePause() {
  if (!isRunning) return;

  if (isPaused) {
    isPaused = false;
    btnPause.textContent = 'Pause';
    timerInterval = setInterval(tick, 1000);

    if (isWork) {
      setStatusBadge('Working...', 'bg-red-100 text-red-600');
      setTimerPanelState('working');
    } else {
      setStatusBadge('On a Break...', 'bg-green-100 text-green-600');
      setTimerPanelState('break');
    }
  } else {
    isPaused = true;
    btnPause.textContent = 'Resume';
    clearInterval(timerInterval);
    timerInterval = null;

    setStatusBadge('Paused', 'bg-amber-100 text-amber-600');
    setTimerPanelState('paused');
  }
}

function tick() {
  if (!isRunning || isPaused) return;
  timeLeft--;
  updateDisplay();
  updateProgressRing();
  updateUrgentPulse();
  if (timeLeft <= 0) {
    clearInterval(timerInterval);
    timerInterval = null;
    timerDisplay.classList.remove('timer-urgent');
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
  totalPhaseTime = timeLeft;
  isPaused = false;
  btnPause.textContent = 'Pause';

  if (isWork) {
    setStatusBadge('Working...', 'bg-red-100 text-red-600');
    setTimerPanelState('working');
  } else {
    setStatusBadge('On a Break...', 'bg-green-100 text-green-600');
    setTimerPanelState('break');
  }

  updateDisplay();
  updateProgressRing();
  isRunning = true;
  timerInterval = setInterval(tick, 1000);
}
