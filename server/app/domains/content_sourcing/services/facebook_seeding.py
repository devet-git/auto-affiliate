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

# Default Appium server URL (run `appium -p 4723` on host machine)
APPIUM_SERVER_URL = "http://127.0.0.1:4723"

# Facebook app package/activity identifiers (Android)
FB_APP_PACKAGE = "com.facebook.katana"
FB_APP_ACTIVITY = "com.facebook.katana.LoginActivity"


def _build_driver_options(udid: str) -> "UiAutomator2Options":
    """Build Appium options for a specific Android device UDID."""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.udid = udid
    options.app_package = FB_APP_PACKAGE
    options.app_activity = FB_APP_ACTIVITY
    options.no_reset = True          # Don't reset app state (keep login session)
    options.new_command_timeout = 120  # 2 min timeout between commands
    return options


def get_driver(udid: str) -> "webdriver.Remote":
    """
    Create an Appium WebDriver session for the given device.

    Args:
        udid: Android device UDID (from `adb devices`). E.g. "emulator-5554"
              or "192.168.1.100:5555" for Wi-Fi ADB.

    Returns:
        Appium WebDriver session connected to the device.

    Raises:
        ImportError: If appium-python-client is not installed.
        Exception: If connection to Appium server fails.
    """
    if not APPIUM_AVAILABLE:
        raise ImportError(
            "appium-python-client is required: pip install Appium-Python-Client"
        )
    options = _build_driver_options(udid)
    return webdriver.Remote(APPIUM_SERVER_URL, options=options)


def comment_on_post(
    udid: str,
    post_url: str,
    comment_text: str,
    timeout: int = 30,
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

    Returns:
        True if comment was submitted successfully, False otherwise.
    """
    if not APPIUM_AVAILABLE:
        raise ImportError("appium-python-client is required.")

    driver = get_driver(udid)
    try:
        wait = WebDriverWait(driver, timeout)

        # Open post via deep link using platform-specific URL scheme
        driver.execute_script("mobile: deepLink", {
            "url": post_url,
            "package": FB_APP_PACKAGE,
        })
        time.sleep(3)  # Allow post to load

        # Tap the comment input box
        comment_box = wait.until(
            EC.presence_of_element_located(
                (AppiumBy.XPATH, '//*[contains(@text, "Write a comment") or contains(@hint, "Write a comment")]')
            )
        )
        comment_box.click()
        time.sleep(1)

        # Type the comment
        comment_box.send_keys(comment_text)
        time.sleep(1)

        # Submit (Send button)
        send_btn = wait.until(
            EC.element_to_be_clickable(
                (AppiumBy.ACCESSIBILITY_ID, "Send")
            )
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
        success = comment_on_post(udid, url, comment_text)
        results[url] = success
        if i < len(post_urls) - 1:
            time.sleep(delay_between)
    return results
