"""Aggregations over pizzeria rankings. Paste into services/pizza_stats/src/pizza_stats/stats.py."""

from collections import Counter
from collections.abc import Iterable

import pydantic

from pizza_shared.schemas import Pizzeria


class CountryStats(pydantic.BaseModel):
    """How one country did."""

    country: str
    pizzerias: int
    best_position: int | None


def by_country(pizzerias: Iterable[Pizzeria]) -> list[CountryStats]:
    """Count pizzerias per country and note the best placement, best country first."""
    counts: Counter[str] = Counter()
    best: dict[str, int | None] = {}
    for pizzeria in pizzerias:
        if not pizzeria.country:
            continue
        counts[pizzeria.country] += 1
        position = pizzeria.best_position
        current = best.get(pizzeria.country)
        if position is not None and (current is None or position < current):
            best[pizzeria.country] = position
        else:
            best.setdefault(pizzeria.country, current)
    return sorted(
        (CountryStats(country=c, pizzerias=n, best_position=best[c]) for c, n in counts.items()),
        key=lambda s: (s.best_position is None, s.best_position, -s.pizzerias),
    )
