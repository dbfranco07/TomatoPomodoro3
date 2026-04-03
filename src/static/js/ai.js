// ── AI Assistant ───────────────────────────────────────────────────────────
let currentAction = 'summarize';

function setAction(action) {
  currentAction = action;
  document.querySelectorAll('.action-btn').forEach(btn => {
    btn.classList.remove('bg-red-500', 'text-white');
    btn.classList.add('bg-stone-100', 'text-stone-600');
  });
  const active = document.getElementById(`btn-action-${action}`);
  active.classList.remove('bg-stone-100', 'text-stone-600');
  active.classList.add('bg-red-500', 'text-white');
  document.getElementById('custom-prompt-wrap').classList.toggle('hidden', action !== 'custom');
}

function toggleAISettings() {
  document.getElementById('ai-settings').classList.toggle('hidden');
}

function onProviderChange() {
  const isCompat = document.getElementById('ai-provider').value === 'openai_compat';
  document.getElementById('ai-base-url-wrap').classList.toggle('hidden', !isCompat);
}

function loadAISettings() {
  const s = JSON.parse(localStorage.getItem('ai_settings') || '{}');
  if (s.provider) document.getElementById('ai-provider').value = s.provider;
  if (s.model)    document.getElementById('ai-model').value    = s.model;
  if (s.api_key)  document.getElementById('ai-api-key').value  = s.api_key;
  if (s.base_url) document.getElementById('ai-base-url').value = s.base_url;
  onProviderChange();
}

function saveAISettings() {
  const s = {
    provider: document.getElementById('ai-provider').value,
    model:    document.getElementById('ai-model').value.trim(),
    api_key:  document.getElementById('ai-api-key').value.trim(),
    base_url: document.getElementById('ai-base-url').value.trim(),
  };
  localStorage.setItem('ai_settings', JSON.stringify(s));
  document.getElementById('ai-settings').classList.add('hidden');
}

async function runAI() {
  const content = document.getElementById('ai-input').value.trim();
  const output  = document.getElementById('ai-output');
  const status  = document.getElementById('ai-status');
  const spinner = document.getElementById('ai-spinner');
  const btn     = document.getElementById('btn-generate');

  if (!content) {
    output.textContent = '';
    status.textContent = 'Input is empty.';
    return;
  }

  const s = JSON.parse(localStorage.getItem('ai_settings') || '{}');
  if (!s.model) {
    status.textContent = 'Open ⚙ Settings and set a model first.';
    return;
  }

  btn.disabled = true;
  spinner.classList.remove('hidden');
  output.textContent = '';
  status.textContent = '';

  try {
    const res = await fetch('/ai/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        provider:      s.provider || 'anthropic',
        model:         s.model,
        api_key:       s.api_key || '',
        base_url:      s.base_url || '',
        action:        currentAction,
        custom_prompt: document.getElementById('ai-custom-prompt').value.trim(),
        content,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      status.textContent = `Error: ${data.detail || res.statusText}`;
    } else {
      output.textContent = data.result;
    }
  } catch (err) {
    status.textContent = `Network error: ${err.message}`;
  } finally {
    btn.disabled = false;
    spinner.classList.add('hidden');
  }
}
