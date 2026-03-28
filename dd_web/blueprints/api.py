"""JSON endpoints for Double-digits examples, inference, and visualizations."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.get("/examples")
def list_examples():
    level = str(request.args.get("level", "single"))
    count = request.args.get("count")
    payload = current_app.extensions["dd_service"].list_examples(level=level, count=(int(count) if count else None))
    return jsonify(payload)


@api_bp.post("/infer")
def infer():
    payload = request.get_json(silent=True) or {}
    result = current_app.extensions["dd_service"].infer(payload)
    return jsonify(result)


@api_bp.get("/visualizations/<kind>")
def visualization(kind: str):
    payload = dict(request.args)
    result = current_app.extensions["dd_service"].visualization(kind, payload)
    return jsonify(result)
