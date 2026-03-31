# Phase 11: Device Monitor & Alerts - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Quản lý thiết bị (hiển thị trạng thái kết nối Appium/ADB) và Notibot cảnh báo trên Discord (offline, kẹt scraper, daily report).
</domain>

<decisions>
## Implementation Decisions

### Device Ping Strategy
- **D-01:** Ping cả `adb devices` và Appium session status định kỳ mỗi 5 phút (qua Celery Beat).

### Offline Alert Sensitivity
- **D-02:** Chỉ gửi cảnh báo (alert) lên Discord khi thiết bị offline sau 3 lần ping thất bại liên tiếp (15 phút offline) để tránh báo động giả do đứt kết nối cáp ngắn hạn.

### Scraper "Stuck" Definition
- **D-03:** Cảnh báo Scraper bị kẹt nếu không có bản ghi mới nào (no database inserts/updates) được xử lý trong vòng X giờ trong khi task (crawler job) vẫn đang chạy.

### Daily Report Schedule & Commands
- **D-04:** Gửi báo cáo tự động (Daily Report) vào lúc 17:00 PM hàng ngày.
- **D-05:** Triển khai thêm Discord command để có thể xuất báo cáo (on-demand) bất cứ lúc nào qua khung chat.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Core Requirements
- `.planning/PROJECT.md` — Vision & Active milestone targets (v1.1).
- `.planning/REQUIREMENTS.md` — Acceptance criteria specifically for `[DEVICES]` and `[NOTIFICATIONS]`.

### Codebase Context (Pre-existing)
- `server/app/domains/devices/models.py` — Contains the `Device` model.
- `server/app/domains/notify/bot.py` — The existing Discord bot implementation to wire alerts into.
</canonical_refs>
