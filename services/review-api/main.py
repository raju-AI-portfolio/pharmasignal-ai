from fastapi import FastAPI
from app.api.routes import router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="PharmaSignal Human Review API",
    description="Human-in-the-loop review and audit trail for adverse event cases",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "service": "PharmaSignal Human Review API",
        "status": "running",
        "docs": "/docs"
    }
