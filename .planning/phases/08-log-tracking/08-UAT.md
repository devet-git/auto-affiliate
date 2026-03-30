---
updated: 2026-03-30T11:38:00Z
status: partial
---

## Current Test
[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running server/service. Clear ephemeral state (temp DBs, caches, lock files). Start the application from scratch. Server boots without errors, any DB tables for task logs are created, and a primary query (health check, homepage load, or basic API call) returns live data.
result: pass

### 2. Verify Background Task Logging
expected: Trigger a background Celery task (e.g. via an existing test job). Verify that its `STARTED` and subsequent `SUCCESS` or `FAILED` states are automatically recorded in the database without manual logging.
result: pass

### 3. Verify Log Retention Setting
expected: Open the System Logs page in the Web UI. Change the Log Retention (Days) value and click Save. Refresh the page to ensure the value persists from the server.
result: pass

### 4. Verify System Logs Dashboard
expected: Navigate to the "System Logs" sidebar item. A Shadcn-styled data table should display recent execution traces. Test the "Refresh" button and filter dropdowns (Status, Task Name) to confirm they update the displayed data.
result: pass

### 5. View Task Error Details
expected: Find a failed task execution in the System Logs table. Click the terminal icon button in its row. A browser alert or modal should display the error traceback successfully.
result: issue
reported: "pass, but error message not detail, like: <traceback object at 0x0000021A192EAD00>"
severity: minor

## Summary

total: 5
passed: 4
issues: 1
pending: 0
skipped: 0

## Gaps

- truth: "Find a failed task execution in the System Logs table. Click the terminal icon button in its row. A browser alert or modal should display the error traceback successfully."
  status: diagnosed
  reason: "User reported: pass, but error message not detail, like: <traceback object at 0x0000021A192EAD00>"
  severity: minor
  test: 5
  root_cause: "In celery_signals.py, task_failure_handler uses str(traceback) which prints the default object representation instead of formatting it."
  artifacts:
    - path: "server/app/domains/sys_worker/celery_signals.py"
      issue: "Using str(traceback) instead of using traceback formatting tools or exception str"
  missing:
    - "Update task_failure_handler to properly format the exception traceback into a readable string."
