# Stack Research

**Domain:** Affiliate Automation System (Shopee -> TikTok)
**Researched:** 2026-03-28
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| FastAPI (Python) | 0.100+ | Backend API | Nhanh, hỗ trợ bất đồng bộ (Async) tốt, tương thích hoàn hảo với hệ sinh thái Python (AI, Playwright). |
| React (Vite) | 18+ | Admin Dashboard | Tương tác UI mượt mà, nhiều template Admin (Shadcn/Tailwind) có sẵn. |
| PostgreSQL | 15+ | Database | Lưu trữ dữ liệu cấu trúc tốt (Campaigns) và phi cấu trúc (JSON data từ Shopee). |
| Redis + Celery | Latest | Task Queue | Bắt buộc để điều phối hàng ngàn job: crawl, render, đăng bài. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Playwright (Python) | Latest | Browser Automation | Đăng bài lên TikTok/FB tự động, Bypass bot detection. |
| MoviePy / FFmpeg | Latest | Video Rendering | Xử lý file video: ghép ảnh tĩnh thành MP4, chèn nhạc, chèn sub. |
| Google Cloud Vertex/Flow | V1 | 3rd-Party AI Video | Gọi API tạo video AI chất lượng cao ở Tier 1. |

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Celery | RQ / Dramatiq | Khi hệ thống nhỏ, cần nhẹ nhàng dễ setup hơn Celery cồng kềnh. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Selenium | Cũ, chậm, dễ bị phát hiện bởi TikTok anti-bot. | Playwright hoac Undetected-Chromedriver |
| Django | Quá cồng kềnh cho một hệ thống nặng về background task và API. | FastAPI |

---
*Stack research for: Auto Affiliate System*
