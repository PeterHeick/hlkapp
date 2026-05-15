"""Scrapy pipeline — skriver crawl-items til SQLite."""
from __future__ import annotations

import logging
import sqlite3

from scrapy_crawler.src.crawler.db import get_connection

log = logging.getLogger(__name__)


class SqlitePipeline:
    def open_spider(self, spider=None) -> None:
        self._conn = get_connection()

    def close_spider(self, spider=None) -> None:
        self._conn.close()

    def process_item(self, item: dict, spider=None) -> dict:  # type: ignore[type-arg]
        if item.get("_link"):
            try:
                self._conn.execute(
                    "INSERT OR IGNORE INTO crawl_links (source_url, target_url) VALUES (?, ?)",
                    (item["source"], item["target"]),
                )
                self._conn.commit()
            except sqlite3.Error as exc:
                log.warning("Link insert fejl: %s", exc)
            return item

        try:
            self._conn.execute(
                """INSERT OR REPLACE INTO crawl_pages
                   (url, status_code, depth, parent_url,
                    title, word_count, redirect_chain, last_modified)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    item.get("url"),
                    item.get("status_code"),
                    item.get("depth", 0),
                    item.get("parent_url"),
                    item.get("title", ""),
                    item.get("word_count", 0),
                    item.get("redirect_chain", "[]"),
                    item.get("last_modified"),
                ),
            )
            self._conn.commit()
        except sqlite3.Error as exc:
            log.warning("DB-skrivning fejlede for %s: %s", item.get("url"), exc)
        return item
