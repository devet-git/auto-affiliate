# Auto Affiliate Control Center

## What This Is

Một nền tảng quản trị trung tâm (Command Center) dạng web application dành cho việc tự động hoá tiếp thị liên kết (affiliate marketing). Hệ thống đóng vai trò quản lý chiến dịch lấy dữ liệu từ Shopee, cào nội dung video nóng, tự chèn comment mồi, và đăng bài đa tầng qua Playwright cùng thiết bị điện thoại Android thật (Appium), được kiểm duyệt sát sao bằng giao diện React và Notibot Discord.

## Core Value

Khả năng vận hành tự động (hands-free) quy mô lớn với độ tin cậy cao, kết hợp linh hoạt giữa xử lý hàng loạt tốc độ cao và cơ chế kiểm duyệt chất lượng thủ công (Approval Queue) để bảo vệ tài sản mạng xã hội.

## Current Milestone: v1.2 Future Enhancements

**Goal:** Chạy nốt nghiệp vụ Crawler Sản Phẩm (Tech Debt từ v1.1) và đóng gói trọn vẹn workflow tự động hoá seeding kiếm tiền.

**Target features:**
1. Quản lý danh mục Sản phẩm Shopee và URL tính năng tự động cào.
2. Nâng cấp các luồng phụ trợ.
Shifting focus of v1.2. The v1.1 milestone "Tooling & Core Features" is complete (excluding Product Management crawler which is pushed to v1.2).

## Requirements

### Validated

- ✓ Giao diện Quản trị (Dashboard) xử lý Approval Queue & CRUD Campaigns — v1.0
- ✓ Automation Pipeline (FastAPI, Postgres, Celery, Redis) đa luồng tính năng cao — v1.0
- ✓ Content Sourcing & Auto Seeding (Shopee Scraper -> Affiliate Generator -> TikTok/Douyin Catcher -> FB Poster) — v1.0
- ✓ Chiến lược Mạng xã hội Phân tầng (Multi-tier: Graph API, Playwright, Phone Appium Automation) — v1.0
- ✓ Chat Bot Notifier (Đổi từ Telegram sang Discord.py tích hợp trong lifespan) — v1.0
- ✓ [TOOL-01] One-click Start Script (`start-all.bat` / `stop-all.bat`) — v1.1
- ✓ [UI-01] Design System từ StitchMCP và làm mịn / tạo mới UI Screens — v1.1
- ✓ [LOG-01] Màn hình Tracking Logs & Execution History — v1.1
- ✓ [TARG-01] Quản lý Target Facebook Groups và Scraped Posts — v1.1
- ✓ [DEV-01] Dashboard Quản lý Health-check Thiết bị Appium/ADB — v1.1
- ✓ [NOTIF-01] Discord Alerts nâng cao — v1.1

### Active

- [ ] [PROD-01] Quản lý Sản phẩm Shopee và Crawler URL (Tech Debt from v1.1)

### Out of Scope

- [Public Facing Website] — Nền tảng này chỉ phục vụ duy nhất bạn (Cá nhân/Admin) quản trị tài nguyên. Không đăng ký membership cho người ngoài.
- [Phân quyền đa mức độ Multi-tenant] — Không cần thiết vì mục đích chỉ là cấp Personal.
- [Video Generation/Rendering] — Không tạo video nữa (kể cả Local FFmpeg hay 3rd-Party API). Tối giản hóa quy trình bằng cách cào video có sẵn và đi bình luận mồi (Seeding).

## Context

- **Workflow Đặc thù**: Yêu cầu thao tác rất nhiều với đa luồng (task queue), giả lập trình duyệt, xử lý media (mp4, mkv) và quản lý state phức tạp.
- **Tính ổn định của Account**: Các nền tảng liên tục thay đổi thuật toán chống bot, do đó việc chia Tier (API & Playwright) là bắt buộc.
- **Bối cảnh hiện tại**: v1.1 đã hoàn tất (shipped 2026-04-01). Sẵn sàng bắt đầu v1.2 tập trung vào Product Management và Crawler nâng cao.

## Constraints

- **Tech Stack Backend**: Dùng Python (FastAPI + Celery/Redis + PostgreSQL).
- **Tech Stack Frontend**: Sử dụng React.js (Vite/Next.js).
- **Tài nguyên phần cứng**: Cần Phone Android thật bật Debug ADB/Appium nối cáp trực tiếp cho Phase Social Farm.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Chọn Python làm Backend | Dễ dàng tương tác với Playwright, FFmpeg và các thư viện AI. Phù hợp nhất cho automation bot. | ✓ Good |
| Hệ thống đăng bài Tier Phone Appium | Giảm thiểu khóa tài khoản hàng loạt định kỳ nhờ dùng device thực sự bơm intent vào ADB. | ✓ Good |
| Ngừng Generate Video | Chuyển sang cào video hot có sẵn và reup, kết hợp auto comment nhóm FB để ra kết quả nhanh hơn. | ✓ Good |
| Chuyển từ Telegram Webhook sang Discord.py Bot | Giảm trừ yêu cầu ngrok public network, bot chạy nền websockets ổn định. | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

---
*Last updated: 2026-04-01 after v1.1 milestone completion*
