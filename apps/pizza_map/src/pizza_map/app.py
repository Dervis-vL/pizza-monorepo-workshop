"""Streamlit entry point. Wiring only; the logic lives in `views`.

# pragma: exclude file
"""

import subprocess
import sys

import streamlit as st
from streamlit_folium import st_folium

from pizza_client import ClientSettings, pizzeria_source
from pizza_map import constants, views
from pizza_shared.schemas import Pizzeria

st.set_page_config(page_title=constants.PAGE_TITLE, page_icon=constants.PAGE_ICON, layout="wide")
st.title(constants.PAGE_TITLE)
st.caption(constants.CAPTION)


@st.cache_data(ttl=constants.CACHE_TTL_SECONDS, show_spinner="Loading pizzerias...")
def load_pizzerias(source_name: str) -> list[Pizzeria]:
    """Cached per source name so a room full of laptops does not DDoS the API."""
    settings = ClientSettings()
    if settings.source != source_name:
        settings = settings.model_copy(update={"source": source_name})
    return pizzeria_source(settings).read_pizzerias()


settings = ClientSettings()
with st.sidebar:
    st.header("Filters")
    source_name = st.radio(
        "Source", ["fixture", "http"], index=0 if settings.source == "fixture" else 1
    )

try:
    pizzerias = load_pizzerias(source_name)
except Exception as exc:  # noqa: BLE001
    st.error(f"Could not load pizzerias: {exc}")
    st.stop()

with st.sidebar:
    selected = st.multiselect("Countries", views.countries(pizzerias), default=[])

shown = views.mappable(pizzerias, selected)

left, middle, right = st.columns(3)
left.metric("Pizzerias", len(pizzerias))
middle.metric("On the map", len(shown))
right.metric("Countries", len(views.countries(shown)))

st_folium(views.build_map(shown), height=constants.MAP_HEIGHT, width="stretch", returned_objects=[])

st.divider()
st.caption("Data: 50 Top Pizza. Coordinates are approximate. Bring an appetite.")


def main() -> None:
    """Console-script entry point: hands over to `streamlit run`."""
    subprocess.run(  # noqa: S603
        [sys.executable, "-m", "streamlit", "run", __file__, *sys.argv[1:]],
        check=True,
    )
