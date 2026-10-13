"""Settings for choosing and configuring a pizzeria source."""

from pathlib import Path
from typing import Literal

import pydantic as pyd
import pydantic_settings as pyd_settings


class ClientSettings(pyd_settings.BaseSettings):
    """Read from the environment (and `.env`), prefixed with `PIZZA_`."""

    model_config = pyd_settings.SettingsConfigDict(
        env_prefix="PIZZA_",
        env_file=".env",
        extra="ignore",
    )

    source: Literal["fixture", "http"] = pyd.Field(
        description="Which adapter supplies pizzerias",
    )
    fixture_path: Path = pyd.Field(
        default=Path("data/pizzerias.json"),
        description="JSON file in the platform API's wire format",
    )
    api_base_url: pyd.AnyHttpUrl = pyd.Field(
        default=pyd.AnyHttpUrl("http://localhost:8000"),
        description="Base URL of the pizza platform API",
    )
    timeout: float = pyd.Field(default=10.0, gt=0, description="Per-request timeout [s]")
    max_attempts: int = pyd.Field(default=3, ge=1, description="Tries incl. the first")
