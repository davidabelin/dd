from __future__ import annotations


def test_home_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Single-digit Lab" in html
    assert "Two-digit Lab" in html
    assert "Arithmetic Lab" in html


def test_examples_endpoint_returns_curated_examples(client):
    response = client.get("/api/v1/examples?level=double")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["level"] == "double"
    assert payload["examples"]
    assert payload["examples"][0]["image_uri"].startswith("data:image/png;base64,")


def test_infer_endpoint_supports_example_and_structured_payloads(client):
    example_response = client.post("/api/v1/infer", json={"level": "single", "example_id": "single_5"})
    assert example_response.status_code == 200
    example_payload = example_response.get_json()
    assert example_payload["level"] == "single"
    assert "prediction" in example_payload

    structured_response = client.post(
        "/api/v1/infer",
        json={"level": "arithmetic", "left": 6, "right": 7, "operator": "multiply"},
    )
    assert structured_response.status_code == 200
    structured_payload = structured_response.get_json()
    assert structured_payload["level"] == "arithmetic"
    assert "result_image_uri" in structured_payload


def test_visualization_endpoint_returns_payload(client):
    response = client.get("/api/v1/visualizations/prototype?level=single&example_id=single_1")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["kind"] == "prototype"
    assert payload["items"]

    comparison_response = client.get("/api/v1/visualizations/comparison?level=arithmetic&example_id=arith_mul_34")
    assert comparison_response.status_code == 200
    comparison_payload = comparison_response.get_json()
    assert comparison_payload["kind"] == "comparison"
    assert comparison_payload["items"]
