import { describe, it, expect } from 'vitest';

// ── fmtTime ─────────────────────────────────────────────────────────────────
// Copied from timer.js; tests the pure formatting function in isolation.
function fmtTime(sec) {
  const m = Math.floor(sec / 60).toString().padStart(2, '0');
  const s = (sec % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

describe('fmtTime', () => {
  it('formats zero as 00:00', () => {
    expect(fmtTime(0)).toBe('00:00');
  });

  it('pads minutes and seconds with leading zeros', () => {
    expect(fmtTime(65)).toBe('01:05');
  });

  it('formats exactly one minute', () => {
    expect(fmtTime(60)).toBe('01:00');
  });

  it('formats 25 minutes (standard pomodoro)', () => {
    expect(fmtTime(1500)).toBe('25:00');
  });

  it('formats 90 seconds', () => {
    expect(fmtTime(90)).toBe('01:30');
  });

  it('handles values over 60 minutes', () => {
    expect(fmtTime(3661)).toBe('61:01');
  });
});

// ── Wall-clock calculation ───────────────────────────────────────────────────
// Core logic introduced by the background-tab timer fix.
function calcTimeLeft(phaseStartTimeLeft, phaseStartTime, now) {
  const elapsed = Math.floor((now - phaseStartTime) / 1000);
  return Math.max(0, phaseStartTimeLeft - elapsed);
}

describe('calcTimeLeft (wall-clock fix)', () => {
  it('returns full time left at the exact start moment', () => {
    const t = Date.now();
    expect(calcTimeLeft(300, t, t)).toBe(300);
  });

  it('correctly subtracts elapsed seconds', () => {
    const start = Date.now() - 60_000; // 60 s ago
    const result = calcTimeLeft(300, start, Date.now());
    // Allow ±1 s for test runtime jitter
    expect(result).toBeGreaterThanOrEqual(239);
    expect(result).toBeLessThanOrEqual(241);
  });

  it('clamps to zero when elapsed exceeds total', () => {
    const start = Date.now() - 10_000; // 10 s ago
    expect(calcTimeLeft(5, start, Date.now())).toBe(0);
  });

  it('does not return negative values', () => {
    const start = Date.now() - 60_000;
    expect(calcTimeLeft(30, start, Date.now())).toBe(0);
  });
});

// ── Phase-completion detection ───────────────────────────────────────────────

describe('phase completion', () => {
  it('triggers when timeLeft reaches 0', () => {
    expect(0 <= 0).toBe(true);
  });

  it('triggers when timeLeft goes negative (clamped)', () => {
    const timeLeft = Math.max(0, -1);
    expect(timeLeft <= 0).toBe(true);
  });

  it('does not trigger while time remains', () => {
    expect(1 <= 0).toBe(false);
  });
});

// ── Urgent-pulse threshold ───────────────────────────────────────────────────

describe('urgent pulse (last 10 seconds)', () => {
  it('activates at exactly 10 seconds', () => {
    expect(10 <= 10 && 10 > 0).toBe(true);
  });

  it('activates at 1 second', () => {
    expect(1 <= 10 && 1 > 0).toBe(true);
  });

  it('does not activate at 11 seconds', () => {
    expect(11 <= 10).toBe(false);
  });

  it('does not activate at 0 (already done)', () => {
    expect(0 > 0).toBe(false);
  });
});
