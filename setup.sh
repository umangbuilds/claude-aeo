#!/usr/bin/env bash
# setup.sh — first-time install for claude-aeo
#
# What this script does:
#   1. Checks for claude CLI
#   2. Checks Python 3.10+
#   3. Asks permission before installing claude-seo (the forked SEO skill collection
#      that aeo-loop builds on top of), with context on why it's needed
#   4. Installs claude-seo via `claude plugin install`
#   5. Verifies the install

set -euo pipefail

BOLD='\033[1m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

print_header() { echo -e "\n${BOLD}${CYAN}$1${NC}"; }
print_ok()     { echo -e "${GREEN}✓${NC} $1"; }
print_warn()   { echo -e "${YELLOW}!${NC} $1"; }
print_err()    { echo -e "${RED}✗${NC} $1"; }

print_header "claude-aeo setup"
echo "This script sets up the AEO/SEO cadence skill for Claude Code."
echo ""

# --- 1. Check claude CLI ---
print_header "Step 1 — Checking Claude Code CLI"
if ! command -v claude &>/dev/null; then
  print_err "Claude Code CLI not found."
  echo "Install from: https://claude.ai/code"
  exit 1
fi
print_ok "claude CLI found: $(claude --version 2>/dev/null || echo 'version unknown')"

# --- 2. Check Python 3.10+ ---
print_header "Step 2 — Checking Python"
PYTHON=""
for candidate in python3 python; do
  if command -v "$candidate" &>/dev/null; then
    version=$("$candidate" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    major=$(echo "$version" | cut -d. -f1)
    minor=$(echo "$version" | cut -d. -f2)
    if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
      PYTHON="$candidate"
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  print_err "Python 3.10 or higher not found."
  echo "Install from: https://python.org — pick version 3.10 or higher."
  exit 1
fi
print_ok "Python found: $($PYTHON --version)"

# --- 3. Ask permission to install claude-seo ---
print_header "Step 3 — Second dependency: claude-seo"
echo ""
echo "  aeo-loop (this skill) builds on top of claude-seo, an open-source SEO"
echo "  skill collection. It handles site audits, GEO readiness, content briefs,"
echo "  keyword clustering, and schema generation — all the capabilities that"
echo "  aeo-loop orchestrates into the weekly AEO loop."
echo ""
echo "  Installing claude-seo will:"
echo "    - Add the claude-seo plugin to your Claude Code install"
echo "    - Make skills like seo-audit, seo-geo, seo-schema, enhance-aeo available"
echo "    - NOT modify any other settings or files"
echo ""
echo "  Without claude-seo, aeo-loop's audit and discovery steps will be limited"
echo "  to WebFetch-based fallbacks instead of the full skill suite."
echo ""

while true; do
  read -r -p "  Install claude-seo now? [Y/n]: " yn
  case ${yn:-Y} in
    [Yy]*)
      INSTALL_SEO=true
      break
      ;;
    [Nn]*)
      INSTALL_SEO=false
      print_warn "Skipping claude-seo install. You can install it later:"
      echo "    claude plugin install claude-seo@YOUR-CLAUDE-SEO-SOURCE"
      echo "  Re-run setup.sh after installing to verify the full setup."
      break
      ;;
    *)
      echo "  Please enter Y or n."
      ;;
  esac
done

# --- 4. Install claude-seo ---
if [ "$INSTALL_SEO" = "true" ]; then
  print_header "Step 4 — Installing claude-seo"

  # Detect which install source to use. The plugin.json in this repo
  # should list the source. Fall back to prompting if unresolved.
  SEO_SOURCE=""

  PLUGIN_JSON="$(dirname "$0")/.claude-plugin/plugin.json"
  if [ -f "$PLUGIN_JSON" ] && command -v jq &>/dev/null; then
    SEO_SOURCE=$(jq -r '.dependencies["claude-seo"] // empty' "$PLUGIN_JSON" 2>/dev/null || true)
  fi

  if [ -z "$SEO_SOURCE" ]; then
    echo ""
    echo "  Could not auto-detect the claude-seo install source from plugin.json."
    echo "  Example: github.com/umangbuilds/claude-seo  or  ~/.claude/plugins/claude-seo"
    read -r -p "  Enter the claude-seo install source (repo/path/URL), or press Enter to skip: " SEO_SOURCE
    if [ -z "$SEO_SOURCE" ]; then
      print_warn "No source provided. Skipping claude-seo install."
      INSTALL_SEO=false
    fi
  fi

  if [ "$INSTALL_SEO" = "true" ] && [ -n "$SEO_SOURCE" ]; then
    echo "  Running: claude plugin install $SEO_SOURCE"
    if claude plugin install "$SEO_SOURCE"; then
      print_ok "claude-seo installed."
    else
      print_warn "claude plugin install exited with a non-zero status."
      echo "  This may mean claude-seo is already installed, or the source was unreachable."
      echo "  Check with: claude plugin list"
    fi
  fi
else
  print_header "Step 4 — Skipped (claude-seo install declined)"
fi

# --- 5. Verify ---
print_header "Step 5 — Verification"

echo "  Checking aeo-loop CLI..."
SCRIPT_DIR="$(dirname "$0")/skills/aeo-loop/scripts"
if [ -f "$SCRIPT_DIR/aeo_loop.py" ]; then
  if $PYTHON "$SCRIPT_DIR/aeo_loop.py" init 2>&1 | grep -q "Initialized\|already"; then
    print_ok "aeo-loop CLI working."
  else
    print_warn "aeo-loop init ran but output looked unexpected. Check manually:"
    echo "    $PYTHON $SCRIPT_DIR/aeo_loop.py init"
  fi
else
  print_warn "aeo-loop scripts not found at expected path: $SCRIPT_DIR"
  echo "  Expected the skills/ directory to be alongside this setup.sh."
fi

echo ""
print_header "Setup complete"
echo ""
echo "  Next steps:"
echo "    1. Add your LLM API keys:"
echo "         open ~/.config/aeo-loop/keys.toml    # Mac"
echo "         notepad %USERPROFILE%\\.config\\aeo-loop\\keys.toml  # Windows"
echo "       Fill in at least 2 of: openai, anthropic, perplexity, gemini"
echo ""
echo "    2. Register your website:"
echo "         /aeo-loop add-property yourdomain.com --brand='Your Brand'"
echo "         # Add --region india if your audience is primarily Indian"
echo ""
echo "    3. Run bootstrap for your first baseline:"
echo "         /aeo-loop bootstrap yourdomain.com"
echo ""
echo "    4. Run your first weekly loop:"
echo "         /aeo-loop weekly yourdomain.com"
echo ""
echo "  Full guide: skills/aeo-loop/GETTING-STARTED.md"
echo ""
