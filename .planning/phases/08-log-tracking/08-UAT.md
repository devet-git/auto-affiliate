---
status: partial
phase: 08-log-tracking
source: [08-PLAN-01-database-signals-SUMMARY.md, 08-PLAN-02-endpoints-and-beat-SUMMARY.md, 08-PLAN-03-web-logs-ui-SUMMARY.md]
started: 2026-03-30T00:33:00Z
updated: 2026-03-30T00:42:00Z
---

## Current Test
<!-- OVERWRITE each test - shows where we are -->

[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running server/service. Clear ephemeral state (temp DBs, caches, lock files). Start the application from scratch. Server boots without errors, any DB tables for task logs are created, and a primary query (health check, homepage load, or basic API call) returns live data.
result: pass

### 2. Verify Background Task Logging
expected: Trigger a background Celery task (e.g. via an existing test job). Verify that its `STARTED` and subsequent `SUCCESS` or `FAILED` states are automatically recorded in the database without manual logging.
result: issue
reported: "fail, tôi chạy 1 campaign nhưng k có log nào được ghi"
severity: major

### 3. Verify Log Retention Setting
expected: Open the System Logs page in the Web UI. Change the Log Retention (Days) value and click Save. Refresh the page to ensure the value persists from the server.
result: pass

### 4. Verify System Logs Dashboard
expected: Navigate to the "System Logs" sidebar item. A Shadcn-styled data table should display recent execution traces. Test the "Refresh" button and filter dropdowns (Status, Task Name) to confirm they update the displayed data.
result: blocked
blocked_by: prior-phase
reason: "blocked, vì không có log nào được ghi"

### 5. View Task Error Details
expected: Find a failed task execution in the System Logs table. Click the terminal icon button in its row. A browser alert or modal should display the error traceback successfully.
result: blocked
blocked_by: prior-phase
reason: "blocked, vì không có log nào được ghi "

## Summary

total: 5
passed: 2
issues: 1
pending: 0
skipped: 0

## Gaps

- truth: "Trigger a background Celery task (e.g. via an existing test job). Verify that its `STARTED` and subsequent `SUCCESS` or `FAILED` states are automatically recorded in the database without manual logging."
  status: failed
  reason: "User reported: fail, tôi chạy 1 campaign nhưng k có log nào được ghi"
  severity: major
  test: 2
  artifacts: []
  missing: []
