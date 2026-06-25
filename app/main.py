from fastapi import FastAPI
from app.api.routes import jobs


app = FastAPI(title="AI Transaction Pipeline")

app.include_router(jobs.router)



@app.get("/")
def root():
    return {"message": "API     Running"}

@app.get("/health")
def health():
    return {"status": "ok"}