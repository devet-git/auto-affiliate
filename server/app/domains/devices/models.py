import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Device(SQLModel, table=True):
    """
    Android device managed by the automation system.
    Each device corresponds to a physical phone connected via ADB + Appium.
    """

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    label: str = Field(
        max_length=100,
        description="Tên thân thiện cho thiết bị (VD: 'Samsung A53 chính')",
    )
    udid: str = Field(
        max_length=100,
        index=True,
        description="ADB device UDID (lấy từ `adb devices`)",
    )
    status: str = Field(
        default="offline",
        description="online | offline | busy",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Ghi chú tuỳ chọn (FB account đang đăng nhập, SIM số, ...)",
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
