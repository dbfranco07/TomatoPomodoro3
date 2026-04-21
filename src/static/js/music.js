// ── YouTube Music Player ────────────────────────────────────────────────────
// Uses YouTube Data API v3 for keyword search and the IFrame Player API for
// playback. The user's API key is stored in localStorage.

let ytPlayer = null;
let ytApiReady = false;
let ytSearchResults = [];
let currentVideoIndex = -1;

// Called by the YouTube IFrame API script when it finishes loading
function onYouTubeIframeAPIReady() {
  ytApiReady = true;
}

// ── Settings ───────────────────────────────────────────────────────────────

function getMusicApiKey() {
  return localStorage.getItem('yt-api-key') || '';
}

function toggleMusicSettings() {
  const drawer = document.getElementById('music-settings-drawer');
  const isHidden = drawer.classList.toggle('hidden');
  if (!isHidden) {
    document.getElementById('yt-api-key-input').value = getMusicApiKey();
    document.getElementById('yt-api-key-input').focus();
  }
}

function saveMusicApiKey() {
  const key = document.getElementById('yt-api-key-input').value.trim();
  localStorage.setItem('yt-api-key', key);
  document.getElementById('music-settings-drawer').classList.add('hidden');
  _setMusicStatus(key ? 'API key saved.' : 'API key cleared.', 2000);
}

// ── Search ─────────────────────────────────────────────────────────────────

async function searchMusic() {
  const query = document.getElementById('music-search-input').value.trim();
  if (!query) return;

  const apiKey = getMusicApiKey();
  if (!apiKey) {
    _setMusicStatus('Enter a YouTube Data API v3 key in settings (⚙) first.');
    document.getElementById('music-settings-drawer').classList.remove('hidden');
    document.getElementById('yt-api-key-input').focus();
    return;
  }

  _setMusicStatus('Searching…');
  document.getElementById('music-results').innerHTML = '';
  document.getElementById('yt-player-container').classList.add('hidden');

  try {
    const params = new URLSearchParams({
      part: 'snippet',
      type: 'video',
      videoCategoryId: '10', // Music category
      maxResults: '10',
      q: query,
      key: apiKey,
    });
    const res = await fetch(
      `https://www.googleapis.com/youtube/v3/search?${params}`
    );
    const data = await res.json();

    if (!res.ok) {
      _setMusicStatus('Error: ' + (data?.error?.message || res.statusText));
      return;
    }

    ytSearchResults = data.items || [];
    currentVideoIndex = -1;
    _renderMusicResults();
    _setMusicStatus(
      ytSearchResults.length
        ? `${ytSearchResults.length} results`
        : 'No results found.',
    );
  } catch (err) {
    _setMusicStatus('Search failed: ' + err.message);
  }
}

function _renderMusicResults() {
  const list = document.getElementById('music-results');
  list.innerHTML = '';

  if (!ytSearchResults.length) {
    list.innerHTML =
      '<p class="text-stone-400 dark:text-stone-500 text-sm italic">No results.</p>';
    return;
  }

  ytSearchResults.forEach((item, i) => {
    const videoId = item.id.videoId;
    const title   = item.snippet.title;
    const channel = item.snippet.channelTitle;
    const thumb   = item.snippet.thumbnails?.default?.url || '';

    const el = document.createElement('div');
    el.className =
      'flex items-center gap-3 p-2 rounded-lg cursor-pointer ' +
      'hover:bg-stone-100 dark:hover:bg-stone-700 transition select-none';
    el.dataset.index = i;
    el.innerHTML = `
      <img src="${thumb}" class="w-14 h-10 rounded object-cover shrink-0" alt="" loading="lazy" />
      <div class="flex-1 min-w-0">
        <div class="text-xs font-medium text-stone-700 dark:text-stone-200 truncate">${_esc(title)}</div>
        <div class="text-[10px] text-stone-400 truncate">${_esc(channel)}</div>
      </div>
      <span class="text-stone-300 dark:text-stone-600 text-lg shrink-0">&#9654;</span>
    `;
    el.onclick = () => playVideo(i);
    list.appendChild(el);
  });
}

// ── Playback ────────────────────────────────────────────────────────────────

function playVideo(index) {
  if (index < 0 || index >= ytSearchResults.length) return;
  currentVideoIndex = index;
  const videoId = ytSearchResults[index].id.videoId;

  _highlightResult(index);

  if (!ytApiReady) {
    _setMusicStatus('Player not ready yet. Please try again in a moment.');
    return;
  }

  const container = document.getElementById('yt-player-container');
  const controls  = document.getElementById('yt-player-controls');
  container.classList.remove('hidden');
  if (controls) controls.classList.remove('hidden');

  if (ytPlayer) {
    ytPlayer.loadVideoById(videoId);
    ytPlayer.playVideo();
  } else {
    ytPlayer = new YT.Player('yt-player', {
      height: '190',
      width: '100%',
      videoId,
      playerVars: { autoplay: 1, playsinline: 1 },
      events: {
        onReady: e => e.target.playVideo(),
        onStateChange: _onPlayerStateChange,
        onError: () => _setMusicStatus('Playback error for this video.'),
      },
    });
  }
  _setMusicStatus('');
}

function _onPlayerStateChange(event) {
  if (event.data === YT.PlayerState.ENDED) {
    const next = currentVideoIndex + 1;
    if (next < ytSearchResults.length) playVideo(next);
  }
}

function playerPrev() {
  if (currentVideoIndex > 0) playVideo(currentVideoIndex - 1);
}

function playerNext() {
  if (currentVideoIndex < ytSearchResults.length - 1) {
    playVideo(currentVideoIndex + 1);
  }
}

// ── Helpers ─────────────────────────────────────────────────────────────────

function _setMusicStatus(msg, clearAfterMs = 0) {
  const el = document.getElementById('music-status');
  if (!el) return;
  el.textContent = msg;
  if (clearAfterMs) setTimeout(() => { el.textContent = ''; }, clearAfterMs);
}

function _highlightResult(activeIndex) {
  const items = document.getElementById('music-results').children;
  [...items].forEach((el, i) => {
    el.classList.toggle('bg-red-50',              i === activeIndex);
    el.classList.toggle('dark:bg-stone-600',      i === activeIndex);
    el.classList.toggle('ring-1',                 i === activeIndex);
    el.classList.toggle('ring-red-300',           i === activeIndex);
  });
}

function _esc(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Init ────────────────────────────────────────────────────────────────────

function initMusic() {
  const searchInput = document.getElementById('music-search-input');
  if (searchInput) {
    searchInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') searchMusic();
    });
  }
  if (!getMusicApiKey()) {
    _setMusicStatus(
      'No API key set — click ⚙ to add your YouTube Data API v3 key.',
    );
  }
}
