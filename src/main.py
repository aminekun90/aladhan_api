from fastapi import FastAPI
from src.api.v1 import prayer_times
from src.api.v1 import soco_devices

app = FastAPI(
    title="Adhan API",
    version="1.0.0",
    description="Prayer times calculation API (Python FastAPI implementation)",
)

# Register routers
app.include_router(prayer_times.router, prefix="/api/v1", tags=["prayer_times"])
app.include_router(soco_devices.router, prefix="/api/v1", tags=["soco_devices"])
