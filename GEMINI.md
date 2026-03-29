# Project Guidelines — Auto Affiliate Control Center

This file is read by all GSD agents (researcher, planner, executor) before doing any work.
Follow every rule here strictly. These are non-negotiable project conventions.

---

## Python Environment

**ALWAYS use the project's virtual environment. NEVER install packages globally.**

- The venv is located at: `server/.venv/`
- Activate before running any Python command:
  ```powershell
  # Windows (PowerShell)
  server\.venv\Scripts\activate

  # Windows (CMD)
  server\.venv\Scripts\activate.bat
  ```
- Install packages ONLY inside the venv:
  ```powershell
  # Correct ✅
  pip install <package>           # (while venv is active)

  # Wrong ❌ — never do this
  pip install <package>           # (without activating venv first)
  ```
- After installing new packages, always freeze:
  ```powershell
  pip freeze > server/requirements.txt
  ```
- When running `python`, `pytest`, `celery`, or any Python CLI tool, always prefix with the venv path or ensure venv is active. Example:
  ```powershell
  server\.venv\Scripts\python -m pytest
  server\.venv\Scripts\celery -A app.core.celery_app worker ...
  ```

---

## Backend Conventions

- **Framework**: FastAPI + SQLModel + Celery/Redis
- **Working directory for server commands**: always `server/` (not project root)
- **Domain structure**: `server/app/domains/<domain_name>/` — each domain has `router.py`, `services/`, `models.py`
- **Auth**: All API endpoints require JWT admin token via `Depends(get_current_admin)` — no public endpoints

## Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI (Python) |
| ORM | SQLModel + SQLAlchemy |
| Database | PostgreSQL |
| Task Queue | Celery + Redis |
| Browser Automation | Playwright (async) |
| Phone Automation | Appium + UiAutomator2 |
| Video Processing | ffmpeg-python + yt-dlp |
| Frontend | React Vite + Shadcn UI + Tailwind CSS |

---

## Frontend Conventions

- **Working directory for web frontend**: always `web/` (not `server/ui/` or project root).
- **Framework**: React Vite + Shadcn UI + Tailwind CSS
- **Routing**: React Router
- **State Management**: Zustand / React Query
- All frontend terminal commands (e.g., `npm install`, `npm run dev`, `npx shadcn@latest add`) MUST be executed inside the `web/` directory.
