from pydantic import BaseModel
from uuid import UUID


class JobUploadResponse(BaseModel):
    job_id: UUID
    status: str