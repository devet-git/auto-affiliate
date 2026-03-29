# Milestone v1.1 Requirements

## [UI/UX] Giao diện & Trải nghiệm
- [ ] **UI-01**: Tích hợp hệ thống MCP (StitchMCP) để thiết lập Design System (màu sắc, typography, components).
- [ ] **UI-02**: Áp dụng Design System mới để Refresh và làm mượt mặt các màn hình hiện tại (Dashboard, Approval Queue, Campaigns).

## [DEVICES] Quản lý Thiết bị
- [ ] **DEV-01**: Xây dựng màn hình Device Management để hiển thị danh sách thiết bị kèm trạng thái kết nối.
- [ ] **DEV-02**: Backend task (Celery Beat) định kỳ ping `adb devices` hoặc Appium session status để cập nhật tình trạng thiết bị (Online, Offline, Busy).

## [PRODUCTS] Quản lý Nguồn Sản phẩm
- [ ] **PROD-01**: Màn hình Web quản lý trực quan danh sách Sản phẩm kéo từ Shopee (Ảnh, Tên, Giá, Affiliate URL đã tạo).
- [ ] **PROD-02**: Thiết lập job cron (background) tự động quét danh mục hoặc keyword trên Shopee để cào sản phẩm mới đổ vào DB.

## [TARGETS] Quản lý Post & Group Seeding
- [ ] **TARG-01**: Màn hình quản lý danh sách Facebook Groups mục tiêu (Tên Group, URL, UID).
- [ ] **TARG-02**: Màn hình xem danh sách các bài viết nhạy/tương tác cao (Scraped Posts) cào được từ các Groups dựa vào keyword liên quan đến sản phẩm hiện có.
- [ ] **TARG-03**: Celery scraper chạy ngầm, dựa trên danh sách Target Groups và keywords để tìm bài viết thả mồi và lưu vào cơ sở dữ liệu.

## [LOGS] Tracking & Lịch sử
- [ ] **LOG-01**: Bổ sung bảng `TaskLog` lưu trữ các hoạt động chạy của Celery, Crawler, Playwright và Appium.
- [ ] **LOG-02**: Màn hình "Execution Logs" lấy log từ DB dạng Table và biểu đồ (như success rate, total runs) để theo dõi tiến độ dễ dàng.

## [NOTIFICATIONS] Bot Discord
- [ ] **NOTIF-01**: Bot tự động cảnh báo channel khi Thiết bị (Device) Offline hoặc mất kết nối mạng.
- [ ] **NOTIF-02**: Cảnh báo tức thời nếu luồng Scraper bị kẹt / IP bị chặn, và một Daily Report vào mỗi sáng.

## [TOOLING] Script Khởi chạy Hệ thống
- [x] **TOOL-01**: Viết `.bat` (Windows) để khởi động toàn bộ dependencies bằng một click: FastAPI, tất cả các hàng đợi Celery workers, Appium Server, Vite React dev server.

## Future Requirements (Deferred)
- (None at present)

## Out of Scope
- [Real-time Log stream = WebSocket] — Chưa thực sự cần thiết, chỉ hiển thị bảng Log có phân trang hoặc nút refresh là đủ để đáp ứng nhu cầu tracking lúc này.
- [Trí tuệ nhân tạo duyệt bài tự động] — Hiện tại Admin vẫn sẽ duyệt tay các bài Scraped Posts hoặc cài auto-approve cứng nhắc chứ chưa dùng LLM vào duyệt content mồi.

## Traceability
* Mapped in ROADMAP.md
