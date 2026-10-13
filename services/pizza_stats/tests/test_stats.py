"""The tests pizza_stats should have had.

Paste into services/pizza_stats/tests/test_stats.py in Act 2.
"""

from pizza_shared.schemas import Pizzeria, Ranking
from pizza_stats.stats import by_country

WORLD = "50 Top Pizza World"


def test_best_country_comes_first() -> None:
    pizzerias = [
        Pizzeria(
            id=1,
            name="A",
            country="Italy",
            rankings=(Ranking(year=2024, category=WORLD, position=1),),
        ),
        Pizzeria(
            id=2,
            name="B",
            country="USA",
            rankings=(Ranking(year=2024, category=WORLD, position=3),),
        ),
        Pizzeria(id=3, name="C", country="Italy"),
    ]
    stats = by_country(pizzerias)
    assert [s.country for s in stats] == ["Italy", "USA"]
    assert stats[0].pizzerias == 2
    assert stats[0].best_position == 1


def test_pizzerias_without_country_are_skipped() -> None:
    assert by_country([Pizzeria(id=1, name="Nowhere")]) == []
