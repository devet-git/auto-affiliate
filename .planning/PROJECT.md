# Auto Affiliate Control Center

## What This Is

Một nền tảng quản trị trung tâm (Command Center) dạng web application dành cho việc tự động hoá tiếp thị liên kết (affiliate marketing). Hệ thống đóng vai trò quản lý chiến dịch lấy dữ liệu từ Shopee, tạo video tự động nhờ AI, và lên lịch đăng bài quy mô lớn lên các mạng xã hội (TikTok, Facebook) qua hệ thống phân tầng tài khoản.

## Core Value

Khả năng vận hành tự động (hands-free) quy mô lớn với độ tin cậy cao, kết hợp linh hoạt giữa xử lý hàng loạt tốc độ cao và cơ chế kiểm duyệt chất lượng thủ công (Approval Queue) để bảo vệ tài sản mạng xã hội.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

(Chưa có - Dự án đang ở giai đoạn khởi tạo cấu trúc tự động hóa cốt lõi mới)

### Active

<!-- Current scope. Building toward these. -->

- [ ] **Giao diện Quản trị (Dashboard)**: Nơi admin thiết lập chiến dịch, theo dõi luồng công việc, quản lý tài khoản và xét duyệt (approve/reject) video.
- [ ] **Automation Pipeline (Hàng đợi tác vụ)**: Hệ thống chạy đa luồng hỗ trợ Automation theo Chiến dịch (lấy gốc từ Shopee, render hàng loạt, auto post).
- [ ] **Hàng đợi Duyệt thủ công (Approval Queue)**: Tính năng chặn lại các video trong luồng để người dùng kiểm tra trước khi hệ thống "bơm" lên TikTok.
- [ ] **Render Video qua 3rd-Party API**: Chuyển giao hoàn toàn việc tạo video cho bên thứ 3 (Google Flow, HeyGen, v.v...) để tối ưu chất lượng thay vì render trên server.
- [ ] **Chiến lược Mạng xã hội Phân tầng (Multi-tier Posting)**: 
  - Tier 1: Nền tảng cấu hình sử dụng Official API (Graph API).
  - Tier 2: Tự động hóa trình duyệt mô phỏng (Playwright/Proxy).
  - Tier 3: **Phone Automation** - Kết nối thiết bị smartphone thật qua cáp/Wifi (ADB/Appium) để thao tác như người dùng mộc, lách luật quét máy ảo.
- [ ] **Chat Bot Notifier**: Báo cáo trực tiếp tình trạng (Lỗi acc, Có video cần duyệt...) về tin nhắn Telegram/Discord/Messenger.

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- [Public Facing Website] — Nền tảng này chỉ phục vụ duy nhất bạn (Cá nhân/Admin) quản trị tài nguyên. Không đăng ký membership cho người ngoài.
- [Phân quyền đa mức độ Multi-tenant] — Không cần thiết vì mục đích chỉ là cấp Personal.
- [Local Server Video Rendering] — Đã thống nhất sử dụng bên thứ 3 thay vì máy chủ chịu tải render FFmpeg thủ công.

## Context

- **Workflow Đặc thù**: Yêu cầu thao tác rất nhiều với đa luồng (task queue), giả lập trình duyệt, xử lý media (mp4, mkv) và quản lý state phức tạp.
- **Tính ổn định của Account**: Các nền tảng liên tục thay đổi thuật toán chống bot, do đó việc chia Tier (API & Playwright) là bắt buộc.
- **Bối cảnh hiện tại**: Đã có mã nguồn backend cơ bản trước đây (FastAPI, auth), cần chuẩn hóa và mở rộng sang hệ thống đa vi xử lý (celery/bull) và ghép nối luồng với Frontend mới.

## Constraints

- **Tech Stack Backend**: Buộc phải dùng Python (FastAPI + Celery/Redis + PostgreSQL) để tận dụng thế mạnh tuyệt đối về thư viện Video (MoviePy, FFmpeg), AI, và Playwright.
- **Tech Stack Frontend**: Sử dụng React.js (Vite/Next.js) tạo Single Page Application cho Dashboard do tính chất tương tác cao của Approval Queue.
- **Tài nguyên phần cứng**: Render video tại server sẽ tốn CPU/RAM, do đó Worker xử lý video cần khả năng scale độc lập với API Web server.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Chọn Python làm Backend | Dễ dàng tương tác với Playwright, FFmpeg và các thư viện AI. Phù hợp nhất cho automation bot. | — Pending |
| Hệ thống đăng bài 2 Tier (API & Playwright) | Giảm thiểu khóa tài khoản hàng loạt định kỳ nhờ luân phiên proxy và mô phỏng thực. | — Pending |
| Hybrid Video Render | Self-hosted render tiết kiệm chi phí lâu dài cho production số lượng khủng thay vì dựa dẫm vào external AI video APIs. | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-28 after project initialization*
