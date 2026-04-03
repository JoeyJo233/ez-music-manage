"""FastAPI entry point - serves API and frontend."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from routers import library, songs, cover, lrc, batch, settings
from services.runtime import resource_path

FRONTEND_DIR = resource_path("frontend")
INDEX_FILE = FRONTEND_DIR / "index.html"

app = FastAPI(title="Music Tag App", version="0.1.0")
app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")

app.include_router(library.router)
app.include_router(songs.router)
app.include_router(cover.router)
app.include_router(lrc.router)
app.include_router(batch.router)
app.include_router(settings.router)


@app.get("/")
async def index():
    return FileResponse(Path(INDEX_FILE))
