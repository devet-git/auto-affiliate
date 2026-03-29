"""
Seeding Tasks — Celery Worker for Facebook Auto-Seeding via Appium
==================================================================
D-03 from 03-CONTEXT.md: Phone-side execution isolated in separate queue.

These tasks run on the `appium_phone` queue which is consumed by a dedicated
Celery worker process connected to a physical Android device. This prevents
slow device interactions from blocking the fast API web workers.

Worker start example:
    celery -A app.core.celery_app worker -Q appium_phone --concurrency=1 --loglevel=info

The concurrency MUST be 1 per device (serialized execution — one action
at a time on each physical phone).
"""

import logging
from typing import Optional

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.domains.sys_worker.seeding_tasks.exec_fb_comment",
    bind=True,
    queue="appium_phone",
    max_retries=2,
    default_retry_delay=60,  # Retry after 1 min if device busy
)
def exec_fb_comment(
    self,
    udid: str,
    post_url: str,
    comment_text: str,
    app_type: str = 'lite',
) -> dict:
    """
    Execute a Facebook comment action on a real Android device via Appium.

    This task runs on the isolated `appium_phone` queue with concurrency=1
    to serialize commands sent to the physical device.

    Args:
        udid: Android device UDID (from `adb devices`).
        post_url: Facebook post URL to comment on.
        comment_text: Comment body — typically an affiliate link.

    Returns:
        dict with keys: status, post_url, task_id
    """
    from app.domains.content_sourcing.services.facebook_seeding import comment_on_post

    logger.info(f"[exec_fb_comment] Device={udid} | App={app_type} | Post={post_url}")
    try:
        success = comment_on_post(udid=udid, post_url=post_url, comment_text=comment_text, app_type=app_type)
        status = "commented" if success else "failed"
        logger.info(f"[exec_fb_comment] Result={status} | Post={post_url}")
        return {
            "status": status,
            "post_url": post_url,
            "task_id": self.request.id,
        }
    except Exception as exc:
        logger.error(f"[exec_fb_comment] Exception: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.domains.sys_worker.seeding_tasks.exec_fb_batch_comment",
    bind=True,
    queue="appium_phone",
    max_retries=1,
    default_retry_delay=120,
)
def exec_fb_batch_comment(
    self,
    udid: str,
    post_urls: list[str],
    comment_text: str,
    delay_between: float = 30.0,
    app_type: str = 'lite',
) -> dict:
    """
    Execute batch Facebook comments on a list of posts.
    Automatically paces with delay_between seconds between comments.

    Args:
        udid: Android device UDID.
        post_urls: List of Facebook post URLs.
        comment_text: Affiliate comment text to post everywhere.
        delay_between: Seconds to wait between each comment (default 30s).

    Returns:
        dict with aggregate results per post URL.
    """
    from app.domains.content_sourcing.services.facebook_seeding import batch_comment

    logger.info(
        f"[exec_fb_batch_comment] Device={udid} | Posts={len(post_urls)} | Delay={delay_between}s"
    )
    try:
        results = batch_comment(
            udid=udid,
            post_urls=post_urls,
            comment_text=comment_text,
            delay_between=delay_between,
            app_type=app_type,
        )
        total = len(results)
        succeeded = sum(1 for v in results.values() if v)
        logger.info(f"[exec_fb_batch_comment] {succeeded}/{total} comments succeeded")
        return {
            "status": "complete",
            "total": total,
            "succeeded": succeeded,
            "results": results,
            "task_id": self.request.id,
        }
    except Exception as exc:
        logger.error(f"[exec_fb_batch_comment] Exception: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.domains.sys_worker.seeding_tasks.exec_fb_post_reel",
    bind=True,
    queue="appium_phone",
    max_retries=1,
    default_retry_delay=60,
)
def exec_fb_post_reel(self, udid: str, local_mp4_path: str, caption: str) -> dict:
    """
    Pushes an MP4 via ADB and uses Appium on FB Main to upload a Reel.
    """
    from app.domains.content_sourcing.services.facebook_seeding import post_reel
    
    logger.info(f"[exec_fb_post_reel] Device={udid} | Video={local_mp4_path}")
    try:
        success = post_reel(udid=udid, local_mp4_path=local_mp4_path, caption=caption)
        status = "posted" if success else "failed"
        return {
            "status": status,
            "udid": udid,
            "task_id": self.request.id,
        }
    except Exception as exc:
        logger.error(f"[exec_fb_post_reel] Exception: {exc}")
        raise self.retry(exc=exc)

import os
import requests

@celery_app.task(
    name="app.domains.sys_worker.seeding_tasks.notify_admin_telegram",
    queue="celery", # Use default queue rather than appium limited queue
    max_retries=3,
    default_retry_delay=10,
)
def notify_admin_telegram(message: str, media_url: Optional[str] = None) -> dict:
    """Send a notification to the admin via Telegram."""
    bot_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id or bot_token == "mock_telegram_token":
        logger.warning("Telegram notification skipped: Missing or mock credentials.")
        return {"status": "skipped"}
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        logger.info(f"[notify_admin_telegram] Notification sent to {chat_id}.")
        return {"status": "sent"}
    except Exception as exc:
        logger.error(f"[notify_admin_telegram] Failed to send: {exc}")
        return {"status": "error", "message": str(exc)}


