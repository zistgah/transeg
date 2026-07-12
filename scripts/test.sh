#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
# The CI oracle, hermetic. Owns its venv — in-folder, never /tmp.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$HERE"
VENV="${VENV:-$HERE/.venv}"
[ -d "$VENV" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" -q install -U pip
"$VENV/bin/pip" -q install -r requirements-dev.txt
"$VENV/bin/python" -m pytest tests -q "$@"
