# TomatoPomodoro3

A web-based Pomodoro timer with a built-in to-do list and notepad — powered by Python (FastAPI) and served in the browser.

## Features

- **Pomodoro Timer** — set custom work and break durations (supports decimals, e.g. `0.5` for 30 seconds)
- **Session tracking** — counts completed work sessions
- **Sound notification** — plays an audio alert when each phase ends
- **Phase modal** — a prompt appears at the end of each work/break phase before auto-starting the next
- **To-Do List** — add tasks, check them off (strikethrough), drag to reorder, and delete them; persists across restarts
- **Notes** — a free-form notepad that auto-saves as you type; persists across restarts

## Project Structure

```
TomatoPomodoro3/
├── src/
│   ├── main.py          # FastAPI app — REST API + static file serving
│   ├── requirements.txt
│   ├── tasks.json       # Persisted to-do list (auto-created)
│   ├── notes.txt        # Persisted notes (auto-created)
│   └── static/
│       └── index.html   # Single-page web app
└── assets/
    └── to_be_continued.mp3
```

## Setup

**1. Create and activate a virtual environment (first time only)**

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
```

**2. Install dependencies**

```bash
pip install -r src/requirements.txt
```

## Running the App

```bash
python src/main.py
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

## Usage

1. Enter your desired **work time** and **break time** in minutes
2. Click **Start Session** — the countdown begins
3. When the timer reaches zero, a sound plays and a modal appears
4. Click **OK** to start the next phase automatically
5. Click **Stop Session** at any time to reset everything

The to-do list and notes are saved automatically and will still be there after a restart.
