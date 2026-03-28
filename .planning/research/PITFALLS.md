# Pitfalls Research

**Domain:** Affiliate Automation System
**Researched:** 2026-03-28

## Critical Mistakes & Traps

1. **Bị Shadowban toàn bộ dàn Account TikTok/FB**
   - *Nguyên nhân*: Dùng 1 IP mộc đẩy 100 video/ngày, lộ fingerprint quá rõ cùa Selenium/API ảo.
   - *Cách tránh*: Sử dụng Proxy di động/IPv4 sạch 1-kèm-1 cho mỗi tài khoản. Dùng Playwright ẩn danh cao cấp.
   - *Phase cần xử lý*: Core Posting Logic.

2. **Server bị sập RAM/CPU vì Render Video đồng loạt**
   - *Nguyên nhân*: Web backend (FastAPI) tự gọi lệnh sinh video FFmpeg. Khi có 10 campaign chạy cùng lúc, disk I/O nghẽn, server văng.
   - *Cách tránh*: Tách bạch Worker xử lý Video ra riêng. Giới hạn `concurrency=1` trên mỗi Render Worker.
   - *Phase cần xử lý*: Worker Architecture.

3. **Chết link Affiliate và mất hoa hồng**
   - *Nguyên nhân*: Cache link Shopee hết hạn hoặc cơ chế tracking bị chặn bởi mạng xã hội.
   - *Cách tránh*: Xây một Landing page nội trú (Bio Link) trung gian để điều hướng, hoặc dùng link rút gọn domain cá nhân.

4. **Bot chạy rác data, bài đăng bị gắn cờ Spam**
   - *Nguyên nhân*: Crawl tất cả sản phẩm shopee không có bộ lọc, kịch bản lặp đi lặp lại.
   - *Cách tránh*: Cơ chế duyệt bài **Approval Queue** và dùng AI Spin content (LLM biến đổi văn bản) mỗi lần lấy.
