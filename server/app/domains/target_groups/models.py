from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import JSON, Column, Field, SQLModel


class PostStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# ---------- DB Tables ----------


class TargetGroup(SQLModel, table=True):
    __tablename__ = "target_groups"

    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(index=True)
    name: str = Field(default="")
    keywords: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class TargetGroupConfig(SQLModel, table=True):
    __tablename__ = "target_group_config"

    id: Optional[int] = Field(default=None, primary_key=True)
    frequency_hours: int = Field(default=12)
    next_run_time: Optional[datetime] = Field(default=None)


class ScrapedPost(SQLModel, table=True):
    __tablename__ = "scraped_posts"

    id: Optional[int] = Field(default=None, primary_key=True)
    original_url: str = Field(index=True)
    content: str = Field(default="")
    author: str = Field(default="")
    comments_count: int = Field(default=0)
    reactions_count: int = Field(default=0)
    target_group_id: int = Field(index=True)
    status: PostStatus = Field(default=PostStatus.PENDING)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# ---------- Pydantic Schemas ----------


class TargetGroupCreate(SQLModel):
    url: str
    name: str = ""
    keywords: List[str] = []


class TargetGroupPublic(SQLModel):
    id: int
    url: str
    name: str
    keywords: List[str]
    is_active: bool
    created_at: Optional[datetime] = None


class ScrapedPostPublic(SQLModel):
    id: int
    original_url: str
    content: str
    author: str
    comments_count: int
    reactions_count: int
    target_group_id: int
    status: PostStatus
    created_at: Optional[datetime] = None


class PostStatusUpdate(SQLModel):
    status: PostStatus
