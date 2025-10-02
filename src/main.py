from fastapi import FastAPI
from src.api.v1 import prayer_times

app = FastAPI(
    title="Adhan API",
    version="1.0.0",
    description="Prayer times calculation API (Python FastAPI implementation)",
)

# Register routers
app.include_router(prayer_times.router, prefix="/api/v1", tags=["prayer_times"])
