# Frontend

Vite + React + TypeScript UI that fetches `/api/hello` from the FastAPI
backend and renders the returned `message`.

## Prerequisites

- Node.js 18+ (Vite 9 requires Node 18 or newer).
- The FastAPI backend (issue #2) running on `http://localhost:8000`.
  Without it, the page will display **"Could not reach API"**.

## Setup

```sh
cd frontend
npm install
```

## Run the dev server

```sh
npm run dev
```

Vite serves the app on [http://localhost:5173](http://localhost:5173).
The dev server proxies `/api/*` to `http://localhost:8000`, so the
frontend can call the backend without any CORS configuration during
development.

When both servers are up, the page should display **"Hello, World!"**
within a couple of seconds of load.

## Build

```sh
npm run build
```

Produces a production bundle in `dist/`.

## Project layout

- `src/App.tsx` — fetches `/api/hello` on mount, stores the message in
  state, and renders it inside an `<h1>`.
- `vite.config.ts` — configures the React plugin and the `/api` dev
  proxy to `http://localhost:8000`.

## What is **not** included

- No tests, no Docker, no CI configuration. The scope of this slice is
  the scaffold + a single fetch on load.
