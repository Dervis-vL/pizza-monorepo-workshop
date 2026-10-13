"""Shared vocabulary of the pizza platform: schemas and ports."""

from importlib.metadata import metadata

from pizza_shared import ports, schemas

_metadata = metadata("pizza-shared")
__version__ = _metadata["Version"]
__description__ = _metadata["Summary"]

__all__ = ["__description__", "__version__", "ports", "schemas"]
