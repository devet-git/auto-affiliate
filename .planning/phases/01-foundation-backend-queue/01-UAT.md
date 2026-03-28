---
status: testing
phase: 01-foundation-backend-queue
source: [01-01-SUMMARY.md, 01-02-SUMMARY.md, 01-03-SUMMARY.md]
started: "2026-03-28T10:38:00Z"
updated: "2026-03-28T10:38:00Z"
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Kill server, start fresh `fastapi dev`. Server boots without errors, logs `Application startup complete.`, and GET /api/v1/health returns {"status": "ok"}.
result: pass

### 2. Admin Login — Valid Credentials
expected: POST /api/v1/auth/login (form-data) with correct username/password returns HTTP 200 with JSON `{"access_token": "eyJ...", "token_type": "bearer"}`.
result: pass

### 3. Admin Login — Wrong Password
expected: POST /api/v1/auth/login with wrong password returns HTTP 401 `{"detail": "Incorrect username or password"}`.
result: pass

### 4. Protected Route Blocks Unauthenticated
expected: Without token → HTTP 401. With valid Bearer token → HTTP 200 `{"task_id": "...", "status": "queued"}`.
result: issue
reported: "lỗi bước 2: không nhận được phản hồi từ server, loading rất lâu"
severity: major

## Summary

total: 4
passed: 3
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "POST /api/v1/worker/test với valid token phải trả về HTTP 200 {task_id, status} ngay lập tức"
  status: failed
  reason: "User reported: không nhận được phản hồi, loading rất lâu. Root cause: Redis chưa chạy → Celery .delay() treo vô thời hạn thay vì raise lỗi ngay"
  severity: major
  test: 4
  artifacts: [server/app/domains/sys_worker/router.py, server/app/domains/sys_worker/tasks.py]
  missing: ["Redis connection health check trước khi push task", "Try/except bắt ConnectionError từ Celery và trả 503 ngay"]

