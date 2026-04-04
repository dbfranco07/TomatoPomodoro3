// ── Auth ──────────────────────────────────────────────────────────────────
const authSection = document.getElementById('auth-section');
const appSection = document.getElementById('app-section');
const authError = document.getElementById('auth-error');
const authTitle = document.getElementById('auth-title');
const authSubmitBtn = document.getElementById('auth-submit-btn');
const authToggleLink = document.getElementById('auth-toggle-link');
const authToggleText = document.getElementById('auth-toggle-text');
const logoutUsername = document.getElementById('logout-username');

let isLoginMode = true;

function setAuthMode(loginMode) {
  isLoginMode = loginMode;
  authTitle.textContent = isLoginMode ? 'Log in' : 'Create account';
  authSubmitBtn.textContent = isLoginMode ? 'Log in' : 'Register';
  authToggleText.textContent = isLoginMode ? "Don't have an account? " : 'Already have an account? ';
  authToggleLink.textContent = isLoginMode ? 'Register' : 'Log in';
  authError.textContent = '';
}

function toggleAuthMode() {
  setAuthMode(!isLoginMode);
}

async function checkAuth() {
  try {
    const res = await fetch('/auth/me');
    if (res.ok) {
      const user = await res.json();
      showApp(user);
      return true;
    }
  } catch (e) { /* not logged in */ }
  showAuth();
  return false;
}

function showApp(user) {
  authSection.classList.add('hidden');
  appSection.classList.remove('hidden');
  if (logoutUsername) logoutUsername.textContent = user.username;
}

function showAuth() {
  appSection.classList.add('hidden');
  authSection.classList.remove('hidden');
  setAuthMode(true);
}

async function submitAuth() {
  const username = document.getElementById('auth-username').value.trim();
  const password = document.getElementById('auth-password').value;
  authError.textContent = '';

  if (!username || !password) {
    authError.textContent = 'Please enter username and password.';
    return;
  }

  const endpoint = isLoginMode ? '/auth/login' : '/auth/register';
  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (res.ok) {
      const user = await res.json();
      showApp(user);
      initApp();
    } else {
      const err = await res.json();
      authError.textContent = err.detail || 'Something went wrong.';
    }
  } catch (e) {
    authError.textContent = 'Network error. Please try again.';
  }
}

async function logout() {
  await fetch('/auth/logout', { method: 'POST' });
  showAuth();
}

// Utility: wraps fetch to handle 401 globally
async function apiFetch(url, options = {}) {
  const res = await fetch(url, options);
  if (res.status === 401) {
    showAuth();
    return null;
  }
  return res;
}
