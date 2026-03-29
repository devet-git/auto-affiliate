# Phase 04: real-device-social-farm - Research

## Objective
Research how to implement Phase 04: Real-Device Social Farm. Evaluate dual-app targeting (FB Main vs Lite) via Appium, ADB media injection, and humanized warm-up behaviors.

## Findings

### 1. Multi-App Context (FB Main vs FB Lite)
Appium can seamlessly target different applications on the same device by just altering the `appPackage` and `appActivity` options. 
- FB Main: `com.facebook.katana`
- FB Lite: `com.facebook.lite`

We need a flexible initialization method in Python:
```python
def init_driver(udid: str, app_type: str = 'main'):
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.udid = udid
    
    if app_type == 'lite':
        options.app_package = 'com.facebook.lite'
        options.app_activity = 'com.facebook.lite.MainActivity'
    else:
        options.app_package = 'com.facebook.katana'
        options.app_activity = 'com.facebook.katana.LoginActivity'
        
    return webdriver.Remote('http://127.0.0.1:4723', options=options)
```
FB Lite is preferred for fast commenting/liking due to its simple UI structure. FB Main is preferred for Reel uploading (Lite sometimes lacks full Reel creator features).

### 2. Media Injection (ADB Push & Gallery Sync)
To post videos from the backend onto the device without going through the device's web browser, we must push the file to the DCIM folder and trigger Android's media scanner so the Facebook app's gallery picker sees it immediately.
```python
import subprocess

def inject_media(udid: str, local_path: str, remote_filename: str = 'affiliate_vid.mp4') -> str:
    remote_path = f"/sdcard/DCIM/Camera/{remote_filename}"
    # Push file
    subprocess.run(["adb", "-s", udid, "push", local_path, remote_path], check=True)
    # Force media scan
    subprocess.run(["adb", "-s", udid, "shell", "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE", "-d", f"file://{remote_path}"], check=True)
    return remote_path
```

### 3. Humanized Behavior (Warm-up)
To avoid bot detection, actions cannot be instantaneous. We need an Appium script that uses `W3C actions` (ActionChains) or simple `driver.swipe` to scroll the news feed randomly, pause, and occasionally click the "Like" button before navigating to the target post/page.
```python
import time
import random

def warmup_feed(driver, duration_sec=30):
    end_time = time.time() + duration_sec
    while time.time() < end_time:
        # Swipe up
        driver.swipe(500, 1500, 500, 500, 800)
        time.sleep(random.uniform(2, 5))
        # Random like behavior (pseudo-code)
        if random.random() > 0.7:
             # Find like button and click
             pass
```

## Architectural Recommendations
1. **Appium Session Management**: Caching the driver session locally to avoid full re-initialization overhead per action.
2. **Device State Locking**: Use Redis locking per `udid` to ensure no two tasks execute on the same phone at the same time. The background task worker already uses `concurrency=1`, but locking ensures safety.

## Validation Architecture
- **Automated Scope**: Unit tests verifying `inject_media` calls generate the correct adb subprocess commands.
- **Manual/Physical Scope**: Run Appium scripts to confirm the driver opens FB Lite, scrolls the feed for 30 seconds, injects a test video via ADB, and selects the video from the FB Main gallery.

## RESEARCH COMPLETE
