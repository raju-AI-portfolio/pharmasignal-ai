from fastapi import FastAPI
from app.api.routes import router
import logging

# Configure logging so we can see what the service is doing
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create the FastAPI app
app = FastAPI(
    title="PharmaSignal Ingestion Service",
    description="Fetches and stores FDA adverse event reports",
    version="1.0.0"
)

# Register our routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "service": "PharmaSignal Ingestion Service",
        "status": "running",
        "docs": "/docs"
    }