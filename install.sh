#!/usr/bin/env bash
# B24_hermes_bot installer for Linux
# Checks for Docker or Python, clones repo if needed, runs setup, starts bot.
set -euo pipefail

REPO_URL="https://github.com/Koykto/B24_hermes_bot.git"
INSTALL_DIR="${B24_BOT_DIR:-$HOME/B24_hermes_bot}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# --- Check prerequisites ---
check_docker() {
    if command -v docker &>/dev/null && docker compose version &>/dev/null 2>&1; then
        return 0
    fi
    return 1
}

check_python() {
    if command -v python3 &>/dev/null; then
        PY=python3
        return 0
    elif command -v python &>/dev/null; then
        PY=python
        return 0
    fi
    return 1
}

USE_DOCKER=false
USE_VENV=false

if check_docker; then
    info "Docker detected."
    USE_DOCKER=true
elif check_python; then
    info "Python detected: $PY"
    USE_VENV=true
else
    error "Neither Docker nor Python3 found. Install one to continue."
fi

# --- Clone repo if not present ---
if [ ! -d "$INSTALL_DIR" ]; then
    info "Cloning repository to $INSTALL_DIR ..."
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# --- Run setup_config.py ---
info "Running setup_config.py ..."
if [ "$USE_DOCKER" = true ]; then
    python3 scripts/setup_config.py 2>/dev/null || python scripts/setup_config.py 2>/dev/null || {
        warn "Could not run setup_config.py automatically. Run it manually:"
        warn "  python3 scripts/setup_config.py --interactive"
    }
else
    # Set up venv if not present
    if [ ! -d "venv" ]; then
        info "Creating virtual environment..."
        $PY -m venv venv
    fi

    source venv/bin/activate
    pip install -q -r requirements.txt 2>/dev/null || true
    python scripts/setup_config.py
fi

# --- Start the bot ---
info "Starting bot..."
if [ "$USE_DOCKER" = true ]; then
    docker compose up -d
    info "Bot started in Docker. Check with: docker compose logs -f"
else
    source venv/bin/activate
    info "Starting bot in foreground (Ctrl+C to stop)..."
    python bot_handler.py
fi
