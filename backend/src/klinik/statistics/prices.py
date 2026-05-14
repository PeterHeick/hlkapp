"""Loader til data/behandlinger.csv — navn → pris mapping."""
from __future__ import annotations

import csv
import re
from pathlib import Path

_PRICES_PATH = Path("data") / "behandlinger.csv"


def _parse_danish_number(s: str) -> float:
    """Konverter talformat fra CSV til float.

    Håndterer dansk format ('1.900' → 1900, '1.900,50' → 1900.5)
    og Python float-format ('12500.0' → 12500).
    """
    cleaned = re.sub(r"[^\d,.]", "", s.strip())
    if not cleaned or not any(c.isdigit() for c in cleaned):
        return 0.0
    # Komma til stede → dansk format: punktum=tusind, komma=decimal
    if "," in cleaned:
        return float(cleaned.replace(".", "").replace(",", "."))
    # Punktum til stede: skeln dansk tusindtalsformat fra Python float
    if "." in cleaned:
        parts = cleaned.split(".")
        # Python float-format: ét punktum og præcis 1-2 decimaler (fx "12500.0")
        if len(parts) == 2 and len(parts[1]) <= 2:
            return float(cleaned)
        # Dansk tusindtalsformat: punktum(mer) med 3 cifre efter (fx "1.900")
        return float(cleaned.replace(".", ""))
    return float(cleaned)


def load_prices() -> dict[str, float]:
    """Returner {behandlingsnavn: pris} fra CSV. Tom dict hvis filen ikke findes."""
    if not _PRICES_PATH.exists():
        return {}
    prices: dict[str, float] = {}
    with _PRICES_PATH.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            navn = (row.get("navn") or "").strip()
            pris_raw = (row.get("pris") or "0").strip()
            if navn:
                prices[navn] = _parse_danish_number(pris_raw)
    return prices
