# Phase 1: Foundation (Backend & Queue) - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Xây dựng móng vững chắc cho hệ thống đa luồng và lưu trữ dữ liệu với Backend là FastAPI, Message Broker là Celery/Redis và Database là PostgreSQL. Kèm cơ chế bảo mật cho đích danh 1 tài khoản quản trị viên duy nhất.

</domain>

<decisions>
## Implementation Decisions

### Cấu trúc thư mục (Directory Structure)
- **D-01:** Áp dụng mô hình **Domain-driven** (gói gọn model, schema, route, service vào các module riêng biệt `app/domains/auth`, `app/domains/worker` v.v...) để code dễ tách biệt và không bị chồng chéo khi có quá nhiều worker xử lý AI/Playwright sau này.

### Thư viện Database ORM
- **D-02:** Lựa chọn **SQLModel**. Do project xài FastAPI, SQLModel sinh ra để tương thích tối đa với Pydantic, giúp tiết kiệm boilerplate code và define bảng CSDL cực kì "sạch sẽ".

### Cấu hình bảo mật quản trị (Admin Auth)
- **D-03:** Load cứng Admin User và Password từ biến môi trường **(`file .env`)**. Hệ thống không cần Seed Data, Controller đăng nhập sẽ so sánh Hash mật khẩu thẳng với giá trị trong `.env`. Nhanh, bảo mật tột độ cho cá nhân, và cực kì dễ setup qua máy chủ mới.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope
- `.planning/PROJECT.md` — Định nghĩa quy mô Personal use và Tech Stack Python.
- `.planning/ROADMAP.md` — Phạm vi các tasks của Phase 1.
- `.planning/REQUIREMENTS.md` — Tính năng cốt lõi (CORE-01 -> CORE-04).

</canonical_refs>

<specifics>
## Specific Ideas

- Tài khoản Admin không cần lưu CSDL bảng Users hay cài cắm hệ thống RBAC (Roles), kiểm dò thẳng từ hệ thống OS ENV.
- Cấu trúc thư mục Backend gốc (`/server/app/`) cần chuẩn bị riêng không gian cho Background Tasks Worker.

</specifics>

<deferred>
## Deferred Ideas

None — discussion focused entirely on phase 1 foundation.

</deferred>

---

*Phase: 01-foundation-backend-queue*
*Context gathered: 2026-03-28 via discuss-phase*
