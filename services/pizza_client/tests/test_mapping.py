"""Tests for the API-to-schema mapping."""

from typing import Any

import pytest

from pizza_client.exceptions import MalformedPayloadError
from pizza_client.mapping import parse_api_payload, parse_pizzeria


def test_maps_first_location_and_rankings(api_record: dict[str, Any]) -> None:
    pizzeria = parse_pizzeria(api_record)

    assert pizzeria.name == "50 Kalò"
    assert pizzeria.city == "Naples"
    assert pizzeria.has_coordinates
    assert len(pizzeria.rankings) == 1
    assert pizzeria.rankings[0].category == "50 Top Pizza World"
    assert pizzeria.best_position == 10


def test_pizzeria_without_locations_has_no_coordinates(api_record: dict[str, Any]) -> None:
    api_record["locations"] = []
    pizzeria = parse_pizzeria(api_record)
    assert pizzeria.city is None
    assert not pizzeria.has_coordinates


def test_missing_rankings_key_is_fine(api_record: dict[str, Any]) -> None:
    del api_record["rankings"]
    assert parse_pizzeria(api_record).rankings == ()


def test_missing_id_is_malformed(api_record: dict[str, Any]) -> None:
    del api_record["id"]
    with pytest.raises(MalformedPayloadError, match="<no id>"):
        parse_pizzeria(api_record)


def test_invalid_field_is_malformed(api_record: dict[str, Any]) -> None:
    api_record["locations"][0]["latitude"] = 999
    with pytest.raises(MalformedPayloadError, match="record 7"):
        parse_pizzeria(api_record)


def test_ranking_missing_edition_is_malformed(api_record: dict[str, Any]) -> None:
    api_record["rankings"][0]["edition"] = None
    with pytest.raises(MalformedPayloadError):
        parse_pizzeria(api_record)


def test_parse_payload_keeps_order(api_record: dict[str, Any]) -> None:
    second = {**api_record, "id": 8, "name": "Second"}
    names = [p.name for p in parse_api_payload([api_record, second])]
    assert names == ["50 Kalò", "Second"]
