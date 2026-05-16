"""Selenium-scraper der henter behandlingspriser fra Gecko bookingside."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

_PRISLISTER_DIR = Path("data") / "prislister"

_sync_running = False
_sync_count = 0
_sync_error: str | None = None


def _parse_price(html: str) -> float:
    """Parse pris fra innerHTML.

    Strategi: strip HTML-tags, find alle talsekvenser med regex, tag gennemsnit.
    Håndterer dermed automatisk enkeltpriser, ranges og tusindtalsadskillere
    uden at hardkode separatorer.

    Eksempler:
      '4500 DKK'       → 4500.0
      '1.700 DKK'      → 1700.0
      '800-1000 DKK'   → 900.0  (gennemsnit af range)
      'Fra 2500 DKK'   → 2500.0
      'DKK'            → 0.0
    """
    if not html:
        return 0.0
    text = re.sub(r"<[^>]+>", "", html).strip()
    # Find alle talsekvenser — punktum regnes som tusindtalsadskiller og fjernes
    numbers = re.findall(r"\d[\d.]*", text)
    values: list[float] = []
    for n in numbers:
        try:
            values.append(float(n.replace(".", "")))
        except ValueError:
            pass
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)


def sync_prices() -> None:
    """Kør Selenium, scrape behandlinger fra Gecko bookingside, gem til CSV."""
    from klinik.config import settings  # noqa: PLC0415

    global _sync_running, _sync_count, _sync_error
    _sync_running = True
    _sync_error = None
    _sync_count = 0

    url = settings.gecko_booking_url
    if not url:
        _sync_error = "gecko_booking_url er ikke konfigureret"
        _sync_running = False
        return

    try:
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
        try:
            driver.get(url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "gecko-list-dropdown__option-row")
                )
            )
            rows = driver.find_elements(By.CLASS_NAME, "gecko-list-dropdown__option-row")
            behandlinger: list[tuple[str, float]] = []
            for row in rows:
                try:
                    navn_el = row.find_element(
                        By.CSS_SELECTOR, ".gecko-list-dropdown__option-name p"
                    )
                    pris_el = row.find_element(
                        By.CSS_SELECTOR, ".gecko-list-dropdown__option-price p"
                    )
                    navn = re.sub(r"<[^>]+>", "", navn_el.get_attribute("innerHTML") or "").strip()
                    pris = _parse_price(pris_el.get_attribute("innerHTML") or "")
                    if navn:
                        behandlinger.append((navn, pris))
                except Exception:
                    continue

            new_prices = {navn: int(round(pris)) for navn, pris in behandlinger}
            _PRISLISTER_DIR.mkdir(parents=True, exist_ok=True)
            # Brug nyeste daterede fil til sammenligning
            existing = sorted(_PRISLISTER_DIR.glob("prisliste_????-??-??.csv"))
            latest = existing[-1] if existing else None
            from klinik.gecko.pricer import prices_changed  # noqa: PLC0415
            if latest is None or prices_changed(new_prices, latest):
                today_str = date.today().isoformat()
                dest = _PRISLISTER_DIR / f"prisliste_{today_str}.csv"
                with dest.open("w", encoding="utf-8") as f:
                    f.write("navn;pris\n")
                    for navn, pris in new_prices.items():
                        f.write(f"{navn};{pris}\n")
            _sync_count = len(behandlinger)
        finally:
            driver.quit()
    except Exception as e:
        _sync_error = str(e)
    finally:
        _sync_running = False


def get_status() -> dict[str, object]:
    return {"running": _sync_running, "count": _sync_count, "error": _sync_error}
