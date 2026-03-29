# -*- coding: utf-8 -*-
"""
Appium Connection Test Script -- Phase 3 UAT
============================================
Chay tung buoc de verify Appium + dien thoai hoat dong truoc khi test FB that.

Usage (trong server/ voi venv active):
    python tests/test_appium_connection.py
"""

import sys
import time

def step(n, desc):
    print(f"\n{'='*50}")
    print(f"  Step {n}: {desc}")
    print(f"{'='*50}")

# --- Step 1: Check imports ----------------------------------------------------
step(1, "Import Appium client")
try:
    from appium import webdriver
    from appium.options.android import UiAutomator2Options
    print("[OK] Appium Python Client imported OK")
except ImportError as e:
    print(f"[FAIL] Import failed: {e}")
    print("   Run: pip install Appium-Python-Client")
    sys.exit(1)

# --- Step 2: Load config ------------------------------------------------------
step(2, "Load config from .env")
try:
    from app.core.config import settings
    print(f"[OK] APPIUM_SERVER_URL = {settings.APPIUM_SERVER_URL}")
    print(f"[OK] APPIUM_DEVICE_UDID = {settings.APPIUM_DEVICE_UDID}")
    if not settings.APPIUM_DEVICE_UDID:
        print("[FAIL] APPIUM_DEVICE_UDID chua set trong .env!")
        sys.exit(1)
except Exception as e:
    print(f"[FAIL] Config error: {e}")
    sys.exit(1)

# --- Step 3: Connect to device (just open home screen — no FB yet) ------------
step(3, "Ket noi Appium -> mo man hinh Home dien thoai")
print(f"   Device: {settings.APPIUM_DEVICE_UDID}")
print(f"   Server: {settings.APPIUM_SERVER_URL}")
print("   (Se mat 15-30 giay de Appium khoi dong session...)")

options = UiAutomator2Options()
options.platform_name = "Android"
options.automation_name = "UiAutomator2"
options.udid = settings.APPIUM_DEVICE_UDID
options.no_reset = True
options.new_command_timeout = 60
# Fix Android 10+ permission error (WRITE_SECURE_SETTINGS on non-rooted devices)
options.set_capability("appium:skipDeviceInitialization", True)
options.set_capability("appium:skipServerInstallation", False)
options.set_capability("appium:ignoreHiddenApiPolicyError", True)
# Khong set app_package -> chi connect device, khong force mo app nao
options.auto_launch = False

try:
    driver = webdriver.Remote(settings.APPIUM_SERVER_URL, options=options)
    print("[OK] Ket noi Appium thanh cong!")
    print(f"   Session ID: {driver.session_id}")
    print(f"   Device: {driver.capabilities.get('deviceName', 'N/A')}")
    print(f"   Android: {driver.capabilities.get('platformVersion', 'N/A')}")
except Exception as e:
    print(f"[FAIL] Ket noi that bai: {e}")
    print("\n   Kiem tra:")
    print("   1. Appium dang chay? (appium -p 4723)")
    print("   2. adb devices co thay thiet bi?")
    print("   3. USB Debugging da bat tren dien thoai?")
    sys.exit(1)

# --- Step 4: Basic interaction test ------------------------------------------
step(4, "Test tuong tac co ban (press Home button)")
try:
    driver.press_keycode(3)  # Keycode 3 = HOME button
    time.sleep(1)
    print("[OK] Nhan HOME thanh cong — dien thoai phan hoi!")
except Exception as e:
    print(f"[WARN] Loi nhan HOME (khong nghiem trong): {e}")

# --- Step 5: Open Facebook app ------------------------------------------------
step(5, "Mo Facebook app tren dien thoai")
FB_PACKAGE = "com.facebook.katana"
try:
    driver.activate_app(FB_PACKAGE)
    time.sleep(4)
    print("[OK] Facebook app da mo!")
    print("   Nhin vao dien thoai — FB co dang hien thi khong?")
except Exception as e:
    print(f"[FAIL] Khong mo duoc Facebook: {e}")
    print("   Kiem tra: App Facebook da cai tren may chua?")
    driver.quit()
    sys.exit(1)

# --- Done --------------------------------------------------------------------
print("\n" + "="*50)
print("  [OK] TAT CA STEPS PASSED — Appium hoat dong OK!")
print("  Dien thoai dang mo Facebook.")
print("  Gio co the chay full test qua Swagger API.")
print("="*50 + "\n")

# Giu session song 5 giay de nhin man hinh, roi quit
time.sleep(5)
driver.quit()
print("Session da dong.")
