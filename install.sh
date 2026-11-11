#!/usr/bin/env bash
# ==============================================================================
# Antigravity Comic Neubrutalism Theme - 1-Click Installer (Linux & macOS)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================================================"
echo "  🎨 Antigravity Comic Neubrutalism Theme Installer"
echo "  Target: Linux & macOS (Darwin)"
echo "================================================================"

if command -v python3 >/dev/null 2>&1; then
    exec python3 "${SCRIPT_DIR}/install.py"
elif command -v python >/dev/null 2>&1; then
    exec python "${SCRIPT_DIR}/install.py"
else
    echo "[!] Python is required to run the installer."
    exit 1
fi
