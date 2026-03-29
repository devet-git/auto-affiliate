# Requirements: Auto Affiliate Control Center

**Defined:** 2026-03-28
**Core Value:** Khả năng vận hành tự động quy mô lớn với độ tin cậy cao, kết hợp linh hoạt xử lý hàng loạt và kiểm duyệt thủ công (Approval Queue).

## v1 Requirements

### Architecture & Backend (CORE)

- [ ] **CORE-01**: Hệ thống API chạy trên FastAPI với PostgreSQL database. Thiết kế dành riêng cho **1 người dùng duy nhất (Cá nhân/Admin)**.
- [ ] **CORE-02**: Tích hợp luồng hàng đợi Celery/Redis để xử lý job background.
- [ ] **CORE-03**: Màn hình đăng nhập bảo mật cho cá nhân tài khoản Admin (React Vite).
- [ ] **CORE-04**: Database lưu trữ cấu trúc Campaign, Profile (TikTok/FB) và Job history.

### Crawler & Data (CRWL)

- [ ] **CRWL-01**: Tích hợp scraper/API lấy dữ liệu sản phẩm từ Shopee (ảnh, tên, giá).
- [ ] **CRWL-02**: Tự động chuyển đổi shortlink sang link Affiliate Shopee.

### Content Sourcing & Seeding (SEED)

- [ ] **SEED-01**: Cào video ngắn hot (TikTok/Douyin/Reels/Shorts) liên quan đến keyword sản phẩm. Tự động tải file MP4 về server.
- [ ] **SEED-02**: Tự động tìm kiếm các bài viết/Hội nhóm Facebook liên quan đến sản phẩm và comment rải link Affiliate Shopee.

### Social Farm & Device Automation (POST)

- [ ] **POST-03**: Điều khiển thiết bị thật qua Appium/ADB mô phỏng thao tác người dùng tự nhiên (Lướt NewsFeed, còm/like mồi - warm-up).
- [ ] **POST-04**: Quản lý thao tác 2 App cùng lúc trên 1 máy (VD: FB Main & FB Lite) để chạy chéo 2 tài khoản.
- [ ] **POST-05**: Bơm file Media (Ảnh/Video Reel) bằng cơ chế ADB đẩy thẳng vào điện thoại và tự động đăng Reels từ Gallery.

### Notifications & Dashboard (UI)

- [ ] **UI-01**: Giao diện Approval Queue - duyệt, xem trước video từ 3rd-party và chỉnh sửa lưới trước khi push.
- [ ] **UI-02**: Quản lý tạo/xoá Campaign dữ liệu hàng loạt.
- [ ] **UI-03**: **Chat Bot Integration**: Tích hợp Telegram / Discord / Messenger API bổ sung Webhook gởi Noti khẩn cấp khi: Video mới cần duyệt chờ chốt, Lỗi tài khoản rớt kết nối mạng điện thoại.

## v2 Requirements

### Analytics & Tracking (STAT)

- **STAT-01**: Dashboard tổng hợp biến động click/doanh thu thực tế theo từng Campaign.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Multi-tenant/Phân quyền phức tạp | Hệ thống đã chốt chỉ dùng cho **1 cá nhân (Personal use)**, tránh tốn thời gian xây quyền Agent/Role vô bổ. |
| Video Generation/Rendering | Quyết định đi thẳng vào hướng re-up video crawl được và Seeding tự động (không render video mới mẻ hay tích hợp bên thứ 3 AI nữa). |
| Public Website | Admin nội bộ, không tin tức, không portal. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CORE-01 | Phase 1 | Pending |
| CORE-02 | Phase 1 | Pending |
| CORE-03 | Phase 1 | Pending |
| CORE-04 | Phase 1 | Pending |
| CRWL-01 | Phase 2 | Pending |
| CRWL-02 | Phase 2 | Pending |
| SEED-01 | Phase 3 | Pending |
| SEED-02 | Phase 3 | Pending |
| POST-03 | Phase 4 | Pending |
| POST-04 | Phase 4 | Pending |
| POST-05 | Phase 4 | Pending |
| UI-01 | Phase 5 | Pending |
| UI-02 | Phase 5 | Pending |
| UI-03 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-28*
*Last updated: 2026-03-28 after user modifications*
