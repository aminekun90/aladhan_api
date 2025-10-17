import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import (
    cities_router,
    prayer_times_router,
    soco_devices_router,
    settings_router,
    audio_router,
)
from src.core.repository_factory import RepositoryContainer
from src.services.device_service import DeviceService
from src.services.env_service import EnvService

# === Helper to get local IP ===


# === Repositories & Services ===
repos = RepositoryContainer()
device_service = DeviceService(repos.device_repo, repos.setting_repo)

# === Lifespan context manager ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    # **Startup logic**
    host_ip = device_service.get_local_ip()
    api_port = int(EnvService.get("API_PORT", "8000"))

    device_service.host_ip = host_ip
    device_service.api_port = api_port

    print(f"🌐 Starting app on {host_ip}:{api_port} — scheduling prayers for all devices")
    response = device_service.schedule_prayers_for_all_devices()
    print(response)
    # Yield control to FastAPI to run the app
    yield

    # **Shutdown logic** (if needed)
    print("🛑 Shutting down — stopping scheduler")
    device_service.scheduler.shutdown(wait=False)

# === Create FastAPI app with lifespan ===
app = FastAPI(
    title="Adhan API",
    version="1.0.0",
    description="Prayer times calculation API (Python FastAPI implementation)",
    lifespan=lifespan,
)

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === API routes ===
PREFIX = "/api/v1"
app.include_router(prayer_times_router, prefix=PREFIX, tags=["Prayer Times"])
app.include_router(soco_devices_router, prefix=PREFIX, tags=["Sonos Devices"])
app.include_router(cities_router, prefix=PREFIX, tags=["Cities"])
app.include_router(settings_router, prefix=PREFIX, tags=["Settings"])
app.include_router(audio_router, prefix=PREFIX, tags=["Audio"])

# === Frontend static serving ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend/dist")
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

@app.get("/{full_path:path}", name="serve_frontend_app", tags=["Frontend"])
async def serve_react_app(full_path: str):
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"error": "index.html not found"}, 404
