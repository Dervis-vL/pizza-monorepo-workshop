"""Translate the platform API's wire format into shared schemas.

This is the anti-corruption layer: the API can nest and rename whatever it
likes, the rest of the workspace only ever sees `pizza_shared.schemas`.
"""

from typing import Any

import pydantic

from pizza_client.exceptions import MalformedPayloadError
from pizza_shared.schemas import Pizzeria, Ranking


def _first_location(raw: dict[str, Any]) -> dict[str, Any]:
    locations = raw.get("locations") or []
    return dict(locations[0]) if locations else {}


def _rankings(raw: dict[str, Any]) -> tuple[Ranking, ...]:
    return tuple(
        Ranking(
            year=ranking["edition"]["year"],
            category=ranking["edition"]["category"]["name"],
            position=ranking["position"],
        )
        for ranking in raw.get("rankings") or []
    )


def parse_pizzeria(raw: dict[str, Any]) -> Pizzeria:
    """Build one `Pizzeria` from one API record."""
    location = _first_location(raw)
    try:
        return Pizzeria(
            id=raw["id"],
            name=raw["name"],
            city=location.get("city"),
            country=location.get("country"),
            latitude=location.get("latitude"),
            longitude=location.get("longitude"),
            rankings=_rankings(raw),
        )
    except (KeyError, TypeError, pydantic.ValidationError) as exc:
        msg = f"Cannot parse pizzeria record {raw.get('id', '<no id>')}: {exc}"
        raise MalformedPayloadError(msg) from exc


def parse_api_payload(payload: list[dict[str, Any]]) -> list[Pizzeria]:
    """Build the full list from the `/pizzerias/all` response body."""
    return [parse_pizzeria(raw) for raw in payload]
