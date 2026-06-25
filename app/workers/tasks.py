from app.database import SessionLocal
from app.models.job import Job


def process_job(job_id: str, csv_content: str):
    """
    STUB: proves the upload -> enqueue -> worker -> DB update flow works end-to-end.
    Real pipeline logic (parse, clean, detect anomalies, classify, summarize)
    gets wired in here in a later step.
    """
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            return

        job.status = "processing"
        db.commit()

        # TODO: replace with real pipeline_runner.run(csv_content) call
        row_count = len(csv_content.strip().splitlines()) - 1  # minus header row

        job.row_count_raw = row_count
        job.status = "completed"
        db.commit()
    finally:
        db.close()