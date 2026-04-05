"""CLI contract tests for Double-digits."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from PIL import Image

from dd_cli.app import main
import dd_cli.app as cli_app
from dd_web.runtime import DoubleDigitsService


@pytest.fixture
def cli_env(monkeypatch, tmp_path: Path, shared_models_dir: Path):
    monkeypatch.setenv("DOUBLEDIGITS_MODELS_DIR", str(shared_models_dir))
    monkeypatch.setenv("DOUBLEDIGITS_DATA_DIR", str(Path(__file__).resolve().parents[1] / "data"))
    monkeypatch.setenv("DOUBLEDIGITS_ARTIFACT_CACHE", "1")
    monkeypatch.setenv("DOUBLEDIGITS_ALLOW_TRAINING", "1")
    for level in ("SINGLE", "DOUBLE", "ARITHMETIC"):
        monkeypatch.setenv(f"DOUBLEDIGITS_TRAIN_SIZE_{level}", "64")
        monkeypatch.setenv(f"DOUBLEDIGITS_TEST_SIZE_{level}", "16")
        monkeypatch.setenv(f"DOUBLEDIGITS_EPOCHS_{level}", "1")
    return tmp_path


def test_cli_help_lists_commands(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "examples" in output
    assert "infer" in output
    assert "visualize" in output
    assert "serve" in output


def test_cli_rejects_incomplete_structured_input(cli_env, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["infer", "--level", "double", "--left", "4"])
    assert exc.value.code == 1
    error = capsys.readouterr().err
    assert "Provide --example-id or both --left and --right" in error


def test_examples_list_json(cli_env, capsys):
    assert main(["examples", "list", "--level", "single", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["level"] == "single"
    assert payload["count"] > 0
    assert "image_uri" not in payload["examples"][0]


def test_examples_show_text(cli_env, capsys):
    assert main(["examples", "show", "--level", "single", "--example-id", "single_5"]) == 0
    output = capsys.readouterr().out
    assert "single_5" in output
    assert "Busy five" in output


def test_examples_generate_writes_batch(cli_env, capsys, tmp_path: Path):
    out_dir = tmp_path / "generated"
    assert main(
        [
            "examples",
            "generate",
            "--level",
            "arithmetic",
            "--count",
            "4",
            "--out",
            str(out_dir),
            "--json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    manifest = pd.read_csv(payload["manifest_path"])
    dataset = np.load(payload["dataset_path"])
    first_image = np.array(Image.open(Path(payload["files"][0])), dtype=np.uint8)

    assert payload["count"] == 4
    assert list(manifest["target"]) == dataset["targets"].tolist()
    assert dataset["images"].shape[0] == 4
    assert first_image.shape[:2] == tuple(dataset["images"][0].shape)
    assert set(["id", "target", "target_name", "metadata_json"]).issubset(manifest.columns)


def test_infer_json(cli_env, capsys):
    assert main(
        ["infer", "--level", "single", "--example-id", "single_5", "--preset", "single_mnist_dense", "--json"]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["level"] == "single"
    assert payload["preset"] == "single_mnist_dense"
    assert 0 <= payload["prediction"]["digit"] <= 9


def test_visualize_json_matches_runtime_and_exports_files(cli_env, capsys, tmp_path: Path, shared_models_dir: Path):
    service = DoubleDigitsService(models_dir=str(shared_models_dir), cache_artifact=True, allow_training=False)
    expected = service.visualization(
        "comparison",
        {"level": "arithmetic", "example_id": "arith_mul_34", "preset": "arithmetic_modelx"},
    )
    out_dir = tmp_path / "visuals"

    assert main(
        [
            "visualize",
            "--kind",
            "comparison",
            "--level",
            "arithmetic",
            "--example-id",
            "arith_mul_34",
            "--preset",
            "arithmetic_modelx",
            "--write-dir",
            str(out_dir),
            "--json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["visualization"] == expected
    assert payload["export"]["count"] == len(list(out_dir.glob("*.png")))
    assert payload["visualization"]["kind"] == "comparison"
    assert payload["visualization"]["preset"] == "arithmetic_modelx"


def test_serve_command_invokes_local_runner(monkeypatch):
    called: dict[str, object] = {}

    def fake_run_local_server(*, host: str, port: int, debug: bool, config=None):
        called["host"] = host
        called["port"] = port
        called["debug"] = debug
        called["config"] = config
        return None

    monkeypatch.setattr(cli_app, "run_local_server", fake_run_local_server)
    assert main(["serve", "--host", "0.0.0.0", "--port", "5011", "--no-debug"]) == 0
    assert called == {"host": "0.0.0.0", "port": 5011, "debug": False, "config": None}
