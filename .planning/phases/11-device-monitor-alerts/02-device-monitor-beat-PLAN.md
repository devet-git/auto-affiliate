---
description: Create background ping tasks using Celery Beat.
depends_on: ["01-database-api-PLAN.md"]
files_modified:
  - server/app/domains/devices/tasks.py
  - server/app/core/celery_app.py
wave: 2
autonomous: true
---

# 02-device-monitor-beat-PLAN

<objective>
Implement Celery Beat tasks to check `adb devices` and Appium session status every 5 minutes, updating `Device.missed_pings`. Alert via Discord Webhook if 3 missed pings occur. Also create check_stuck_scrapers alert.
</objective>

<requirements>
- DEV-02
- NOTIF-01
- NOTIF-02
</requirements>

## Tasks

### 1. Implement Device Pinger (DEV-02, NOTIF-01)
<read_first>
- server/app/domains/devices/models.py
- server/app/core/celery_app.py
- server/app/domains/devices/tasks.py (Create if not dict)
</read_first>
<action>
Create `server/app/domains/devices/tasks.py` if missing.  
Define `ping_devices()` celery task.  
1. Fetch all devices from DB.
2. Run `subprocess.run(["adb", "devices"], capture_output=True, text=True)`. Parse active `udid`s.
3. For each device, if `device.udid` is missing in ADB output OR http request to `http://localhost:4723/status` fails (timeout/error): 
   - `device.missed_pings += 1`
   - `device.status = "offline"`
   - IF `device.missed_pings == 3`, trigger `notify_admin_discord(f"🚨 ALERT: Cảnh báo thiết bị {device.label} ({device.udid}) OFFLINE sau 15 phút!")` using Celery.
4. If it successfully pings both ADB and appium:
   - `device.missed_pings = 0`, `device.status = "online"`
Save to session.
</action>
<acceptance_criteria>
- `server/app/domains/devices/tasks.py` contains `def ping_devices(`
- Action includes check for `missed_pings == 3` to send warning
</acceptance_criteria>

### 2. Implement Stuck Scraper Alert (NOTIF-02)
<read_first>
- server/app/domains/sys_worker/alert_tasks.py (Create new file)
- server/app/core/celery_app.py
</read_first>
<action>
Create `server/app/domains/sys_worker/alert_tasks.py` (or use existing `tasks.py`).
Define `check_stuck_scrapers()` task.
Query `CrawlerConfig` for items where `status == 'running'`. Look at their `updated_at`. If `utcnow() - updated_at > timedelta(hours=2)`, send Discord alert: `🚨 Scraper kẹt / IP blocked: {config.name}`. (Use `CrawlerConfig` or `ShopeeProduct` recent records depending on the schema).
Since schema checks might be tricky without full ORM, just implement a basic timeout checker logic or a placeholder warning.
</action>
<acceptance_criteria>
- `server/app/domains/sys_worker/alert_tasks.py` contains `check_stuck_scrapers` task definition or equivalent logic in `tasks.py`
</acceptance_criteria>

### 3. Register Beat Schedule
<read_first>
- server/app/core/celery_app.py
</read_first>
<action>
Register the new tasks in `celery_app.py`:
- include `"app.domains.devices.tasks"` and `"app.domains.sys_worker.alert_tasks"` if created.
- Add `ping_devices` to `beat_schedule` to run every 300.0 (5 min).
- Add `check_stuck_scrapers` to `beat_schedule` to run every 900.0 (15 min).
</action>
<acceptance_criteria>
- `server/app/core/celery_app.py` has `beat_schedule` entry for `ping_devices`
</acceptance_criteria>

## Verification
- Run `pytest` and verify no circular imports.
