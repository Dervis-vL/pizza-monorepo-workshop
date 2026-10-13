"""Tests for the shared schemas."""

import pydantic
import pytest

from pizza_shared.schemas import Pizzeria, Ranking


def test_ranking_rejects_position_zero() -> None:
    with pytest.raises(pydantic.ValidationError):
        Ranking(year=2024, category="50 Top Pizza World", position=0)


def test_ranking_rejects_prehistoric_year() -> None:
    with pytest.raises(pydantic.ValidationError):
        Ranking(year=1999, category="50 Top Pizza World", position=1)


def test_pizzeria_strips_name_whitespace() -> None:
    pizzeria = Pizzeria(id=1, name="  50 Kalò  ")
    assert pizzeria.name == "50 Kalò"


def test_pizzeria_without_coordinates_is_not_mappable() -> None:
    pizzeria = Pizzeria(id=1, name="Da Attilio", city="Naples")
    assert pizzeria.has_coordinates is False


def test_pizzeria_with_coordinates_is_mappable() -> None:
    pizzeria = Pizzeria(id=1, name="50 Kalò", latitude=40.836, longitude=14.242)
    assert pizzeria.has_coordinates is True


@pytest.mark.parametrize(("latitude", "longitude"), [(40.8, None), (None, 14.2)])
def test_pizzeria_rejects_half_a_coordinate(
    latitude: float | None, longitude: float | None
) -> None:
    with pytest.raises(pydantic.ValidationError, match="both be set"):
        Pizzeria(id=1, name="Half", latitude=latitude, longitude=longitude)


def test_pizzeria_rejects_latitude_out_of_range() -> None:
    with pytest.raises(pydantic.ValidationError):
        Pizzeria(id=1, name="Nope", latitude=91.0, longitude=0.0)


def test_best_position_is_none_without_rankings() -> None:
    assert Pizzeria(id=1, name="New kid").best_position is None


def test_best_position_takes_the_minimum() -> None:
    pizzeria = Pizzeria(
        id=1,
        name="I Masanielli",
        rankings=(
            Ranking(year=2023, category="50 Top Pizza World", position=3),
            Ranking(year=2024, category="50 Top Pizza World", position=1),
        ),
    )
    assert pizzeria.best_position == 1


def test_pizzeria_is_frozen() -> None:
    pizzeria = Pizzeria(id=1, name="Frozen")
    with pytest.raises(pydantic.ValidationError):
        pizzeria.name = "Thawed"  # type: ignore[misc]


def test_coordinates_tuple() -> None:
    pizzeria = Pizzeria(id=1, name="50 Kalò", latitude=40.836, longitude=14.242)
    assert pizzeria.coordinates == (40.836, 14.242)


def test_coordinates_raise_when_missing() -> None:
    with pytest.raises(ValueError, match="no coordinates"):
        _ = Pizzeria(id=1, name="Da Attilio").coordinates
