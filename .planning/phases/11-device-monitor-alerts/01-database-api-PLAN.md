---
description: Add state tracking for missing pings and expose Device API
depends_on: []
files_modified:
  - server/app/domains/devices/models.py
  - server/app/domains/devices/router.py
wave: 1
autonomous: true
---

# 01-database-api-PLAN

<objective>
Update the Device database model to track consecutive missed pings, and expose missing APIs for the dashboard.
</objective>

<requirements>
- DEV-01
- DEV-02
</requirements>

## Tasks

### 1. Update Device Model
<read_first>
- server/app/domains/devices/models.py
</read_first>
<action>
Add `missed_pings: int = Field(default=0, description="Consecutive missed pings check")` to the `Device` class in `server/app/domains/devices/models.py`. Ensure alembic migrations are ignored since SQLModel in this project uses auto-create in lifespan, BUT if it requires alembic just assume SQLite/Postgres auto-alters it if needed, or create a migration if alembic is explicitly configured. (Actually, just add the field to the model).
</action>
<acceptance_criteria>
- `server/app/domains/devices/models.py` contains `missed_pings: int`
</acceptance_criteria>

### 2. Update Device Router API
<read_first>
- server/app/domains/devices/models.py
- server/app/domains/devices/router.py (Create if not exists)
</read_first>
<action>
In `server/app/domains/devices/router.py` construct an APIRouter.
Add `GET /` to fetch a list of `Device` items.
Add `POST /{device_id}/reset` to reset `missed_pings` to 0 and status to `'online'` for a specific device. Ensure it correctly queries the DB session.
Export the router.
If it's a new file, make sure to include it in `server/app/api/main.py` or the equivalent central router.
</action>
<acceptance_criteria>
- `server/app/domains/devices/router.py` contains `router.get("/")`
- `server/app/domains/devices/router.py` contains `router.post("/{device_id}/reset")`
</acceptance_criteria>

## Verification
- Can import `Device` with the new field without Syntax error
- Router compiles cleanly.
