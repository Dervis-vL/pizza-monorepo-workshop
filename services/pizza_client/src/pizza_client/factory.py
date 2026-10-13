"""Pick an adapter from settings. The only place that knows both exist."""

from pizza_client.adapters import FixturePizzeriaSource, HttpPizzeriaSource
from pizza_client.settings import ClientSettings
from pizza_shared.ports import PizzeriaSource


def pizzeria_source(settings: ClientSettings) -> PizzeriaSource:
    """Return the adapter that `PIZZA_SOURCE` asks for."""
    if settings.source == "http":
        return HttpPizzeriaSource(
            base_url=str(settings.api_base_url),
            timeout=settings.timeout,
            max_attempts=settings.max_attempts,
        )
    return FixturePizzeriaSource(path=settings.fixture_path)
