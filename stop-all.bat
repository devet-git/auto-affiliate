@echo off
echo =======================================================
echo     Auto Affiliate Control Center - Shutdown
echo =======================================================
echo.
echo Terminating Auto Affiliate Services...

taskkill /F /FI "WINDOWTITLE eq Appium Server*" /T >nul 2>&1
echo [1/5] Appium Server - stopped

taskkill /F /FI "WINDOWTITLE eq FastAPI Server*" /T >nul 2>&1
echo [2/5] FastAPI Server - stopped

taskkill /F /FI "WINDOWTITLE eq Celery Default Core*" /T >nul 2>&1
echo [3/5] Celery Default Core - stopped

taskkill /F /FI "WINDOWTITLE eq Celery Appium Node*" /T >nul 2>&1
echo [4/5] Celery Appium Node - stopped

taskkill /F /FI "WINDOWTITLE eq Web UI Frontend*" /T >nul 2>&1
echo [5/5] Web UI Frontend - stopped

echo.
echo All known auto-affiliate processes terminated.
