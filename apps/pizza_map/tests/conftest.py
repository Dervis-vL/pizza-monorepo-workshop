"""Fixtures for the map app tests."""

import pytest

from pizza_shared.schemas import Pizzeria, Ranking


@pytest.fixture
def pizzerias() -> list[Pizzeria]:
    world = "50 Top Pizza World"
    return [
        Pizzeria(
            id=1,
            name="I Masanielli",
            city="Caserta",
            country="Italy",
            latitude=41.07,
            longitude=14.33,
            rankings=(Ranking(year=2024, category=world, position=1),),
        ),
        Pizzeria(
            id=2,
            name="Una Pizza Napoletana",
            city="New York",
            country="USA",
            latitude=40.71,
            longitude=-73.99,
            rankings=(
                Ranking(year=2023, category=world, position=2),
                Ranking(year=2024, category=world, position=3),
            ),
        ),
        Pizzeria(id=3, name="Da Attilio", city="Naples", country="Italy"),
        Pizzeria(id=4, name="Nowhere", latitude=0.0, longitude=0.0),
    ]
