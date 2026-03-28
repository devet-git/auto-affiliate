# Phase 2: Shopee Data Pipeline - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Lõi Crawler tự động lấy data sản phẩm (ảnh, tên, giá) từ danh sách trending thông qua việc thiết lập Playwright Bot. Đồng thời thao tác tạo tracking link Affiliate để cấp bộ phôi tài nguyên cho quá trình lên video hàng loạt ở Phase 3. 

</domain>

<decisions>
## Implementation Decisions

### Shopee Scraping Approach
- **D-01:** Sử dụng `Playwright` mô phỏng hành vi tải trang (trình duyệt ẩn danh/có giao diện tùy chọn) để kéo nội dung sản phẩm. Chấp nhận tải phần cứng nhằm vượt cơ chế chống bot siêu việt của Cloudflare/Shopee.

### Data Storage (Lưu trữ Media)
- **D-02:** Tải vĩnh viễn toàn bộ ảnh, text (và cả video gốc của list sản phẩm nếu có) về dồn đóng dưới ổ cứng hệ thống Local. Thao tác này giúp thiết lập kho lưu backup đề phòng link ảnh trỏ về Shopee thay đổi hoặc expired.

### Affiliate Link Creation
- **D-03:** Sử dụng luồng `Playwright` tự động hóa: Truy cập và đăng nhập vào công cụ Custom Link của trang Shopee Affiliate Portal (thông qua cookie/session), tự dán url gốc vào box và sao chép mã short link được generate ra. Bỏ qua con đường đệ trình Shopee Open API khó khăn phức tạp.

### Input Trigger
- **D-04:** Chế độ Auto-Scaling đầu vào: Admin không cần cấp URL sản phẩm rác rưởi, chỉ cần nhập "Từ khoá" tìm kiếm hoặc tham số "Ngành hàng" (Category). Crawler sẽ scan trang liệt kê danh sách, tự động cào 100 sản phẩm có lượt mua cao/đứng top trending về nhồi kho dữ liệu.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope
- `.planning/PROJECT.md` — Định hướng tổng quan dự án Auto Affiliate. Quyết định D-04 cào hàng loạt cực kỳ phù hợp với định hướng Core Value tạo ra hàng ngàn video auto-scaling ở đây.
- `.planning/REQUIREMENTS.md` — Yêu cầu CRWL-01 và CRWL-02 trong lộ trình làm Product Crawler API.
- `.planning/phases/01-foundation-backend-queue/01-CONTEXT.md` — Áp dụng Module kiến trúc Domain-Driven cho Playwright Worker vào Folder Service riêng rẽ, không dính líu với API web controller chính.

</canonical_refs>

<code_context>
## Existing Code Insights

### Integration Points
- Cơ chế Queue (Celery/Redis) đã được thiết lập ở Phase 1 là chìa khóa để triển khai cào top 100 sản phẩm ở chế độ nền (Background Worker) mà không gây Time-Out (504) trên trang web điều hành của Frontend FastAPI. Cần tạo 1 Worker Task `fetch_trending_items`.
</code_context>

<specifics>
## Specific Ideas

- Việc sử dụng cơ chế Browser Automation (Playwright) ở tận Phase 2 là tiền đề thiết yếu cho Phase 4 sau này (Bot Posting Tiktok). Cần xây dựng một **Browser Manager Service** (Quản lý Cookie Shopee, Quản lý Proxy) có tính tái sử dụng cao.
- Cookie của bộ phận Crawler và Cookie của bộ phận sinh Link Affiliate có thể là 2 tập account/phiên tách biệt nhau, tránh bị Shopee quét hành vi đồng thời.

</specifics>

<deferred>
## Deferred Ideas

None
</deferred>

---

*Phase: 02-shopee-data-pipeline*
*Context gathered: 2026-03-28*
