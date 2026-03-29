# Phase 04: real-device-social-farm - Validation Strategy

**Date:** 2026-03-29

## Strategy Goal
Verify that the Android device can execute Appium automation for multiple apps sequentially, successfully inject MP4 media via ADB, and mimic human scrolling/liking behaviors without crashing or throwing Appium errors.

## Automated Verification
1. **Unit Tests for ADB Wrapper**: Validate that `subprocess.run` calls the correct arguments for `adb push` and `am broadcast` media scanning.
2. **Appium Driver Config**: Validate the logic that switches `appPackage` based on the requested app context ('main' or 'lite').

## Manual/Physical Verification
1. **Warm-up Action Check**: Manually trigger the Celery task and watch the physical Android device to verify it scrolls down the Facebook feed, pauses at random intervals, and finds/clicks the Like button accurately.
2. **Media Post Check**: Trigger a Reel-posting job. Verify the file is pushed to `/sdcard/DCIM/Camera/`, appears in the Facebook App's Gallery picker, and is successfully selected and uploaded.
3. **Dual-App Test**: Send a Like task (FB Lite) immediately followed by a Post task (FB Main) to the same `udid` to verify the sessions don't conflict and the phone switches context successfully.

## Verification Complete
