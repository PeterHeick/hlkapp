"""BFS-dybdeberegning gennem crawl-linktræet.

Spidderen sætter depth=1 på alt (REST API giver ingen sti-hierarki).
Her korrekteres det via BFS — linktræet suppleres med URL-sti-afledede
parent→child-kanter, så sider som /a/b/ automatisk linkes fra /a/ selvom
menuen ikke indeholder det link eksplicit.
"""
from __future__ import annotations

from collections import deque
from urllib.parse import urlparse

import pandas as pd


def _norm(url: str) -> str:
    """Normaliser URL: strip trailing slash, bevar root '/', strip www.-præfiks."""
    p = urlparse(url)
    netloc = p.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = p.path.rstrip("/") or "/"
    return f"{p.scheme}://{netloc}{path}"


def _path_parent_links(known_norm: set[str]) -> dict[str, set[str]]:
    """Udled parent→child-kanter fra URL-stier for alle kendte normaliserede sider."""
    extra: dict[str, set[str]] = {}
    for url in known_norm:
        p = urlparse(url)
        path = p.path  # ingen trailing slash (garanteret af _norm)
        if not path or path == "/":
            continue
        base = f"{p.scheme}://{p.netloc}"
        inner = path[1:]  # fjern leading '/'
        if "/" not in inner:
            # Top-level side: parent er roden
            parent_norm = base + "/"
        else:
            parent_path = path.rsplit("/", 1)[0] or "/"
            parent_norm = base + parent_path
        if parent_norm in known_norm and parent_norm != url:
            extra.setdefault(parent_norm, set()).add(url)
    return extra


def recalculate_depths(
    pages: pd.DataFrame,
    links: pd.DataFrame,
    root_url: str,
) -> dict[str, int]:
    # Byg normaliserings-mapping: norm_url → første matchende original-URL
    norm_to_orig: dict[str, str] = {}
    for u in pages["url"]:
        n = _norm(u)
        norm_to_orig.setdefault(n, u)

    known_norm = set(norm_to_orig.keys())
    root_norm = _norm(root_url)

    # Byg adj-graf med normaliserede URL'er
    adj: dict[str, set[str]] = {}
    for row in links.itertuples(index=False):
        src = _norm(row.source_url)
        tgt = _norm(row.target_url)
        adj.setdefault(src, set()).add(tgt)

    # Supplér med URL-sti-hierarki (virker også ved tom crawl_links)
    for src, targets in _path_parent_links(known_norm).items():
        adj.setdefault(src, set()).update(targets)

    # Find seed: prøv root_norm, ellers korteste rod-sti på domænet
    if root_norm in known_norm or root_norm in adj:
        seed = root_norm
    else:
        root_netloc = urlparse(root_url).netloc
        potential_roots = [
            u for u in known_norm
            if urlparse(u).path in ("", "/") and urlparse(u).netloc == root_netloc
        ]
        seed = min(potential_roots, key=len) if potential_roots else root_norm

    # BFS på normaliserede URL'er
    depth_map_norm: dict[str, int] = {}
    queue: deque[tuple[str, int]] = deque([(seed, 0)])
    visited: set[str] = {seed}

    while queue:
        url, depth = queue.popleft()
        if url in known_norm:
            depth_map_norm[url] = depth
        for neighbour in adj.get(url, set()):
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append((neighbour, depth + 1))

    # Map tilbage til originale URL'er
    return {
        norm_to_orig[n]: d
        for n, d in depth_map_norm.items()
        if n in norm_to_orig
    }
