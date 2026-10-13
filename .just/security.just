[doc("Scan the workspace lock and its resolved dependencies.")]
[group("Security")]
[script]
audit-uv:
    #!/usr/bin/env bash

    echo "{{ green }}🔒 Auditing workspace dependencies...{{ nc }}"
    if ! {{_uv_audit}} --no-dev; then
        echo "{{style('bold')}}✗ Audit found vulnerabilities or adverse project statuses.{{nc}}" >&2
        echo "  Run 'just audit-blame <package>' to see which members pull it in." >&2
        echo "  Suppress non-actionable findings in [tool.uv.audit]." >&2
        exit 1
    fi
    echo "{{ green }}✓ Dependency audit passed.{{ nc }}"


[doc("[WIP] Scan committed tree for secrets.")]
[group("Security")]
audit-secrets:
    @exit 0


[doc("Show which workspace members depend on a package.")]
[group("Security")]
audit-blame member:
    uv tree --invert --package "{{ member }}" --no-dev


[doc("Full security gate.")]
[group("Security")]
audit: audit-uv audit-secrets
