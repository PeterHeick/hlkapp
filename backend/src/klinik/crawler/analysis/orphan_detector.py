"""Detekterer forældreløse sider — sider uden indbindende interne links."""
from __future__ import annotations

import pandas as pd


def find_orphans(pages: pd.DataFrame, links: pd.DataFrame) -> pd.DataFrame:
    empty = pd.DataFrame(columns=["url", "depth", "status_code", "title", "issue"])
    # Sider med depth==0 er rod-sider og altid nåbare (ingen linker til dem, men de er ikke orphans)
    start_urls = set(pages.loc[pages["depth"] == 0, "url"])
    reachable = set(links["target_url"]) | start_urls
    orphans = pages[~pages["url"].isin(reachable)].copy()
    if orphans.empty:
        return empty
    orphans["issue"] = "orphan"
    return orphans[["url", "depth", "status_code", "title", "issue"]].reset_index(drop=True)
