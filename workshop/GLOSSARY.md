# 📖 Glossary

Every term, config key, flag and recipe you meet in this workshop, in one place.
Grouped by where you meet it, alphabetical within each group.

---

## 🧠 Concepts

| Term | Meaning |
|---|---|
| **Borrowed config** 🫣 | A member's tests pass only because *another* member's environment is loaded into the same process. Act 1: the client lived on the map's `PIZZA_SOURCE`. |
| **Borrowed coverage** 🫣 | A member looks well tested only because *another* member's tests run its code in the same process. Coverage records which lines ran, not which test ran them. Act 2. |
| **Dependency confusion** 🔒 | A package name you use privately also exists on a public index, and the public one gets installed instead. Install, import and call all succeed: you are running a stranger's code. Act 3. |
| **Deployable** 🚀 | Something you actually ship and run: an app, a container, a job. A monorepo holds many. In this repo: `apps/*`. |
| **Editable install** ✏️ | The package is installed as a pointer to its source folder, so code changes are live without reinstalling. Workspace members are editable by default. |
| **Lockfile** 🔒 | `uv.lock`: the exact resolved version of every package, for every platform and Python version the workspace supports. One per workspace. Commit it. |
| **Member** 🎷 | A project inside the workspace with its own `pyproject.toml`, version, tests and build. Shares the root's lockfile, venv and config. |
| **Monolith** 🗿 | One codebase, **one** deployable. |
| **Monorepo** 🏢 | One repository, **many** deployables that live together. Not a monolith. |
| **Path dependency** 🏡 | A local package referenced by path (`{ path = "..." }`) that is *not* a member. You still develop it locally, but the workspace doesn't govern it. Act 3's "neighbour". |
| **Polyrepo** 🌪️ | One repository per project. Independent by default; sharing code means publishing and upgrading packages. |
| **Ports and adapters** 🔌 | Hexagonal architecture. Business code depends on an interface (the port, `PizzeriaSource`), and adapters (`FixturePizzeriaSource`, `HttpPizzeriaSource`) plug into it. |
| **Resolution** 🧩 | Finding one set of versions that satisfies every requirement at once. In a workspace, uv resolves **all members together**. If no such set exists, you get the Act 1 error. |
| **Resolution split** 🔀 | uv resolves separately per Python version and platform you claim to support (`python_full_version >= '3.15' and sys_platform == 'win32'`). It refuses to write a lockfile that would be wrong on any of them. |
| **src layout** 🗂️ | Code lives in `src/<package>/`, tests next to it in `tests/`. Stops you importing your package before it is installed. |
| **Virtual root** 🎼 | A workspace root that builds and ships nothing (`package = false`). It only declares the members and holds shared config. The conductor. |
| **Wheel** 🛞 | The built, installable package (`.whl`). A member's wheel *requires* its siblings, it never contains them. |
| **Workspace** 🎻 | uv's way to manage several projects in one repo: one root, many members, one lockfile, one venv. |

---

## ⚙️ Root `pyproject.toml`

| Key | Meaning |
|---|---|
| `[dependency-groups] dev` 🧰 | Development tools (pytest, ruff, mypy, deptry, ...) installed for everyone, shipped by nobody. Dev tools at the root, production dependencies in the members. |
| `[tool.coverage.report] fail_under` 📊 | The coverage gate, here 90%. pytest-cov applies it to **each** per-member run, and to the combined report. |
| `[tool.pytest]` 🧪 | Shared pytest config for every member (pytest 9+; older versions use `[tool.pytest.ini_options]`). |
| `[tool.pytest_env] env_files` ⚠️ | pytest-env setting that loads `.env` files into the test process. Listing every member's `vars.env` merges them into one environment, last file wins. The source of Act 1's leak, removed in Act 2. |
| `[tool.ruff]`, `[tool.mypy]` 🧹 | Lint and type config, defined once at the root and applied to every member. |
| `[tool.uv]` 🔧 | Workspace-wide uv settings. |
| `[tool.uv] constraint-dependencies` 🛡️ | Version rules for packages that **someone else** brings in. Never adds a package, only limits which versions are allowed. Act 3: `["urllib3>=2.8.0"]` fixes a CVE for every member in one line. |
| `[tool.uv] exclude-newer` ⏳ | Ignore anything published to PyPI after this date. Pin it to a timestamp and every laptop resolves the same snapshot. |
| `[tool.uv] package = false` 🎼 | Makes the root virtual: no build, no wheel, no `[build-system]` needed. |
| `[tool.uv] required-version` 📌 | Which uv versions may work on this repo. An outdated uv fails loudly instead of acting differently. |
| `[tool.uv.audit]` 🔍 | Settings for `uv audit`. `ignore` for findings that can't reach you (add a comment saying why), `ignore-until-fixed` for findings with no upstream fix yet. |
| `[tool.uv.index]` 🏪 | Extra package indexes. With `explicit = true`, an index is only used for packages that name it in `[tool.uv.sources]`: the dependency confusion fix. |
| `[tool.uv.workspace] members` 🎻 | Globs of the folders that are members (`apps/*`, `libs/*`, `services/*`). A new folder matching a glob joins automatically. |
| `[tool.uv.workspace] exclude` 🚪 | Folders that match a glob but are *not* members. Step one of taking a member out. |

---

## 📦 Member `pyproject.toml`

| Key | Meaning |
|---|---|
| `[build-system]` 🏗️ | How this member becomes a wheel. Here `uv_build`, uv's own fast backend. Hatchling and setuptools work too, and members can mix backends. |
| `[project] dependencies` 📋 | **What** this member needs at runtime. Siblings are listed exactly like PyPI packages (`"pizza-shared"`). |
| `[project] requires-python` 🐍 | Python versions this member supports. In a workspace, the lockfile uses the **intersection** over all members: one member requiring 3.13 moves everyone to 3.13. |
| `[project] version` 🏷️ | This member's own version. Members version independently. |
| `[tool.bumpversion]` 🔖 | bump-my-version config: which files to update and the per-member tag format (`pizza-client/v{new_version}`). |
| `[tool.deptry]` 🧐 | deptry config. `DEP002`: declared but never imported. `DEP003`: imported but only available transitively. |
| `[tool.uv.sources]` 🗺️ | **Where** to get a dependency. `dependencies` says what, `sources` says where: two halves of one idea. |
| `{ workspace = true }` ✨ | Source: take it from the workspace member with this name. Required for every sibling, and uv refuses anything else while the package is a member. |
| `{ path = "...", editable = true }` 🏡 | Source: a local folder that is not a member. |
| `{ index = "internal" }` 🏪 | Source: only from this named index. |

---

## 📄 Per-member files

| File | Meaning |
|---|---|
| `CHANGELOG.md` 📝 | Needs an `[Unreleased]` section before a release. `just check-changelog` enforces it. |
| `py.typed` 🏷️ | Marker file: "this package ships type hints". Lets mypy check calls into this member from other members. |
| `release_scope.env` 🎚️ | `RELEASE=patch`, `minor` or `major`: what the next `just bump` will do. |
| `tests/vars.env` 🌱 | This member's test environment. `just test` loads only this file for this member. |

---

## ⌨️ uv commands and flags

| Command / flag | Meaning |
|---|---|
| `uv audit` 🔍 | Checks every locked package against known vulnerabilities (preview feature). |
| `uv build --package X` 🛞 | Builds member X into a wheel. |
| `uv lock` 🔒 | Resolves the whole workspace and writes `uv.lock`. Fails if members contradict each other. |
| `uv lock --check` ✅ | Fails if `uv.lock` is out of date. |
| `uv lock --upgrade-package X` ⬆️ | Upgrades one package for every member at once. |
| `uv run` ▶️ | Runs a command in the workspace venv. **Locks and syncs first**, unless told otherwise. |
| `uv sync` 🔄 | Makes `.venv` match `uv.lock` (locking first if needed). |
| `uv tree` 🌳 | Shows the dependency graph. `--package X` for one member, `--invert --package X` for "who depends on X?". |
| `--all-packages` 🎻 | Act on every member, not just the root. |
| `--env-file` 🌱 | Load environment variables from a file for this run. |
| `--frozen` 🧊 | Use `uv.lock` as it is, without checking it against the pyproject files. |
| `--locked` 🔒 | Use `uv.lock`, and **fail** if it is out of date. Preferred in CI and Docker. |
| `--no-dev` 🚫 | Leave out development dependency groups. Used in Docker. |
| `--no-editable` 🧱 | Install members as real wheels instead of pointers to source. Used in Docker. |
| `--no-install-workspace` 📦 | Install third-party dependencies only, not the members. Used for Docker layer caching. |
| `--no-sync` ⏭️ | Don't sync before running (implies `--frozen`). Lets tools run while the workspace doesn't resolve. |
| `--package X` 🎯 | Act on member X and only what it needs. |
| `--directory X` 📂 | Run from folder X. Not the same as `--package`: it changes the working directory, so root config may no longer be found. |

---

## 🧰 Recipes (`just --list` shows all)

| Recipe | Meaning |
|---|---|
| `just setup` 🚀 | Sync the workspace and create `.env` from `.env.example`. |
| `just run` 🗺️ | Start the Streamlit map. |
| `just show` 👀 | List members, modules and deployables. |
| `just new-member <dir> --depends a,b` 🏗️ | Scaffold a member from `templates/member`. |
| `just test [dirs]` 🧪 | Every member (or the given ones) in its own process, in parallel, with its own `vars.env` and coverage gate, then a combined report. |
| `just test-member <dir>` 🧪 | One member. Refuses a member without tests. |
| `just check` ✅ | The whole gate: format, lock, lint, types, deps, release info, tests. |
| `just check-deps` 🧐 | deptry per member. |
| `just show-metadata <dir>` 🧾 | Build a member's wheel and print its `Requires-Dist` lines. |
| `just bump <dir> [--dry-run]` 🏷️ | Bump one member's version from its `release_scope.env`, commit and tag it. |
| `just changed-members` / `affected-members` 🔎 | Members changed since their last tag / plus everything that depends on them. |
| `just audit-uv` 🔍 | `uv audit` on the lockfile. |
| `just audit-blame <pkg>` 🔎 | Which members pull in this package. |
| `just build` / `build-image <dir> <tag>` 🐳 | Container images per deployable, tagged with the member version. |
| `just compose` 🐳 | Run the stack locally. |
| `just rescue <n>` 🛟 | Stash your work and jump to the start of act n. |

---

## 🛠️ Other tools

| Tool | Meaning |
|---|---|
| **bump-my-version** 🔖 | Bumps version numbers in files, commits and tags. |
| **coverage / pytest-cov** 📊 | Measures which lines ran during tests. |
| **deptry** 🧐 | Checks that imports and declared dependencies match. Compares **names**, never versions. |
| **just** ⚡ | Command runner. One set of recipes for your terminal, your hooks and your CI. Installed with `uv tool install rust-just`. |
| **mypy** 🔎 | Static type checker. |
| **pytest-env** 🌱 | pytest plugin that sets environment variables from config. |
| **ruff** 🧹 | Linter and formatter. |
| **Streamlit** 🎈 | The Python web framework the map is built with. |
| **testcontainers** 🧪 | Starts real services (Postgres, ...) in Docker from inside your tests. The "what's next" for integration tests. |
