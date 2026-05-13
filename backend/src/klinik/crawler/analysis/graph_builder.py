"""Bygger D3.js netværksgraf HTML fra crawl-data."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

from klinik.config import settings


def _short_label(url: str, max_len: int = 32) -> str:
    path = urlparse(url).path or "/"
    return path if len(path) <= max_len else "…" + path[-(max_len - 1):]


def build_graph_html(
    pages: pd.DataFrame,
    links: pd.DataFrame,
    orphan_urls: set[str],
    broken_urls: set[str],
    output_path: Path | None = None,
) -> Path:
    out = output_path or (Path("data") / "graph.html")
    template = settings.assets_dir / "graph_template.html"

    inbound = links.groupby("target_url").size().to_dict()
    nodes = []
    for _, row in pages.iterrows():
        url = row["url"]
        d = int(row["depth"])
        st = int(row["status_code"] or 0)
        if url in orphan_urls:      ntype = "orphan"
        elif url in broken_urls:    ntype = "error"
        elif d > settings.deep_threshold: ntype = "deep"
        else:                       ntype = "ok"
        nodes.append({
            "id": url, "url": url, "label": _short_label(url),
            "title": str(row.get("title") or ""),
            "depth": d, "status": st, "type": ntype,
            "inbound": inbound.get(url, 0),
        })

    url_set = {n["id"] for n in nodes}
    edges = [
        {"source": r["source_url"], "target": r["target_url"]}
        for _, r in links.iterrows()
        if r["source_url"] in url_set and r["target_url"] in url_set
    ]

    payload = json.dumps({"nodes": nodes, "links": edges})
    html = template.read_text(encoding="utf-8").replace("__GRAPH_DATA__", payload)
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
