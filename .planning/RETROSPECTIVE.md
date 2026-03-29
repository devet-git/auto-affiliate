# Living Retrospective

This document tracks execution velocity, architectural lessons, and process friction across all project milestones.

## Cross-Milestone Trends

| Milestone | Phases | Plans | Duration | Key Friction Point | Lasting Pattern Intro |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **v1.0** | 5 | 14 | 1 Days | Android ADB Setup & Discord OAuth Cache | Appium ADB Device Injector |

---

## Milestone: v1.0 — Foundation

**Shipped:** 2026-03-29
**Phases:** 5 | **Plans:** 14

### What Was Built
- Xây dựng lõi hệ thống vững chắc bằng FastAPI, PostgreSQL, và background worker Celery/Redis.
- Shopee scraper dùng Playwright ngầm bóc tách thông tin và sinh linh Affiliate an toàn.
- Cào video short (TikTok/Douyin) tự động kết hợp bot seeding comment vào Hội nhóm Facebook.
- Real-Device Automation Farm: Điền khiển điện thoại thật qua Appium, tự thả video qua ADB và đẩy Reels.
- React Web Dashboard quản lý duyệt bài kèm Discord Bot gởi lệnh phê duyệt (Approval Queue).

### What Worked
- Python là chìa khóa vàng: Tích hợp liền mạch FastAPI, AI, Celery, Playwright và Appium trên cùng một stack.
- Mô hình "Tiered Publishing": Tách biệt Graph API, Playwright và Phone thật giúp đánh lừa bot quá hiệu quả.
- Tích hợp Bot Discord chạy ngầm chung lifespan của FastAPI giải quyết sự rườm rà của Telegram Webhook + Ngrok.

### What Was Inefficient
- ADB và Appium đòi hỏi cấu hình thiết bị thật cồng kềnh, không thể setup chạy trên Cloud Docker hay CI/CD dễ dàng.
- Việc chờ Discord đồng bộ Slash command mất khá nhiều thời gian ban đầu trước khi nhận ra có thể sync theo GuildID.

### Patterns Established
- Approval Automation Loop: Web/Crawler tạo Draft -> Báo Cáo Discord -> Admin ấn slash command duyệt -> Background queue đăng Reel.

### Key Lessons
- Việc từ bỏ Graph API tự động hoặc giả lập Web để chuyển sang dùng thiết bị thật (Appium) chọc thẳng bằng Intent Android là chìa khóa sống còn của các hệ thống Re-up.
- Background tasks (lifespan) của FastAPI mạnh mẽ tới mức có thể chạy được bot websocket bên trong.

### Cost Observations
- Model mix: 100% Gemini 3.1 Pro models for parallel agent scaling.
- Notable: Zero context leak errors utilizing independent GSD agents sequentially.
