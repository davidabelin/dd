"""Backward-compatible local entrypoint for the Double-digits Flask app."""

from dd_web.serve import build_local_app, run_local_server


app = build_local_app()


if __name__ == "__main__":
    run_local_server()
