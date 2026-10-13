# Versioning is per member: every member has its own version, changelog, release scope and git tag (<name>/v<version>).

[doc("List members that changed since their last release tag (<name>/v*).")]
[group("Versioning")]
[script]
changed-members:
    #!/usr/bin/env bash
    for project in {{ _members }}; do
        name="$({{ _just }} _meta "$project" name)"
        last_tag="$(git describe --tags --match "$name/v*" --abbrev=0 2>/dev/null || true)"
        if [[ -z "$last_tag" ]]; then
            echo "$project"
        elif git diff --name-only "$last_tag" HEAD -- "$project" ":(exclude)$project/release_scope.env" | grep -q .; then
            echo "$project"
        fi
    done


[doc("List members that are affected by changed members.")]
[group("Versioning")]
[script]
affected-members:
    #!/usr/bin/env bash
    changed="$({{ _just }} changed-members)"
    if [[ -z "$changed" ]]; then
        exit 0
    fi
    # Resolve a workspace package name to its member dir (empty if not a member), always returns 0
    dir_of_name() {
        local n="$1" dir name
        for dir in {{ _members }}; do
            name="$(grep -m1 '^name' "$dir/pyproject.toml" | sed -E 's/^name *= *"//; s/".*//')"
            if [[ "$name" == "$n" ]]; then
                echo "$dir"
                return 0
            fi
        done
        return 0
    }
    # List the workspace-member dirs that a member directly depends on from its [project] dependencies.
    deps_of_dir() {
        local dir="$1" block entry base d
        block="$(awk '/^dependencies *= *\[/{f=1;next} /^[[:space:]]*\]/{f=0} f{print}' "$dir/pyproject.toml")"
        while IFS= read -r entry; do
            base="$(sed -E 's/[][<>=!~ ].*//' <<<"$entry")"
            d="$(dir_of_name "$base")"
            if [[ -n "$d" ]]; then
                echo "$d"
            fi
        done < <(grep -oE '"[^"]+"' <<<"$block" | tr -d '"')
    }
    is_in() { grep -qxF "$1" <<<"$2"; }
    # Seed with directly-changed members, then mark a member affected whenever one of its deps is affected
    affected="$changed"
    progress=1
    while (( progress )); do
        progress=0
        for dir in {{ _members }}; do
            if is_in "$dir" "$affected"; then
                continue
            fi
            for d in $(deps_of_dir "$dir"); do
                if is_in "$d" "$affected"; then
                    affected="$affected"$'\n'"$dir"
                    progress=1
                    break
                fi
            done
        done
    done

    for dir in {{ _members }}; do
        if is_in "$dir" "$affected"; then
            echo "$dir"
        fi
    done


[doc("Bump one member from its release_scope.env, commit and tag it. Add --dry-run to look first.")]
[group("Versioning")]
[script]
bump member *args: (check-changelog member) (check-scope member)
    #!/usr/bin/env bash

    var="{{ _release_scope }}"
    source "{{ member }}/release_scope.env"
    scope="${!var:-}"

    echo -e "{{ green }}Bumping {{ member }} ($scope){{ nc }}"

    cur="$(uv run --no-sync --directory "{{ member }}" bump-my-version show current_version)"
    new="$(uv run --no-sync --directory "{{ member }}" bump-my-version show --increment "$scope" new_version)"
    name="$({{ _just }} _meta "{{ member }}" name)"
    echo -e "{{ green }}  $cur → $new{{ nc }}"

    # --no-sync: otherwise uv run rewrites uv.lock (the member version changed)
    # and dirties the tree, which makes bump-my-version refuse to commit.
    (cd "{{ member }}" && uv run --no-sync bump-my-version bump "$scope" {{ args }})

    if [[ " {{ args }} " == *" --dry-run "* ]]; then
        echo -e "{{ yellow }}Dry run: would tag ${name}/v${new}, nothing was changed{{ nc }}"
    else
        echo -e "{{ green }}Tagged: ${name}/v${new}{{ nc }}"
    fi
