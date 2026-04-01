---
status: complete
phase: 11-device-monitor-alerts
source: [01-database-api-SUMMARY.md, 02-device-monitor-beat-SUMMARY.md, 03-discord-notibot-SUMMARY.md]
started: 2026-03-31T23:13:00Z
updated: 2026-03-31T23:13:00Z
---

## Current Test

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running server/service. Start the application from scratch. Server boots without errors and basic API call returns live data.
result: pass

### 2. Device Reset API
expected: Calling `POST /devices/{device_id}/reset` resets the device's `missed_pings` to 0 and its `status` to 'online'. Verified by hitting `GET /devices` to see the updated output.
result: issue
reported: "Không thể tải danh sách thiết bị."
severity: major

### 3. Celery Ping Devices
expected: With a missing ADB or Appium session for a device, the `ping_devices` Celery beat task runs every 5 minutes and increments `missed_pings`. Reaching exactly 3 sends a discord alert via the bot webhook.
result: issue
reported: "failed"
severity: blocker

### 4. Discord /report Command
expected: Running `/report` in Discord responds with a summary embed displaying new Shopee products and Facebook posts scraped today.
result: pass

## Summary

total: 4
passed: 2
issues: 2
pending: 0
skipped: 0

## Gaps

- truth: Calling `POST /devices/{device_id}/reset` resets the device's `missed_pings` to 0 and its `status` to 'online'. Verified by hitting `GET /devices` to see the updated output.
  status: failed
  reason: "User reported: Không thể tải danh sách thiết bị."
  severity: major
  test: 2
  artifacts: []
  missing: []

- truth: With a missing ADB or Appium session for a device, the `ping_devices` Celery beat task runs every 5 minutes and increments `missed_pings`. Reaching exactly 3 sends a discord alert via the bot webhook.
  status: failed
  reason: "User reported: failed"
  severity: blocker
  test: 3
  artifacts: []
  missing: []
