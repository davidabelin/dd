"""Console-script bootstrap for ``python -m dd_cli``.

This wrapper keeps the process entrypoint small while routing all real command
construction and execution logic through ``dd_cli.app``.
"""

from __future__ import annotations

import sys

from dd_cli.app import main


if __name__ == "__main__":
    raise SystemExit(main())
