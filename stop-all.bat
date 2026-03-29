@echo off
echo =======================================================
echo     Auto Affiliate Control Center - Shutdown
echo =======================================================
echo.
echo Terminating Auto Affiliate Services...

:: 1. Stop Appium (Port 4723)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :4723') do (
    if NOT "%%a"=="0" taskkill /F /PID %%a /T >nul 2>&1
)
echo [1/5] Appium Server - stopped

:: 2. Stop FastAPI (Port 8000)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    if NOT "%%a"=="0" taskkill /F /PID %%a /T >nul 2>&1
)
:: Also catch uvicorn/fastapi processes just in case
wmic process where "name='python.exe' and commandline like '%%fastapi dev%%'" call terminate >nul 2>&1
echo [2/5] FastAPI Server - stopped

:: 3. Stop Celery Default Core
wmic process where "name='python.exe' and commandline like '%%celery -A app.core.celery_app worker%%default%%'" call terminate >nul 2>&1
echo [3/5] Celery Default Core - stopped

:: 4. Stop Celery Appium Node
wmic process where "name='python.exe' and commandline like '%%celery -A app.core.celery_app worker -Q appium_phone%%'" call terminate >nul 2>&1
echo [4/5] Celery Appium Node - stopped

:: 5. Stop Vite React Frontend (Port 5173)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
    if NOT "%%a"=="0" taskkill /F /PID %%a /T >nul 2>&1
)
wmic process where "name='node.exe' and commandline like '%%vite%%'" call terminate >nul 2>&1
echo [5/5] Web UI Frontend - stopped

echo.
echo All known auto-affiliate processes terminated cleanly.
