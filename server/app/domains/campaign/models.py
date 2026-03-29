import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Campaign(SQLModel, table=True):
    """
    Core Campaign model — drives the affiliate automation pipeline.
    Each campaign represents a product source + publishing configuration.
    """

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    name: str = Field(max_length=255, description="Campaign display name")
    status: str = Field(
        default="draft",
        description="draft | active | paused | archived",
    )

    # === Automation Config ===
    shopee_keyword: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Từ khoá tìm kiếm Shopee (VD: 'áo thun nam')",
    )
    affiliate_link: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Link affiliate cố định để nhúng vào comment",
    )
    comment_template: Optional[str] = Field(
        default=None,
        description="Template nội dung comment. Dùng {affiliate_link} để nhúng link tự động.",
    )
    facebook_post_urls: Optional[str] = Field(
        default=None,
        description="Danh sách URL bài FB cần comment — JSON array string. VD: '[\"https://fb.com/...\"]'",
    )
    target_device_udid: Optional[str] = Field(
        default=None,
        max_length=100,
        description="UDID thiết bị Android mặc định cho campaign này (override .env nếu có)",
    )
    comment_delay_seconds: float = Field(
        default=30.0,
        description="Thời gian chờ (giây) giữa mỗi comment trong batch",
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
