# Recipes that only exist for the workshop. Delete this file when you take the
# repo home; nothing else depends on it.

[doc("Fell behind? `just rescue 2` stashes your work and puts you at the start of Act 2.")]
[group("Workshop")]
[script]
rescue act:
    #!/usr/bin/env bash

    tag="act{{ act }}-start"
    if ! git rev-parse -q --verify "refs/tags/$tag" >/dev/null; then
        echo -e "{{ red }}No tag '$tag'. Run: git fetch --tags{{ nc }}" >&2
        exit 1
    fi
    echo -e "{{ green }}📦 Stashing your work as 'rescue-{{act}}' (nothing is deleted: git stash list){{ nc }}"
    git stash push --include-untracked -m "rescue-{{ act }}" >/dev/null || true
    git checkout -q -B rescue "$tag"
    echo -e "{{ green }}📦 Syncing{{ nc }}"
    uv sync
    echo -e "{{ green }}✓ You are at the start of Act {{ act }}. Follow along.{{ nc }}"
