#!/usr/bin/env bash
# setup-codex.sh — first-time install for the Codex variant of claude-aeo
#
# What this script does:
#   1. Checks for codex CLI (warns but does not abort if missing)
#   2. Checks Python 3.10+
#   3. Installs the /aeo-loop slash prompt into ~/.codex/prompts/
#   4. Symlinks (or copies) AGENTS.md guidance so Codex picks it up
#   5. Runs `aeo_loop.py init` to scaffold ~/.config/aeo-loop/keys.toml + the SQLite store

set -euo pipefail

BOLD='\033[1m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'
GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
h() { echo -e "\n${BOLD}${CYAN}$1${NC}"; }
ok(){ echo -e "${GREEN}✓${NC} $1"; }
warn(){ echo -e "${YELLOW}!${NC} $1"; }
err(){ echo -e "${RED}✗${NC} $1"; }

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
PROMPTS_DIR="$CODEX_HOME/prompts"

h "claude-aeo — Codex variant setup"
echo "Repo root: $REPO_ROOT"
echo "Codex home: $CODEX_HOME"

# --- 1. Check codex CLI -----------------------------------------------------
h "Step 1 — Checking Codex CLI"
if command -v codex &>/dev/null; then
  ok "codex CLI found: $(codex --version 2>/dev/null || echo 'version unknown')"
else
  warn "codex CLI not found on PATH."
  echo "  Install from: https://github.com/openai/codex"
  echo "  Continuing — the slash prompt will still be staged for when you install it."
fi

# --- 2. Check Python 3.10+ --------------------------------------------------
h "Step 2 — Checking Python"
PYTHON=""
for c in python3 python; do
  if command -v "$c" &>/dev/null; then
    v=$("$c" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    maj=${v%.*}; min=${v#*.}
    if [ "$maj" -ge 3 ] && [ "$min" -ge 10 ]; then PYTHON="$c"; break; fi
  fi
done
if [ -z "$PYTHON" ]; then
  err "Python 3.10+ not found. Install from https://python.org and re-run."
  exit 1
fi
ok "Python found: $($PYTHON --version)"

# --- 3. Install slash prompt -----------------------------------------------
h "Step 3 — Installing /aeo-loop slash prompt"
mkdir -p "$PROMPTS_DIR"
SRC="$REPO_ROOT/codex/prompts/aeo-loop.md"
DST="$PROMPTS_DIR/aeo-loop.md"
if [ ! -f "$SRC" ]; then
  err "Source prompt not found at $SRC"; exit 1
fi
if [ -e "$DST" ] && ! cmp -s "$SRC" "$DST"; then
  warn "$DST already exists and differs — backing up to $DST.bak"
  cp -f "$DST" "$DST.bak"
fi
cp -f "$SRC" "$DST"
ok "Installed: $DST"

# Export AEO_LOOP_REPO so the prompt can locate this checkout.
PROFILE_HINT="export AEO_LOOP_REPO=\"$REPO_ROOT\""
if ! grep -qs "AEO_LOOP_REPO=" "$HOME/.profile" "$HOME/.bashrc" "$HOME/.zshrc" 2>/dev/null; then
  echo ""
  echo "  To let /aeo-loop find this repo from any directory, add to your shell rc:"
  echo "    $PROFILE_HINT"
fi

# --- 4. Codex project AGENTS.md -------------------------------------------
h "Step 4 — Codex AGENTS.md"
if [ -f "$REPO_ROOT/AGENTS.md" ]; then
  ok "Repo-root AGENTS.md present — Codex will pick it up when invoked from $REPO_ROOT."
else
  warn "AGENTS.md not found at repo root. Codex sessions in this repo will miss project guidance."
fi

# --- 5. Initialize config + store -----------------------------------------
h "Step 5 — aeo-loop init (config + SQLite store)"
INIT_OUT=$("$PYTHON" "$REPO_ROOT/skills/aeo-loop/scripts/aeo_loop.py" init 2>&1 || true)
echo "$INIT_OUT" | sed 's/^/  /'
if echo "$INIT_OUT" | grep -qE "Initialized|already"; then
  ok "aeo-loop CLI working."
else
  warn "aeo-loop init output looked unexpected. Run manually:"
  echo "    $PYTHON $REPO_ROOT/skills/aeo-loop/scripts/aeo_loop.py init"
fi

# --- Done -----------------------------------------------------------------
h "Setup complete"
cat <<EOF

Next steps:
  1. Add your LLM API keys:
       \$EDITOR ~/.config/aeo-loop/keys.toml
     Fill in at least 2 of: openai, anthropic, perplexity, gemini

  2. Launch Codex from this repo:
       cd $REPO_ROOT && codex

  3. Inside Codex, run three slash commands in order:
       /aeo-loop init
       /aeo-loop add-property yourdomain.com --brand="Your Brand"
       /aeo-loop bootstrap yourdomain.com

  4. Then weekly:
       /aeo-loop weekly yourdomain.com

  Full Codex guide: codex/INSTALL-CODEX.md
  Operating contract: codex/AGENTS-aeo-loop.md
EOF
