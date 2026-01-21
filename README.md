# Helpdesk API (FastAPI + SQLModel + SQLite)

A small REST API that models a helpdesk ticket workflow.  
Demonstrates CRUD operations, validation, search filtering, and partial updates (PATCH) backed by a SQLite database.

---

## Tech

- FastAPI
- SQLModel (SQLAlchemy + Pydantic)
- SQLite

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

### 1) Create and activate a virtual environment

**Windows (Command Prompt):**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

---

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

---

### 3) Run the API
```bash
uvicorn main:app --reload
```

Open:
- API docs: http://127.0.0.1:8000/docs
- Root: http://127.0.0.1:8000/

---

## Demo client

Run the demo script (creates tickets, patches, searches, deletes):

```bash
python demo_client.py
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
