"""Tests for the pure view logic."""

import folium

from pizza_map import views
from pizza_shared.schemas import Pizzeria


def test_countries_are_sorted_and_unique(pizzerias: list[Pizzeria]) -> None:
    assert views.countries(pizzerias) == ["Italy", "USA"]


def test_mappable_drops_entries_without_coordinates(pizzerias: list[Pizzeria]) -> None:
    names = [p.name for p in views.mappable(pizzerias, [])]
    assert "Da Attilio" not in names
    assert len(names) == 3


def test_mappable_filters_by_country(pizzerias: list[Pizzeria]) -> None:
    assert [p.name for p in views.mappable(pizzerias, ["USA"])] == ["Una Pizza Napoletana"]


def test_popup_lists_rankings_newest_first(pizzerias: list[Pizzeria]) -> None:
    html = views.popup_html(pizzerias[1])
    assert "<b>Una Pizza Napoletana</b>" in html
    assert "New York, USA" in html
    assert html.index("2024") < html.index("2023")


def test_popup_without_location_has_no_dangling_comma(pizzerias: list[Pizzeria]) -> None:
    html = views.popup_html(pizzerias[3])
    assert "<i></i>" in html


def test_build_map_places_one_marker_per_pizzeria(pizzerias: list[Pizzeria]) -> None:
    shown = views.mappable(pizzerias, [])
    fmap = views.build_map(shown)
    assert isinstance(fmap, folium.Map)
    rendered = fmap.get_root().render()
    for pizzeria in shown:
        assert pizzeria.name in rendered


def test_build_map_without_pizzerias_still_renders() -> None:
    fmap = views.build_map([])
    assert isinstance(fmap, folium.Map)
