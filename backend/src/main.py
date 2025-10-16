import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1 import cities_router, prayer_times_router, soco_devices_router,settings_router, audio_router

app = FastAPI(
    title="Adhan API",
    version="1.0.0",
    description="Prayer times calculation API (Python FastAPI implementation)",
)
# Add CORS middleware before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- allow all origins; for production, restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Allow all headers
)
# === Frontend path ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend/dist")
PREFIX = "/api/v1"


# === API routes ===
app.include_router(prayer_times_router, prefix=PREFIX, tags=["Prayers Times Calculations"])
app.include_router(soco_devices_router, prefix=PREFIX,   tags=["Sonos Devices"])
app.include_router(cities_router, prefix=PREFIX, tags=["Cities"])
app.include_router(settings_router, prefix=PREFIX, tags=["Settings"])
app.include_router(audio_router, prefix=PREFIX, tags=["Audio"])



# === Serve static assets (JS, CSS, etc.) ===
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")
# === React catch-all route (after API) ===
@app.get("/{full_path:path}",name="serve_frontend_app",tags=["Frontend"])
async def serve_react_app(full_path: str):
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"error": "index.html not found"}, 404
