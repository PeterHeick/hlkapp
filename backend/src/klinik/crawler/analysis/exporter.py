"""Eksporterer analyse-resultater til CSV-filer med atomisk skrivning."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from klinik.config import settings
from klinik.crawler.repository import CrawlRepository


def _atomic_write(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    df.to_csv(tmp, index=False, encoding="utf-8-sig")
    tmp.replace(path)


def export_inventory(
    path: Path | None = None,
    repo: CrawlRepository | None = None,
) -> Path:
    out = path or (settings.exports_dir / "inventory_full.csv")
    pages = (repo or CrawlRepository()).pages()
    df = pages[["url", "title", "status_code", "depth", "word_count", "is_orphan", "crawled_at"]].copy()
    df.columns = pd.Index(["URL", "Titel", "Status", "Dybde", "Antal_ord", "Forældrelos", "Crawlet"])
    df["Forældrelos"] = df["Forældrelos"].map({0: "Nej", 1: "Ja"})
    _atomic_write(df, out)
    return out


def export_matrix(
    path: Path | None = None,
    repo: CrawlRepository | None = None,
) -> Path:
    out = path or (settings.exports_dir / "link_matrix.csv")
    links = (repo or CrawlRepository()).links()
    if links.empty:
        _atomic_write(pd.DataFrame(), out)
        return out
    matrix = pd.crosstab(links["source_url"], links["target_url"])
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    matrix.to_csv(tmp, encoding="utf-8-sig")
    tmp.replace(out)
    return out


def export_todo(
    path: Path | None = None,
    repo: CrawlRepository | None = None,
) -> Path:
    out = path or (settings.exports_dir / "todo_reparations.csv")
    pages = (repo or CrawlRepository()).pages()
    mask = (
        (pages["status_code"] != 200)
        | (pages["is_orphan"] == 1)
        | (pages["redirect_chain"].notna() & (pages["redirect_chain"] != "[]"))
    )
    df = pages[mask][["url", "title", "status_code", "depth", "is_orphan", "redirect_chain"]].copy()
    df["Problem"] = df.apply(_classify_todo, axis=1)
    df = df.drop(columns=["is_orphan", "redirect_chain"])
    df.columns = pd.Index(["URL", "Titel", "Status", "Dybde", "Problem"])
    _atomic_write(df, out)
    return out


def _classify_todo(row: pd.Series) -> str:  # type: ignore[type-arg]
    if row["is_orphan"]:
        return "Forældrelos side"
    try:
        chain = json.loads(row.get("redirect_chain") or "[]")
        if chain:
            return f"Redirect ({len(chain)} hop)"
    except (ValueError, TypeError):
        pass
    code = int(row.get("status_code") or 0)
    if code == 404:        return "404 Ikke fundet"
    if code == 0:          return "Utilgængelig"
    if 400 <= code < 500:  return f"Klientfejl ({code})"
    if 500 <= code < 600:  return f"Serverfejl ({code})"
    return "Ukendt"
