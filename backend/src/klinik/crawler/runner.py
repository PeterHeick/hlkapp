"""Starter og stopper Scrapy-crawl som subprocess med stdout-drain."""
from __future__ import annotations

import collections
import logging
import os
import subprocess
import sys
import threading
from pathlib import Path

import psutil

logger = logging.getLogger(__name__)

if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys.executable).parent
else:
    PROJECT_ROOT = Path(__file__).resolve().parents[4]
SCRAPY_SETTINGS = "scrapy_crawler.src.crawler.settings"

_log_buffer: collections.deque[str] = collections.deque(maxlen=100)
_active_proc: subprocess.Popen | None = None  # type: ignore[type-arg]


def _drain_stdout(proc: subprocess.Popen, buf: collections.deque[str]) -> None:  # type: ignore[type-arg]
    """Læs subprocess stdout linje for linje — forhindrer 64KB pipe-deadlock."""
    if proc.stdout is None:
        return
    for line in proc.stdout:
        stripped = line.rstrip()
        if stripped:
            buf.append(stripped)
            logger.debug("[scrapy] %s", stripped)


def start_crawl(url: str, depth: int = 5) -> subprocess.Popen:  # type: ignore[type-arg]
    global _active_proc
    _log_buffer.clear()
    if getattr(sys, "frozen", False):
        cmd = [
            sys.executable, "--scrapy-worker",
            "crawl", "site_spider",
            "-a", f"start_url={url}",
            "-a", f"max_depth={depth}",
        ]
        env = {**os.environ, "SCRAPY_SETTINGS_MODULE": SCRAPY_SETTINGS}
    else:
        cmd = [
            sys.executable, "-m", "scrapy", "crawl", "site_spider",
            "-a", f"start_url={url}",
            "-a", f"max_depth={depth}",
        ]
        env = {
            **os.environ,
            "SCRAPY_SETTINGS_MODULE": SCRAPY_SETTINGS,
            "PYTHONPATH": f"{PROJECT_ROOT}{os.pathsep}{PROJECT_ROOT / 'backend' / 'src'}",
        }
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        text=True,
        cwd=str(PROJECT_ROOT),
        env=env,
        **({"creationflags": subprocess.CREATE_NO_WINDOW} if sys.platform == "win32" else {}),
    )
    _active_proc = proc
    threading.Thread(
        target=_drain_stdout,
        args=(proc, _log_buffer),
        daemon=True,
        name="scrapy-drain",
    ).start()
    return proc


def stop_crawl(proc: subprocess.Popen | None = None) -> None:  # type: ignore[type-arg]
    global _active_proc
    target = proc or _active_proc
    if target is None or target.poll() is not None:
        return
    try:
        parent = psutil.Process(target.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass
    _active_proc = None


def is_running() -> bool:
    return _active_proc is not None and _active_proc.poll() is None


def get_log_tail() -> list[str]:
    return list(_log_buffer)
