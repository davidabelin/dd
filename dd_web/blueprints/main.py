"""HTML routes for the Double-digits standalone app."""

from __future__ import annotations

from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home() -> str:
    return render_template("pages/home.html", title="Double-digits")
