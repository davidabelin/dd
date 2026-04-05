"""Shared pytest fixtures for Double-digits web and model tests."""

from __future__ import annotations

from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dd_web import create_app


@pytest.fixture(scope="session")
def shared_models_dir(tmp_path_factory):
    """Provide a shared temp directory seeded with shipped model artifacts."""

    target = tmp_path_factory.mktemp("shared-models")
    source = ROOT / "models"
    for pattern in ("*.keras", "*.json"):
        for path in source.glob(pattern):
            shutil.copy2(path, target / path.name)
    return target


@pytest.fixture
def app(tmp_path: Path, shared_models_dir: Path, monkeypatch):
    """Build a test Flask app with tiny training overrides and seeded artifacts."""

    for level in ("SINGLE", "DOUBLE", "ARITHMETIC"):
        monkeypatch.setenv(f"DOUBLEDIGITS_TRAIN_SIZE_{level}", "64")
        monkeypatch.setenv(f"DOUBLEDIGITS_TEST_SIZE_{level}", "16")
        monkeypatch.setenv(f"DOUBLEDIGITS_EPOCHS_{level}", "1")
    app = create_app(
        {
            "TESTING": True,
            "DOUBLEDIGITS_MODELS_DIR": str(shared_models_dir),
            "DOUBLEDIGITS_DATA_DIR": str(ROOT / "data"),
            "DOUBLEDIGITS_ARTIFACT_CACHE": True,
        }
    )
    yield app


@pytest.fixture
def client(app):
    """Provide a Flask test client bound to the configured DD app."""

    return app.test_client()
