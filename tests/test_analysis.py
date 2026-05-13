"""Smoke tests for analyse-moduler."""
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "src"))

from klinik.crawler.analysis.broken_links import find_broken_links
from klinik.crawler.analysis.orphan_detector import find_orphans


@pytest.fixture
def sample_pages() -> pd.DataFrame:
    return pd.DataFrame([
        {"url": "https://ex.com/",       "status_code": 200, "depth": 0, "title": "Forside", "word_count": 100, "is_orphan": 0, "redirect_chain": "[]"},
        {"url": "https://ex.com/a",      "status_code": 200, "depth": 1, "title": "A",       "word_count": 50,  "is_orphan": 0, "redirect_chain": "[]"},
        {"url": "https://ex.com/b",      "status_code": 404, "depth": 2, "title": "",        "word_count": 0,   "is_orphan": 0, "redirect_chain": "[]"},
        {"url": "https://ex.com/orphan", "status_code": 200, "depth": 3, "title": "Orphan",  "word_count": 30,  "is_orphan": 0, "redirect_chain": "[]"},
    ])


@pytest.fixture
def sample_links() -> pd.DataFrame:
    return pd.DataFrame([
        {"source_url": "https://ex.com/",  "target_url": "https://ex.com/a"},
        {"source_url": "https://ex.com/a", "target_url": "https://ex.com/b"},
    ])


def test_find_broken_links(sample_pages: pd.DataFrame, sample_links: pd.DataFrame) -> None:
    result = find_broken_links(sample_pages, sample_links)
    assert len(result) == 1
    assert result.iloc[0]["url"] == "https://ex.com/b"
    assert "404" in result.iloc[0]["issue"]


def test_find_orphans(sample_pages: pd.DataFrame, sample_links: pd.DataFrame) -> None:
    result = find_orphans(sample_pages, sample_links)
    assert len(result) == 1
    assert result.iloc[0]["url"] == "https://ex.com/orphan"


def test_no_orphans_when_all_linked(sample_pages: pd.DataFrame) -> None:
    links = pd.DataFrame([
        {"source_url": "https://ex.com/",  "target_url": "https://ex.com/a"},
        {"source_url": "https://ex.com/",  "target_url": "https://ex.com/b"},
        {"source_url": "https://ex.com/",  "target_url": "https://ex.com/orphan"},
    ])
    result = find_orphans(sample_pages, links)
    assert len(result) == 0
