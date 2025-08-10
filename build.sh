#!/usr/bin/env bash
set -euo pipefail

# Build a single-file Linux executable using PyInstaller
# Usage: ./build.sh [--manylinux]

ROOT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$ROOT_DIR"

if [[ "${1:-}" == "--manylinux" ]]; then
  docker run --rm -v "$ROOT_DIR":/workspace -w /workspace quay.io/pypa/manylinux2014_x86_64 \
    /bin/bash -lc '
set -e; \
/opt/python/cp311-cp311/bin/python -m pip install --upgrade pip && \
/opt/python/cp311-cp311/bin/pip install . pyinstaller && \
/opt/python/cp311-cp311/bin/pyinstaller --name uupdump --onefile scripts/entrypoint.py && \
chown -R 1000:1000 dist build
'
else
  python -m pip install --upgrade pip
  pip install . pyinstaller
  pyinstaller --name uupdump --onefile scripts/entrypoint.py
fi

echo "Built binary at: dist/uupdump"


