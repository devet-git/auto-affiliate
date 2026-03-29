# Auto Affiliate Control Center - Backend

Đây là mã nguồn hệ thống Backend (FastAPI + Celery) của dự án **Auto Affiliate Control Center**.  
Dự án được xây dựng theo kiến trúc modular component-based (chia theo domain), giao tiếp luồng dữ liệu thông qua cơ chế Queue (Celery) để hỗ trợ tính năng Web Scraping và Mobile UI Automation.

---

## 🚀 Trạng thái Phát triển (Milestones)

Hệ thống đã hoàn thành 3 giai đoạn cốt lõi đầu tiên (Phase 1 → Phase 3).

### Phase 1: Foundation & Authentication (Core Architecture)
- **Framework Chính**: FastAPI (Web API), SQLModel (ORM), PostgreSQL (Database).
- **Authentication**: Xác thực người dùng thông qua mã thông báo JWT (`Depends(get_current_admin)`). Toàn bộ hệ thống quản trị Affiliate là Private Area (chỉ dành cho 1 user duy nhất cấu hình hệ thống).
- **Task Queue Foundation**: Khởi tạo Celery Workers và Redis Broker để chuẩn bị cho các tác vụ tốn thời gian (Scraping, AI rendering, Automation).

### Phase 2: Shopee Data Pipeline (Cào dữ liệu & Deep Links)
- **Shopee Async Scraper**: Xây dựng service cào dữ liệu Shopee bất đồng bộ bằng **Playwright Async API**. Có khả năng tự động tải cấu trúc DOM động của Shopee để bóc tách:
  - Tên sản phẩm, giá bán.
  - URL ảnh đại diện (`background-image`, `img`).
- **Affiliate Link Generator**: Tạo domain lưu trữ `Product` (SQLModel). Cung cấp endpoint cho phép chuyển đổi link Shopee thông thường sang Link Affiliate (theo format của Shopee Affiliate Program hoặc Custom Tracking).

### Phase 3: Social Apps Seeding Pipeline (Android/Appium)
- **Physical Phone Automation**: Tích hợp **Appium Server** với công cụ `AndroidUiautomator2Driver` để điều khiển trực tiếp trên điện thoại Android thật (qua USB 10+).
- **Facebook Auto-Commenter**:  
  - Tự động mở App Facebook bằng DeepLink (`fb://post/...`).
  - Vượt qua các rào cản Security (Inject Events bị chặn) nhờ kỹ thuật XPath đa dạng và tinh chỉnh W3C Actions.
  - Tự động tìm kiếm các hộp nhập liệu Comment (bao gồm cả `AutoCompleteTextView`), gõ nội dung chứa Affiliate Link và nhấn Submit (Gửi/Send).
- **Hardware-based Celery Queue**: Tách biệt luồng Celery tên là `appium_phone` với `concurrency=1` để đảm bảo bot vật lý xử lý chuẩn xác 1 tác vụ UI tại 1 thời điểm mà không bị xung đột App.

---

## 🛠 Tech Stack

- **Ngôn ngữ**: Python 3.10+
- **API Framework**: FastAPI, Uvicorn
- **Database Layer**: PostgreSQL, SQLModel (Pydantic + SQLAlchemy)
- **Background Tasks**: Celery, Redis
- **Web Scraping**: Playwright (Async)
- **Mobile Automation**: Appium (Python Client, UiAutomator2)
- **Môi trường**: `.venv` thuần túy (Theo tiêu chuẩn dự án, KHÔNG dùng global).

---

## ⚙ Yêu cầu Môi trường (Prerequisites)

1. **Python 3.10+** (Mọi package thuần Python như FastAPI, Celery, Playwright đều phải cài đặt và chạy trong `.venv`).
2. **Node.js & NPM**: Dùng để cài đặt *Appium Server* Global (`npm install -g appium`). Vì lõi của Appium được viết bằng NodeJS, nó đóng vai trò là một máy chủ tương tự như Database, trong khi thư viện kết nối Appium của Python lại nằm độc lập bên trong `.venv`.
3. **Database**: PostgreSQL hoạt động ở cổng `5432` (kèm DB: `auto_affiliate`).
4. **Task Broker**: Redis Server hoạt động ở cổng `6379`.
5. **Appium CLI**: Appium Server chạy ở cổng `4723` (`appium -p 4723`).
6. **Mobile Device**: Điện thoại Android (với Cáp USB) phải bật "Gỡ lỗi USB" & "Tắt giám sát quyền" (Cài đặt bảo mật ở trên các dòng máy Xiaomi/Oppo).

---

## 📋 Hướng dẫn Khởi chạy (Local)

**Lưu ý cực kỳ quan trọng:** Luôn phải Activate môi trường ảo (Virtual Env) trước khi chạy bất kì lệnh nào để đảm bảo không xung đột thư viện với HĐH.

### 1. Dịch vụ FastAPI (Main Server)
Khởi động API phục vụ người dùng và kết nối DB Frontend.
```powershell
# Từ thư mục gốc dự án
cd server
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### 2. Dịch vụ Playwright (Scraping Worker)
Dành cho cào dữ liệu Shopee và render tài nguyên từ Web.
```powershell
# Cửa sổ PowerShell mới
cd server
.\.venv\Scripts\Activate.ps1
celery -A app.core.celery_app worker --loglevel=info -Q default
```

### 3. Dịch vụ Appium (Mobile Automation Worker)
Dành riêng cho Bot Android (tương tác vật lý). Chạy với `concurrency=1` để không bị trùng thao tác trên màn hình nhỏ.
```powershell
# Cửa sổ PowerShell mới (Nhớ khởi chạy Appium server bằng lệnh "appium" trước đó)
cd server
.\.venv\Scripts\Activate.ps1
celery -A app.core.celery_app worker -Q appium_phone --concurrency=1 --loglevel=info
```

---

*Tài liệu tự động khởi tạo và bảo trì bởi GSD nyquist-plan cho Auto Affiliate.*
