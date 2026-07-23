#!/bin/bash
# Builds the macOS .app bundle into dist/Color Extractor.app
#
# Uses venv-arm64 (a native Apple Silicon virtualenv) when present, so the
# bundle runs natively rather than through Rosetta. Falls back to venv
# otherwise.
set -e
cd "$(dirname "$0")"

if [ -d venv-arm64 ]; then
    PYINSTALLER=./venv-arm64/bin/pyinstaller
else
    PYINSTALLER=./venv/bin/pyinstaller
fi

"$PYINSTALLER" --noconfirm "Color Extractor.spec"

echo "Built: dist/Color Extractor.app"
