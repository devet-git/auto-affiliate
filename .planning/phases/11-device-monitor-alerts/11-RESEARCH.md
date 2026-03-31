# Phase 11: Device Monitor & Alerts - Technical Research

## Research Objective
Implement the device monitoring & discord alerting system (DEV-01, DEV-02, NOTIF-01, NOTIF-02) based on the decisions captured in `11-CONTEXT.md`.

## Key Technical Decisions to Plan

### 1. Device Ping System (Celery Beat)
- **Context:** Decided to ping both ADB and Appium every 5 minutes (D-01).
- **Execution:** Create a Celery task `ping_devices` in a new file `app/domains/devices/tasks.py`. Map it in `app.core.celery_app.beat_schedule` to run every 300 seconds.
- **ADB Check:** Use Python `subprocess.run(["adb", "devices"], capture_output=True)` to parse connected device serials.
- **Appium Check:** Use `httpx` to send a GET request to `http://localhost:4723/status`. If status 200, Appium is online.
- **State tracking:** 
  - Need to add `missed_pings` (int, default 0) to `Device` model to track consecutive failures (D-02).
  - Update `Device.status` accordingly (online vs offline).

### 2. Discord Notibot Alerts
- **Context:** Alert Discord when 3 consecutive missed pings occur (D-02) or scraper is stuck (D-03). Daily reports at 17:00 (D-04).
- **Execution:** We already have `bot.py` using `discord.py` running in FastAPI lifespan. However, Celery runs in a separate process and cannot directly use `bot.py` instances. 
- **Solution:** 
  - Modify `bot.py` or `celery_app.py` to use a **Webhook URL** to send alerts directly from Celery without needing a live bot connection.
  - Or add a `notify_admin_discord(message)` Celery task (we already have it mapped in `celery_app.py` `task_routes`) and implement it in `sys_worker/seeding_tasks.py` using `discord.Webhook.from_url` or basic `requests.post`. 
  - Implement `/report` Slash Command in `bot.py` for on-demand Daily Reports (D-05).

### 3. Stuck Scraper Detection
- **Context:** Alert if a scraper runs but no DB inserts/updates occur for X hours (D-03).
- **Execution:** Add a Celery task that queries `CrawlerConfig` or `TargetGroupConfig` where `status == "running"`, then checks `updated_at`. If `utcnow() - updated_at > 2 hours`, trigger an alert.
- **State reset:** Ensure crawler tasks update their `CrawlerConfig.updated_at` each time they insert a record.

## Validation Architecture
- Provide `ping_devices` unit tests with mocked subprocess output.
- Perform an end-to-end webhook alert test.
- Create UI routes to fetch device states for the dashboard.
