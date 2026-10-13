"""Tests for the settings-driven factory."""

import pytest

from pizza_client.adapters import HttpPizzeriaSource
from pizza_client.factory import pizzeria_source
from pizza_client.settings import ClientSettings


def test_env_selects_http(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PIZZA_SOURCE", "http")
    monkeypatch.setenv("PIZZA_API_BASE_URL", "https://pizza.example.com")
    settings = ClientSettings(_env_file=None)
    source = pizzeria_source(settings)
    assert isinstance(source, HttpPizzeriaSource)


def test_test_env_supplies_the_member_dataset() -> None:
    # No monkeypatch: tests/vars.env configures this, the way .env does for the app.
    pizzerias = pizzeria_source(ClientSettings(_env_file=None)).read_pizzerias()
    assert len(pizzerias) == 3


def test_unknown_source_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PIZZA_SOURCE", "carrier-pigeon")
    with pytest.raises(ValueError, match="fixture"):
        ClientSettings(_env_file=None)
