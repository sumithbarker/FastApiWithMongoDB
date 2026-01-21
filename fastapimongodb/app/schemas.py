from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskResponse(TaskCreate):
    id: str
    status: str
    created_at: datetime