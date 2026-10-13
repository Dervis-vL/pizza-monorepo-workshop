# 🍕 pizza-monorepo-wrkshp

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![deptry](https://img.shields.io/badge/deptry-checked-4B8BBE)](https://github.com/fpgmaas/deptry)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Coverage gate](https://img.shields.io/badge/coverage%20gate-90%25%20per%20member-brightgreen)](.just/test.just)

[![just](https://img.shields.io/badge/just-command%20runner-1E1E1E)](https://github.com/casey/just)
[![prek](https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge.svg)](https://github.com/j178/prek)

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](apps/pizza_map/Dockerfile)

The hands-on repo for **Everyone Hates Monorepos (Until They Don't): Building a
Solid Python Monorepo with uv**. A small workspace that is shaped exactly like a
production one: one shared package, one service library, one deployable app,
and the tooling that keeps them honest.

```
pizza-monorepo-wrkshp/
├── pyproject.toml              👈 the root: the conductor (package = false)
├── uv.lock                     one lockfile for the whole band
├── justfile  .just/            one command runner, recipes split by concern
├── templates/member/           what `just new-member` stamps out (Jinja)
├── data/pizzerias.json         offline fixture, the map works on a plane
├── packages/pizza_shared/      🧱 schemas + the PizzeriaSource port
├── services/pizza_client/      🔌 two adapters for that port: fixture and live API
├── apps/pizza_map/             🗺️ Streamlit + Folium, the deployable
└── workshop/                   the acts, the snippets, the facilitator notes
```

## Start here

```bash
uv sync                       # one resolver, one .venv, one truth
uv tool install rust-just     # `just`, installed outside the workspace on purpose
just                          # every recipe, grouped
just setup && just run        # the map, from the fixture
```

No `just` on PATH? `uvx --from rust-just just <recipe>`. On Windows use Git Bash or WSL.

Requires uv 0.12.0+ and Python 3.12+. The workspace pins `exclude-newer` for security reasons.

## The recipes you will use

| Recipe | What |
|---|---|
| `just new-member services/x --depends pizza-shared` | scaffold a member from `templates/member` |
| `just test` | every member in its own process, coverage gate per member |
| `just check` | lock, lint, types, deps, tests |
| `just show-metadata services/pizza_client` | build a wheel and print what it requires |
| `just bump services/pizza_client [--dry-run]` | version, changelog, tag, per member |
| `just rescue 2` | fell behind? stash and jump to the start of Act 2 |

## Design notes worth stealing

- **Root ships nothing.** Dev tools and shared config at the root, production deps in members.
- **`dependencies` says what, `[tool.uv.sources]` says where.** `{ workspace = true }` is the one magic line.
- **Ports and adapters.** `pizza_map` depends on `PizzeriaSource`, never on `requests`. `PIZZA_SOURCE=fixture|http` picks the adapter.
- **Per-member everything.** Version, changelog, tag, tests, coverage. `just test` refuses a member without tests.
- **`.just/scripts/*.py` are PEP 723 scripts.** They run in their own environment, so `just` keeps working while the workspace is broken.

## The production version

This repo is the workshop-sized twin of
[best-pizza-services](https://github.com/Dervis-vL/best-pizza-services): FastAPI,
a worker, Postgres, S3, Alembic, three services, the same patterns at full size.
