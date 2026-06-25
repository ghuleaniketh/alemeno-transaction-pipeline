import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobUploadResponse
from app.redis_conn import queue
from app.workers.tasks import process_job
from app.schemas.job import JobUploadResponse, JobStatusResponse


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

@router.get("/{job_id}/status", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    summary = None
    if job.status == "completed":
        summary = {
            "row_count_raw": job.row_count_raw,
            "row_count_clean": job.row_count_clean,
        }

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        filename=job.filename,
        row_count_raw=job.row_count_raw,
        row_count_clean=job.row_count_clean,
        created_at=job.created_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
        summary=summary,
    )
