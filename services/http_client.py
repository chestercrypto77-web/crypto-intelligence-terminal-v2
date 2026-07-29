from typing import Any
import requests
from config import REQUEST_TIMEOUT_SECONDS


class DataServiceError(RuntimeError):
    pass


def get_json(url: str, params: dict[str, Any] | None = None) -> Any:
    try:
        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
            headers={"accept": "application/json", "user-agent": "Crypto-Intelligence-Terminal-V2"},
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        raise DataServiceError("The live data service is temporarily unavailable.") from exc
