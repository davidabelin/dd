"""Flask application factory for the Double-digits guided lab."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urljoin

from flask import Flask

from dd_web.runtime import DoubleDigitsService


def _parse_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip() not in {"", "0", "false", "False", "no", "No"}


def _normalize_base_url(value: str) -> str:
    raw = str(value or "").strip()
    return raw or "/"


def _aix_page_url(base_url: str, path: str) -> str:
    base = _normalize_base_url(base_url)
    if base == "/":
        return path
    return urljoin(base.rstrip("/") + "/", path.lstrip("/"))


def create_app(config: dict | None = None) -> Flask:
    root = Path(__file__).resolve().parents[1]
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_mapping(
        AIX_HUB_URL=os.getenv("AIX_HUB_URL", "/"),
        DOUBLEDIGITS_MODELS_DIR=os.getenv("DOUBLEDIGITS_MODELS_DIR", str(root / "models")),
        DOUBLEDIGITS_DATA_DIR=os.getenv("DOUBLEDIGITS_DATA_DIR", str(root / "data")),
        DOUBLEDIGITS_ARTIFACT_CACHE=str(os.getenv("DOUBLEDIGITS_ARTIFACT_CACHE", "1")).strip() not in {"0", "false", "False"},
    )
    if config:
        app.config.update(config)

    app.config["DOUBLEDIGITS_ARTIFACT_CACHE"] = _parse_bool(app.config.get("DOUBLEDIGITS_ARTIFACT_CACHE", True))

    app.extensions["dd_service"] = DoubleDigitsService(
        models_dir=str(app.config["DOUBLEDIGITS_MODELS_DIR"]),
        cache_artifact=bool(app.config["DOUBLEDIGITS_ARTIFACT_CACHE"]),
    )

    from dd_web.blueprints.api import api_bp
    from dd_web.blueprints.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_template_globals() -> dict[str, str]:
        hub_url = _normalize_base_url(app.config.get("AIX_HUB_URL", "/"))
        return {
            "aix_hub_url": hub_url,
            "aix_contact_url": _aix_page_url(hub_url, "/contact"),
            "aix_privacy_url": _aix_page_url(hub_url, "/privacy"),
            "aix_toc_url": _aix_page_url(hub_url, "/toc"),
        }

    return app
