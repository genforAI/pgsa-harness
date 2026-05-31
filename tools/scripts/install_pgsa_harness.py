from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from pgsa_core.templates.initializer import init_pgsa


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize PGSA artifacts in a target repository.")
    parser.add_argument("target", help="target repository root")
    parser.add_argument("--force", action="store_true", help="overwrite existing PGSA scaffold files")
    args = parser.parse_args()
    written = init_pgsa(Path(args.target), force=args.force)
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
