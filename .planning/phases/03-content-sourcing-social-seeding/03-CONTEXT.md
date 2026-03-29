# Phase 3: Content Sourcing & Social Seeding - Context

**Gathered:** 2026-03-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Tìm và tải tự động các video hot liên quan để chuẩn bị lên bài (reup). Đồng thời tự động quét bài viết/nhóm FB để seeding comment link Affiliate. Xây dựng module xử lý video (Deduplication) chống quét bản quyền, và sử dụng máy thật (Appium) để đi comment.

</domain>

<decisions>
## Implementation Decisions

### Video Source Strategy
- **D-01:**  **Cấu hình đa nguồn**. Thiết kế một Interface / Base Crawler chung có thể dễ dàng plug thêm các nguồn cào khác (TikTok, Douyin, YouTube Shorts, FB Reels) thông qua file config/database.

### Facebook Seeding Target
- **D-02:** **Nhắm theo Hội nhóm (Groups) + Extensible**. Trọng tâm đầu tiên là tự động quét danh sách Group ID do Admin nạp sẵn để lấy Top posts hằng ngày. Vẫn thiết kế module mở để sau này có thể thêm tính năng nhắm rải link lên Fanpage mà không bẻ gãy code.

### Anti-Checkpoint cho Seeding FB
- **D-03:** **Mix Automation (Bot săn mồi + Phone comment)**. Crawler (Playwright/HTTP Request) siêu tốc chịu trách nhiệm cào và lọc mã ID các bài viết/video hot, sau đó đổ vào Job Queue để cho Máy điện thoại thật (chạy qua Appium/ADB) vô tận nơi thả comment.

### Video Deduplication (Lách luật Re-up) 
- **D-04:** **Đa chiến thuật (Tùy chọn)**. Tích hợp FFmpeg hỗ trợ cả 2 option để Admin gạt Switch:
  - Bọc nhẹ: Xoá Metadata + sửa Hash byte.
  - Phẩu thuật sâu: Flip video, thêm blur background tĩnh, đổi speed/mute nhạc. 

### the agent's Discretion
- Kiến trúc schema Job Queue cho Phone chạy Seeding làm sao để gánh tác vụ chậm (chờ thiết bị điện thoại).
- Lựa chọn thư viện Python FFmpeg-python hoặc Subprocess để build engine Deduplication video siêu tốc mà không quá tải RAM.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope
- `.planning/PROJECT.md` — Định nghĩa quy mô chiến lược cào reup và auto seeding mới đổi.
- `.planning/ROADMAP.md` — Luồng xử lý lấy dữ liệu Shopee -> Video Hot/FB.
- `.planning/REQUIREMENTS.md` — Múc SEED-01 và SEED-02 về sourcing và FB spam.

</canonical_refs>

<specifics>
## Specific Ideas

- Vì bạn dùng ADB/Appium, Worker xử lý Comment cần cô lập và giới hạn rate-limit cẩn thận do thao tác trên điện thoại vật lý mất nhiều thời gian hơn call API/Playwright.
- Thao tác sửa luồng (thay Phase 3 cũ bằng Sourcing/Seeding) đã chuyển dự án lên 1 tầm cao mới với khả năng "Tự cào, tự chỉnh lách bản quyền, tự tìm bài rải Link Affiliate."

</specifics>

<deferred>
## Deferred Ideas

- None.

</deferred>
