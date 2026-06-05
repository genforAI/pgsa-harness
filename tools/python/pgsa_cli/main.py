from __future__ import annotations

from pgsa_cli import promote_shim
from pgsa_cli.cli import main


promote_shim.install()


if __name__ == "__main__":
    raise SystemExit(main())
