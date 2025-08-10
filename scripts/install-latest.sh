#!/usr/bin/env bash
set -euo pipefail

# Install the latest Linux x86_64 uupdump binary from GitHub Releases
# Usage:
#   ./scripts/install-latest.sh [<owner>/<repo>] [--bin-dir DIR]
# Example:
#   ./scripts/install-latest.sh phantomic12/uupdumpapi-downloader --bin-dir /usr/local/bin

# Default repository (can be overridden by passing <owner>/<repo>)
OWNER_REPO_DEFAULT="phantomic12/uupdumpapi-downloader"
OWNER_REPO="${1:-$OWNER_REPO_DEFAULT}"
if [[ $# -gt 0 ]]; then shift || true; fi
BIN_DIR="/usr/local/bin"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --bin-dir|-b)
      BIN_DIR="$2"; shift 2;;
    *)
      echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

# Fallback if not writable
if [[ ! -w "$BIN_DIR" ]]; then
  BIN_DIR="$HOME/.local/bin"
  mkdir -p "$BIN_DIR"
fi

API_URL="https://api.github.com/repos/${OWNER_REPO}/releases"

echo "Fetching latest release assets for ${OWNER_REPO}..." >&2
JSON=$(curl -fsSL "${API_URL}")

# Prefer the most recent release entry
ASSET_URL=$(printf '%s' "$JSON" | awk -v RS= '{print}' | \
  grep -o '"browser_download_url"\s*:\s*"[^"]*/uupdump"' | \
  head -n 1 | sed -E 's/.*"(https:[^"]+)".*/\1/')

if [[ -z "$ASSET_URL" ]]; then
  echo "Could not find any uupdump-linux-x86_64-* asset in releases." >&2
  exit 1
fi

FILENAME=$(basename "$ASSET_URL")
DEST_PATH="${BIN_DIR}/uupdump"

echo "Downloading ${ASSET_URL} -> ${DEST_PATH}" >&2
curl -fsSL "$ASSET_URL" -o "$DEST_PATH"
chmod +x "$DEST_PATH"
echo "Installed ${DEST_PATH}" >&2
echo "Run: uupdump version" >&2


