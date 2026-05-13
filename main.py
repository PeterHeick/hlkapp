"""KlinikPortal entry point — starter FastAPI og åbner browser."""
from __future__ import annotations

import sys
import threading
import time
import webbrowser
from pathlib import Path

import uvicorn

if getattr(sys, "frozen", False):
    import os
    os.chdir(Path(sys.executable).parent)

from klinik.app import app  # noqa: E402
from klinik.config import settings  # noqa: E402


def _open_browser() -> None:
    time.sleep(1.2)
    webbrowser.open(f"http://localhost:{settings.port}")


if __name__ == "__main__":
    threading.Thread(target=_open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=settings.port, log_level="info")
