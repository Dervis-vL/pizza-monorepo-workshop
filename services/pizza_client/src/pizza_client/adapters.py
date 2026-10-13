"""Concrete `PizzeriaSource` implementations."""

import json
import logging
from pathlib import Path

import requests
import tenacity

from pizza_client import constants
from pizza_client.exceptions import MalformedPayloadError, TransientAPIError
from pizza_client.mapping import parse_api_payload
from pizza_shared.schemas import Pizzeria

logger = logging.getLogger(__name__)


class FixturePizzeriaSource:
    """Reads pizzerias from a JSON file in the API's wire format. Works on a plane."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def read_pizzerias(self) -> list[Pizzeria]:
        """Load and parse the fixture file."""
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            msg = f"Fixture not found: {self._path}"
            raise MalformedPayloadError(msg) from exc
        except json.JSONDecodeError as exc:
            msg = f"Fixture is not valid JSON: {self._path}"
            raise MalformedPayloadError(msg) from exc
        return parse_api_payload(payload)


class HttpPizzeriaSource:
    """Reads pizzerias from the live platform API, retrying transient failures."""

    def __init__(self, base_url: str, timeout: float = 10.0, max_attempts: int = 3) -> None:
        self._url = base_url.rstrip("/") + constants.PIZZERIAS_ENDPOINT
        self._timeout = timeout
        self._max_attempts = max_attempts

    def read_pizzerias(self) -> list[Pizzeria]:
        """Fetch and parse `/pizzerias/all`, with exponential backoff on transient errors."""
        retrying = tenacity.Retrying(
            stop=tenacity.stop_after_attempt(self._max_attempts),
            wait=tenacity.wait_exponential(multiplier=0.5, max=5),
            retry=tenacity.retry_if_exception_type(TransientAPIError),
            before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
            reraise=True,
        )
        return retrying(self._fetch)

    def _fetch(self) -> list[Pizzeria]:
        try:
            response = requests.get(self._url, timeout=self._timeout)
        except (requests.ConnectionError, requests.Timeout) as exc:
            msg = f"Pizza platform API unreachable: {exc}"
            raise TransientAPIError(msg) from exc

        if response.status_code in constants.RETRYABLE_STATUS:
            msg = f"Pizza platform API returned HTTP {response.status_code}"
            raise TransientAPIError(msg)
        response.raise_for_status()
        return parse_api_payload(response.json())
