"""Module entrypoint for ``python -m dd_cli``."""

from __future__ import annotations

import sys

from dd_cli.app import main


if __name__ == "__main__":
    raise SystemExit(main())
