"""Rapporterer brudte links (4xx/5xx), utilgængelige sider og redirect-chains."""
from __future__ import annotations

import json

import pandas as pd


def find_broken_links(pages: pd.DataFrame, links: pd.DataFrame) -> pd.DataFrame:
    def has_redirect(chain_json: str) -> bool:
        try:
            return bool(json.loads(chain_json or "[]"))
        except (ValueError, TypeError):
            return False

    broken_mask = (pages["status_code"] != 200) | pages["redirect_chain"].apply(has_redirect)
    broken = pages[broken_mask].copy()
    broken["referrers"] = broken["url"].apply(
        lambda u: list(links.loc[links["target_url"] == u, "source_url"])
    )
    broken["issue"] = [_classify(row) for _, row in broken.iterrows()]
    return broken[["url", "status_code", "depth", "title", "issue", "referrers"]].reset_index(drop=True)


def _classify(row: pd.Series) -> str:  # type: ignore[type-arg]
    chain = row.get("redirect_chain", "[]")
    try:
        if json.loads(chain or "[]"):
            return "redirect"
    except (ValueError, TypeError):
        pass
    code = int(row.get("status_code") or 0)
    if code == 0:          return "utilgængelig"
    if code == 404:        return "404_ikke_fundet"
    if 400 <= code < 500:  return f"klientfejl_{code}"
    if 500 <= code < 600:  return f"serverfejl_{code}"
    return "anden_fejl"
