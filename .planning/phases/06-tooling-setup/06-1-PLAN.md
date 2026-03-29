---
wave: 1
depends_on: []
files_modified: []
autonomous: true
requirements_addressed:
  - TOOL-01
---

# Phase 6: Tooling & Setup
# Wave 1: Creation of Start and Stop Windows batch scripts

<objective>
Create `start-all.bat` and `stop-all.bat` in the project root to orchestrate the backend and frontend services using staggered concurrent windows, resolving requirement TOOL-01.
</objective>

<verification_criteria>
- `start-all.bat` can spin up Appium, FastAPI, Celery Default, Celery Appium, and Vite.
- `stop-all.bat` successfully tears down exactly the spawned windows and child processes.
</verification_criteria>

<must_haves>
- Uses `start cmd /k "title ..."` for distinct windows
- Delays the execution between backend initialization and celery queue workers using `timeout /t 5`
- `stop-all.bat` uses `taskkill /F /FI "WINDOWTITLE eq ...*"`
</must_haves>

<tasks>

<task>
<description>Create `start-all.bat`</description>
<read_first>
- `.planning/phases/06-tooling-setup/06-CONTEXT.md`
</read_first>
<action>
Create `start-all.bat` in the project root directory (`E:\Projects\Personal\auto-affiliate\start-all.bat`).
Paste the following command layout:

```bat
@echo off
echo =======================================================
echo     Auto Affiliate Control Center - Orchestrator
echo =======================================================
echo.
echo Starting Appium Server...
start "Appium Server" cmd /k "title Appium Server && cd server && appium -p 4723"

echo Starting FastAPI Backend...
start "FastAPI Server" cmd /k "title FastAPI Server && cd server && .venv\Scripts\activate && fastapi dev"

echo Waiting 5 seconds before starting Celery Workers...
timeout /t 5 /nobreak >nul

echo Starting Celery Default Core...
start "Celery Default Core" cmd /k "title Celery Default Core && cd server && .venv\Scripts\activate && celery -A app.core.celery_app worker --loglevel=info -Q default"

echo Starting Celery Appium Node...
start "Celery Appium Node" cmd /k "title Celery Appium Node && cd server && .venv\Scripts\activate && celery -A app.core.celery_app worker -Q appium_phone --concurrency=1"

echo Starting Vite React Frontend...
start "Web UI Frontend" cmd /k "title Web UI Frontend && cd web && npm run dev"

echo.
echo All services launched! Check individual command windows.
```
</action>
<acceptance_criteria>
- `cat start-all.bat` contains the precise staggered start script with the matching Windows titles.
</acceptance_criteria>
</task>

<task>
<description>Create `stop-all.bat`</description>
<read_first>
- `.planning/phases/06-tooling-setup/06-CONTEXT.md`
</read_first>
<action>
Create `stop-all.bat` in the project root directory (`E:\Projects\Personal\auto-affiliate\stop-all.bat`).
Paste the following commands:

```bat
@echo off
echo Terminating Auto Affiliate Services...

taskkill /F /FI "WINDOWTITLE eq Appium Server*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq FastAPI Server*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Celery Default Core*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Celery Appium Node*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Web UI Frontend*" /T >nul 2>&1

echo All known auto-affiliate processes terminated.
```
</action>
<acceptance_criteria>
- `cat stop-all.bat` contains the precise `taskkill` commands with `/FI "WINDOWTITLE eq ...*"` filters.
</acceptance_criteria>
</task>

</tasks>
