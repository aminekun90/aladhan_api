import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.api.v1 import prayer_times, soco_devices

app = FastAPI(
    title="Adhan API",
    version="1.0.0",
    description="Prayer times calculation API (Python FastAPI implementation)",
)

# === Frontend path ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend/dist")

# === Serve static assets (JS, CSS, etc.) ===
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

# === API routes ===
app.include_router(prayer_times.router, prefix="/api/v1", tags=["prayer_times"])
app.include_router(soco_devices.router, prefix="/api/v1", tags=["soco_devices"])

# === React catch-all route (after API) ===
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"error": "index.html not found"}, 404
