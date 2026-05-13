"""Bygger D3.js kollapsibelt hierarki-træ HTML fra crawl-data."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

from klinik.config import settings


def build_hierarchy_html(
    pages: pd.DataFrame,
    orphan_urls: set[str],
    broken_urls: set[str],
    output_path: Path | None = None,
) -> Path:
    out = output_path or (Path("data") / "hierarchy.html")
    template = settings.assets_dir / "hierarchy_template.html"
    tree_data = _build_tree(pages, orphan_urls, broken_urls)
    html = template.read_text(encoding="utf-8").replace("__TREE_DATA__", json.dumps(tree_data))
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out


def _build_tree(pages: pd.DataFrame, orphan_urls: set[str], broken_urls: set[str]) -> dict:  # type: ignore[type-arg]
    root: dict = {"name": "/", "url": "", "type": "ok", "_children": {}}  # type: ignore[type-arg]
    for _, row in pages.iterrows():
        url = row["url"]
        depth = int(row["depth"])
        status = int(row["status_code"] or 0)
        parts = [p for p in (urlparse(url).path or "/").split("/") if p]
        ntype = _classify(url, depth, orphan_urls, broken_urls)
        node = root
        for i, part in enumerate(parts):
            if part not in node["_children"]:
                node["_children"][part] = {
                    "name": part, "url": "", "type": "ok",
                    "status": 200, "depth": 0, "word_count": 0, "_children": {},
                }
            if i == len(parts) - 1:
                node["_children"][part].update({
                    "url": url, "type": ntype, "status": status,
                    "depth": depth, "word_count": int(row.get("word_count") or 0),
                })
            node = node["_children"][part]
    return _to_d3(root)


def _classify(url: str, depth: int, orphan_urls: set[str], broken_urls: set[str]) -> str:
    if url in orphan_urls:            return "orphan"
    if url in broken_urls:            return "error"
    if depth > settings.deep_threshold: return "deep"
    return "ok"


def _to_d3(node: dict) -> dict:  # type: ignore[type-arg]
    result: dict = {  # type: ignore[type-arg]
        "name": node["name"], "url": node.get("url", ""),
        "type": node.get("type", "ok"), "status": node.get("status", 200),
        "depth": node.get("depth", 0), "word_count": node.get("word_count", 0),
    }
    children = [_to_d3(c) for c in node.get("_children", {}).values()]
    if children:
        result["children"] = children
    return result
