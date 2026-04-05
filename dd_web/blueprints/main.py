"""HTML routes for the Double-digits app.

The same routes support standalone local usage and mounted AIX usage. The page
template depends on server-rendered navigation links and frontend config rather
than hard-coded route assumptions.
"""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home() -> str:
    """Render the Double-digits landing page."""

    return render_template("pages/home.html", title="Double-digits")


@main_bp.get("/healthz")
def healthz():
    """Return a lightweight health payload for the standalone DD app."""

    return jsonify(current_app.extensions["dd_service"].health())
