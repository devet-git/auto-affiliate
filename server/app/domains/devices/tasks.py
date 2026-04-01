import logging
import subprocess
import httpx
from datetime import datetime
from sqlmodel import Session, select
from app.core.database import engine
from app.domains.devices.models import Device
from app.core.celery_app import celery_app
from app.domains.sys_worker.seeding_tasks import notify_admin_discord

logger = logging.getLogger(__name__)

@celery_app.task(name="app.domains.devices.tasks.ping_devices")
def ping_devices():
    """
    Called periodically every 5 minutes by Celery Beat.
    Checks ADB and Appium status for all devices.
    """
    logger.info("Starting ping_devices task...")
    
    # 1. Fetch ADB connected devices
    active_udids = set()
    try:
        result = subprocess.run(
            ["adb", "devices"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        lines = result.stdout.strip().split("\n")[1:] # skip header
        for line in lines:
            if "\tdevice" in line:
                active_udids.add(line.split("\t")[0])
    except Exception as e:
        logger.error(f"Error checking adb devices: {e}")

    with Session(engine) as session:
        devices = session.exec(select(Device)).all()
        known_udids = {d.udid: d for d in devices}
        
        # Auto-add new devices detected from ADB
        for adb_udid in active_udids:
            if adb_udid not in known_udids:
                new_device = Device(
                    udid=adb_udid,
                    label=adb_udid,
                    status="online",
                    is_active=True
                )
                session.add(new_device)
                session.commit()
                session.refresh(new_device)
                known_udids[adb_udid] = new_device
                devices.append(new_device)
                logger.info(f"Auto-registered new device: {adb_udid}")

        for device in devices:
            # 2. Check Appium condition (We assume Appium server is at localhost:4723)
            # For a more robust app, each device might have its own Appium port. 
            appium_ok = False
            try:
                # Appium 2.x standard status endpoint
                resp = httpx.get("http://127.0.0.1:4723/status", timeout=5.0)
                if resp.status_code == 200:
                    appium_ok = True
            except Exception as e:
                logger.warning(f"Appium status check failed: {e}")

            # 3. Determine connectivity
            adb_ok = device.udid in active_udids
            
            if adb_ok and appium_ok:
                device.status = "online"
                device.missed_pings = 0
            else:
                device.status = "offline"
                device.missed_pings += 1

            # 4. Alert if missed_pings hits exact threshold 3
            if device.missed_pings == 3:
                msg = f"🚨 **ALERT**: Cảnh báo thiết bị `{device.label}` (UDID: `{device.udid}`) OFFLINE sau 15 phút không nhận được tín hiệu!"
                notify_admin_discord.delay(msg)
                
            device.updated_at = datetime.utcnow()
            session.add(device)
            
        session.commit()
    logger.info("Finished ping_devices task.")
