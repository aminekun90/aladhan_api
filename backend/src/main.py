import os
from contextlib import asynccontextmanager
from logging.config import dictConfig

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.v1 import (
    audio_router,
    cities_router,
    devices_router,
    health_router,
    prayer_times_router,
    settings_router,
)
from src.core.repository_factory import RepositoryContainer
from src.schemas.log_config import LogConfig
from src.services.device_service import DeviceService
from src.services.env_service import EnvService
from src.utils.version import get_version

# === Repositories & Services ===
repos = RepositoryContainer()
device_service = DeviceService(repos.device_repo, repos.setting_repo)
dictConfig(LogConfig().model_dump())
logger = LogConfig.get_logger()

# === Lifespan context manager ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    # **Startup logic**
    host_ip = device_service.get_local_ip()
    api_port = int(EnvService.get("API_PORT", "8000"))

    device_service.host_ip = host_ip
    device_service.api_port = api_port

    logger.info(f"Starting app on {host_ip}:{api_port} - scheduling prayers for all devices")
    device_service.ensure_local_device()  # always-available 'this device' player
    response = device_service.schedule_prayers_for_all_devices()
    logger.info(f"Scheduled prayers for all devices: {response}")
    # Yield control to FastAPI to run the app
    yield

    # Shutdown logic
    logger.info("Shutting down - stopping scheduler")
    device_service.scheduler.shutdown(wait=False)

# === Create FastAPI app with lifespan ===
app = FastAPI(
    title="Adhan API",
    version=get_version(),
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
app.include_router(devices_router, prefix=PREFIX, tags=["Sonos Devices"])
app.include_router(cities_router, prefix=PREFIX, tags=["Cities"])
app.include_router(settings_router, prefix=PREFIX, tags=["Settings"])
app.include_router(audio_router, prefix=PREFIX, tags=["Audio"])
app.include_router(health_router, prefix=PREFIX, tags=["Health"])

# === Frontend static serving ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend/dist")
ASSETS_DIR = os.path.join(FRONTEND_DIR, "assets")
# Only mount when a build exists, so the API still boots in dev without a frontend.
if os.path.isdir(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
else:
    logger.warning(f"Frontend assets not found at {ASSETS_DIR}; skipping static mount")

@app.get("/{full_path:path}", name="serve_frontend_app", tags=["Frontend"])
async def serve_react_app(full_path: str):
    """Serve static frontend files (manifest, icons, …) or fall back to the SPA.

    Real files in the build directory are served directly so PWA assets work;
    any other path returns index.html for client-side routing.
    """
    if full_path:
        candidate = os.path.realpath(os.path.join(FRONTEND_DIR, full_path))
        # Path-traversal guard: candidate must stay inside FRONTEND_DIR.
        if candidate.startswith(os.path.realpath(FRONTEND_DIR) + os.sep) and os.path.isfile(candidate):
            return FileResponse(candidate)

    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Frontend build not found")
