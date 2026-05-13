"""Crawler FastAPI-router — alle /api/crawler endpoints."""
from __future__ import annotations

import asyncio
import logging
import socket
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from klinik.config import settings
from klinik.crawler import runner
from klinik.crawler.analysis.exporter import export_inventory, export_matrix, export_todo
from klinik.crawler.analysis.pipeline import run_analysis
from klinik.crawler.repository import CrawlRepository

log = logging.getLogger(__name__)
router = APIRouter(tags=["crawler"])
_repo = CrawlRepository()

_finishing = False


def _reject_private_url(url: str) -> None:
    """Afviser URLs der peger på private/loopback-adresser."""
    hostname = urlparse(url).hostname or ""
    try:
        ip = ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise HTTPException(status_code=422, detail="Interne netværksadresser er ikke tilladt")
    except ValueError:
        # Hostname — slå det op og tjek den opløste IP
        try:
            resolved = socket.getaddrinfo(hostname, None)
            for *_, sockaddr in resolved:
                try:
                    ip = ip_address(sockaddr[0])
                except ValueError:
                    # Windows kan returnere IPv6 zone IDs (fe80::1%eth0) som ip_address ikke forstår
                    continue
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                    raise HTTPException(status_code=422, detail="Interne netværksadresser er ikke tilladt")
        except socket.gaierror:
            pass  # kan ikke slås op — lad Scrapy håndtere det


class StartBody(BaseModel):
    url: str
    depth: int = 5


@router.post("/start")
async def start_crawl(body: StartBody) -> dict[str, str]:
    if runner.is_running():
        raise HTTPException(status_code=409, detail="Crawl er allerede i gang")
    if not body.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=422, detail="URL skal starte med http:// eller https://")
    await asyncio.to_thread(_reject_private_url, body.url)

    await asyncio.to_thread(settings.save, last_url=body.url)
    await asyncio.to_thread(_repo.reset)
    await asyncio.to_thread(runner.start_crawl, body.url, body.depth)
    return {"status": "started"}


@router.post("/stop")
async def stop_crawl() -> dict[str, str]:
    runner.stop_crawl()
    await _finish()
    return {"status": "stopped"}


@router.get("/status")
async def crawl_status() -> dict:  # type: ignore[type-arg]
    page_count = await asyncio.to_thread(_repo.page_count)
    return {
        "running": runner.is_running(),
        "page_count": page_count,
        "log_tail": runner.get_log_tail(),
    }


@router.get("/results")
async def crawl_results() -> dict:  # type: ignore[type-arg]
    pages = await asyncio.to_thread(_repo.pages)
    link_counts = await asyncio.to_thread(_repo.link_counts)

    pages_list = [
        {
            "url": row["url"],
            "title": row.get("title") or "",
            "status_code": int(row.get("status_code") or 0),
            "depth": int(row.get("depth") or 0),
            "is_orphan": bool(row.get("is_orphan")),
            "word_count": int(row.get("word_count") or 0),
        }
        for _, row in pages.iterrows()
    ]
    return {"pages": pages_list, "link_counts": link_counts}


@router.get("/export/inventory")
async def export_inv() -> StreamingResponse:
    path = await asyncio.to_thread(export_inventory)
    return _csv_response(path, "inventory_full.csv")


@router.get("/export/matrix")
async def export_mat() -> StreamingResponse:
    path = await asyncio.to_thread(export_matrix)
    return _csv_response(path, "link_matrix.csv")


@router.get("/export/todo")
async def export_td() -> StreamingResponse:
    path = await asyncio.to_thread(export_todo)
    return _csv_response(path, "todo_reparations.csv")


@router.post("/finish")
async def finish_crawl() -> dict[str, str]:
    """Kaldes af frontend når polling opdager at crawl er stoppet naturligt."""
    await _finish()
    return {"status": "ok"}


@router.get("/graph")
async def get_graph() -> FileResponse:
    p = Path("data") / "graph.html"
    if not p.exists():
        raise HTTPException(
            status_code=404, detail="Graf ikke genereret endnu — kør en crawl først"
        )
    return FileResponse(str(p), media_type="text/html")


@router.get("/hierarchy")
async def get_hierarchy() -> FileResponse:
    p = Path("data") / "hierarchy.html"
    if not p.exists():
        raise HTTPException(
            status_code=404, detail="Hierarki ikke genereret endnu — kør en crawl først"
        )
    return FileResponse(str(p), media_type="text/html")


def _csv_response(path: Path, filename: str) -> StreamingResponse:
    def _iter():  # type: ignore[return]
        with open(path, "rb") as f:
            yield from f

    return StreamingResponse(
        _iter(),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


async def _finish() -> None:
    global _finishing
    if _finishing:
        return
    _finishing = True
    try:
        try:
            await asyncio.to_thread(run_analysis)
        except Exception:
            log.exception("Analyse fejlede")
    finally:
        _finishing = False


