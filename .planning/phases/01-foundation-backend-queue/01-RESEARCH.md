# Phase 1: Foundation (Backend & Queue) - Research

**Date:** 2026-03-28
**Goal:** What do I need to know to PLAN this phase well?

## 1. Domain-Driven Structure Implementation
Theo quyết định D-01, cấu trúc Backend không nên dùng MVC thông thường của FastAPI. Thay vào đó, chúng ta chia theo `domains`:
```text
server/
├── app/
│   ├── core/
│   │   ├── config.py       # Pydantic BaseSettings load biến ENV
│   │   ├── database.py     # SQLModel engine & session maker
│   │   ├── security.py     # JWT & Hashing
│   │   └── celery_app.py   # Khởi tạo Celery với Redis broker
│   ├── domains/
│   │   ├── admin/          # Xử lý Auth Admin từ ENV
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── dependencies.py
│   │   ├── campaign/       # Quản lý Database Campaign
│   │   │   ├── models.py   # SQLModel tables
│   │   │   └── router.py
│   │   └── sys_worker/     # Background tasks management
│   │       ├── router.py   # Giao tiếp worker (ví dụ trigger thử job)
│   │       └── tasks.py    # Định nghĩa @celery.task
│   └── main.py             # App init & include routers
```

## 2. SQLModel & Database Initialization (D-02)
- **Thư viện:** Dùng `sqlmodel` bản mới nhất hỗ trợ FastAPI / Pydantic V2.
- **Kết nối:** Dùng psycopg2-binary (`postgresql://user:pass@host/db`).
- **Khởi tạo:** Trong file `main.py` sự kiện `lifespan`, hoặc `on_startup` để chạy `SQLModel.metadata.create_all(engine)`. Không cần Alembic ở phase 1 vì chưa quan trọng việc migrate phức tạp.

## 3. Hardcoded Admin Authentication (D-03)
Không cần bảng `User` trong DB. Bỏ qua luồng MVC Auth phức tạp.
- **Config:** `.env` cung cấp `ADMIN_USERNAME` và `ADMIN_PASSWORD_HASH` (hoặc plain-text tùy thích, nếu plain-text thì server sẽ hash lúc runtime để check).
- **Endpoint:** `/api/v1/auth/login` nhận form `OAuth2PasswordRequestForm`. Nếu `username == settings.ADMIN_USERNAME` và verify `password` thành công, trả về JWT Token.
- **Verify:** Tạo dependency `get_current_admin` giải mã JWT token. Áp dụng chuẩn Security `Depends(OAuth2PasswordBearer)`.

## 4. Celery with Redis
- Gói: `celery` và `redis`.
- Khởi tạo Celery config với `broker="redis://..."` và `backend="redis://..."`.
- Lệnh chạy Worker: `celery -A app.core.celery_app:celery_app worker --loglevel=info`

## Validation Architecture

### Giao diện kiểm thử (CLI / curl):
1. **API Health & DB:** Gọi `/docs` qua trình duyệt hoặc `curl /api/v1/health` trả status 200, báo DB connected.
2. **Auth Verification:** Gửi POST `/api/v1/auth/login` với user/pass lấy từ ENV, kì vọng nhận được chuỗi `access_token` hợp lệ. Dùng token đó truy cập `/api/v1/campaigns` để xem danh sách Campaign rỗng. Nếu sai pass, nhận HTTP 401.
3. **Queue Functional:** Gọi Endpoint `/api/v1/worker/test-job` đẩy 1 toán hạng tính sum() đơn giản vào Celery, Celery Console báo log đã Execute, và redis đã ghi nhận kết quả success.

## Đề xuất cho Planner (gsd-planner)
- Tạo 3 file Plan theo đúng như Roadmap đã đề ra.
- Plan 1: Init thư mục, config ENV, setup Auth Hardcoded.
- Plan 2: Celery Redis init (Redis sẽ chạy theo docker container ở dev).
- Plan 3: Setup SQLModel, tạo table Campaign ban đầu.
