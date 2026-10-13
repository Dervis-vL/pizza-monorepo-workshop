"""Pydantic models every workspace member speaks."""

from typing import Self

import pydantic as pyd


class Ranking(pyd.BaseModel):
    """One placement of a pizzeria in one edition of a ranking."""

    model_config = pyd.ConfigDict(frozen=True)

    year: int = pyd.Field(..., ge=2017, description="Edition year")
    category: str = pyd.Field(
        ..., min_length=1, description="Ranking name, e.g. '50 Top Pizza World'"
    )
    position: int = pyd.Field(..., ge=1, description="Placement in that edition")


class Pizzeria(pyd.BaseModel):
    """A pizzeria with its location and ranking history."""

    model_config = pyd.ConfigDict(frozen=True)

    id: int = pyd.Field(..., description="Platform identifier")
    name: str = pyd.Field(..., min_length=1, max_length=100)
    city: str | None = None
    country: str | None = None
    latitude: float | None = pyd.Field(default=None, ge=-90, le=90)
    longitude: float | None = pyd.Field(default=None, ge=-180, le=180)
    rankings: tuple[Ranking, ...] = ()

    @pyd.field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: str) -> str:
        """Names come from scraped HTML; trim the whitespace before validating length."""
        return value.strip()

    @pyd.model_validator(mode="after")
    def coordinates_come_in_pairs(self) -> Self:
        """A latitude without a longitude is a bug upstream, not a location."""
        if (self.latitude is None) != (self.longitude is None):
            msg = f"{self.name}: latitude and longitude must both be set or both be missing"
            raise ValueError(msg)
        return self

    @property
    def has_coordinates(self) -> bool:
        """True when the pizzeria can be placed on a map."""
        return self.latitude is not None and self.longitude is not None

    @property
    def coordinates(self) -> tuple[float, float]:
        """(latitude, longitude), for callers that already checked `has_coordinates`."""
        if self.latitude is None or self.longitude is None:
            msg = f"{self.name} has no coordinates"
            raise ValueError(msg)
        return (self.latitude, self.longitude)

    @property
    def best_position(self) -> int | None:
        """The highest placement ever achieved, or None without rankings."""
        if not self.rankings:
            return None
        return min(ranking.position for ranking in self.rankings)
