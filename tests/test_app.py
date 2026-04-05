from __future__ import annotations

from werkzeug.test import Client
from werkzeug.wrappers import Response

from dd_web.serve import build_local_app


def test_home_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Single-digit Lab" in html
    assert "Two-digit Lab" in html
    assert "Arithmetic Lab" in html
    assert '"apiBase": "/api/v1"' in html
    assert "Comparison Strip" in html


def test_healthz_stays_lightweight(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["runtime_loaded"] is False


def test_presets_endpoint_returns_metadata(client):
    response = client.get("/api/v1/presets?level=double")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["level"] == "double"
    assert payload["default_preset"] == "double_project_modelx"
    assert payload["presets"]
    assert any(item["artifact_ready"] for item in payload["presets"])


def test_examples_endpoint_returns_curated_examples(client):
    response = client.get("/api/v1/examples?level=double")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["level"] == "double"
    assert payload["examples"]
    assert payload["examples"][0]["image_uri"].startswith("data:image/png;base64,")


def test_infer_endpoint_supports_example_and_structured_payloads(client):
    example_response = client.post(
        "/api/v1/infer",
        json={"level": "single", "example_id": "single_5", "preset": "single_mnist_dense"},
    )
    assert example_response.status_code == 200
    example_payload = example_response.get_json()
    assert example_payload["level"] == "single"
    assert example_payload["preset"] == "single_mnist_dense"
    assert "prediction" in example_payload

    structured_response = client.post(
        "/api/v1/infer",
        json={"level": "arithmetic", "left": 8, "right": 4, "operator": "divide", "preset": "arithmetic_modelx"},
    )
    assert structured_response.status_code == 200
    structured_payload = structured_response.get_json()
    assert structured_payload["level"] == "arithmetic"
    assert structured_payload["preset"] == "arithmetic_modelx"
    assert "result_image_uri" in structured_payload


def test_visualization_endpoint_returns_payload(client):
    response = client.get("/api/v1/visualizations/prototype?level=single&example_id=single_1&preset=single_mnist_dense")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["kind"] == "prototype"
    assert payload["preset"] == "single_mnist_dense"
    assert payload["items"]

    comparison_response = client.get("/api/v1/visualizations/comparison?level=arithmetic&example_id=arith_mul_34")
    assert comparison_response.status_code == 200
    comparison_payload = comparison_response.get_json()
    assert comparison_payload["kind"] == "comparison"
    assert comparison_payload["items"]


def test_infer_rejects_mismatched_preset(client):
    response = client.post(
        "/api/v1/infer",
        json={"level": "single", "example_id": "single_5", "preset": "double_project_modelx"},
    )
    assert response.status_code == 400
    payload = response.get_json()
    assert "does not belong to level" in payload["error"]


def test_build_local_app_respects_app_base_path(monkeypatch):
    monkeypatch.setenv("APP_BASE_PATH", "/doubledigits")
    app = build_local_app({"TESTING": True})
    client = Client(app, Response)

    home_response = client.get("/doubledigits/")
    assert home_response.status_code == 200
    home_html = home_response.get_data(as_text=True)
    assert '"mountBase": "/doubledigits"' in home_html
    assert '"apiBase": "/doubledigits/api/v1"' in home_html

    examples_response = client.get("/doubledigits/api/v1/examples?level=single")
    assert examples_response.status_code == 200

    health_response = client.get("/doubledigits/healthz")
    assert health_response.status_code == 200
