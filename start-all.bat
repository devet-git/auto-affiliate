@echo off
echo =======================================================
echo     Auto Affiliate Control Center - Orchestrator
echo =======================================================
echo.

echo Starting Appium Server...
start "Appium Server" cmd /k "title Appium Server && cd /d %~dp0server && appium -p 4723"

echo Starting FastAPI Backend...
start "FastAPI Server" cmd /k "title FastAPI Server && cd /d %~dp0server && .venv\Scripts\activate && fastapi dev"

echo Waiting 5 seconds before starting Celery Workers...
timeout /t 5 /nobreak >nul

echo Starting Celery Default Core...
start "Celery Default Core" cmd /k "title Celery Default Core && cd /d %~dp0server && .venv\Scripts\activate && celery -A app.core.celery_app worker --loglevel=info -Q default"

echo Starting Celery Appium Node...
start "Celery Appium Node" cmd /k "title Celery Appium Node && cd /d %~dp0server && .venv\Scripts\activate && celery -A app.core.celery_app worker -Q appium_phone --concurrency=1"

echo Starting Vite React Frontend...
start "Web UI Frontend" cmd /k "title Web UI Frontend && cd /d %~dp0web && npm run dev"

echo.
echo All services launched! Check individual command windows.
echo Run stop-all.bat to shut everything down when done.
