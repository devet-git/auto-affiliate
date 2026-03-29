import time
import random

def warmup_news_feed(driver, duration_sec: int = 30):
    """
    Simulate human scrolling of the Facebook news feed to bypass heuristics.
    
    Args:
        driver: The Appium webdriver remote session.
        duration_sec: Total time in seconds to perform the warmup sequence.
    """
    end_time = time.time() + duration_sec
    print(f"Bắt đầu khởi động (warm-up) Feed trong {duration_sec} giây...")
    while time.time() < end_time:
        try:
            # Swipe up (scroll down the feed)
            driver.swipe(start_x=500, start_y=1500, end_x=500, end_y=500, duration=800)
            
            # Mimic human pause to read/view content
            sleep_time = random.uniform(2.0, 5.0)
            time.sleep(sleep_time)
            
        except Exception as e:
            print(f"Lỗi trong quá trình warm-up: {e}")
            break
            
    print("Hoàn tất quy trình warm-up.")
