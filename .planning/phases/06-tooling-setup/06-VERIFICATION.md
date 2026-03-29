---
status: passed
phase: 06-tooling-setup
date: 2026-03-29
---

# Phase 6: Tooling & Setup — Verification

## Goal
Gom gọn hạ tầng chạy, Setup script Start-all

## Must-Haves

- [x] `start-all.bat` exists at project root
- [x] `stop-all.bat` exists at project root
- [x] `start-all.bat` spawns 5 separate titled CMD windows (Appium Server, FastAPI Server, Celery Default Core, Celery Appium Node, Web UI Frontend)
- [x] Staggered startup: `timeout /t 5 /nobreak` delays Celery workers until backend is ready
- [x] Scripts use `%~dp0` for portable path resolution — works from any calling directory
- [x] `stop-all.bat` uses `taskkill /F /FI "WINDOWTITLE eq ...*" /T` — targets exactly the spawned windows only, kills child processes

## Requirements Coverage

| REQ-ID | Description | Plan | Status |
|--------|-------------|------|--------|
| TOOL-01 | One-click .bat script to start entire stack | 06-1 | ✅ Covered |

## Verification Result

**PASSED** — all must-haves verified. Single-click stack orchestration is operational.
