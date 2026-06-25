import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobUploadResponse
from app.redis_conn import queue
from app.workers.tasks import process_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/upload", response_model=JobUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    print("upload_csv called with file:", file.filename)
    # 1. Basic validation — reject anything that isn't a .csv by filename/content-type.
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")

    # 2. Read the raw bytes and decode to text — this is what gets passed to the worker.
    raw_bytes = await file.read()
    try:
        csv_content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File is not valid UTF-8 text")

    if not csv_content.strip():
        raise HTTPException(status_code=400, detail="Uploaded CSV is empty")

    # 3. Create the Job record — status starts as "pending".
    job = Job(
        id=uuid.uuid4(),
        filename=file.filename,
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # 4. Enqueue the actual processing task on RQ, passing job_id + csv content.
    queue.enqueue(process_job, str(job.id), csv_content)

    # 5. Return immediately — the client will poll /status from here.
    return JobUploadResponse(job_id=job.id, status=job.status)

@router.get("/test", response_model=JobUploadResponse)
async def test():
    return {"message": " hello API Running"}