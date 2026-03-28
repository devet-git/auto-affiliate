# Roadmap: Auto Affiliate Control Center

## Overview

Hành trình xây dựng hệ thống tự động hóa tiếp thị liên kết (Shopee -> Video 3rd Party -> TikTok/FB) dành cho 1 Admin quản lý. Dự án đi từ việc xây dựng lõi Backend FastAPI/Celery, đến module lấy dữ liệu, gọi API sinh video, đăng bài đa tầng (API + Playwright + Phone) và cuối cùng là hoàn thiện Dashboard kiểm duyệt + Notibot.

## Phases

- [x] **Phase 1: Foundation (Backend & Queue)** - Khởi tạo cấu trúc API, Database và luồng Message Broker. (completed 2026-03-28)
- [x] **Phase 2: Shopee Data Pipeline** - Tự động hóa lấy data sản phẩm và sinh link Affiliate. (completed 2026-03-28)
- [ ] **Phase 3: 3rd-Party Video Generation** - Đẩy data qua API bên thứ ba (Google Flow/HeyGen) để sinh video dọc.
- [ ] **Phase 4: Multi-tier Posting Options** - Xây dựng các Node đăng mạng xã hội (Official API, Browser Automation, Phone Appium).
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

### Phase 3: 3rd-Party Video Generation
**Goal**: Chuyển đổi dữ liệu và gửi yêu cầu tạo video tự động qua API nền tảng AI.
**Depends on**: Phase 2
**Requirements**: [REND-01, REND-02]
**Success Criteria**:
  1. Code gọi API Google Flow / 3rd Party trả về Response chứa Video MP4 mượt mà.
  2. Video tự động tải về / tinh chỉnh kích thước đúng form Tiktok 9:16 lưu vào hệ thống cục bộ.
**Plans**: 2 plans

Plans:
- [ ] 03-01: Tích hợp API Client 3rd-Party Video Generation
- [ ] 03-02: Format Media Downloader Worker

### Phase 4: Multi-tier Posting Options
**Goal**: Tự động lên lịch và đăng tải video trên nhiều cấp độ để chống Anti-bot.
**Depends on**: Phase 3
**Requirements**: [POST-01, POST-02, POST-03, POST-04]
**Success Criteria**:
  1. Post bài chạy ngầm bằng Browser gán Proxy hoàn tất không bị văng lỗi màn hình.
  2. Gửi lệnh qua Appium Mobile điều khiển mở app TikTok và upload video thành công.
**Plans**: 3 plans

Plans:
- [ ] 04-01: Automation Tier 1 (Official Graph API)
- [ ] 04-02: Automation Tier 2 (Playwright + Proxy Management)
- [ ] 04-03: Mobile Automation Tier 3 (Appium/ADB integration)

### Phase 5: Command Center UI & Bot
**Goal**: Giao diện điều khiển tập trung giúp Admin duyệt bài trước khi hệ thống "bơm" lên kênh.
**Depends on**: Phase 1, 4
**Requirements**: [UI-01, UI-02, UI-03]
**Success Criteria**:
  1. Màn hình Approval Queue hiển thị đầy đủ list video chờ duyệt. Bấm Approve -> tự chạy đăng bài.
  2. Có video mới cần duyệt -> Hệ thống tự gởi tin nhắn vô Telegram Admin kèm thumbnail/link.
**Plans**: 3 plans

Plans:
- [ ] 05-01: Khởi tạo React Vite / Giao diện & Đăng nhập
- [ ] 05-02: Màn hình Approval Queue & Quản lý Campaign
- [ ] 05-03: Tích hợp Webhook Telegram/Discord Notifier

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/3 | Complete    | 2026-03-28 |
| 2. Shopee Data | 0/2 | Complete    | 2026-03-28 |
| 3. Video Generation | 0/2 | Not started | - |
| 4. Posting Options | 0/3 | Not started | - |
| 5. Command Center | 0/3 | Not started | - |
