# pizza-map 🗺️

The deployable. A Streamlit page that puts every pizzeria with coordinates on a
Folium map, with a country filter in the sidebar.

```bash
just run            # or: uv run streamlit run apps/pizza_map/src/pizza_map/app.py
```

It never touches an adapter directly: it asks `pizza_client.pizzeria_source()`
for whatever `PIZZA_SOURCE` says. `views.py` holds the pure logic (filters,
popup HTML, map building) and is the part that gets unit tested. `app.py` is the
Streamlit script and is excluded from coverage on purpose.
