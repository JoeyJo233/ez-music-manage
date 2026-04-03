"""Local desktop-style launcher for the FastAPI app."""

from __future__ import annotations

import os
import socket
import threading
import time
import webbrowser

import uvicorn

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def _find_available_port(host: str, preferred_port: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, preferred_port))
            return preferred_port
        except OSError:
            sock.bind((host, 0))
            return int(sock.getsockname()[1])


def _open_browser_when_ready(url: str, host: str, port: int, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                webbrowser.open(url)
                return
        except OSError:
            time.sleep(0.2)


def main() -> None:
    host = os.environ.get("EZ_MUSIC_HOST", DEFAULT_HOST)
    preferred_port = int(os.environ.get("EZ_MUSIC_PORT", DEFAULT_PORT))
    should_open_browser = os.environ.get("EZ_MUSIC_OPEN_BROWSER", "1") != "0"
    port = _find_available_port(host, preferred_port)
    url = f"http://{host}:{port}"

    if should_open_browser:
        threading.Thread(
            target=_open_browser_when_ready,
            args=(url, host, port),
            daemon=True,
        ).start()

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        access_log=False,
    )


if __name__ == "__main__":
    main()
