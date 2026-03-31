# Phase 11: Device Monitor & Alerts - Discussion Log

**Date:** 2026-03-31

## Q&A Log

**Q1: Device Ping Strategy (How often and what tool to ping)?**
- **Presented Options:** 
  - A: Ping `adb devices` every 1 minute.
  - B: Ping `adb devices` every 5 minutes.
  - C: Ping both `adb devices` and Appium session status every 5 minutes.
- **User Selection:** 1C (Ping both `adb devices` and Appium session status every 5 minutes)

**Q2: Offline Alert Sensitivity (Immediate alert vs delayed to confirm)?**
- **Presented Options:**
  - A: Notify immediately on the first missed ping.
  - B: Delay: Notify after 2 consecutive missed pings.
  - C: Delay: Notify after 3 consecutive missed pings.
- **User Selection:** 2C (Notify after 3 consecutive missed pings)

**Q3: Scraper "Stuck" Definition (How to detect a stuck job or IP ban)?**
- **Presented Options:**
  - A: If a task runs for over a specific time limit.
  - B: If there are no new database inserts/updates for X hours while the crawler task is running.
  - C: Capture specific `TimeoutError` / IP Ban exceptions from Playwright and alert instantly.
- **User Selection:** 3B (If there are no new database inserts/updates for X hours while the crawler task is running)

**Q4: Daily Report Schedule (When to send the daily report)?**
- **Presented Options:**
  - A: 08:00 AM
  - B: 17:00 PM (5:00 PM)
  - C: 23:59 PM (Midnight)
- **User Selection:** 4B (17:00 PM) and "or when I send a command in discord" (Support for on-demand generation via Discord bot).
