from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".git"}
EXCLUDED_NAMES = {".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc", ".zip"}


def include(path: Path) -> bool:
    if set(path.parts) & EXCLUDED_PARTS:
        return False
    if path.name in EXCLUDED_NAMES:
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Package pgsa-harness as a GitHub-ready zip.")
    parser.add_argument("--source", default=".", help="pgsa-harness repository root")
    parser.add_argument("--output", required=True, help="zip output path")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    root_name = "pgsa-harness"
    output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file() or not include(path.relative_to(source)):
                continue
            archive.write(path, Path(root_name) / path.relative_to(source))

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
