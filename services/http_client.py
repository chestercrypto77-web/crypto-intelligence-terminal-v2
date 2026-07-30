from __future__ import annotations

import time
from typing import Any

import requests

try:
    import config
    REQUEST_TIMEOUT_SECONDS = getattr(config, "REQUEST_TIMEOUT_SECONDS", 20)
except ImportError:
    REQUEST_TIMEOUT_SECONDS = 20


class DataServiceError(RuntimeError):
    pass


def get_json(url: str, params: dict[str, Any] | None = None) -> Any:
    last_error: Exception | None = None
    headers = {
        "accept": "application/json",
        "user-agent": "Crypto-Intelligence-Terminal-V2/1.0.1",
    }

    for attempt in range(3):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
                headers=headers,
            )

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after and retry_after.isdigit() else 1.5 * (attempt + 1)
                last_error = requests.HTTPError("429 Too Many Requests")
                time.sleep(delay)
                continue

            response.raise_for_status()
            return response.json()

        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(1.0 * (attempt + 1))

    detail = str(last_error) if last_error else "unknown connection error"
    raise DataServiceError(
        f"The live data service is temporarily unavailable. Connection detail: {detail}"
    ) from last_error
