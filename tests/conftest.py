from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dd_web import create_app


@pytest.fixture(scope="session")
def shared_models_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("shared-models")


@pytest.fixture
def app(tmp_path: Path, shared_models_dir: Path, monkeypatch):
    for level in ("SINGLE", "DOUBLE", "ARITHMETIC"):
        monkeypatch.setenv(f"DOUBLEDIGITS_TRAIN_SIZE_{level}", "64")
        monkeypatch.setenv(f"DOUBLEDIGITS_TEST_SIZE_{level}", "16")
        monkeypatch.setenv(f"DOUBLEDIGITS_EPOCHS_{level}", "1")
    app = create_app(
        {
            "TESTING": True,
            "DOUBLEDIGITS_MODELS_DIR": str(shared_models_dir),
            "DOUBLEDIGITS_DATA_DIR": str(tmp_path / "data"),
            "DOUBLEDIGITS_ARTIFACT_CACHE": True,
        }
    )
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
