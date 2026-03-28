# Architecture Research

**Domain:** Affiliate Automation System
**Researched:** 2026-03-28

## Major Components

1. **Dashboard (React)**: GUI Server.
2. **Control Node (FastAPI)**: Xử lý API, Auth, Quản lý State.
3. **Queue Broker (Redis)**: Điều phối task.
4. **Scraper Workers**: Chuyên lấy dữ liệu Shopee.
5. **Render Workers**: Máy chủ chạy CPU/GPU nặng cho thao tác Video (FFmpeg).
6. **Poster Workers (Playwright)**: Chạy headless browser qua Proxy để đăng TikTok/FB.

## Data Flow
- [Admin] tạo `Campaign` trên Dashboard -> `Control Node` lưu DB.
- `Control Node` đẩy job vào `Queue Broker`.
- `Scraper Worker` lấy job -> Crawl Shopee -> Đẩy dữ liệu thô về `Control Node`.
- `Control Node` gọi AI -> Sinh kịch bản -> Đẩy job render vào Queue.
- `Render Worker` làm việc -> Tạo file `video.mp4` -> Lưu S3/Local.
- `Control Node` đổi trạng thái thành "Pending Approval".
- [Admin] vào Dashboard -> Duyệt video.
- Video được duyệt -> `Control Node` đẩy job Post vào Queue.
- `Poster Worker` lấy Proxy tương ứng -> Playwright login cookie -> Upload video lên TikTok.
