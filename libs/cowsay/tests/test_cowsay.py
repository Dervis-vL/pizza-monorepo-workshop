"""Smoke test: the package imports and knows its version."""

import cowsay


def test_version() -> None:
    """Dummy test."""
    assert cowsay.__version__
