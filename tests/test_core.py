"""Core runtime and visualization contract tests for Double-digits."""

from __future__ import annotations

from dd_core.constants import ARITHMETIC_SCENE_SIZE, DIGIT_SIZE, DOUBLE_SCENE_SIZE
from dd_core.examples import ExampleCatalog, get_results
from dd_models.baselines import BaselineRuntime
from dd_visuals.explain import build_visualization


def test_examples_have_expected_shapes():
    catalog = ExampleCatalog()
    single = catalog.example_from_id("single", "single_3")
    double = catalog.example_from_id("double", "double_12")
    arithmetic = catalog.example_from_id("arithmetic", "arith_add_37")
    assert single.image.shape == DIGIT_SIZE
    assert double.image.shape == DOUBLE_SCENE_SIZE
    assert arithmetic.image.shape == ARITHMETIC_SCENE_SIZE


def test_controlled_arithmetic_results():
    assert get_results(3, 7, "add")["result"] == 10
    assert get_results(7, 3, "subtract")["result"] == 4
    assert get_results(6, 7, "multiply")["result"] == 42


def test_baseline_runtime_infers_across_levels(tmp_path):
    runtime = BaselineRuntime(models_dir=str(tmp_path / "models"), cache_artifact=True)
    single = runtime.examples.example_from_id("single", "single_7")
    double = runtime.examples.example_from_id("double", "double_56")
    arithmetic = runtime.examples.example_from_id("arithmetic", "arith_mul_34")

    single_result = runtime.infer_from_example(single)
    double_result = runtime.infer_from_example(double)
    arithmetic_result = runtime.infer_from_example(arithmetic)

    assert 0 <= single_result.prediction["digit"] <= 9
    assert 0 <= double_result.prediction["value"] <= 99
    assert arithmetic_result.prediction["operator"] in {"add", "subtract", "multiply"}
    assert arithmetic_result.result_image_uri is not None


def test_visualization_payloads_have_expected_sections(tmp_path):
    runtime = BaselineRuntime(models_dir=str(tmp_path / "models"), cache_artifact=False)
    example = runtime.examples.example_from_id("double", "double_27")
    inference = runtime.infer_from_example(example)
    feature_maps = build_visualization("feature_maps", runtime=runtime, inference=inference)
    prototype = build_visualization("prototype", runtime=runtime, inference=inference)
    comparison = build_visualization("comparison", runtime=runtime, inference=inference)
    assert feature_maps["kind"] == "feature_maps"
    assert feature_maps["items"]
    assert prototype["kind"] == "prototype"
    assert prototype["items"]
    assert comparison["kind"] == "comparison"
    assert comparison["items"]
