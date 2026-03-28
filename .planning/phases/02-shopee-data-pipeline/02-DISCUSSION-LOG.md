# Phase 2: Shopee Data Pipeline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the analysis.

**Date:** 2026-03-28
**Phase:** 02-shopee-data-pipeline
**Mode:** batch

## Assumptions Presented

### Shopee Scraping Approach
- Options Provided:
  - 1: Requests/HTTPX thuần kết hợp Headers/Proxy
  - 2: Playwright mô phỏng trình duyệt có giao diện
  - 3: Sử dụng Shopee Open API chính thức
- Chosen: 2 (Playwright)

### Data Storage (Lưu trữ file Media)
- Options Provided:
  - 1: Chỉ lưu URL gốc của ảnh/video Shopee vào database
  - 2: Tải toàn bộ media về ổ cứng Local
  - 3: Upload đẩy thẳng lên một nền tảng Cloud Storage bên thứ 3
- Chosen: 1 (Chỉ lưu URL)

### Affiliate Link Creation
- Options Provided:
  - 1: Chuyển đổi qua API chính thống của Shopee Affiliate
  - 2: Chuyển đổi qua API mạng lưới trung gian
  - 3: Dùng thủ thuật (Playwright login vào Web Shopee Affiliate và tự gõ tự click tạo link)
- Chosen: 3 (Playwright trên Portal)

### Input Trigger
- Options Provided:
  - 1: Dán 1 Link Sản phẩm tĩnh vào box
  - 2: Dán Link Shop
  - 3: Nhập từ khoá / Ngành hàng
- Chosen: 3 (Từ khóa/Ngành hàng)

## Corrections Made
No corrections — choices were selected directly from provided batch.

## External Research
None.
