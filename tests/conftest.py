from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dd_web import create_app


@pytest.fixture
def app(tmp_path: Path):
    app = create_app(
        {
            "TESTING": True,
            "DOUBLEDIGITS_MODELS_DIR": str(tmp_path / "models"),
            "DOUBLEDIGITS_DATA_DIR": str(tmp_path / "data"),
            "DOUBLEDIGITS_ARTIFACT_CACHE": True,
        }
    )
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
