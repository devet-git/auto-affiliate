from datetime import datetime
from typing import Optional, Any
from sqlmodel import Field, SQLModel, Column, JSON

class TaskLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: str = Field(index=True, max_length=100)
    task_name: str = Field(index=True, max_length=200)
    status: str = Field(index=True, max_length=50)
    
    # Store JSON representation of kwargs/result, and full traceback for errors
    result: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    kwargs: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    error_traceback: Optional[str] = None
    
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None

class AppSetting(SQLModel, table=True):
    key: str = Field(primary_key=True, max_length=100)
    value: str = Field(max_length=255)
