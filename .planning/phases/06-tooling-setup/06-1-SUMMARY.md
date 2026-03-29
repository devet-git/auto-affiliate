---
plan: 06-1
phase: 06-tooling-setup
status: complete
completed: 2026-03-29
commit: 52429b9
---

# Plan 06-1 Summary: Start & Stop Scripts

## What Was Built

Two Windows batch scripts at the project root:

- **`start-all.bat`** — Launches 5 services as separate titled CMD windows with a 5-second stagger between backend init and Celery worker spawn.
- **`stop-all.bat`** — Kills all 5 service windows by their exact `WINDOWTITLE` filter, eliminating the need to manually track and hunt process windows.

## Key Files

### key-files.created
- `start-all.bat`
- `stop-all.bat`

## Acceptance Criteria Verified

- [x] `start-all.bat` uses `start "Name" cmd /k "title Name && ..."` for 5 distinct windows
- [x] `timeout /t 5 /nobreak` stagger between Appium/FastAPI and Celery workers
- [x] Uses `%~dp0` for portable path resolution (works from any terminal location)
- [x] `stop-all.bat` uses `taskkill /F /FI "WINDOWTITLE eq Name*" /T` for all 5 services

## Notes

- Upgraded path to `cd /d %~dp0server` and `cd /d %~dp0web` so the scripts always resolve relative to their own location, not the current working directory of the caller. This makes them double-click friendly.
- `stop-all.bat` echoes progress for each of 5 services so you can confirm what was terminated.

## Self-Check: PASSED
