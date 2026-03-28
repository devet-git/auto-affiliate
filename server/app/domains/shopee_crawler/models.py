from enum import Enum
from typing import List, Optional

from sqlmodel import JSON, Column, Field, SQLModel


class ProductStatus(str, Enum):
    PENDING = "PENDING"
    CONVERTED = "CONVERTED"
    FAILED = "FAILED"


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
