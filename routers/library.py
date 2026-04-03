"""Library scanning router."""

import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.scanner import library

router = APIRouter(prefix="/api", tags=["library"])


class ScanRequest(BaseModel):
    path: str


@router.post("/scan")
async def scan_directory(req: ScanRequest):
    try:
        songs = library.scan(req.path)
        return {"songs": songs, "total": len(songs)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/browse-folder")
async def browse_folder():
    """Open a native macOS Finder folder picker and return the selected path."""
    script = (
        'tell application "Finder"\n'
        '  activate\n'
        '  set chosen to choose folder with prompt "选择音乐文件夹"\n'
        '  return POSIX path of chosen\n'
        'end tell'
    )
    try:
        proc = await asyncio.create_subprocess_exec(
            "osascript", "-e", script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=60)
        path = stdout.decode().strip()
        if not path:
            raise HTTPException(status_code=204, detail="No folder selected")
        return {"path": path}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Folder picker timed out")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
