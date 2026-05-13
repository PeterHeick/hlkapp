"""Analyse-pipeline — kørselspunkt for al post-crawl analyse."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from klinik.config import settings
from klinik.crawler.analysis.broken_links import find_broken_links
from klinik.crawler.analysis.depth_calculator import recalculate_depths
from klinik.crawler.analysis.graph_builder import build_graph_html
from klinik.crawler.analysis.hierarchy_builder import build_hierarchy_html
from klinik.crawler.analysis.orphan_detector import find_orphans
from klinik.crawler.repository import CrawlRepository

log = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    orphans: pd.DataFrame
    broken: pd.DataFrame
    graph_path: Path
    hierarchy_path: Path

    @property
    def orphan_urls(self) -> set[str]:
        return set(self.orphans["url"])

    @property
    def broken_urls(self) -> set[str]:
        return set(self.broken["url"])

    @property
    def summary(self) -> str:
        return f"{len(self.orphans)} forældreløse · {len(self.broken)} fejl/redirects"


def run_analysis(repo: CrawlRepository | None = None) -> AnalysisResult:
    r = repo or CrawlRepository()
    pages = r.pages()
    links = r.links()

    root_url = settings.last_url

    log.info("Analyse: %d sider, %d links, root=%r", len(pages), len(links), root_url)

    if root_url:
        depth_map = recalculate_depths(pages, links, root_url)
        depths = {d: sum(1 for v in depth_map.values() if v == d)
                  for d in sorted(set(depth_map.values()))}
        log.info("BFS: %d sider nået, fordeling=%s", len(depth_map), depths)
        if depth_map:
            r.update_depths(depth_map)
            pages = r.pages()
        else:
            log.warning("BFS fandt ingen sider fra '%s'", root_url)

    orphans = find_orphans(pages, links)
    broken = find_broken_links(pages, links)
    orphan_urls = set(orphans["url"])
    broken_urls = set(broken["url"])

    r.mark_orphans(orphan_urls)

    graph_path = build_graph_html(pages, links, orphan_urls, broken_urls)
    hierarchy_path = build_hierarchy_html(pages, orphan_urls, broken_urls)

    return AnalysisResult(
        orphans=orphans,
        broken=broken,
        graph_path=graph_path,
        hierarchy_path=hierarchy_path,
    )
