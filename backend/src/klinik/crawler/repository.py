"""CrawlRepository — al SQL på ét sted. DI-seam via connection_factory."""
from __future__ import annotations

import sqlite3
from collections.abc import Callable

import pandas as pd

from klinik.database import get_connection


class CrawlRepository:
    def __init__(
        self,
        connection_factory: Callable[[], sqlite3.Connection] | None = None,
    ) -> None:
        self._get_conn = connection_factory or get_connection

    def pages(self) -> pd.DataFrame:
        conn = self._get_conn()
        df = pd.read_sql("SELECT * FROM crawl_pages ORDER BY depth, url", conn)
        conn.close()
        return df

    def links(self) -> pd.DataFrame:
        conn = self._get_conn()
        df = pd.read_sql("SELECT source_url, target_url FROM crawl_links", conn)
        conn.close()
        return df

    def link_counts(self) -> dict[str, dict[str, int]]:
        """Returnerer {url: {in: N, out: M}} — bruges af /results endpoint."""
        conn = self._get_conn()
        inbound: dict[str, int] = {}
        for row in conn.execute(
            "SELECT target_url, COUNT(*) AS n FROM crawl_links GROUP BY target_url"
        ):
            inbound[row["target_url"]] = row["n"]
        outbound: dict[str, int] = {}
        for row in conn.execute(
            "SELECT source_url, COUNT(*) AS n FROM crawl_links GROUP BY source_url"
        ):
            outbound[row["source_url"]] = row["n"]
        conn.close()
        all_urls = set(inbound) | set(outbound)
        return {
            url: {"in": inbound.get(url, 0), "out": outbound.get(url, 0)}
            for url in all_urls
        }

    def page_count(self) -> int:
        conn = self._get_conn()
        row = conn.execute("SELECT COUNT(*) FROM crawl_pages").fetchone()
        conn.close()
        return int(row[0]) if row else 0

    def mark_orphans(self, urls: set[str]) -> None:
        if not urls:
            return
        conn = self._get_conn()
        conn.executemany(
            "UPDATE crawl_pages SET is_orphan=1 WHERE url=?",
            [(u,) for u in urls],
        )
        conn.commit()
        conn.close()

    def update_depths(self, depth_map: dict[str, int]) -> None:
        if not depth_map:
            return
        conn = self._get_conn()
        conn.executemany(
            "UPDATE crawl_pages SET depth=? WHERE url=?",
            [(depth, url) for url, depth in depth_map.items()],
        )
        conn.commit()
        conn.close()

    def reset(self) -> None:
        conn = self._get_conn()
        conn.executescript(
            "DROP TABLE IF EXISTS crawl_pages; DROP TABLE IF EXISTS crawl_links;"
        )
        conn.commit()
        conn.close()
        from klinik.database import init_db
        init_db()
