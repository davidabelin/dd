"""Shared helpers for local Flask serving and CLI integration."""

from __future__ import annotations

import os
from typing import Any

from flask import Flask

from dd_web import create_app


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5003
DEFAULT_DEBUG = True


class PathPrefixMiddleware:
    """Strip one configured URL prefix so routes work behind dispatch-style mounts."""

    def __init__(self, wsgi_app, prefix: str) -> None:
        self._app = wsgi_app
        self._prefix = "/" + str(prefix or "").strip().strip("/")

    def __call__(self, environ, start_response):
        """Forward one request after removing the configured prefix when present."""

        if self._prefix == "/":
            return self._app(environ, start_response)
        path_info = str(environ.get("PATH_INFO", "") or "")
        if path_info == self._prefix or path_info.startswith(self._prefix + "/"):
            environ["SCRIPT_NAME"] = self._prefix
            new_path = path_info[len(self._prefix) :]
            environ["PATH_INFO"] = new_path if new_path else "/"
        return self._app(environ, start_response)


def build_local_app(config: dict[str, Any] | None = None) -> Flask:
    """Create the local Flask app and apply any configured path prefix."""

    app = create_app(config)
    base_path = str(os.getenv("APP_BASE_PATH", "")).strip()
    if base_path:
        app.wsgi_app = PathPrefixMiddleware(app.wsgi_app, base_path)
    return app


def run_local_server(
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    debug: bool = DEFAULT_DEBUG,
    config: dict[str, Any] | None = None,
) -> Flask:
    """Run the local Flask development server and return the configured app."""

    app = build_local_app(config)
    app.run(host=host, port=int(port), debug=bool(debug))
    return app
