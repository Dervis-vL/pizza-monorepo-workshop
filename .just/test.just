# =============================================================================
# 🧪 Testing
#
# One lockfile, one venv, N isolated test processes.
#
# `test` syncs ONCE against the lockfile, then every member runs with
# --no-sync. That is the workspace dividend made operational:
#   - one resolution for the whole repo, asserted current (--locked)
#   - no member can drift to a different version of a shared dependency
#   - parallel members cannot race each other syncing the shared .venv
#
# Scoping is done by handing pytest the member's test path, NOT by
# `uv run --directory`. --directory would move cwd into the member and
# pytest and coverage would stop finding the ROOT config, which is exactly
# the single-standard property a monorepo is for.
#
# Parallel is the default. Pass --no-parallel to run them one at a time.
# =============================================================================

[doc("Test every workspace member; --no-parallel for sequential; pass pytest args, e.g. --integration.")]
[group("Quality Checks")]
[script]
test *args:
    #!/usr/bin/env bash

    # Split args into pytest flags and member directories
    parallel=true
    flags=()
    dirs=()
    for arg in {{ args }}; do
        case "$arg" in
            --no-parallel) parallel=false ;;
            -*)            flags+=("$arg") ;;
            *)             dirs+=("$arg") ;;
        esac
    done

    if [[ ${#dirs[@]} -eq 0 ]]; then
        dirs=({{ _members }})
    fi

    # Decide how many jobs
    cores="$(getconf _NPROCESSORS_ONLN 2>/dev/null || nproc 2>/dev/null || echo 1)"
    jobs="$cores"
    (( jobs > 4 )) && jobs=4
    (( jobs > ${#dirs[@]} )) && jobs=${#dirs[@]}
    (( jobs < 1 )) && jobs=1
    [[ "$parallel" == "false" ]] && jobs=1

    # One sync for whole workspace
    echo -e "{{ green }}🔗 Syncing workspace against uv.lock{{ nc }}"
    {{ uv }} sync --locked --all-packages

    rm -rf "{{ _cov_data }}"
    mkdir -p "{{ _cov_data }}"

    # Parallelism lives HERE
    failed=()

    if (( jobs <= 1 )); then
        echo -e "{{ green }}🧪 Testing {{ nc }}${#dirs[@]}{{ green }} member(s), one at a time{{ nc }}"
        for d in "${dirs[@]}"; do
            {{ _just }} test-member "$d" ${flags[@]+"${flags[@]}"} || failed+=("$d")
        done
    else
        echo -e "{{ green }}🧪 Testing {{ nc }}${#dirs[@]}{{ green }} member(s) across {{ nc }}${jobs}{{ green }} jobs{{ nc }}"
        logs="$(mktemp -d)"
        trap 'rm -rf "$logs"' EXIT

        # Batching rather than `wait -n`, which needs bash >= 4.3 and so is
        # missing on macos' /bin/bash 3.2.
        i=0
        for d in "${dirs[@]}"; do
            member="$(basename "$d")"
            (
                rc=0
                {{ _just }} test-member "$d" ${flags[@]+"${flags[@]}"} \
                    > "$logs/${member}.log" 2>&1 || rc=$?
                echo "$rc" > "$logs/${member}.rc"
            ) &
            i=$(( i + 1 ))
            (( i % jobs == 0 )) && wait
        done
        wait

        # Printed per member after the fact, because parallel output would
        # interleave and a failure could not be attributed.
        for d in "${dirs[@]}"; do
            member="$(basename "$d")"
            printf '\n═══ %s ═══\n' "$member"
            [[ -f "$logs/${member}.log" ]] && cat "$logs/${member}.log"
            rc="$(cat "$logs/${member}.rc" 2>/dev/null || echo 1)"
            if (( rc != 0 )); then
                failed+=("$d")
            fi
        done
        echo
    fi

    if (( ${#failed[@]} < ${#dirs[@]} )); then
        {{ _just }} coverage-report || failed+=("coverage")
    fi

    if (( ${#failed[@]} )); then
        echo -e "{{ red }}💥 Tests failed for: ${failed[*]}{{ nc }}" >&2
        exit 1
    fi

    echo -e "{{ yellow }}👍 All tests passed{{ nc }}"


[doc("Test one member, e.g. `just test-member services/pizza_client`.")]
[group("Quality Checks")]
[script]
test-member member *args:
    #!/usr/bin/env bash

    project="{{ member }}"
    member="$(basename "$project")"

    if [[ ! -d "$project/" ]]; then
        echo -e "{{ red }}💥 '$project' is not a workspace member directory...{{ nc }}" >&2
        exit 1
    fi

    # Runs with --no-sync
    if [[ ! -d ".venv" ]]; then
        echo -e "{{ red }}💥 No .venv found; run 'uv sync --locked' first{{ nc }}" >&2
        exit 1
    fi

    # Every member must carry tests. pytest alone would not catch this:
    # a test-less member collects nothing and exits zero 👻.
    if ! find "$project/tests" -name '__pycache__' -prune -o -name 'test_*.py' -print 2>/dev/null | grep -q .; then
        echo -e "{{ red }}💥 '$project' has no test_*.py files under tests/{{ nc }}" >&2
        exit 1
    fi

    # Only THIS member's env file is loaded
    env_args=()
    if [[ -f "$project/tests/vars.env" ]]; then
        env_args+=("--env-file" "$project/tests/vars.env")
    fi

    echo -e "{{ green }}🧪 Running tests for {{ nc }}${member}{{ nc }}"

    mkdir -p "{{ _cov_data }}"

    # One process per member: --cov only sees this member's module, and only
    # this member's tests exercise it. No borrowed coverage from siblings.
    COVERAGE_FILE="{{ _cov_data }}/${member}.coverage" \
    {{ run }} --no-sync ${env_args[@]+"${env_args[@]}"} \
        pytest "$project/tests" \
        {{ args }} \
        "--cov=$project/src" \
        "--junitxml=$project/test-report.xml"

    echo -e "{{ green }}✓ Tests passed for {{ nc }}${member}{{ nc }}"


[doc("Combine per-member coverage data into one report (coverage.xml for CI).")]
[group("Quality Checks")]
[script]
coverage-report:
    #!/usr/bin/env bash

    shopt -s nullglob
    data_files=("{{ _cov_data }}"/*.coverage)
    if (( ${#data_files[@]} == 0 )); then
        echo -e "{{ red }}💥 No coverage data found; run tests first{{ nc }}" >&2
        exit 1
    fi

    echo -e "{{ green }}📊 Combining coverage from {{ nc }}${#data_files[@]}{{ green }} member(s){{ nc }}"
    {{ run }} --no-sync coverage combine "${data_files[@]}"
    {{ run }} --no-sync coverage xml
    {{ run }} --no-sync coverage report
    echo -e "{{ green }}✓ Coverage meets threshold{{ nc }}"
