"""FastAPI app — middleware, routers, static files, settings endpoint."""
from __future__ import annotations

import asyncio
import os
import signal
import threading
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from klinik.config import settings
from klinik.crawler.router import router as crawler_router
from klinik.database import init_db
from klinik.gecko.router import router as gecko_router
from klinik.gecko.sync import start_backfill_loop
from klinik.statistics.router import router as stats_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    await asyncio.to_thread(init_db)
    static = Path(__file__).parent / "static" / "dist"
    if static.exists():
        _app.mount("/", StaticFiles(directory=str(static), html=True), name="frontend")
    if settings.gecko_api_token:
        await start_backfill_loop()
    yield


app = FastAPI(title="KlinikPortal", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crawler_router, prefix="/api/crawler")
app.include_router(gecko_router, prefix="/api/gecko")
app.include_router(stats_router, prefix="/api/stats")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


class SettingsOut(BaseModel):
    site_url: str
    max_depth: int
    port: int
    gecko_api_token: str
    gecko_booking_url: str


class SettingsIn(BaseModel):
    site_url: str | None = None
    max_depth: int | None = None
    gecko_api_token: str | None = None
    gecko_booking_url: str | None = None


@app.get("/api/settings", response_model=SettingsOut)
async def get_settings() -> SettingsOut:
    return SettingsOut(
        site_url=settings.site_url,
        max_depth=settings.max_depth,
        port=settings.port,
        gecko_api_token=settings.gecko_api_token,
        gecko_booking_url=settings.gecko_booking_url,
    )


@app.put("/api/settings")
async def put_settings(body: SettingsIn) -> JSONResponse:
    await asyncio.to_thread(
        settings.save,
        site_url=body.site_url,
        max_depth=body.max_depth,
        gecko_api_token=body.gecko_api_token,
        gecko_booking_url=body.gecko_booking_url,
    )
    return JSONResponse({"ok": True})


@app.post("/api/shutdown")
async def shutdown() -> JSONResponse:
    threading.Timer(0.3, lambda: os.kill(os.getpid(), signal.SIGTERM)).start()
    return JSONResponse({"ok": True})
