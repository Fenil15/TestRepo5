# Hello World App

A minimal full-stack hello-world demo:

- **Backend** — FastAPI service exposing `GET /api/hello` returning
  `{"message": "Hello, World!"}`. Runs on port 8000.
- **Frontend** — Vite + React + TypeScript single-page app that fetches
  `/api/hello` on load and renders the message. Dev server on port 5173,
  with `/api/*` proxied to the backend.

## Run locally

In one terminal:

```sh
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```sh
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173.

## Out of scope

This scaffold intentionally has no tests, no Docker, and no CI configuration —
those can be layered on later.
