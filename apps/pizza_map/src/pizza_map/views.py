"""Pure view logic: no Streamlit in here, so it can be tested like any function."""

from collections.abc import Iterable

import folium
from folium import plugins as folium_plugins

from pizza_map import constants
from pizza_shared.schemas import Pizzeria
from pizza_stats.stats import by_country


def countries(pizzerias: Iterable[Pizzeria]) -> list[str]:
    """Sorted, de-duplicated list of countries for the sidebar filter."""
    return sorted({p.country for p in pizzerias if p.country})


def mappable(pizzerias: Iterable[Pizzeria], selected_countries: Iterable[str]) -> list[Pizzeria]:
    """Pizzerias that have coordinates and fall inside the selected countries.

    An empty selection means "everything", which is what users expect from a filter.
    """
    wanted = set(selected_countries)
    return [
        p for p in pizzerias if p.has_coordinates and (not wanted or (p.country or "") in wanted)
    ]


def popup_html(pizzeria: Pizzeria) -> str:
    """The little ranking table shown when a marker is clicked."""
    rows = "".join(
        f"<tr><td><b>{r.category}</b></td><td>{r.year}</td><td>#{r.position}</td></tr>"
        for r in sorted(pizzeria.rankings, key=lambda r: (r.category, -r.year))
    )
    where = ", ".join(part for part in (pizzeria.city, pizzeria.country) if part)
    return f"<b>{pizzeria.name}</b><br><i>{where}</i><table>{rows}</table>"


def build_map(pizzerias: list[Pizzeria]) -> folium.Map:
    """A Folium map centred on the selection, with clustered markers."""
    if pizzerias:
        points = [p.coordinates for p in pizzerias]
        centre = (
            sum(lat for lat, _ in points) / len(points),
            sum(lng for _, lng in points) / len(points),
        )
    else:
        centre = (41.9, 12.5)  # Rome, because of course

    fmap = folium.Map(location=centre, zoom_start=constants.DEFAULT_ZOOM, tiles=constants.TILES)
    cluster = folium_plugins.MarkerCluster().add_to(fmap)  # type: ignore[no-untyped-call]
    for pizzeria in pizzerias:
        folium.Marker(
            location=pizzeria.coordinates,
            tooltip=pizzeria.name,
            popup=folium.Popup(popup_html(pizzeria), max_width=320),
            icon=folium.Icon(color="red", icon="cutlery", prefix="fa"),
        ).add_to(cluster)
    return fmap


def leaderboard(pizzerias: Iterable[Pizzeria]) -> list[dict[str, str | int]]:
    """Rows for the country table under the map."""
    return [stat.model_dump() for stat in by_country(pizzerias)]
