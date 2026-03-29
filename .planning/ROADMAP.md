# Milestone v1.1 Roadmap

**Phases:** 6 mapped, 100% requirements covered.

| # | Phase | Goal | Requirements | Criteria |
|---|-------|------|--------------|----------|
| 06 | Tooling & Setup | Gom gọn hạ tầng chạy, Setup script Start-all | TOOL-01 | 1 |
| 07 | Design System UI | Triển khai Design Token mới qua StitchMCP cho Frontend Web App | UI-01, UI-02 | 2 |
| 08 | Log Tracking | Thiết kế Logging & Màn hình hiển thị Lịch sử System | LOG-01, LOG-02 | 2 |
| 09 | Product Management | Crawl sản phẩm Shopee background và Màn hình hiển thị danh sách SP | PROD-01, PROD-02 | 2 |
| 10 | Target Groups Tracker | Cấu trúc tự động cào bài viết nhạy theo Groups và UI quản lý mồi | TARG-01, TARG-02, TARG-03 | 3 |
| 11 | Device Monitor & Alerts | Health-check Appium Devices, Discord Bot Report & Warning | DEV-01, DEV-02, NOTIF-01, NOTIF-02| 4 |

### Phase Details

**Phase 06: Tooling & Setup**
Goal: Gom gọn hạ tầng chạy, Setup script Start-all
Requirements: TOOL-01
Success criteria:
1. Có thể click vào một file `.bat` duy nhất để bật toàn bộ Backend, Queue, UI và Appium.

**Phase 07: Design System UI**
Goal: Triển khai Design Token mới qua StitchMCP cho Frontend Web App
Requirements: UI-01, UI-02
Success criteria:
1. StitchMCP áp dụng color palette và theme mới cho App.
2. Các màn hình cũ (Dashboard, Approval) đổi sang giao diện mới chuẩn và thân thiện hơn.

**Phase 08: Log Tracking**
Goal: Thiết kế Logging & Màn hình hiển thị Lịch sử System
Requirements: LOG-01, LOG-02
Success criteria:
1. Mọi task chạy qua Celery sinh dòng log vào bảng.
2. Admin xem được lịch sử và trace error log từ giao diện Dashboard.

**Phase 09: Product Management**
Goal: Crawl sản phẩm Shopee background và Màn hình hiển thị danh sách SP
Requirements: PROD-01, PROD-02
Success criteria:
1. Có màn hình trực quan dạng Grid/Table load ảnh và affiliate link của product.
2. Sản phẩm mới tự popup vào DB mỗi ngày.

**Phase 10: Target Groups Tracker**
Goal: Cấu trúc tự động cào bài viết nhạy theo Groups và UI quản lý mồi
Requirements: TARG-01, TARG-02, TARG-03
Success criteria:
1. Lên cấu hình danh sách nhóm đích.
2. Có Celery job quét bài về.
3. Có màn duyệt bài Scraped để chuẩn bị cho Auto-comment.

**Phase 11: Device Monitor & Alerts**
Goal: Health-check Appium Devices, Discord Bot Report & Warning
Requirements: DEV-01, DEV-02, NOTIF-01, NOTIF-02
Success criteria:
1. Background task ping được appium.
2. UI Devices báo đúng trạng thái thiết bị thực.
3. Bot Discord báo động khi rớt Appium/ADB, thống kê log cuối ngày.
