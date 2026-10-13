"""The map gets its pizzerias through the client, as app.py does."""

from pizza_client import ClientSettings, pizzeria_source
from pizza_map import views


def test_map_loads_pizzerias_through_the_client() -> None:
    # No monkeypatch: whatever the test environment configures is what the map reads.
    pizzerias = pizzeria_source(ClientSettings(_env_file=None)).read_pizzerias()
    assert views.mappable(pizzerias, [])
