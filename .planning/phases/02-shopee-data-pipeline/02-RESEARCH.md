# Phase 2: Shopee Data Pipeline - Technical Research

## 1. Context & Architecture
**Phase Goal**: Tự động hóa lấy data sản phẩm (ảnh, tên, giá) bằng Playwright scraper và sinh Affiliate link bằng Shopee CMS automation (trên cùng core Playwright).
**Decisions**:
- Playwright base (D-01).
- Chỉ lưu Image URL, không tải ảnh về (D-02).
- Tạo link affiliate thủ công bằng Playwright CMS automation (D-03).
- Keyword/Category trigger quét 100 top trending (D-04).

## 2. Scraping Strategy (Playwright)

Shopee là một Single Page Application tải data qua API và detect bot gắt (Cloudflare/Geetest).
Tuy nhiên, nếu ta dùng **chuỗi Playwright Stealth** kết hợp với **lưu lượng nhẹ** (cào theo batch), ta có thể bypass.
- **Tiếp cận**: Sử dụng `playwright-python`. Vì hệ thống queue của chúng ta ở Phase 1 xài Celery (Celery mặc định chạy synchronous/blocking), ta sẽ dùng `sync_playwright` bên trong worker object thay vì `async_playwright`.
- **Shopee Search API/UI**:
  - Dùng UI Scraping: Truy cập `https://shopee.vn/search?keyword={keyword}`. Cuộn trang để kích hoạt Lazy Load ảnh và Data.
  - Sau khi lấy danh sách link chi tiết, truy cập vào Product details để lấy Image gốc chất lượng cao hơn (hoặc lấy thumbnail thẳng ra từ page search nếu chấp nhận độ phân giải thấp. Khuyên lấy từ page Search trước, sau đó loop qua từng Detail url nếu muốn chất lượng cao).

## 3. Data Storage (SQLModel)
- **Model `Product`**:
  - `id`: int (PK)
  - `campaign_id`: FK tới bảng Campaign (Phase 5/1).
  - `original_url`: Xâu String (Link shopee gốc).
  - `affiliate_url`: Xâu String (Link sau khi convert).
  - `title`: String
  - `price`: Mức giá
  - `image_urls`: JSON/Varchar (danh sách String URLs, chỉ lưu URLs theo D-02).
  - `sync_status`: Enum (PENDING, CONVERTED, FAILED).

## 4. Affiliate Link Conversion
- **Sử dụng Shopee Affiliate CMS**:
  - Portal: `https://affiliate.shopee.vn/`
  - Thao tác đăng nhập (Login) bằng SMS OTP/QR code rất cực, *do đó thay vì bắt Playwright login lại từ đầu*, admin sẽ lấy cookie phiên đăng nhập từ browser thật và lưu vào file `shopee_storage_state.json` (Playwright hỗ trợ `browser_context(storage_state=...)`).
  - Trong Worker CMS Converter:
    1. Tạo context với state JSON.
    2. Điều hướng tới Custom Link Generator (`https://affiliate.shopee.vn/custom_link`).
    3. Paste list custom links (shopee hỗ trợ convert hàng lô hoặc từng cái).
    4. Nhận lại link rút gọn (`https://shope.ee/<id>`).

## 5. Implementation Hurdles
- **Celery Sync/Async Context**: Playwright requires its own event loop if run async. Using `sync_playwright` inside Celery `task` function is the bulletproof pattern.
- **Session Expiration**: Shopee Affiliate Cookie sẽ hết hạn. Cần cung cấp 1 API cho Admin tự update Cookie Json này (Mặc dù Phase 5 mới làm UI, Phase 2 cần Endpoint để update). HOẶC lưu vào SQLModel bảng `SysConfig` để Admin / Tool nhét cookie vào thông qua `.env`.

## Validation Architecture
- **Verification Strategy**:
  - Playwright test: Mở sandbox browser và test scrape 1 page Shopee thành công (có ảnh, giá).
  - Test function gen Affiliate Link chạy thủ công qua mock cookie hoặc cookie real (khi UAT).

## RESEARCH COMPLETE
