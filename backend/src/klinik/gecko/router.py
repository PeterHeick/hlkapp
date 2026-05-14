"""Gecko Booking API router — pris-sync og opslag."""
from __future__ import annotations

import asyncio

import httpx
from fastapi import APIRouter, HTTPException

from klinik.config import settings
from klinik.gecko import scraper
from klinik.statistics.prices import load_prices

router = APIRouter(tags=["gecko"])


def _require_token() -> None:
    if not settings.gecko_api_token:
        raise HTTPException(status_code=400, detail="Gecko API token ikke konfigureret")


@router.post("/sync-prices")
async def sync_prices() -> dict[str, object]:
    _require_token()
    if scraper.get_status()["running"]:
        raise HTTPException(status_code=409, detail="Prissync kører allerede")
    asyncio.create_task(asyncio.to_thread(scraper.sync_prices))
    return {"ok": True, "message": "Prissync startet"}


@router.get("/config-check")
async def config_check() -> dict[str, object]:
    """Returner konfiguration uden at lave netværkskald."""
    token = settings.gecko_api_token
    return {
        "base_url": settings.gecko_base_url,
        "token_length": len(token),
        "token_prefix": token[:4] + "..." if len(token) > 4 else "(tom)",
        "token_has_whitespace": token != token.strip(),
    }


@router.get("/prices-status")
async def prices_status() -> dict[str, object]:
    return scraper.get_status()


@router.get("/prices")
async def prices() -> dict[str, object]:
    return {"prices": load_prices()}


@router.get("/prices-raw")
async def prices_raw() -> dict[str, object]:
    """Debug: kør scraper og returner rå tekster uden parsing."""
    import asyncio  # noqa: PLC0415

    _require_token()

    from klinik.config import settings as _s  # noqa: PLC0415

    url = _s.gecko_booking_url
    if not url:
        raise HTTPException(status_code=400, detail="gecko_booking_url ikke konfigureret")

    async def _scrape() -> list[dict[str, str]]:
        from selenium import webdriver  # noqa: PLC0415
        from selenium.webdriver.chrome.options import Options  # noqa: PLC0415
        from selenium.webdriver.common.by import By  # noqa: PLC0415
        from selenium.webdriver.support import expected_conditions as EC  # noqa: PLC0415
        from selenium.webdriver.support.ui import WebDriverWait  # noqa: PLC0415

        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=opts)
        rows_out: list[dict[str, str]] = []
        try:
            driver.get(url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "gecko-list-dropdown__option-row")
                )
            )
            for row in driver.find_elements(By.CLASS_NAME, "gecko-list-dropdown__option-row"):
                try:
                    navn_el = row.find_element(By.CSS_SELECTOR, ".gecko-list-dropdown__option-name p")
                    pris_el = row.find_element(By.CSS_SELECTOR, ".gecko-list-dropdown__option-price p")
                    rows_out.append({
                        "navn": navn_el.text,
                        "pris_text": pris_el.text,
                        "pris_html": pris_el.get_attribute("innerHTML") or "",
                    })
                except Exception:
                    continue
        finally:
            driver.quit()
        return rows_out

    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_scrape), timeout=30)
        return {"count": len(raw), "rows": raw}
    except TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout")


@router.get("/probe")
async def probe() -> dict[str, object]:
    """Debug: send en rå request til Gecko og returner status + body."""
    import asyncio  # noqa: PLC0415

    _require_token()
    token = settings.gecko_api_token.strip()
    base = settings.gecko_base_url.rstrip("/")

    async def _call() -> dict[str, object]:
        timeout = httpx.Timeout(connect=5, read=8, write=5, pool=5)
        hdrs = {"Authorization": f"Bearer {token}"}
        attempts = [
            ("from+to",             {"from": "2026-01-01", "to": "2026-01-31"}),
            ("periodFrom+periodTo", {"periodFrom": "2026-01-01", "periodTo": "2026-01-31"}),
            ("period=YYYY-MM-DD,",  {"period": "2026-01-01,2026-01-31"}),
            ("period=YYYY-MM-DD/",  {"period": "2026-01-01/2026-01-31"}),
            ("startDate+endDate",   {"startDate": "2026-01-01", "endDate": "2026-01-31"}),
            ("start+end",           {"start": "2026-01-01", "end": "2026-01-31"}),
        ]
        results = []
        async with httpx.AsyncClient(timeout=timeout) as client:
            for label, prms in attempts:
                resp = await client.get(f"{base}/booking", headers=hdrs, params=prms)
                is_json = "json" in resp.headers.get("content-type", "")
                body = resp.json() if is_json else resp.text[:300]
                results.append({"params": label, "status": resp.status_code, "body": body})
                if resp.status_code < 400:
                    break
        return {"url": f"{base}/booking", "attempts": results}

    try:
        return await asyncio.wait_for(_call(), timeout=12)
    except TimeoutError:
        return {"status": 0, "url": base, "body": "Timeout — Gecko-serveren svarede ikke inden for 12 sekunder"}
    except httpx.RequestError as exc:
        return {"status": 0, "url": base, "body": f"Forbindelsesfejl: {exc}"}
