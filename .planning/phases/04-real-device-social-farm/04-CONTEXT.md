# Phase 4: Real-Device Social Farm - Context

**Gathered:** 2026-03-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Điều khiển thiết bị thật (Appium/ADB) để tương tác. Đóng giả người dùng thật lướt feed (warm-up) rồi đăng bài (text/link/media) hoặc comment bằng nick cá nhân/fanpage. Hỗ trợ thao tác song song/chéo giữa 2 ứng dụng mạng xã hội (App Main / Lite) trên cùng 1 điện thoại.

</domain>

<decisions>
## Implementation Decisions

### A. Phạm vi thiết bị (Device Scope)
- **D-01:** **1 Máy / Đa App (Dual-App Context)**. Tạm thời sử dụng 1 thiết bị vật lý cắm cáp để test chuẩn hóa toàn bộ luồng (A-Z). Trong đó, thiết bị này sẽ sử dụng tối thiểu 2 bản ứng dụng (ví dụ: FB Main và FB Lite) để Appium có thể điều khiển 2 tài khoản (Cá nhân + Fanpage) chéo nhau độc lập trên cùng 1 phần cứng. 

### B. Hành vi (Behavior)
- **D-02:** **Ngụy trang tự nhiên (Humanized Warm-up)**. Bắt buộc: Trước khi thực hiện hành động chính (đăng bài / comment spam link), hệ thống phải chạy kịch bản "làm ấm": Lướt News Feed ngẫu nhiên tầm 30 giây, tìm các bài ngẫu nhiên để thả Like/Reaction hoặc dừng lại xem, nhằm tích luỹ Trust Score cho session.

### C. Media & Posting (Chiến lược Đăng)
- **D-03:** **Hỗ trợ Toàn diện (Core Text + Media Push)**. Hệ thống chạy cả 2 option (quyết định lúc cấu hình Campaign):
  1. Ưu tiên mặc định: Đăng Text/Link nhanh vào Comment của đối thủ, Hội nhóm.
  2. Nâng cao: Đăng Media (Reel/Video). Cơ chế **Media Injection**: Dùng lệnh `adb push` đẩy file video gốc lấy từ Phase 3 thẳng vào thư viện ảnh máy (`DCIM`), ép máy cập nhật media (`MEDIA_SCANNER_SCAN_FILE`), sau đó dùng Appium mở giao diện đăng Reel chọn file nằm sẵn đầu thư viện.
  
### the agent's Discretion
- Kiến trúc Code Appium: Hàm helper để khởi tạo driver rẽ nhánh an toàn cho `appPackage` `com.facebook.katana` (FB Main) và `com.facebook.lite` (FB Lite).
- Bắt XPath/UI automator của các app mạng xã hội cực kỳ trơn láng (Gợi ý dùng FB Lite cho tương tác comment đi dạo vì cấu trúc nhẹ tĩnh).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope
- `.planning/PROJECT.md` — Tái định nghĩa quy mô sang thiết bị thật và loại tháo bỏ Browser API tier.
- `.planning/ROADMAP.md` — Luồng xử lý phân tích và kế hoạch triển khai Phase 4 (POST-03 -> POST-05).
- `.planning/REQUIREMENTS.md` — Core definitions cho Multi-App execution.

</canonical_refs>

<specifics>
## Specific Ideas

- **Tương tác mồi chéo (Synergistic Seeding)**: FB Lite dùng đăng bài chia sẻ giá trị. Đăng xong -> Trigger FB Main mở lên -> Tìm bài đó thả tim + thả bình luận chèn link Shopee. Hiệu ứng đám đông mồi.
- Việc xử lý `adb push` cần timeout cẩn thận vì file MP4 có thể lên đến 50MB.

</specifics>

<deferred>
## Deferred Ideas

- OCR AI Captcha Bypass lúc bị Checkpoint (Sử dụng Gemini Scan screencap). Mới nghĩ đến chứ chưa cần làm ngay, dùng warm-up để bù đắp trước.
- Database Device Pool quy mô lớn (Do user chỉ ưu tiên Setup 1 máy ở Version này).

</deferred>

---

*Phase: 04-real-device-social-farm*
*Context gathered: 2026-03-29 via discuss-phase*
