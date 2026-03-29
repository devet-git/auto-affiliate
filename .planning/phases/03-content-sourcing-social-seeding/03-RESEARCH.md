# Phase 03: content-sourcing-social-seeding - Research

## Objective
Research how to implement Phase 03: Content Sourcing & Social Seeding. Evaluate Appium connection, FFmpeg deduplication, and TikTok downloader configurations.

## Findings

### 1. Appium Python Configuration
Appium 2.x and `Appium-Python-Client` v3/v4 have strict requirements for options. We must use `UiAutomator2Options` rather than legacy Desired Capabilities dictionaries.
The Appium server runs independently (e.g. `appium -p 4723`).
```python
from appium import webdriver
from appium.options.android import UiAutomator2Options

options = UiAutomator2Options()
options.platform_name = 'Android'
options.automation_name = 'UiAutomator2'
options.udid = 'emulator-5554'  # or real device UDID from adb devices
options.app_package = 'com.facebook.katana'
options.app_activity = 'com.facebook.katana.LoginActivity'

driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
```
- Rate limiting is essential since real devices process interactions slower than Playwright browsers. Celery queue workers handling Appium need a concurrency of 1 per physical device.

### 2. FFmpeg-Python for Deduplication
To implement "đổi áo" (Deduplication) per D-04 in CONTEXT.md, `ffmpeg-python` provides an elegant interface for complex filter graphs without large memory overheads (FFmpeg processes stream directly):
- **Wipe metadata (Siêu Nhẹ)**: `-map_metadata -1`
- **Flip Video (Xào Sâu)**: `hflip` filter.
- **Speed Change**: `setpts=0.95*PTS` (video), `atempo=1.05` (audio).
```python
import ffmpeg

# Siêu nhẹ (Metadata Wipe & minimal hash change)
# Có thể render thêm 1 pixel noise hoặc bitrate lẻ để ăn chắc MD5 đổi.
ffmpeg.input('in.mp4').output('out_light.mp4', map_metadata='-1', vcodec='copy', acodec='copy').run()

# Sâu (Flip & Speed)
in_obj = ffmpeg.input('in.mp4')
v = in_obj.video.hflip().setpts('0.95*PTS')
a = in_obj.audio.filter('atempo', 1.05)
ffmpeg.output(v, a, 'out_deep.mp4').run()
```

### 3. Sourcing Crawler / Downloader
For D-01 (Cấu hình đa nguồn), an interface like `BaseVideoSource` must be defined.
For TikTok/Douyin, rather than building complete scrapers, lightweight tools like `yt-dlp` or public APIs (RapidAPI / TikWM) are highly recommended. A `yt-dlp` integration can download from YouTube Shorts, TikTok, Facebook Reels natively. 

## Architectural Recommendations
1. **Queue Isolation**: The `Facebook Auto-Seeding & Commenting Worker` should use a dedicated Celery queue (e.g., `queue='phone_workers'`) to avoid blocking fast API tasks like Shopee scraping.
2. **Device Pool Mapping**: The database should track available Android devices (`udid`) and their status (busy/idle) if scaling beyond 1 device.

## Validation Architecture
- **Automated Scope**: Unit tests for FFmpeg wrappers evaluating `os.path.exists()` and comparing MD5 hashes of output vs input.
- **Manual/Physical Scope**: Connecting physical Android device via USB/Wi-Fi to verify the driver instantiates and `appium` controls the Facebook app.

## RESEARCH COMPLETE
