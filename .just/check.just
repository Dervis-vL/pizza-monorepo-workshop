[doc("Format and apply safe lint fixes (ruff).")]
[group("Quality Checks")]
fix *members=".":
    @echo "{{ green }}🔍 Ruff format + fix...{{ nc }}"
    {{ run }} ruff format {{ members }}
    {{ run }} ruff check {{ members }} --fix
    @echo "{{ green }}✓ All fixing done{{ nc }}"


[doc("Lint every member (ruff).")]
[group("Quality Checks")]
check-lint *members=".":
    @echo "{{ green }}🔍 Ruff check...{{ nc }}"
    {{ run }} ruff check {{ members }}
    {{ run }} ruff format --check {{ members }}
    @echo "{{ green }}✓ Lint passed.{{ nc }}"

[doc("Type check every member (mypy).")]
[group("Quality Checks")]
check-type *members=_modules:
    @echo "{{ green }}🔍 Type checking...{{ nc }}"
    {{ run }} mypy {{ prepend('-p ', members) }}
    @echo "{{ green }}✓ Types passed.{{ nc }}"


[doc("Check dependencies per member (deptry).")]
[group("Quality Checks")]
[script]
check-deps *members=_members:
    #!/usr/bin/env bash
    echo "{{ green }}🔍 Checking dependencies...{{ nc }}"
    for d in {{ members }}; do
        echo "→ $d"
        {{ run }} --directory "$d" deptry .
    done
    echo "{{ green }}✓ Dependencies are honest.{{ nc }}"


[doc("Check for stale lock files (uv).")]
[group("Quality Checks")]
check-lock:
    @echo "{{ green }}🔍 Checking lock files...{{ nc }}"
    uv lock --check
    @echo "{{ green }}✓ Lock files are up to date.{{ nc }}"


[doc("Fail unless the member's CHANGELOG.md has an [Unreleased] section.")]
[group("Quality Checks")]
[script]
check-changelog member:
    #!/usr/bin/env bash

    echo "{{ green }}🔍 Checking changelog...{{ nc }}"
    changelog="{{member}}/CHANGELOG.md"
    if [[ ! -f "$changelog" ]]; then
        echo "ERROR: $changelog not found"
        exit 1
    fi
    if ! grep -q '\[Unreleased\]' "$changelog"; then
        echo "ERROR: No [Unreleased] section in $changelog; add changelog entries before merging"
        exit 1
    fi
    echo "{{ green }}✓ [Unreleased] found in $changelog{{ nc }}"


[doc("Fail unless the member's release_scope.env says patch, minor or major.")]
[group("Quality Checks")]
[script]
check-scope member:
    #!/usr/bin/env bash

    echo "{{ green }}🔍 Checking release scope...{{ nc }}"
    var="{{ _release_scope }}"
    env_file="{{member}}/release_scope.env"
    if [[ ! -f "$env_file" ]]; then 
        echo -e "{{ red }}💥 $env_file not found{{ nc }}" >&2
        exit 1
    fi

    source "$env_file"
    scope="${!var:-}"
    if [[ ! "$scope" =~ ^(patch|minor|major)$ ]]; then
        echo -e "{{ red }}💥 SCOPE in $env_file must be patch, minor or major (got '${scope:-}'){{ nc }}" >&2
        exit 1
    fi
    echo -e "{{ green }}✓ $var=$scope in $env_file{{ nc }}"


[doc("Validate changelogs and release scopes for the affected (or given) projects.")]
[group("Quality Checks")]
[script]
check-release *members:
    #!/usr/bin/env bash

    echo "{{ yellow }}🔍 Checking release information...{{ nc }}"
    dirs=({{ members }})
    if [[ ${#dirs[@]} -eq 0 ]]; then
        while IFS= read -r line; do
            if [[ -n "$line" ]]; then
                dirs+=("$line")
            fi
        done < <({{ _just }} affected-members)
        echo "Affected members (changed + dependents):"
    else
        echo "Checking members:"
    fi

    if [[ ${#dirs[@]} -eq 0 ]]; then
        echo "No members changes detected; nothing to check"
        exit 0
    fi
    printf '%s\n' "${dirs[@]}"

    for member in "${dirs[@]}"; do
        {{ _just }} check-changelog "$member"
        {{ _just }} check-scope "$member"
    done
    echo "{{ yellow }}✓ Release information check passed for: ${dirs[*]}{{ nc }}"


[doc("The whole quality gate: fmt, lock, lint, types, deps, tests.")]
[group("Quality Checks")]
check: fix check-lock check-release check-lint check-type check-deps test
    @echo "{{ yellow }}👍 Quality gate passed{{nc}}"


[doc("Quality gate for changed members: fmt, lock, lint, types, deps, tests.")]
[group("Quality Checks")]
[script]
check-changed *members: check-lock
    #!/usr/bin/env bash
    echo "{{ green }}🔍 Checking changed members...{{ nc }}"
    dirs=({{ members }})
    if [[ ${#dirs[@]} -eq 0 ]]; then
        dirs=($({{ _just }} affected-members))
    fi

    if [[ ${#dirs[@]} -eq 0 ]]; then
        echo "{{ green }}✓ No changed members to check.{{ nc }}"
        exit 0
    fi

    echo "Checking: ${dirs[*]}"

    modules=("${dirs[@]##*/}")

    {{ _just }} check-release "${dirs[@]}"
    {{ _just }} fix "${dirs[@]}"
    {{ _just }} check-lint "${dirs[@]}"
    {{ _just }} check-type "${modules[@]}"
    {{ _just }} check-deps "${dirs[@]}"
    {{ _just }} test "${dirs[@]}"

    echo "{{ yellow }}👍 All checks passed for: ${dirs[*]}{{ nc }}"
