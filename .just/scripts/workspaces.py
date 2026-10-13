# /// script
# requires-python = ">=3.12"
# ///
"""Print workspace member paths from [tool.uv.workspace] in the root pyproject.toml.

Runs as a PEP 723 script in an isolated environment, so it keeps working when
the workspace itself cannot resolve. `just` stays usable while you fix it.
"""

import pathlib
import sys
import tomllib

root = pathlib.Path(sys.argv[1])
project_path = root / "pyproject.toml"
kind = sys.argv[2]

try:
    ws = tomllib.loads(project_path.read_text())["tool"]["uv"]["workspace"]
except tomllib.TOMLDecodeError as exc:
    sys.exit(f"{project_path} is not valid TOML: {exc}")
except KeyError as exc:
    sys.exit(f"{project_path} has no [tool.uv.workspace] table (missing {exc})")

excluded = set(ws.get("exclude", []))

members = sorted(
    p
    for pattern in ws["members"]
    for p in root.glob(pattern)
    if p.is_dir()
    and (p / "pyproject.toml").exists()
    and p.relative_to(root).as_posix() not in excluded
)

match kind:
    case "members":
        out = [p.relative_to(root).as_posix() for p in members]
    case "modules":
        out = [p.name for p in members]
    case "deployables":
        out = [p.relative_to(root).as_posix() for p in members if (p / "Dockerfile").exists()]
    case _:
        sys.exit(f"unknown kind: {kind}")

print(" ".join(out))
