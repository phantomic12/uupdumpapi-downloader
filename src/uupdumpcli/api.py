from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

import requests


DEFAULT_BASE_URL = os.environ.get(
    "UUPDUMP_JSON_API_BASE_URL", "https://api.uupdump.net"
)


class UUPDumpApiError(Exception):
    pass


def _raise_for_api_error(payload: Mapping) -> None:
    response = payload.get("response")
    if isinstance(response, Mapping) and "error" in response:
        err = response.get("error")
        raise UUPDumpApiError(str(err))


def _get_json(
    path: str,
    params: Optional[Mapping[str, str]] = None,
    *,
    base_url: str = DEFAULT_BASE_URL,
    max_retries: int = 5,
    base_delay_sec: float = 1.0,
) -> Mapping:
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    headers = {"User-Agent": f"uupdumpcli/{__import__('uupdumpcli').__version__}"}
    last_exc: Optional[Exception] = None
    for attempt in range(max(1, max_retries)):
        try:
            resp = requests.get(url, params=params, timeout=60, headers=headers)
            if resp.status_code in (429, 503):
                # Respect Retry-After if present
                retry_after = resp.headers.get("Retry-After")
                try:
                    delay = float(retry_after) if retry_after else base_delay_sec * (2 ** attempt)
                except Exception:
                    delay = base_delay_sec * (2 ** attempt)
                time.sleep(min(delay, 30))
                last_exc = requests.HTTPError(f"{resp.status_code} Too Many Requests")
                continue
            resp.raise_for_status()
            data = resp.json()
            _raise_for_api_error(data)
            return data
        except requests.RequestException as e:
            last_exc = e
            time.sleep(base_delay_sec * (2 ** attempt))
        except ValueError as e:
            # JSON decode error; retry once
            last_exc = e
            time.sleep(base_delay_sec * (2 ** attempt))
    assert last_exc is not None
    raise last_exc


def list_builds(search: Optional[str] = None, sort_by_date: bool = True, *, base_url: str = DEFAULT_BASE_URL) -> List[Mapping]:
    params: Dict[str, str] = {}
    if search:
        params["search"] = search
    if sort_by_date:
        params["sortByDate"] = "1"
    data = _get_json("listid.php", params=params, base_url=base_url)
    response = data.get("response", {})
    builds = response.get("builds", [])
    # Some API responses may return a mapping keyed by UUID; normalize to list of dicts
    if isinstance(builds, dict):
        return list(builds.values())
    return list(builds)


def list_languages(update_id: str, *, base_url: str = DEFAULT_BASE_URL) -> Mapping[str, str]:
    data = _get_json("listlangs.php", params={"id": update_id}, base_url=base_url)
    return data.get("response", {}).get("langs", {})


def list_editions(update_id: str, lang: str, *, base_url: str = DEFAULT_BASE_URL) -> List[str]:
    data = _get_json(
        "listeditions.php", params={"id": update_id, "lang": lang}, base_url=base_url
    )
    return data.get("response", {}).get("editions", [])


def get_downloads(update_id: str, lang: Optional[str] = None, edition: Optional[str] = None, *, base_url: str = DEFAULT_BASE_URL) -> Tuple[Mapping, Mapping[str, Mapping]]:
    params: Dict[str, str] = {"id": update_id}
    if lang:
        params["lang"] = lang
    if edition:
        params["edition"] = edition
    data = _get_json("get.php", params=params, base_url=base_url)
    response = data.get("response", {})
    meta = {k: response.get(k) for k in ("updateName", "arch", "build")}
    files = response.get("files", {})
    return meta, files


