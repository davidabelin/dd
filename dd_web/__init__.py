"""Flask application factory and shared configuration helpers."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urljoin
from typing import Any

from flask import Flask, request, url_for

from dd_web.runtime import DoubleDigitsService


def _parse_bool(value: object) -> bool:
    """Interpret common string and numeric tokens as booleans."""

    if isinstance(value, bool):
        return value
    return str(value or "").strip() not in {"", "0", "false", "False", "no", "No"}


def _normalize_base_url(value: str) -> str:
    """Normalize the configured AIX hub base URL for footer/navigation links."""

    raw = str(value or "").strip()
    return raw or "/"


def _aix_page_url(base_url: str, path: str) -> str:
    """Build one AIX-owned page URL from the configured hub base URL."""

    base = _normalize_base_url(base_url)
    if base == "/":
        return path
    return urljoin(base.rstrip("/") + "/", path.lstrip("/"))


def default_app_config(root: Path | None = None) -> dict[str, Any]:
    """Build the default application config from the current environment."""

    project_root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    return {
        "AIX_HUB_URL": os.getenv("AIX_HUB_URL", "/"),
        "DOUBLEDIGITS_MODELS_DIR": os.getenv("DOUBLEDIGITS_MODELS_DIR", str(project_root / "models")),
        "DOUBLEDIGITS_DATA_DIR": os.getenv("DOUBLEDIGITS_DATA_DIR", str(project_root / "data")),
        "DOUBLEDIGITS_ARTIFACT_CACHE": _parse_bool(os.getenv("DOUBLEDIGITS_ARTIFACT_CACHE", "1")),
        "DOUBLEDIGITS_ALLOW_TRAINING": _parse_bool(os.getenv("DOUBLEDIGITS_ALLOW_TRAINING", "1")),
    }


def create_app(config: dict | None = None) -> Flask:
    """Create the standalone Double-digits Flask application."""

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_mapping(default_app_config())
    if config:
        app.config.update(config)

    app.config["DOUBLEDIGITS_ARTIFACT_CACHE"] = _parse_bool(app.config.get("DOUBLEDIGITS_ARTIFACT_CACHE", True))
    app.config["DOUBLEDIGITS_ALLOW_TRAINING"] = _parse_bool(app.config.get("DOUBLEDIGITS_ALLOW_TRAINING", True))

    app.extensions["dd_service"] = DoubleDigitsService(
        models_dir=str(app.config["DOUBLEDIGITS_MODELS_DIR"]),
        cache_artifact=bool(app.config["DOUBLEDIGITS_ARTIFACT_CACHE"]),
        allow_training=bool(app.config["DOUBLEDIGITS_ALLOW_TRAINING"]),
    )

    from dd_web.blueprints.api import api_bp
    from dd_web.blueprints.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_template_globals() -> dict[str, Any]:
        hub_url = _normalize_base_url(app.config.get("AIX_HUB_URL", "/"))
        mount_base = (request.script_root or "").rstrip("/")
        examples_url = url_for("api.list_examples")
        api_base = examples_url.rsplit("/examples", 1)[0]
        return {
            "aix_hub_url": hub_url,
            "aix_contact_url": _aix_page_url(hub_url, "/contact"),
            "aix_privacy_url": _aix_page_url(hub_url, "/privacy"),
            "aix_toc_url": _aix_page_url(hub_url, "/toc"),
            "dd_frontend_config": {
                "mountBase": mount_base,
                "apiBase": api_base,
            },
        }

    return app
