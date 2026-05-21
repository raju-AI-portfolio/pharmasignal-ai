from fastapi import FastAPI
from app.api.routes import router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="PharmaSignal RAG Service",
    description="Indexes and searches regulatory documents for agent use",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "service": "PharmaSignal RAG Service",
        "status": "running",
        "docs": "/docs"
    }