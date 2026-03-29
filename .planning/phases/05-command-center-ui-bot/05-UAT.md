---
status: testing
phase: 05-command-center
source: 
  - 05-01-SUMMARY.md
  - 05-02-SUMMARY.md
  - 05-03-SUMMARY.md
started: 2026-03-29T18:01:00Z
updated: 2026-03-29T18:43:00Z
---

## Current Test

number: 5
name: Discord Bot Approval
expected: |
  Send `/approve 123` via Discord Slash Command. The bot replies with " Không tìm thấy bản ghi" hoặc "✅ Đã duyệt thành công".
awaiting: 

## Tests

### 1. Cold Start Smoke Test
expected: Start the frontend application (`npm run dev`) and backend API (`fastapi dev`). The applications boot without errors. The user can navigate to `http://localhost:5173` without encountering a blank screen or immediately crashing.
result: [passed]

### 2. Login Flow and JWT Deflection
expected: Accessing `http://localhost:5173/` while logged out redirects to `/login`. Submitting valid credentials (`admin` / `admin`) logs in successfully, stores the session, and grants access to Dashboard.
result: [passed]

### 3. Approval Queue UI
expected: The Dashboard Sidebar shows "Approval Queue". The interface toggles between Grid and Table views without errors. The "Edit" button allows modifying the post UI caption seamlessly.
result: [passed]

### 4. Campaigns UI
expected: The Dashboard Sidebar shows "Campaigns". Clicking "New Campaign" opens a Shadcn Dialog.
result: [passed]

### 5. Discord Bot Approval
expected: Send `/approve 123` via Discord Slash Command. The bot replies with " Không tìm thấy bản ghi" hoặc "✅ Đã duyệt thành công".
result: [passed]

## Summary

total: 5
passed: 5
issues: 0
pending: 0
skipped: 0

## Gaps
