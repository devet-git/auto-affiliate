import time
from typing import Optional

try:
    from appium import webdriver
    from appium.options.android import UiAutomator2Options
    APPIUM_AVAILABLE = True
except ImportError:
    APPIUM_AVAILABLE = False

from app.core.config import settings

APPIUM_SERVER_URL = settings.APPIUM_SERVER_URL


def get_driver(udid: str, app_type: str = 'main') -> "webdriver.Remote":
    """
    Create an Appium WebDriver session for the given device.

    Args:
        udid: Android device UDID.
        app_type: 'main' for FB Main, 'lite' for FB Lite.

    Returns:
        webdriver.Remote: Connected Appium session.
    """
    if not APPIUM_AVAILABLE:
        raise ImportError(
            "appium-python-client is required: pip install Appium-Python-Client"
        )
        
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.udid = udid
    
    if app_type == 'lite':
        options.app_package = "com.facebook.lite"
        options.app_activity = "com.facebook.lite.MainActivity"
    else:
        options.app_package = "com.facebook.katana"
        options.app_activity = "com.facebook.katana.LoginActivity"

    options.no_reset = True          # Don't reset app state (keep login session)
    options.new_command_timeout = 120  # 2 min timeout between commands
    
    # Fix Android 10+ permission error (WRITE_SECURE_SETTINGS on non-rooted devices)
    options.set_capability("appium:skipDeviceInitialization", True)
    options.set_capability("appium:skipServerInstallation", False)
    options.set_capability("appium:ignoreHiddenApiPolicyError", True)
    
    return webdriver.Remote(APPIUM_SERVER_URL, options=options)
