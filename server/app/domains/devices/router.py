"""
Devices API Router
==================
CRUD for managing Android devices connected via ADB + Appium.

Endpoints:
  GET    /devices          — List all devices
  POST   /devices          — Register a new device
  GET    /devices/{id}     — Get device details
  PUT    /devices/{id}     — Update device info
  PATCH  /devices/{id}/status — Update device status (online/offline/busy)
  DELETE /devices/{id}     — Remove device
"""

import uuid
import subprocess
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.database import get_session
from app.domains.admin.dependencies import get_current_admin
from app.domains.devices.models import Device

router = APIRouter(prefix="/devices", tags=["devices"])


# ─── Schemas ──────────────────────────────────────────────────────────────────


class DeviceCreate(BaseModel):
    label: str
    udid: str
    status: str = "offline"
    notes: Optional[str] = None


class DeviceUpdate(BaseModel):
    label: Optional[str] = None
    udid: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class DeviceStatusUpdate(BaseModel):
    status: str  # online | offline | busy


# ─── Endpoints ────────────────────────────────────────────────────────────────


@router.get("", response_model=List[Device])
def list_devices(
    session: Session = Depends(get_session),
    _admin=Depends(get_current_admin),
):
    """Danh sách tất cả thiết bị Android đã đăng ký."""
    return session.exec(select(Device)).all()


@router.post("/scan", response_model=List[Device])
def scan_devices_now(
    session: Session = Depends(get_session),
    _admin=Depends(get_current_admin),
):
    """Quét ADB ngay lập tức để nạp các thiết bị đang kết nối vào CSDL."""
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
        print(f"Error checking adb devices: {e}")

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
            
    return devices


@router.get("/{device_id}", response_model=Device)
def get_device(
    device_id: str,
    session: Session = Depends(get_session),
    _admin=Depends(get_current_admin),
):
    """Lấy chi tiết một thiết bị."""
    device = session.get(Device, uuid.UUID(device_id))
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.put("/{device_id}", response_model=Device)
def update_device(
    device_id: str,
    payload: DeviceUpdate,
    session: Session = Depends(get_session),
    _admin=Depends(get_current_admin),
):
    """Cập nhật thông tin thiết bị."""
    device = session.get(Device, uuid.UUID(device_id))
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if payload.label is not None:
        device.label = payload.label
    if payload.udid is not None:
        device.udid = payload.udid
    if payload.notes is not None:
        device.notes = payload.notes
    if payload.is_active is not None:
        device.is_active = payload.is_active
    device.updated_at = datetime.utcnow()

    session.add(device)
    session.commit()
    session.refresh(device)
    return device


@router.patch("/{device_id}/status", response_model=Device)
def update_device_status(
    device_id: str,
    payload: DeviceStatusUpdate,
    session: Session = Depends(get_session),
    _admin=Depends(get_current_admin),
):
    """Cập nhật trạng thái thiết bị (online/offline/busy)."""
    allowed = {"online", "offline", "busy"}
    if payload.status not in allowed:
        raise HTTPException(
            status_code=422,
            detail=f"status phải là một trong: {allowed}",
        )

    device = session.get(Device, uuid.UUID(device_id))
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device.status = payload.status
    device.updated_at = datetime.utcnow()
    session.add(device)
    session.commit()
    session.refresh(device)
    return device


@router.post("/{device_id}/reset", response_model=Device)
def reset_device_pings(
    device_id: str,
    session: Session = Depends(get_session),
    _admin=Depends(get_current_admin),
):
    """Reset missed_pings về 0 và trạng thái về 'online'."""
    device = session.get(Device, uuid.UUID(device_id))
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device.missed_pings = 0
    device.status = "online"
    device.updated_at = datetime.utcnow()
    
    session.add(device)
    session.commit()
    session.refresh(device)
    return device
