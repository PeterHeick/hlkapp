"""KlinikPortal entry point — starter FastAPI og åbner browser."""
from __future__ import annotations

import sys as _sys
if "--scrapy-worker" in _sys.argv:
    import os as _os
    from pathlib import Path as _Path
    if getattr(_sys, "frozen", False):
        _os.chdir(_Path(_sys.executable).parent)
    _sys.argv = [_sys.argv[0]] + [a for a in _sys.argv[1:] if a != "--scrapy-worker"]
    from scrapy.cmdline import execute
    execute()
    _sys.exit(0)

import errno
import socket
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


def _find_free_port(start: int, max_tries: int = 20) -> int:
    for port in range(start, start + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError as e:
                if e.errno not in (errno.EADDRINUSE, errno.EACCES):
                    raise
    raise OSError(f"Ingen ledig port fundet i {start}–{start + max_tries - 1}")


def _open_browser(port: int) -> None:
    time.sleep(1.2)
    webbrowser.open(f"http://localhost:{port}")


if __name__ == "__main__":
    port = _find_free_port(settings.port)
    threading.Thread(target=_open_browser, args=(port,), daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info", log_config=None)
