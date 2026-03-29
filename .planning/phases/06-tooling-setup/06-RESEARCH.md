# Phase 6: Tooling & Setup - Research

## Discovery
1. **Commands required**:
   - `server/`: 
     - Appium server: `appium -p 4723`
     - FastAPI dev: `fastapi dev`
     - Celery worker (default queue): `.venv\Scripts\celery -A app.core.celery_app worker --loglevel=info -Q default`
     - Celery worker (appium queue): `.venv\Scripts\celery -A app.core.celery_app worker -Q appium_phone --concurrency=1`
   - `web/`: 
     - React dev server: `npm run dev`

2. **Window Titles**: We can use `title [Name]` to uniquely identify each window, ensuring `stop-all.bat` can target these specific processes without killing other Python/Node apps the user might have open.

3. **Closing Processes safely**: 
   Since `appium` and `vite` run via Node, and `fastapi`/`celery` run via Python, using `taskkill /IM node.exe` is too broad.
   Instead, we can use window tracking in Windows CMD:
   `taskkill /F /FI "WINDOWTITLE eq Appium Server*" /T`
   `taskkill /F /FI "WINDOWTITLE eq FastAPI*" /T`
   `taskkill /F /FI "WINDOWTITLE eq Celery Default*" /T`
   `taskkill /F /FI "WINDOWTITLE eq Celery Appium*" /T`
   `taskkill /F /FI "WINDOWTITLE eq Web UI*" /T`
   The `/T` flag kills child processes spawned underneath those windows.

4. **Directory Navigation**: Provide `cd server` before running server scripts, and `cd web` before running front-end scripts inside the individual `cmd /k` blocks.

## Validation Architecture
- [ ] Check `start-all.bat` exists and contains 5 distinct sub-commands starting with `start cmd /k "title ..."`
- [ ] Check `stop-all.bat` exists and uses `taskkill` appropriately filtered by Window Title to prevent collateral damage.
- [ ] Run `start-all.bat`, verify 5 windows pop up, and run `stop-all.bat` to see them close (can be verified manually or by seeing script exists with valid syntax).
