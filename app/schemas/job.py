from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime


class JobUploadResponse(BaseModel):
    job_id: UUID
    status: str


class JobStatusResponse(BaseModel):
    job_id: UUID
    status: str
    filename: str
    row_count_raw: Optional[int] = None
    row_count_clean: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    summary: Optional[dict] = None  # populated only when status == "completed"