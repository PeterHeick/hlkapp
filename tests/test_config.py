"""Test Settings loader."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "src"))


def test_settings_defaults() -> None:
    from klinik.config import Settings
    s = Settings()
    assert s.port == 8765
    assert s.max_pages == 1000
    assert s.deep_threshold == 4


def test_settings_from_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"site_url": "https://test.dk", "max_depth": 3}))

    import klinik.config as cfg_module
    monkeypatch.setattr(cfg_module, "_CONFIG_PATH", config)

    from klinik.config import Settings
    s = Settings.load()
    assert s.site_url == "https://test.dk"
    assert s.max_depth == 3
