"""Streamlit map of the world's best pizzerias."""

from importlib.metadata import metadata

_metadata = metadata("pizza-map")
__version__ = _metadata["Version"]
__description__ = _metadata["Summary"]

__all__ = [
    "__description__",
    "__version__",
]
