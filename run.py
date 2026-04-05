"""Backward-compatible local entrypoint for the Double-digits Flask app.

This module keeps the small ``run.py`` entrypoint expected by local development
and the App Engine ``run:app`` entrypoint while delegating the real app setup to
``dd_web.serve``.
"""

from dd_web.serve import build_local_app, run_local_server


app = build_local_app()


if __name__ == "__main__":
    run_local_server()
