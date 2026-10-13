# /// script
# requires-python = ">=3.12"
# dependencies = ["jinja2>=3.1"]
# ///
"""Scaffold a workspace member from templates/member.

Usage: new_member.py <root> <kind>/<dir_name> [--description TEXT] [--depends a,b]

Every file under templates/member is rendered with Jinja. Paths are templated
too (`{{ module }}` in a directory name), and a `.jinja` suffix is dropped.
"""

import argparse
import datetime as dt
import pathlib
import re
import sys

import jinja2


def main() -> None:
    """Scaffold a workspace member from templates/member."""
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=pathlib.Path)
    parser.add_argument("target", help="e.g. services/pizza_stats")
    parser.add_argument("--description", default="")
    parser.add_argument("--depends", default="", help="comma-separated workspace package names")
    args = parser.parse_args()

    target = pathlib.Path(args.target)
    if len(target.parts) != 2 or target.parts[0] not in {"apps", "libs", "services"}:
        sys.exit("target must look like apps/<name>, libs/<name> or services/<name>")
    kind, module = target.parts
    if not re.fullmatch(r"[a-z][a-z0-9_]*", module):
        sys.exit(f"'{module}' must be a valid python module name (snake_case)")

    dest = args.root / target
    if dest.exists():
        sys.exit(f"{dest} already exists")

    context = {
        "kind": kind,
        "module": module,
        "name": module.replace("_", "-"),
        "description": args.description or f"The {module.replace('_', ' ')} member",
        "depends": [d.strip() for d in args.depends.split(",") if d.strip()],
        "today": dt.date.today().isoformat(),  # noqa: DTZ011
    }

    template_root = args.root / "templates" / "member"
    if not template_root.is_dir():
        sys.exit(f"{template_root} not found; is {args.root} the repo root?")
    env = jinja2.Environment(  # noqa: S701
        loader=jinja2.FileSystemLoader(template_root),
        keep_trailing_newline=True,
        undefined=jinja2.StrictUndefined,
    )

    created: list[pathlib.Path] = []
    for src in sorted(p for p in template_root.rglob("*") if p.is_file()):
        rel = src.relative_to(template_root)
        rendered_rel = pathlib.Path(env.from_string(str(rel)).render(context))
        if rendered_rel.suffix == ".jinja":
            rendered_rel = rendered_rel.with_suffix("")
        out = dest / rendered_rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(env.get_template(rel.as_posix()).render(context), encoding="utf-8")
        created.append(out.relative_to(args.root))

    for path in created:
        print(f"  + {path}")


if __name__ == "__main__":
    main()
