from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from typing import Any, Dict


def run_json(cmd: list[str]) -> Dict[str, Any] | list[Any]:
    result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    return json.loads(result.stdout)


def main() -> int:
    print("Listing builds...", flush=True)
    builds = run_json([
        "uupdump",
        "list",
        "--search",
        "Windows 11",
        "--sort-by-date",
        "--json",
    ])
    if not isinstance(builds, list) or not builds:
        print("No builds returned", file=sys.stderr)
        return 1

    print(f"Got {len(builds)} builds, probing for files...", flush=True)
    chosen_uuid = None
    chosen_title = None
    chosen_smallest = None

    for build in builds[:100]:
        if not isinstance(build, dict):
            continue
        uuid = build.get("uuid")
        if not uuid:
            continue
        try:
            details = run_json(["uupdump", "show", uuid, "--links", "--json"])  # meta + files
        except subprocess.CalledProcessError:
            continue
        files = details.get("files", {}) if isinstance(details, dict) else {}
        if not isinstance(files, dict) or not files:
            continue
        smallest_name = min(files.items(), key=lambda kv: int(kv[1].get("size") or 0))[0]
        chosen_uuid = uuid
        chosen_title = build.get("title")
        chosen_smallest = smallest_name
        break

    if not chosen_uuid:
        print("Did not find a build with downloadable files in first 100 entries.")
        return 2

    print("Chosen:")
    print(f"  UUID:   {chosen_uuid}")
    print(f"  Title:  {chosen_title}")
    print(f"  File:   {chosen_smallest}")

    regex = f"^{re.escape(chosen_smallest)}$"
    print("Downloading smallest file only...", flush=True)
    subprocess.run(
        [
            "uupdump",
            "download",
            chosen_uuid,
            "--out",
            "./downloads",
            "--include-regex",
            regex,
            "--limit",
            "1",
            "--no-resume",
        ],
        check=True,
    )

    path = os.path.join("./downloads", chosen_smallest)
    if not os.path.exists(path):
        print(f"File not found after download: {path}", file=sys.stderr)
        return 3
    size = os.path.getsize(path)
    print(f"Downloaded: {path} ({size} bytes)")
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


