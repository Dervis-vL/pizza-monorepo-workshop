"""Ports: the interfaces the platform depends on, implemented by adapters elsewhere."""

from typing import Protocol

from pizza_shared.schemas import Pizzeria


class PizzeriaSource(Protocol):
    """Anything that can hand us a list of pizzerias.

    The app depends on this Protocol, never on a concrete adapter. Swapping the
    live API for a JSON file is a configuration change, not a code change.
    """

    def read_pizzerias(self) -> list[Pizzeria]:
        """Return every known pizzeria."""
        ...
