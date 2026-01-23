# Helpdesk API (FastAPI + SQLModel + SQLite)

A small REST API that models a helpdesk ticket workflow.  
Demonstrates CRUD operations, validation, search filtering, and partial updates (PATCH) backed by a SQLite database.

---

## Tech

- FastAPI
- SQLModel (SQLAlchemy + Pydantic)
- SQLite
- Docker

---

## Features

- Create tickets (POST)
- List tickets (GET)
- Get ticket by ID (GET)
- Search tickets via query parameters (GET)
- Update tickets partially (PATCH)
- Delete tickets (DELETE)
- Enum-restricted status: `open | in_progress | closed`
- Priority validation: 1–5

---

## Setup

### 1) Create a virtual environment

```bash
python -m venv .venv
```
---

### 2) Activate the virtual environment (manual)
You only need to do this if you are NOT using the provided run script.

**Windows (Command Prompt):**
```bash
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

---

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run the API

### Option 1) Run manually (any platform)
```bash
uvicorn main:app --reload
```

### Option 2) Run using the provided script (Windows only):
```bash
run_api.cmd
```

Open:
- API docs: http://127.0.0.1:8000/docs
- Root: http://127.0.0.1:8000/

### Option 3) Run with Docker (recommended)

Build the image:
```bash
docker build -t helpdesk-api .
```

Run the container:
```bash
docker run --rm -p 8000:8000 helpdesk-api
```

---

## Demo client

⚠️ The API must be running in a separate terminal before running the demo client.

Run the demo script (creates tickets, patches, searches, deletes):

### Option 1) Run manually (any platform)
```bash
python demo_client.py
```

### Option 2) Run using the provided script (Windows only):
```bash
run_demo.cmd
```

---

## Endpoints

### Create ticket
POST `/tickets/`

Body:
```json
{
  "title": "Printer not working",
  "description": "Office printer keeps jamming",
  "priority": 3
}
```

Response (example):
```json
{
  "id": 1,
  "title": "Printer not working",
  "description": "Office printer keeps jamming",
  "priority": 3,
  "status": "open"
}
```

---

### List tickets
GET `/tickets/?offset=0&limit=100`

---

### Get ticket by ID
GET `/tickets/{ticket_id}`

---

### Search tickets
GET `/tickets/search?priority=5&status=open`

---

### Patch ticket
PATCH `/tickets/{ticket_id}`

Body (example):
```json
{
  "status": "in_progress"
}
```

---

### Delete ticket
DELETE `/tickets/{ticket_id}`

---

## Notes

- The SQLite database file (`database.db`) is intentionally not committed.
- Database tables are created automatically on application startup.
- The API is stateless and follows REST conventions.
