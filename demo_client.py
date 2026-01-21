import requests

BASE = "http://127.0.0.1:8000"

# -----------------
# Add / POST
# -----------------

print("\n=== ADD TICKETS ===")

# HTTP request is sent (Python to JSON)
resp = requests.post(
    f"{BASE}/tickets/",
    json={
        "title": "Printer not working",
        "description": "Office printer keeps jamming",
        "priority": 3
    },
)
print("\nAdd ticket 1:")
print("Status:", resp.status_code)
# json() converts from JSON to Python
ticket1 = resp.json()
print("Response:", ticket1)

resp = requests.post(
    f"{BASE}/tickets/",
    json={
        "title": "Laptop overheating",
        "description": "Fan is loud and laptop shuts down",
        "priority": 5
    },
)
print("\nAdd ticket 2:")
print("Status:", resp.status_code)
ticket2 = resp.json()
print("Response:", ticket2)

resp = requests.post(
    f"{BASE}/tickets/",
    json={
        "title": "Email not syncing",
        "description": "Outlook not updating inbox",
        "priority": 2
    },
)
print("\nAdd ticket 3:")
print("Status:", resp.status_code)
ticket3 = resp.json()
print("Response:", ticket3)

# -----------------
# Update / PATCH
# -----------------

print("\n=== PATCH TICKET ===")

resp = requests.patch(
    f"{BASE}/tickets/{ticket1['id']}",
    json={"status": "in_progress"},
)
print(f"\nPatch ticket {ticket1['id']} (status : in_progress):")
print("Status:", resp.status_code)
patched_ticket = resp.json()
print("Response:", patched_ticket)

# -----------------
# Search / QUERY
# -----------------

print("\n=== SEARCH TICKETS ===")

resp = requests.get(
    f"{BASE}/tickets/search",
    params={"priority": 5},
)
print("\nSearch by priority (5):")
print("Status:", resp.status_code)
print("Response:", resp.json())

resp = requests.get(
    f"{BASE}/tickets/search",
    params={"status": "in_progress"},
)
print("\nSearch by status (in_progress):")
print("Status:", resp.status_code)
print("Response:", resp.json())

resp = requests.get(
    f"{BASE}/tickets/search",
    params={"priority": 2, "status": "open"},
)
print("\nSearch by priority + status:")
print("Status:", resp.status_code)
print("Response:", resp.json())

# -----------------
# Delete
# -----------------

print("\n=== DELETE TICKET ===")

resp = requests.delete(
    f"{BASE}/tickets/{ticket2['id']}"
)
print(f"\nDelete ticket {ticket2['id']}:")
print("Status:", resp.status_code)
print("Response:", resp.json())

# -----------------
# Verify deletion
# -----------------

print("\n=== VERIFY DELETE ===")

resp = requests.get(
    f"{BASE}/tickets/{ticket2['id']}"
)
print(f"\nGet deleted ticket {ticket2['id']}:")
print("Status:", resp.status_code)
print("Response:", resp.json())
