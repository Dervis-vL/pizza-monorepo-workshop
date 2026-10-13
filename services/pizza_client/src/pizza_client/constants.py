"""Constants for the pizza client."""

from typing import Final

PIZZERIAS_ENDPOINT: Final[str] = "/pizzerias/all"
RETRYABLE_STATUS: Final[frozenset[int]] = frozenset({429, 500, 502, 503, 504})
