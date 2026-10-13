# Multi-stage build straight from the lockfile.
# Stage 1 resolves and installs; stage 2 ships only the virtualenv.
FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

# Manifests first, so this layer is cached until a dependency changes.
# uv needs every member's pyproject.toml to load the workspace, not just ours.
COPY pyproject.toml uv.lock ./
COPY apps/pizza_map/pyproject.toml   apps/pizza_map/README.md   apps/pizza_map/
COPY libs/pizza_shared/pyproject.toml libs/pizza_shared/README.md libs/pizza_shared/
COPY services/pizza_client/pyproject.toml services/pizza_client/README.md services/pizza_client/
COPY services/pizza_stats/pyproject.toml services/pizza_stats/README.md services/pizza_stats/

# Third-party dependencies only: --no-install-workspace skips our own members.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package pizza-map --no-dev --locked --no-install-workspace

# Now the source trees pizza-map actually needs, and nothing else.
COPY apps/pizza_map/src           apps/pizza_map/src
COPY libs/pizza_shared/src        libs/pizza_shared/src
COPY services/pizza_client/src    services/pizza_client/src
COPY services/pizza_stats/src     services/pizza_stats/src
COPY data                         data

# Members become real, non-editable wheels inside .venv.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package pizza-map --no-dev --locked --no-editable


FROM python:3.14-slim AS production

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/data  /app/data

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PIZZA_SOURCE=fixture \
    HOME=/home/appuser

# No installer at runtime: the app runs from /app/.venv, which uv built without pip.
RUN rm -rf /usr/local/lib/python3*/site-packages/pip \
           /usr/local/lib/python3*/site-packages/pip-*.dist-info \
           /usr/local/lib/python3*/ensurepip \
           /usr/local/bin/pip /usr/local/bin/pip3* && \
    groupadd --system appgroup && \
    useradd --system --gid appgroup --create-home --home-dir /home/appuser appuser

USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "/app/.venv/lib/python3.14/site-packages/pizza_map/app.py", \
     "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
