"""A cow that only talks about pizza. Paste into packages/cowsay/src/cowsay/__init__.py."""

from importlib.metadata import metadata

from cowsay.speech import get_output_string

_metadata = metadata("cowsay")
__version__ = _metadata["Version"]
__description__ = _metadata["Summary"]

__all__ = [
    "__description__",
    "__version__",
    "get_output_string",
]
