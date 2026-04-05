"""Command-line entrypoint re-export for Double-digits.

``python -m dd_cli`` is the canonical shell-neutral interface for maintainers
who need to inspect data, browse examples, run inference, export artifacts, or
train notebook-derived presets outside the web UI.
"""

from dd_cli.app import main

__all__ = ["main"]
