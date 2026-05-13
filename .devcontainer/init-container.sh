#!/usr/bin/env bash
# Generisk devcontainer init-script.
# Kører én gang (postCreateCommand). Idempotent — safe at re-køre ved rebuild.
#
# Auto-detekterer:  Python/uv, Node/pnpm, monorepo-struktur.
# Projekt-specifik logik:  læg i .devcontainer/project-setup.sh (valgfri hook).

set -euo pipefail

WORKSPACE="$PWD"
PROJECT_NAME=$(basename "$WORKSPACE")

# ── uv (Python package manager) ─────────────────────────────────────────────
echo "── uv ──"
if command -v uv >/dev/null 2>&1; then
  echo "  $(uv --version) — allerede installeret"
else
  curl -LsSf https://astral.sh/uv/install.sh | sh
  if ! grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
  fi
  export PATH="$HOME/.local/bin:$PATH"
fi

# ── pnpm ─────────────────────────────────────────────────────────────────────
echo "── pnpm ──"
if command -v pnpm >/dev/null 2>&1; then
  echo "  pnpm $(pnpm --version) — allerede installeret"
else
  npm install -g pnpm@latest
fi

# ── Python venv (auto-detect: har projektet pyproject.toml eller setup.py?) ──
echo "── Python venv ──"
VENV_DIR="$HOME/.venvs/$PROJECT_NAME"
_python_roots=()

# Tjek for Python-projekt i rod
if [[ -f "pyproject.toml" || -f "setup.py" ]]; then
  _python_roots+=(".")
fi

# Tjek for Python-underprojekt i server/ (Mimer-stil og lignende)
if [[ -f "server/pyproject.toml" || -f "server/setup.py" ]]; then
  _python_roots+=("server")
fi

if [[ ${#_python_roots[@]} -gt 0 ]]; then
  # Validér eller genskab venv
  if [[ -d "$VENV_DIR" ]] && ! "$VENV_DIR/bin/python" --version >/dev/null 2>&1; then
    echo "  Broken venv — sletter $VENV_DIR"
    rm -rf "$VENV_DIR"
  fi
  if [[ ! -d "$VENV_DIR" ]]; then
    uv venv "$VENV_DIR"
  fi

  for root in "${_python_roots[@]}"; do
    echo "  uv pip install -e $root"
    (cd "$root" && VIRTUAL_ENV="$VENV_DIR" uv pip install -e .)
  done

  # Auto-activate i nye shells
  _marker="# >>> claude-devcontainer auto-activate >>>"
  if ! grep -qF "$_marker" "$HOME/.bashrc" 2>/dev/null; then
    cat >> "$HOME/.bashrc" <<'BASHRC'

# >>> claude-devcontainer auto-activate >>>
if [[ -n "${PWD:-}" ]]; then
  _pname=$(basename "$PWD")
  if [[ -f "$HOME/.venvs/$_pname/bin/activate" ]]; then
    source "$HOME/.venvs/$_pname/bin/activate"
  fi
  unset _pname
fi
# <<< claude-devcontainer auto-activate <<<
BASHRC
    echo "  Auto-activate tilføjet til ~/.bashrc"
  fi
else
  echo "  Ingen pyproject.toml/setup.py fundet — springer over"
fi

# ── Volume permissions ────────────────────────────────────────────────────────
# Docker opretter volume-mountpoints som root. Fix ownership til vscode-bruger.
echo "── Volume permissions ──"
_fix_ownership() {
  local p="$1"
  if [[ -d "$p" ]] && [[ "$(stat -c '%u' "$p")" != "$(id -u)" ]]; then
    echo "  chown $p"
    sudo chown -R "$(id -u):$(id -g)" "$p"
  fi
}

_fix_ownership "$HOME/.claude"

# Fix node_modules-volumes: find alle package.json-mapper i projektet
while IFS= read -r pkgjson; do
  dir=$(dirname "$pkgjson")
  nm="$dir/node_modules"
  if [[ -d "$nm" ]]; then
    _fix_ownership "$nm"
  fi
done < <(find "$WORKSPACE" -maxdepth 4 -name "package.json" \
           ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null)

# ── Claude bypassPermissions ─────────────────────────────────────────────────
# Skriver KUN til container-volumet (~/.claude/settings.json) — aldrig til
# workspace-filerne. Host-maskinens Claude-installation påvirkes ikke.
echo "── Claude bypassPermissions ──"
CLAUDE_SETTINGS="$HOME/.claude/settings.json"
mkdir -p "$(dirname "$CLAUDE_SETTINGS")"

if [[ ! -f "$CLAUDE_SETTINGS" ]]; then
  cat > "$CLAUDE_SETTINGS" <<'JSON'
{
  "skipDangerousModePermissionPrompt": true,
  "permissions": {
    "defaultMode": "bypassPermissions"
  }
}
JSON
  echo "  Oprettede $CLAUDE_SETTINGS"
elif ! grep -q '"bypassPermissions"' "$CLAUDE_SETTINGS" 2>/dev/null; then
  if command -v jq >/dev/null 2>&1; then
    tmp=$(mktemp)
    jq '.permissions.defaultMode = "bypassPermissions" | .skipDangerousModePermissionPrompt = true' \
      "$CLAUDE_SETTINGS" > "$tmp" && mv "$tmp" "$CLAUDE_SETTINGS"
    echo "  Tilføjede bypassPermissions til eksisterende $CLAUDE_SETTINGS"
  else
    echo "  ADVARSEL: jq ikke fundet — patch manuelt: bypassPermissions i $CLAUDE_SETTINGS"
  fi
else
  echo "  bypassPermissions allerede aktiv — rører ikke"
fi

# ── Node deps (auto-detect) ───────────────────────────────────────────────────
echo "── Node deps ──"
_node_found=false
while IFS= read -r pkgjson; do
  dir=$(dirname "$pkgjson")
  echo "  pnpm install i $dir"
  (cd "$dir" && CI=true pnpm install --silent)
  _node_found=true
done < <(find "$WORKSPACE" -maxdepth 4 -name "package.json" \
           ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null)
if [[ "$_node_found" == false ]]; then
  echo "  Ingen package.json fundet — springer over"
fi

# ── Projekt-specifik hook ─────────────────────────────────────────────────────
if [[ -f ".devcontainer/project-setup.sh" ]]; then
  echo "── Projekt-specifik setup (.devcontainer/project-setup.sh) ──"
  bash ".devcontainer/project-setup.sh"
fi

echo ""
echo "✓ Container klar."
echo ""
echo "  Næste shell auto-aktiverer venv (hvis Python-projekt)."
echo "  Aktiver i nuværende shell: source $HOME/.venvs/$PROJECT_NAME/bin/activate"
echo ""
echo "  Husk: Postgres/ChromaDB/Ollama på host nås via 172.17.0.1"
echo "  eller host.docker.internal (tilføj 'extra_hosts' i devcontainer.json)."
