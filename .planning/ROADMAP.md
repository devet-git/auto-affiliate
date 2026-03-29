# Roadmap: Auto Affiliate Control Center

## Overview

Hành trình xây dựng hệ thống tự động hóa tiếp thị liên kết (Shopee -> Cào Video Hot & Seeding -> TikTok/FB) dành cho 1 Admin quản lý. Dự án đi từ việc xây dựng lõi Backend FastAPI/Celery, đến module lấy dữ liệu, cào nội dung video nóng, tự chèn comment mồi, đăng bài đa tầng (API + Playwright + Phone) và cuối cùng là hoàn thiện Dashboard kiểm duyệt + Notibot.

## Phases

- [x] **Phase 1: Foundation (Backend & Queue)** - Khởi tạo cấu trúc API, Database và luồng Message Broker. (completed 2026-03-28)
- [x] **Phase 2: Shopee Data Pipeline** - Tự động hóa lấy data sản phẩm và sinh link Affiliate. (completed 2026-03-28)
- [x] **Phase 3: Content Sourcing & Social Seeding** - Cào video có sẵn trên mạng và rải comment link Affiliate vào Hội nhóm FB. (completed 2026-03-29)
- [x] **Phase 4: Real-Device Social Farm** - Đăng bài và tương tác bằng Thiết bị thật, hỗ trợ thao tác chéo giữa nhiều tài khoản App trên cùng 1 máy. (completed 2026-03-29)
- [ ] **Phase 5: Command Center UI & Bot** - Hoàn thiện React Dashboard và hệ thống thông báo báo cáo Telegram.

## Phase Details

### Phase 1: Foundation (Backend & Queue)
**Goal**: Xây dựng móng vững chắc cho hệ thống đa luồng và lưu trữ.
**Depends on**: Nothing
**Requirements**: [CORE-01, CORE-02, CORE-03, CORE-04]
**Success Criteria**:
  1. Hệ thống API FastAPI khởi chạy và kết nối trơn tru tới PostgreSQL.
  2. Admin test login gõ đúng mật khẩu trả ra JWT Token.
  3. Gửi thành công 1 job tính toán nhỏ vào Celery/Redis và chờ kết quả.
**Plans**: 3 plans

Plans:
- [ ] 01-01: Cài đặt FastAPI, cấu trúc thư mục, PostgreSQL & JWT Auth
- [ ] 01-02: Thiết lập luồng Worker Celery/Redis
- [ ] 01-03: Xây dựng Schema Database cốt lõi (Campaigns, Profiles, Job Log)

### Phase 2: Shopee Data Pipeline
**Goal**: Lõi Crawler tự động phân tích và lấy tài nguyên sản phẩm dùng để làm nội dung.
**Depends on**: Phase 1
**Requirements**: [CRWL-01, CRWL-02]
**Success Criteria**:
  1. Hàm fetch data có khả năng bóc tách ảnh/giá/mô tả từ link Shopee thô.
  2. Link lấy ra đã tự động quy đổi thành tracking link affiliate.
**Plans**: 2 plans

Plans:
- [x] 02-01: Module Shopee Scraper
- [x] 02-02: Module Affiliate Link Generator

### Phase 3: Content Sourcing & Social Seeding
**Goal**: Tìm và tải tự động các video hot liên quan để chuẩn bị lên bài (reup). Đồng thời tự động quét bài viết/nhóm FB để seeding comment link Affiliate.
**Depends on**: Phase 2
**Requirements**: [SEED-01, SEED-02]
**Success Criteria**:
  1. Bot cào được video MP4 từ nguồn (TikTok/Douyin/Shorts) về lưu trữ thành công.
  2. Playwright/API tự lập session login FB và comment thành công link Aff vào một bài test.
**Plans**: 2 plans

Plans:
- [x] 03-01: Hot Video Crawler (TikTok/Douyin) & Downloader
- [x] 03-02: Facebook Auto-Seeding & Commenting Worker

### Phase 4: Real-Device Social Farm
**Goal**: Điều khiển điện thoại thật (Appium) để tương tác. Đóng giả người dùng thật lướt feed (warm-up) rồi đăng bài (text/link/media) hoặc comment bằng nick cá nhân/fanpage.
**Depends on**: Phase 3
**Requirements**: [POST-03, POST-04, POST-05]
**Success Criteria**:
  1. Điện thoại lướt feed (warm-up) trơn tru trước khi thực hiện hành động chính mà không bị checkpoint.
  2. Bơm video thành công qua adb vào điện thoại và thực hiện đăng Reel lên Fanpage / Cá nhân.
  3. Hỗ trợ thao tác song song trên 2 ứng dụng Facebook khác nhau (VD: FB Main và FB Lite) để chạy chéo 2 tài khoản trên 1 thiết bị.
**Plans**: 3 plans

Plans:
- [ ] 04-01: Appium Controller & Multi-App Context (FB Main + FB Lite)
- [ ] 04-02: Humanized Behavior & Warm-up Actions (Scroll/Like)
- [ ] 04-03: Media Injection & Posting Automation (Reel/Photo/Link)

### Phase 5: Command Center UI & Bot
**Goal**: Giao diện điều khiển tập trung giúp Admin duyệt bài trước khi hệ thống "bơm" lên kênh.
**Depends on**: Phase 1, 4
**Requirements**: [UI-01, UI-02, UI-03]
**Success Criteria**:
  1. Màn hình Approval Queue hiển thị đầy đủ list video chờ duyệt. Bấm Approve -> tự chạy đăng bài.
  2. Có video mới cần duyệt -> Hệ thống tự gởi tin nhắn vô Telegram Admin kèm thumbnail/link.
**Plans**: 3 plans

Plans:
- [x] 05-01: Khởi tạo React Vite / Giao diện & Đăng nhập
- [x] 05-02: Màn hình Approval Queue & Quản lý Campaign
- [x] 05-03: Tích hợp Webhook Telegram/Discord Notifier

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/3 | Complete    | 2026-03-28 |
| 2. Shopee Data | 0/2 | Complete    | 2026-03-28 |
| 3. Sourcing & Seeding | 0/2 | Complete    | 2026-03-29 |
| 4. Social Farm | 0/3 | Complete    | 2026-03-29 |
| 5. Command Center | 0/3 | Not started | - |
