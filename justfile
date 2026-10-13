# --- SETTINGS -------------------------------------------
set shell              := ["bash", "-euo", "pipefail", "-c"]
set windows-shell      := ["bash", "-euo", "pipefail", "-c"]
set script-interpreter := ["bash", "-euo", "pipefail"]

set minimum-version := '1.58.0'
set positional-arguments
set default-list
set lazy

# --- IMPORTS --------------------------------------------
import '.just/vars.just'
import '.just/setup.just'
import '.just/check.just'
import '.just/test.just'
import '.just/build.just'
import '.just/security.just'
import '.just/version.just'
import '.just/workshop.just'

# --- TARGETS --------------------------------------------
# Read a field out of a member's pyproject.toml
[private]
_meta dir field:
    @grep -m1 '^{{ field }}' {{ dir }}/pyproject.toml | sed -E 's/^{{ field }} *= *"//; s/".*//'


[doc("Show workspace members, modules and deployables.")]
[group("Meta")]
show:
    @echo "{{ yellow }}⚙ Workspace members:{{ nc }}"
    @for m in {{ _members }}; do \
        echo "{{ green }}  - $m{{ nc }}"; \
    done
    @echo "{{ yellow }}⚙ Workspace modules:{{ nc }}"
    @for m in {{ _modules }}; do \
        echo "{{ green }}  - $m{{ nc }}"; \
    done
    @echo "{{ yellow }}⚙ Workspace deployables:{{ nc }}"
    @for m in {{ _deployables }}; do \
        echo "{{ green }}  - $m{{ nc }}"; \
    done
