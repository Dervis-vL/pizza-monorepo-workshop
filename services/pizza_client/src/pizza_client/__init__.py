"""Adapters that supply pizzerias to the platform."""

from importlib.metadata import metadata

from pizza_client.adapters import FixturePizzeriaSource, HttpPizzeriaSource
from pizza_client.factory import pizzeria_source
from pizza_client.settings import ClientSettings

_metadata = metadata("pizza-client")
__version__ = _metadata["Version"]
__description__ = _metadata["Summary"]

__all__ = [
    "ClientSettings",
    "FixturePizzeriaSource",
    "HttpPizzeriaSource",
    "__description__",
    "__version__",
    "pizzeria_source",
]
