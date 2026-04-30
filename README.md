# TaskMaster

A gamified task management application with machine-learning-powered completion predictions.

---

## What it does

- Create, edit, complete, and organise tasks by category and priority
- Earn points and unlock badges as you complete tasks (gamification)
- Maintain a daily streak for bonus points
- See a ML-predicted completion probability on every pending task

---

## Prerequisites

You need these installed once on your machine:

| Tool | Version | Download |
|---|---|---|
| Python | 3.11 or newer | https://www.python.org/downloads/ |
| Node.js | 18 or newer (includes npm) | https://nodejs.org/ |

Verify in a terminal:
```bash
python --version
node --version
npm --version
```

---

## First-time setup

Only needs to be done once after cloning/copying the project.

### 1. Backend dependencies

Open a terminal in the project root, then:

```bash
cd backend
pip install -r requirements.txt
```

### 2. Frontend dependencies

Open another terminal in the project root, then:

```bash
cd frontend
npm install
```

That's it for setup.

---

## Running the app

You need **two terminal windows open at the same time** — one for the backend, one for the frontend.

### Terminal 1 — Backend

```bash
cd backend
python run.py
```

Wait until you see: `Uvicorn running on http://0.0.0.0:8000`.

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

Wait until you see: `Local: http://localhost:5173`.

### Open the app

Open your browser to:

> **http://localhost:5173**

That's the app. The frontend talks to the backend automatically — you don't need to visit `localhost:8000` (though `localhost:8000/docs` shows the auto-generated Swagger API docs if you're curious).

### To stop the app

Press **Ctrl+C** in each terminal.

---

## Optional: seed demo data for the ML feature

The ML model needs at least 20 completed/overdue tasks before it can train. To skip the manual grind, run the seed script which generates 60 demo tasks:

```bash
cd backend
python -m app.seed
```

Restart the backend, refresh the app, then click **Stats & ML → Train Model**.

---

## Quick reference

| Task | Command |
|---|---|
| Install backend deps | `cd backend && pip install -r requirements.txt` |
| Install frontend deps | `cd frontend && npm install` |
| Start backend | `cd backend && python run.py` |
| Start frontend | `cd frontend && npm run dev` |
| Seed demo data | `cd backend && python -m app.seed` |
| Open the app | http://localhost:5173 |
| API docs | http://localhost:8000/docs |
| Stop a server | Ctrl+C in its terminal |
