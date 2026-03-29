# Nyquist Validation Strategy: Phase 05 - command-center-ui-bot

**Date:** 2026-03-29
**Status:** Draft

## Validation Matrix

### 1. Core Objectives
| Goal/Requirement | Verification Method | Acceptance Criteria |
|------------------|---------------------|---------------------|
| Màn hình Approval Queue (Grid & Table) | Web UI Test / Manual | UI renders without console errors. Toggle buttons switch between layouts. |
| Inline edit title/caption | API Mock / Manual | Edited text submits correctly to the backend via PUT/PATCH request. |
| Telegram Bot Instant Notification | Webhook mock trigger | Bot sends a message to configured chat_id when an item transitions to "pending approval" state. |
| Telegram Two-way `/approve` Command | Webhook cURL test | Sending POST to `/webhook` with `/approve <id>` changes the DB state to approved. |

### 2. Integration Points
- **FastAPI <-> React**: CORS must be properly configured in FastAPI to allow the Vite Dev Server (`localhost:5173`) to query the API.
- **FastAPI <-> Telegram**: FastAPI server must expose a public (or ngrok-forwarded) `/webhook` URL that accepts incoming messages from Telegram.
- **Celery <-> Aiogram**: Celery workers must be able to securely initialize an `aiogram.Bot` instance (session) to push outbound notifications without blocking task execution.

### 3. Edge Cases & Error Handling
- Ngrok/Localhost offline: How does the system handle webhook registration failures on boot?
  - *Mitigation*: Start the bot passively or log failure gracefully without crashing the main FastAPI thread.
- Invalid webhook token:
  - *Test*: Submit a mocked Telegram Webhook POST without the `X-Telegram-Bot-Api-Secret-Token`.
  - *Expected*: FastAPI returns 401 Unauthorized or 403 Forbidden.

## Autonomous Verification Scripts

```bash
# Verify Frontend initialized
test -f server/ui/package.json
test -d server/ui/src/components/ui

# Verify Backend endpoint
grep "@app.post(\"/webhook" server/app/main.py
```
