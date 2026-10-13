[doc("Build one member into a wheel, e.g. `just build-wheel services/pizza_client`.")]
[group("Build & Deploy")]
[script]
build-wheel dir:
    #!/usr/bin/env bash

    name="$({{ _just }} _meta {{ dir }} name)"
    echo -e "{{ green }}📦 Building wheel for {{ nc }}$name"
    uv build --package "$name" --out-dir dist
    echo -e "{{ green }}✓ dist/ now holds {{ nc }}$name"


[doc("Show what a member's wheel declares as dependencies. Siblings are dependencies, not vendored source.")]
[group("Build & Deploy")]
[script]
show-metadata dir: (build-wheel dir)
    #!/usr/bin/env bash

    name="$({{ _just }} _meta {{ dir }} name | tr '-' '_')"
    wheel="$(ls -t dist/${name}-*.whl | head -1)"
    echo -e "{{ yellow }}$wheel{{ nc }}"
    {{ run }} python - "$wheel" <<'PY'
    import sys, zipfile
    with zipfile.ZipFile(sys.argv[1]) as whl:
        meta = next(n for n in whl.namelist() if n.endswith("METADATA"))
        for line in whl.read(meta).decode().splitlines():
            if line.startswith(("Name:", "Version:", "Requires-Dist:", "Requires-Python:")):
                print("  " + line)
    PY


[doc("Build one deployable image with an explicit tag, e.g. `just build-image apps/pizza_map 0.1.0`.")]
[group("Build & Deploy")]
[script]
build-image dir tag:
    #!/usr/bin/env bash

    image="{{ _image_prefix }}$({{ _just }} _meta {{ dir }} name):{{ tag }}"
    echo -e "{{ green }}🐋 {{ dir }} → {{ nc }}$image"
    {{ container }} build -f "{{ dir }}/Dockerfile" -t "$image" .
    echo -e "{{ green }}✓ Built {{ nc }}$image"


[doc("Build deployable images tagged with their member version; all deployables by default.")]
[group("Build & Deploy")]
[script]
build *dirs=_deployables:
    #!/usr/bin/env bash

    for d in {{ dirs }}; do
        {{ _just }} build-image "$d" "$({{ _just }} _meta "$d" version)"
    done


[doc("Build and push dev images tagged with a SHA. Needs REGISTRY.")]
[group("Build & Deploy")]
[script]
push-to-registry-dev sha: _require-registry
    #!/usr/bin/env bash

    for d in {{ _deployables }}; do
        {{ _just }} build-image "$d" "{{ sha }}"
        {{ container }} push "{{ _image_prefix }}$({{ _just }} _meta "$d" name):{{ sha }}"
    done


[doc("Push every deployable as <version> and latest, building first if missing. Needs REGISTRY.")]
[group("Build & Deploy")]
[script]
push-to-registry: _require-registry
    #!/usr/bin/env bash

    for d in {{ _deployables }}; do
        name="{{ _image_prefix }}$({{ _just }} _meta "$d" name)"
        version="$({{ _just }} _meta "$d" version)"
        if ! {{ container }} image inspect "$name:$version" >/dev/null 2>&1; then
            {{ _just }} build-image "$d" "$version"
        fi
        {{ container }} push "$name:$version"
        {{ container }} tag  "$name:$version" "$name:latest"
        {{ container }} push "$name:latest"
    done


# Pushing without a registry would try docker.io/library/<name>: fail early instead.
[private]
_require-registry:
    @[[ -n "{{ _registry }}" ]] || { echo -e "{{ red }}💥 No registry set. Export REGISTRY (e.g. ghcr.io/you) to push; local builds need nothing.{{ nc }}" >&2; exit 1; }


[doc("Run the compose stack.")]
[group("Build & Deploy")]
compose env_file=".env":
    {{ container }} compose --env-file {{ env_file }} up --build


[doc("Stop the compose stack.")]
[group("Build & Deploy")]
compose-down:
    {{ container }} compose down
