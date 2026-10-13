[doc("Install everything: workspace sync, .env, and a green banner.")]
[group("Setup")]
[script]
setup:
    #!/usr/bin/env bash

    echo -e "{{ green }}📦 Syncing the workspace{{ nc }}"
    uv sync
    if [[ ! -f .env ]]; then
        cp .env.example .env
        echo -e "{{ green }}✓ Created .env from .env.example{{ nc }}"
    fi
    echo -e "{{ green }}✓ Workspace ready. Try: just run{{ nc }}"


[doc("Run the Streamlit map locally.")]
[group("Setup")]
run:
    {{ run }} streamlit run apps/pizza_map/src/pizza_map/app.py


[doc("Scaffold a new member from templates/member, e.g. `just new-member services/pizza_stats --depends pizza-shared`")]
[group("Setup")]
[script]
new-member target *args:
    #!/usr/bin/env bash

    echo -e "{{ green }}📦 Scaffolding {{target}}{{ nc }}"
    # positional-arguments keeps quoted values intact, e.g. --description "Aggregations over the rankings"
    {{ _scripts }}/new_member.py {{ quote(justfile_directory()) }} "$1" "${@:2}"
    echo -e "{{ green }}📦 Syncing the workspace (the glob in [tool.uv.workspace] already includes it){{ nc }}"
    {{ uv }} sync
    echo -e "{{ green }}✓ {{target}} is a workspace member. Run: just test-member {{target}}{{ nc }}"
