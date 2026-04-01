from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "auto_affiliate",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.domains.sys_worker.tasks",
        "app.domains.sys_worker.seeding_tasks",  # FB comment/reel via Appium
        "app.domains.shopee_crawler.tasks",      # Shopee product crawler
        "app.domains.target_groups.tasks",       # Facebook group scraper
        "app.domains.devices.tasks",             # Monitor devices
        "app.domains.sys_worker.alert_tasks",    # Error alerting and daily reporting
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
    task_default_queue="default",
    task_routes={
        "app.domains.sys_worker.tasks.*": {"queue": "default"},
        "app.domains.sys_worker.seeding_tasks.exec_fb_comment": {"queue": "appium_phone"},
        "app.domains.sys_worker.seeding_tasks.exec_fb_batch_comment": {"queue": "appium_phone"},
        "app.domains.sys_worker.seeding_tasks.exec_fb_post_reel": {"queue": "appium_phone"},
        "app.domains.sys_worker.seeding_tasks.notify_admin_discord": {"queue": "default"},
    },
    task_track_started=True,
    beat_schedule={
        "cleanup_logs_daily": {
            "task": "app.domains.sys_worker.tasks.cleanup_expired_logs",
            "schedule": 86400.0,  # Run every day (in seconds)
        },
        "crawler_scheduler_tick": {
            "task": "app.domains.shopee_crawler.tasks.crawler_scheduler_tick",
            "schedule": 900.0,  # Run every 15 minutes — checks CrawlerConfig.next_run_time
        },
        "facebook_scheduler_tick": {
            "task": "app.domains.target_groups.tasks.facebook_scheduler_tick",
            "schedule": 900.0,  # Run every 15 minutes — checks TargetGroupConfig.next_run_time
        },
        "device_monitor_tick": {
            "task": "app.domains.devices.tasks.ping_devices",
            "schedule": 300.0,
        },
        "stuck_scraper_monitor_tick": {
            "task": "app.domains.sys_worker.alert_tasks.check_stuck_scrapers",
            "schedule": 900.0,
        },
        "daily_discord_report": {
            "task": "app.domains.sys_worker.alert_tasks.send_daily_report_discord",
            "schedule": crontab(hour=17, minute=0),
        },
    },
    # Windows fix: billiard spawn pool gây PermissionError trên Windows
    # Solo pool chạy task trong cùng process — đúng cho worker concurrency=1 (appium_phone)
    worker_pool="solo",
)

# Register signals
import app.domains.sys_worker.celery_signals  # noqa: F401
