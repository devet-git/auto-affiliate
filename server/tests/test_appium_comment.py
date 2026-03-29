import os
import sys

# Đảm bảo import app.* được
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.domains.content_sourcing.services.facebook_seeding import comment_on_post

def main():
    print("="*50)
    print("  TEST TRỰC TIẾP LỆNH COMMENT TRÊN ĐIỆN THOẠI")
    print("="*50)
    
    udid = settings.APPIUM_DEVICE_UDID
    if not udid:
        print("[FAIL] APPIUM_DEVICE_UDID chưa có trong .env!")
        return
        
    post_url = "https://www.facebook.com/thangq.279/posts/3427730780802456"
    test_comment = "Sản phẩm tốt, test chức năng auto từ Phase 3: https://s.shopee.vn/test_affiliate_link"

    print(f"Thiết bị: {udid}")
    print(f"Bài viết: {post_url}")
    print("Đang khởi động Appium Driver... (Sẽ mở Facebook sau vài giây)")
    print()

    # Chạy trực tiếp hàm để dễ debug lỗi nếu có
    try:
        success = comment_on_post(udid=udid, post_url=post_url, comment_text=test_comment)
        if success:
            print("[OK] Đã comment THÀNH CÔNG trên thiết bị!")
        else:
            print("[FAIL] Thất bại ở một bước nào đó (xem log Appium hoặc trên điện thoại).")
    except Exception as e:
        print(f"[FAIL] Lỗi Python: {e}")

if __name__ == "__main__":
    main()
