# Phase 2: Shopee Data Pipeline - Context

**Gathered:** 2026-03-28 (assumptions mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

Lõi Crawler tự động phân tích lấy tài nguyên sản phẩm (ảnh, tên, giá) và sinh tracking link Affiliate. Quá trình cào theo từ khóa/ngành hàng để cho ra danh sách sản phẩm tiềm năng.

</domain>

<decisions>
## Implementation Decisions

### Shopee Scraping Approach
- **D-01:** Sử dụng Playwright mô phỏng trình duyệt để tránh bị Shopee block. Tái sử dụng Playwright (chuẩn bị sớm cho Tier 2 Automation ở Phase 4).

### Data Storage (Lưu file Media)
- **D-02:** Chỉ lưu URL gốc của file ảnh/video Shopee vào CSDL. Sẽ trực tiếp chuyển URL gốc sang cho API (3rd Party Video Gen ở Phase 3) tự động tải thay vì ôm về server nội bộ.

### Affiliate Link Creation
- **D-03:** "Tà đạo": Sử dụng Playwright (giả lập thao tác tay) truy cập vào Web Shopee Affiliate CMS, đăng nhập và tự động tạo/convert link hàng loạt thay vì dùng API Open (phức tạp / không được duyệt whitelist).

### Input Trigger
- **D-04:** Chạy bằng Từ khóa / Ngành hàng: Quét tự động top các sản phẩm (ví dụ: cào 100 sản phẩm top trending dựa vào keyword Admin nhập vào).

### the agent's Discretion
- Kiến trúc cụ thể cho script Playwright, cách chia page/context pool để tối ưu tốc độ cào hàng trăm items.
- Schema bảng lưu trữ URL image.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope
- `.planning/PROJECT.md` — Định nghĩa quy mô chiến lược đa tầng và mục đích hệ thống Automation.
- `.planning/ROADMAP.md` — Luồng xử lý lấy dữ liệu Shopee -> Video AI.
- `.planning/REQUIREMENTS.md` — CRWL-01 và CRWL-02 mô tả việc cào và sinh link Affiliate.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/domains/sys_worker/` - Kiến trúc Worker chạy ngầm để lập lịch chạy job (giao cho Celery).
- SQLModel database schemas (kế thừa từ Phase 1).

### Integration Points
- API FastAPI sẽ cung cấp Endpoints tiếp nhận Keyword/Trigger.
- Celery Task: Chạy Playwright scraping và update trạng thái database.

</code_context>

<specifics>
## Specific Ideas

- Vì bạn đã chọn cào bằng Playwright và convert link cũng bằng CMS của Shopee Affiliate thông qua giả lập Playwright, toàn bộ Phase rẽ hướng rất mạnh vào việc thiết kế một "Scraping Pool" chạy ổn định và login duy trì session tốt.
- Không tải file media về server (ít I/O disk) giúp Worker nhẹ máy chủ.

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-shopee-data-pipeline*
*Context gathered: 2026-03-28*
