"""Local desktop launcher for the FastAPI app (native window via pywebview)."""

from __future__ import annotations

import os
import socket
import threading
import time

import uvicorn
import webview

from main import app

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


def _wait_for_server(host: str, port: int, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return
        except OSError:
            time.sleep(0.2)


def main() -> None:
    host = os.environ.get("EZ_MUSIC_HOST", DEFAULT_HOST)
    preferred_port = int(os.environ.get("EZ_MUSIC_PORT", DEFAULT_PORT))
    port = _find_available_port(host, preferred_port)
    url = f"http://{host}:{port}"

    threading.Thread(
        target=uvicorn.run,
        kwargs=dict(app=app, host=host, port=port, reload=False, access_log=False),
        daemon=True,
    ).start()

    _wait_for_server(host, port)

    window = webview.create_window(
        "EZ Music Manage",
        url,
        width=1280,
        height=820,
        min_size=(900, 600),
    )
    webview.start()


if __name__ == "__main__":
    main()
