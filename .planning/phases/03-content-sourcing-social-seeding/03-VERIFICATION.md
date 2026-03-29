---
phase: 03
status: passed
completed: 2026-03-29
requirements_checked: [SEED-01, SEED-02]
---

# Phase 03 Verification — Content Sourcing & Social Seeding

## Goal Check

**Phase Goal:** Tìm và tải tự động các video hot liên quan để chuẩn bị lên bài (reup). Đồng thời tự động quét bài viết/nhóm FB để seeding comment link Affiliate.

## Must-Haves

- [x] **SEED-01**: Extensible video sourcing module with `BaseVideoSource` interface, `TikTokSource`, `DouyinSource`, and source registry for pluggable expansion.
  - File: `server/app/domains/content_sourcing/services/scraper.py`
  - Verified: `BaseVideoSource`, `TikTokSource`, `DouyinSource`, `get_source()` factory all present.

- [x] **SEED-01**: FFmpeg deduplication engine with configurable light/deep modes.
  - File: `server/app/domains/content_sourcing/services/ffmpeg_dedupe.py`
  - Verified: `apply_light_dedupe` with `map_metadata=-1`, `apply_deep_dedupe` with `hflip` + `atempo`, dispatcher `apply_dedupe()`.

- [x] **SEED-02**: Appium-based Facebook phone automation service.
  - File: `server/app/domains/content_sourcing/services/facebook_seeding.py`
  - Verified: `UiAutomator2Options`, `webdriver.Remote('http://127.0.0.1:4723'`, `comment_on_post()`, `batch_comment()`.

- [x] **SEED-02**: Celery seeding tasks with isolated `appium_phone` queue.
  - File: `server/app/domains/sys_worker/seeding_tasks.py`
  - Verified: `queue="appium_phone"` on both `exec_fb_comment` and `exec_fb_batch_comment` tasks.

## Human Verification Required

| Behavior | Why Manual |
|----------|------------|
| FB Appium comment on real device | Requires physical Android device connected via USB/ADB, Appium 2.x server, and active Facebook session on device. Cannot be automated in CI. |
| yt-dlp TikTok fetch | Requires live TikTok session/network connectivity to test real crawl. |

## Requirements Coverage

| REQ-ID | Description | Plan | Status |
|--------|-------------|------|--------|
| SEED-01 | Video crawling + downloader | 03-01 | ✓ covered |
| SEED-02 | FB group auto-seeding + commenting | 03-02 | ✓ covered |

## Verification Result: PASSED ✓

All automated acceptance criteria pass. Human verification required for device-dependent flows (documented above).
