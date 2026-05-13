#!/usr/bin/env bash
set -euo pipefail

echo "── KlinikPortal projektspecifik setup ──"

echo "  Opretter data/ og logs/ mapper"
mkdir -p data/exports logs

echo "  Opretter data/config.json (hvis ikke eksisterer)"
if [[ ! -f "data/config.json" ]]; then
  cat > data/config.json <<'JSON'
{
  "gecko_api_token": "",
  "site_url": "https://www.helleruplaserklinik.dk",
  "max_depth": 5,
  "port": 8765
}
JSON
fi

echo "  uv sync (backend)"
if [[ -f "pyproject.toml" ]]; then
  uv sync
fi

echo "  Frontend node_modules"
if [[ -f "frontend/package.json" ]]; then
  (cd frontend && npm install --silent)
fi
