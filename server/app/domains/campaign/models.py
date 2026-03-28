import uuid
from datetime import datetime

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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
