# Backend — FastAPI

Minimal FastAPI service that exposes `GET /api/hello`.

## Requirements

- Python 3.11+

## Setup

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```sh
uvicorn app.main:app --reload --port 8000
```

The server listens on `http://localhost:8000`.

## Endpoint

`GET http://localhost:8000/api/hello` returns:

```json
{"message": "Hello, World!"}
```

CORS is configured to allow the Vite dev server origin
(`http://localhost:5173`) for `GET` requests.
