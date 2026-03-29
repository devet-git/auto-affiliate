# Phase 05: Command Center UI & Bot - Context

**Gathered:** 2026-03-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Xây dựng giao diện Frontend hoàn chỉnh trên nền tảng React Vite kết hợp quản trị hiển thị các danh sách pending action, cộng hưởng với Bot Telegram kết nối API hai chiều để nhận Noti tức thời cũng như phản hồi Action thẳng từ xa.
</domain>

<decisions>
## Implementation Decisions

### Approval Queue UX/UI
- **D-01:** Hỗ trợ View Toggle (đổi chế độ View): Người dùng có thể chuyển đổi mượt mà giữa Dạng Thẻ (Card Grid - ưu tiên xem thumbnail) và Dạng Bảng (Data Table - xem list lượng lớn).
- **D-02:** Hỗ trợ Inline Edit: Các trường Caption/Tiêu đề của Video có thể bấm sửa trực tiếp (Inline) trên màn hình xếp hàng trước khi bấm "Approve" (duyệt).

### Telegram Bot Integration
- **D-03:** Instant Notifications: Gửi noti ngay lập tức cho Admin khi có 1 bài Post mới chui vào mẻ lưới "Cần duyệt". 
- **D-04:** Two-way Command Execution: Hỗ trợ webhook hai chiều. Admin có thể ném lệnh ngược lại cho con Bot (ví dụ: `/approve <id>`, `/reject <id>`) để duyệt bài ngay lập tức thông qua khung chat của Telegram, giúp xử lý gọn lệnh mà không cần mở máy tính hay vào Web Dashboard.

### Dashboard Aesthetics
- **D-05:** Core Components: Sử dụng **Shadcn UI** làm thành phần cốt lõi xây dựng layout để đảm bảo tốc độ build nhanh, chuẩn cấu trúc component hiện đại, kết hợp với Tailwind CSS.

### the agent's Discretion
- Logic tự động chọn Dark hay Light mode của OS hiện tại làm mặc định.
- Cơ chế Router/State Management (Zustand hay Context API).
- Quản lý Webhook (Polling hay thư viện TeleBot `aiogram`/`python-telegram-bot`).
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope & Guidelines
- `.planning/PROJECT.md` — Core value is large-scale automation with manual approval queue
- `.planning/REQUIREMENTS.md` — UI-01, UI-02, UI-03 definitions
- `.planning/ROADMAP.md` — Phase 5 goals and success criteria
</canonical_refs>

<specifics>
## Specific Ideas
- Web Dashboard cần có cơ chế fetch luồng Data API (Sử dụng Axios/React Query).
- Hệ thống Telegram Bot cần được chạy trên 1 Task Worker hoặc một endpoint API chịu trách nhiệm Handle Event từ Telegram bắn về (Webhook vs Long Polling).
</specifics>

<deferred>
## Deferred Ideas
None — Full Command Center coverage.
</deferred>

---

*Phase: 05-command-center-ui-bot*
*Context gathered: 2026-03-29 via discussion*
