@echo off
echo =======================================================
echo     Auto Affiliate Control Center - Orchestrator
echo =======================================================
echo.

:: Check if Windows Terminal is installed
where wt >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Windows Terminal detected! Opening all services in a single window with tabs...
    wt -w "AutoAffiliate" nt --title "Appium Server" -d "%~dp0server" cmd /k "appium -p 4723" ; ^
       nt --title "FastAPI Server" -d "%~dp0server" cmd /k ".venv\Scripts\activate && fastapi dev" ; ^
       nt --title "Celery Default Core" -d "%~dp0server" cmd /k "timeout /t 5 >nul && .venv\Scripts\activate && celery -A app.core.celery_app worker --loglevel=info -Q default" ; ^
       nt --title "Celery Appium Node" -d "%~dp0server" cmd /k "timeout /t 5 >nul && .venv\Scripts\activate && celery -A app.core.celery_app worker -Q appium_phone --concurrency=1" ; ^
       nt --title "Web UI Frontend" -d "%~dp0web" cmd /k "timeout /t 5 >nul && npm run dev"
) else (
    echo Opening multiple CMD windows...
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
)

echo.
echo All services launched! Check individual command windows or tabs.
echo Run stop-all.bat to shut everything down cleanly when done.
