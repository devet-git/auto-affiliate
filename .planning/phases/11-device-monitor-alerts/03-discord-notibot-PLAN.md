---
description: Enhance the Discord bot with /report daily command and celery webhook logic.
depends_on: ["02-device-monitor-beat-PLAN.md"]
files_modified:
  - server/app/domains/notify/bot.py
  - server/app/core/celery_app.py
wave: 2
autonomous: true
---

# 03-discord-notibot-PLAN

<objective>
Update Discord Bot to handle on-demand reports and configure the 17:00 Daily Report schedule.
</objective>

<requirements>
- NOTIF-02
</requirements>

## Tasks

### 1. Update Discord Bot Commands
<read_first>
- server/app/domains/notify/bot.py
</read_first>
<action>
Open `server/app/domains/notify/bot.py`.
Add a new command: `@bot.tree.command(name="report", description="Lấy báo cáo tự động (Daily Report) thủ công")`
Inside the async function, query DB for counts of products/comments created today. Send an embed message back: "Automated Daily Report On Demand: ..."
</action>
<acceptance_criteria>
- `server/app/domains/notify/bot.py` contains `tree.command(name="report"`
</acceptance_criteria>

### 2. Daily Report Scheduled Task
<read_first>
- server/app/core/celery_app.py
- server/app/domains/sys_worker/alert_tasks.py
</read_first>
<action>
In `alert_tasks.py`, implement `send_daily_report_discord()` which formats the same report data and uses the webhook to post to Discord.
In `celery_app.py`, use `crontab(hour=17, minute=0)` (mind the timezone) for the `send_daily_report_discord` task in `beat_schedule`.
Note: The system timezone in `celery_app.py` is `Asia/Ho_Chi_Minh` so `crontab(hour=17, minute=0)` works perfectly.
</action>
<acceptance_criteria>
- `server/app/core/celery_app.py` contains `crontab(hour=17` for daily report
</acceptance_criteria>

## Verification
- Bot file python compiles without errors.
- Celery scheduled strings are valid syntactically.
