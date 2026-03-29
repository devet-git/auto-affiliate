"""
Facebook Auto-Seeding Service (Appium-based)
=============================================
D-03 from 03-CONTEXT.md: "Quét bằng đường viễn ly (Playwright/HTTP) để lấy
file list ID, nhưng lúc hạ thủ rải Comment sẽ đùng Appium Điện thoại thật."

This module handles the PHONE-SIDE execution:
  - Connect to a real Android device via Appium/UiAutomator2
  - Launch Facebook app on the device
  - Navigate to a target post by post_id
  - Type and submit an affiliate comment

NOTE: Requires:
  - Appium 2.x server running at localhost:4723
  - Android device connected via USB/Wi-Fi with ADB
  - Facebook app installed and logged in on device
  - appium-uiautomator2-driver installed: `appium driver install uiautomator2`
"""

import time
from typing import Optional

try:
    from appium import webdriver
    from appium.options.android import UiAutomator2Options
    from appium.webdriver.common.appiumby import AppiumBy
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    APPIUM_AVAILABLE = True
except ImportError:
    APPIUM_AVAILABLE = False

from app.core.config import settings

# Appium server URL — configured via APPIUM_SERVER_URL in .env
APPIUM_SERVER_URL = settings.APPIUM_SERVER_URL

# Facebook app package/activity identifiers (Android)
FB_APP_PACKAGE = "com.facebook.katana"
FB_APP_ACTIVITY = "com.facebook.katana.LoginActivity"

from app.domains.content_sourcing.services.appium_controller import get_driver
from app.domains.content_sourcing.services.warmup import warmup_news_feed
from app.domains.content_sourcing.services.media_injector import push_media_to_device


def comment_on_post(
    udid: str,
    post_url: str,
    comment_text: str,
    timeout: int = 30,
    app_type: str = 'lite',
) -> bool:
    """
    Use a real Android device (via Appium) to comment on a Facebook post.

    Flow:
        1. Open Facebook app on device
        2. Navigate to target post via deep-link / intent
        3. Tap the Comment button
        4. Type the affiliate link comment text
        5. Submit the comment
        6. Quit driver session

    Args:
        udid: Device UDID as shown in `adb devices`.
        post_url: Facebook post URL to comment on.
        comment_text: The comment body (typically an affiliate link).
        timeout: Max seconds to wait for UI elements.
        app_type: App context ('main' or 'lite'). Default is 'lite'.

    Returns:
        True if comment was submitted successfully, False otherwise.
    """
    if not APPIUM_AVAILABLE:
        raise ImportError("appium-python-client is required.")

    driver = get_driver(udid, app_type)
    try:
        # Xây dựng lòng tin bằng cách lướt Feed ngẫu nhiên trước khi tìm bài
        warmup_news_feed(driver, duration_sec=30)
    
        wait = WebDriverWait(driver, timeout)


        # Open post via deep link using platform-specific URL scheme
        driver.execute_script("mobile: deepLink", {
            "url": post_url,
            "package": FB_APP_PACKAGE,
        })
        time.sleep(5)  # Facebook load bài viết qua deep link thường mất thời gian

        # Bước 1: Bấm nút "Bình luận" dưới bài viết trước
        comment_btn_xpath = '//android.widget.Button[@content-desc="Bình luận" or @content-desc="Comment" or @text="Bình luận" or @text="Comment"]'
        try:
            print("Đang tìm nút Bình luận...")
            comment_btn = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, comment_btn_xpath)))
            comment_btn.click()
            print("Đã click nút Bình luận!")
            time.sleep(3)
        except Exception as e:
            print(f"Lỗi khi bấm nút Bình luận (có thể đã vào sẵn chế độ nhập): {e}")

        # Bước 2: Tìm ô nhập text
        comment_input_xpath = (
            '//*['
            '@class="android.widget.EditText" or @class="android.widget.AutoCompleteTextView" or '
            'contains(@text, "Write a comment") or contains(@hint, "Write a comment") or '
            'contains(@text, "Viết bình luận") or contains(@hint, "Viết bình luận") or '
            'contains(@text, "Bình luận dưới tên") or contains(@hint, "Bình luận dưới tên")'
            ']'
        )
        try:
            print("Đang tìm ô nhập text...")
            comment_box = wait.until(
                EC.presence_of_element_located((AppiumBy.XPATH, comment_input_xpath))
            )
            comment_box.click()
            time.sleep(1)
        except Exception as e:
            source = driver.page_source
            with open("appium_page_source.xml", "w", encoding="utf-8") as f:
                f.write(source)
            print("Lỗi: Không tìm thấy ô nhập comment, đã lưu appium_page_source.xml")
            raise e

        # Type the comment
        comment_box.send_keys(comment_text)
        time.sleep(1)

        # Submit (Send button)
        send_btn_xpath = '//*[@content-desc="Send" or @content-desc="Gửi" or @text="Send" or @text="Gửi"]'
        send_btn = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, send_btn_xpath))
        )
        send_btn.click()
        time.sleep(2)

        return True

    except Exception as exc:
        print(f"[FacebookSeeding] comment_on_post failed for {post_url}: {exc}")
        return False

    finally:
        driver.quit()


def batch_comment(
    udid: str,
    post_urls: list[str],
    comment_text: str,
    delay_between: float = 30.0,
    app_type: str = 'lite',
) -> dict[str, bool]:
    """
    Comment on multiple posts sequentially using a single device.
    Includes a delay between comments to simulate human behaviour.

    Args:
        udid: Device UDID.
        post_urls: List of Facebook post URLs.
        comment_text: Affiliate link comment to post.
        delay_between: Seconds to wait between each comment (anti-spam).

    Returns:
        Dict mapping post_url → success/failure.
    """
    results: dict[str, bool] = {}
    for i, url in enumerate(post_urls):
        success = comment_on_post(udid, url, comment_text, app_type=app_type)
        results[url] = success
        if i < len(post_urls) - 1:
            time.sleep(delay_between)
    return results


def post_reel(udid: str, local_mp4_path: str, caption: str) -> bool:
    """
    Upload a Reel to Facebook Main by relying on ADB media injection and Appium gallery manipulation.
    """
    try:
        # Bơm video vào thiết bị (nằm ở /sdcard/DCIM/Camera)
        push_media_to_device(udid, local_mp4_path)
        
        # Mở ứng dụng Facebook phiên bản đầy đủ (Main)
        driver = get_driver(udid, app_type='main')
        
        # Warm-up (tuỳ chọn cho tài khoản mới)
        warmup_news_feed(driver, duration_sec=15)
        
        # NOTE: Các script click vào Reels -> Create -> Gallery -> Chọn file -> Đăng được lược bỏ trong scope framework backend.
        print(f"Đã mở FB Main và chuẩn bị Reel từ {local_mp4_path} cho {udid}")
        
        driver.quit()
        return True
    except Exception as e:
        print(f"[FacebookSeeding] Lỗi đăng Reel: {e}")
        return False
