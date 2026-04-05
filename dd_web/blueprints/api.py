"""JSON endpoints for Double-digits examples, inference, and visualizations."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


def _json_error(exc: Exception, *, status: int):
    """Return a compact JSON error response for predictable frontend handling."""

    return jsonify({"error": str(exc)}), int(status)


@api_bp.get("/examples")
def list_examples():
    """Return curated example summaries for the requested level."""

    level = str(request.args.get("level", "single"))
    count = request.args.get("count")
    try:
        payload = current_app.extensions["dd_service"].list_examples(level=level, count=(int(count) if count else None))
        return jsonify(payload)
    except ValueError as exc:
        return _json_error(exc, status=400)


@api_bp.get("/presets")
def list_presets():
    """Return notebook-derived preset metadata for one level."""

    level = str(request.args.get("level", "single"))
    try:
        payload = current_app.extensions["dd_service"].list_presets(level=level)
        return jsonify(payload)
    except ValueError as exc:
        return _json_error(exc, status=400)


@api_bp.post("/infer")
def infer():
    """Run baseline inference for one posted example payload."""

    payload = request.get_json(silent=True) or {}
    try:
        result = current_app.extensions["dd_service"].infer(payload)
        return jsonify(result)
    except ValueError as exc:
        return _json_error(exc, status=400)
    except KeyError as exc:
        return _json_error(exc, status=404)
    except FileNotFoundError as exc:
        return _json_error(exc, status=409)
    except RuntimeError as exc:
        return _json_error(exc, status=409)


@api_bp.get("/visualizations/<kind>")
def visualization(kind: str):
    """Return one explanation or feature-visualization payload."""

    payload = dict(request.args)
    try:
        result = current_app.extensions["dd_service"].visualization(kind, payload)
        return jsonify(result)
    except ValueError as exc:
        return _json_error(exc, status=400)
    except KeyError as exc:
        return _json_error(exc, status=404)
    except FileNotFoundError as exc:
        return _json_error(exc, status=409)
    except RuntimeError as exc:
        return _json_error(exc, status=409)
