"""FastAPI entry point - serves API and frontend."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from routers import library, songs, cover, lrc, batch, settings

app = FastAPI(title="Music Tag App", version="0.1.0")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

app.include_router(library.router)
app.include_router(songs.router)
app.include_router(cover.router)
app.include_router(lrc.router)
app.include_router(batch.router)
app.include_router(settings.router)


@app.get("/")
async def index():
    return FileResponse("frontend/index.html")
