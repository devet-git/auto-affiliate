# Project Research Summary

**Project:** Auto Affiliate Control Center
**Domain:** Affiliate Marketing Automation
**Researched:** 2026-03-28
**Confidence:** HIGH

## Executive Summary

Hệ thống MMO Automation không phải là một website thông thường; nó là một trung tâm điều phối tài nguyên máy tính (Command Center). Bài nghiên cứu chỉ ra rằng thách thức lớn nhất không nằm ở tính năng, mà nằm ở **Kiến trúc giới hạn sự cố** và **Lách luật Anti-Bot**.

Giải pháp tối ưu là sử dụng **Python (FastAPI + Celery/Redis)** kết hợp **Playwright** và hệ thống hàng đợi phân tán (Queue). Rủi ro chí tử nhất là việc bị Shadowban dàn tài khoản và sập máy chủ do render video. Do đó, kiến trúc Worker độc lập và tính năng Approval Queue là bắt buộc.

## Key Findings

### Recommended Stack
**Core technologies:**
- Python FastAPI: Backbone cho Bot.
- Celery / Redis: Điều phối hàng ngàn job đan chéo cực mượt.
- React: SPA Dashboard giao diện thân thiện.
- Playwright: Công cụ bypass Bot-detection xịn nhất hiện tại.

### Expected Features
**Must have (table stakes):**
- Quản lý profile social riêng biệt, kết nối Proxy IPv4 cá nhân.
- Hàng đợi Duyệt (Approval Queue) đóng role màng lọc con người trước khi đăng.
- Basic hybrid Video render (Hình ảnh -> Video MP4 + Audio).

### Architecture Approach
Tuân thủ kiến trúc Micro-worker: 
1. Control Node (FastAPI): Giao tiếp user.
2. Render Worker (FFmpeg): Chuyên ngốn CPU tạo video.
3. Poster Worker (Playwright): Bóc tách độc lập.

### Critical Pitfalls
1. **Shadowban TikTok**: Né bằng Proxy sạch 1-kèm-1 và warm-up profile.
2. **Server Crash**: Tách Worker render tách biệt khỏi Web server để tránh ăn nghẽn I/O.
3. **Spam Flagging**: Chống bằng Spin kịch bản AI nhiều mẫu.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Foundation (Backend & Architecture)
**Rationale:** Database structure (Postgres) và Luồng Hàng đợi (Redis/Celery) phải làm trước tiên. Thất bại hàng đợi kéo theo sụp cả dự án.
**Delivers:** FastAPI setup tinh gọn, Redis queue, Auth (JWT).
**Avoids:** Sai lầm luồng logic đa tác vụ.

### Phase 2: Shopee Data & AI Generator Engine 
**Rationale:** Phải có nội dung rồi mới có thứ để render.
**Delivers:** Crawl Shopee, Spin Text LLM, tạo kịch bản, chốt data đầu vào.
**Implements:** The Scraper Worker.

### Phase 3: Hybrid Video Render Worker
**Rationale:** Module tốn tài nguyên nhất, phát triển độc lập.
**Delivers:** Worker gọi module sinh Video MP4 từ kịch bản, lưu file.
**Avoids:** Video Render block Web server thread.

### Phase 4: Posting Networks & Stealth Worker
**Rationale:** Trọng tâm cuối: đẩy lên mạng.
**Delivers:** Module Playwright quản lý Profile Chromium tĩnh ghép proxy HTTPs, Đăng bài.
**Adresses:** Tránh vi phạm Anti-Bot.

### Phase 5: C&C Control Dashboard (Frontend)
**Rationale:** Phần Giao diện hiển thị cho Admin.
**Delivers:** React Dashboard, Quản lý Approval Queue cho các Video hoàn thiện.

---
*Research completed: 2026-03-28*
*Ready for roadmap: yes*
