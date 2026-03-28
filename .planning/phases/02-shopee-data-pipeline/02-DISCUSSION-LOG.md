# Phase 2: Shopee Data Pipeline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the conversational analysis.

**Date:** 2026-03-28
**Phase:** 02-shopee-data-pipeline
**Mode:** interactive-batch

## Areas Discussed

### Shopee Scraping Approach
- **Options presented:** 1 - Requests thuần kết hợp Headers fake/Proxy, 2 - Playwright mô phỏng trình duyệt ẩn danh, 3 - Shopee Open API.
- **User selection:** **2** - Playwright mô phỏng trình duyệt có giao diện.

### Data Storage (Lưu trữ file Media)
- **Options presented:** 1 - Chỉ lưu URL gốc của Shopee, 2 - Tải toàn bộ media về ổ cứng Local, 3 - Cloud Storage S3.
- **User selection:** **2** - Tải toàn bộ media về ổ cứng Local để nhỡ bị die link vẫn giữ lại file backup.

### Affiliate Link Creation
- **Options presented:** 1 - Shopee Affiliate Open API, 2 - Mạng trung gian, 3 - Dùng Playwright tự login vào Shopee Affiliate Portal và convert thủ công.
- **User selection:** **3** - Dùng thủ thuật (Playwright login vào Web Shopee Affiliate và tự gõ tự click tạo link).

### Input Trigger
- **Options presented:** 1 - 1 link sản phẩm cố định, 2 - Rải quét link 1 Shop, 3 - Nhập từ khoá / Ngành hàng để nó tự động cào 100 sản phẩm top Trending ra.
- **User selection:** **3** - Nhập từ khoá / Ngành hàng để quét auto 100 item trending nhất.
