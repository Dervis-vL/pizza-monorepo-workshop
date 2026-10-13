"""Shared fixtures for pizza_client tests."""

from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def api_record() -> dict[str, Any]:
    """One pizzeria in the platform API's wire format."""
    return {
        "id": 7,
        "name": "50 Kalò",
        "description": None,
        "webpages": [],
        "locations": [
            {
                "id": 70,
                "pizzeria_id": 7,
                "address": "Piazza Sannazaro 201/c",
                "city": "Naples",
                "country": "Italy",
                "latitude": 40.836,
                "longitude": 14.242,
                "phone": None,
            }
        ],
        "rankings": [
            {
                "id": 700,
                "position": 10,
                "edition_id": 1,
                "pizzeria_id": 7,
                "edition": {
                    "id": 1,
                    "year": 2024,
                    "url": "https://www.50toppizza.it/50-top-pizza-world-2024/",
                    "category_id": 1,
                    "category": {
                        "id": 1,
                        "slug": "world",
                        "name": "50 Top Pizza World",
                        "description": "The world ranking",
                    },
                },
            }
        ],
        "awards": [],
    }


@pytest.fixture
def fixture_file() -> Path:
    """The real fixture shipped in the repo."""
    return REPO_ROOT / "data" / "pizzerias.json"
