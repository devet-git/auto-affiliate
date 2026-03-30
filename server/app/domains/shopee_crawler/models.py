from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import JSON, Column, Field, SQLModel


class ProductStatus(str, Enum):
    PENDING = "PENDING"
    CONVERTED = "CONVERTED"
    FAILED = "FAILED"


class SourceType(str, Enum):
    KEYWORD = "KEYWORD"
    SHOP_URL = "SHOP_URL"


# ---------- DB Tables ----------

class ShopeeProduct(SQLModel, table=True):
    __tablename__ = "shopee_products"

    id: Optional[int] = Field(default=None, primary_key=True)
    original_url: str = Field(index=True)
    affiliate_url: Optional[str] = Field(default=None)
    title: str = Field(default="")
    price: Optional[str] = Field(default=None)
    image_urls: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: ProductStatus = Field(default=ProductStatus.PENDING)
    keyword: Optional[str] = Field(default=None, index=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class CrawlerSource(SQLModel, table=True):
    __tablename__ = "crawler_sources"

    id: Optional[int] = Field(default=None, primary_key=True)
    source_type: SourceType
    value: str = Field(index=True)
    is_active: bool = Field(default=True)


class CrawlerConfig(SQLModel, table=True):
    __tablename__ = "crawler_config"

    id: Optional[int] = Field(default=None, primary_key=True)
    frequency_hours: int = Field(default=24)
    next_run_time: Optional[datetime] = Field(default=None)


# ---------- Pydantic Schemas ----------

class ShopeeProductPublic(SQLModel):
    id: int
    original_url: str
    affiliate_url: Optional[str] = None
    title: str
    price: Optional[str] = None
    image_urls: List[str] = []
    status: ProductStatus
    keyword: Optional[str] = None
    created_at: Optional[datetime] = None


class CrawlerSourceCreate(SQLModel):
    source_type: SourceType
    value: str


class CrawlerSourcePublic(SQLModel):
    id: int
    source_type: SourceType
    value: str
    is_active: bool


class CrawlerConfigUpdate(SQLModel):
    frequency_hours: Optional[int] = None
    next_run_time: Optional[datetime] = None


class CrawlerConfigPublic(SQLModel):
    id: int
    frequency_hours: int
    next_run_time: Optional[datetime] = None
