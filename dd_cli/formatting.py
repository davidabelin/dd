"""Formatting helpers for Double-digits CLI commands."""

from __future__ import annotations

import json
from typing import Any


def dump_json(payload: Any) -> str:
    """Serialize one CLI payload as stable indented JSON."""

    return json.dumps(payload, indent=2, sort_keys=True)


def format_example_list(payload: dict[str, Any]) -> str:
    """Render one example-list payload for terminal display."""

    lines = [f"Level: {payload['level']}", f"Examples: {payload['count']}"]
    for example in payload["examples"]:
        lines.append(f"- {example['id']}: {example['title']} | {_format_metadata(example['metadata'])}")
    return "\n".join(lines)


def format_example_detail(payload: dict[str, Any]) -> str:
    """Render one example-detail payload for terminal display."""

    example = payload["example"]
    lines = [
        f"Level: {payload['level']}",
        f"ID: {example['id']}",
        f"Title: {example['title']}",
        f"Shape: {payload['image_shape'][0]}x{payload['image_shape'][1]}",
        f"Metadata: {_format_metadata(example['metadata'])}",
        f"Explanation: {example['explanation']}",
    ]
    return "\n".join(lines)


def format_dataset_detail(payload: dict[str, Any]) -> str:
    """Render one raw-MNIST dataset sample payload for terminal display."""

    lines = [
        f"Split: {payload['split']}",
        f"Index: {payload['index']}",
        f"Label: {payload['digit']}",
        f"Shape: {payload['image_shape'][0]}x{payload['image_shape'][1]}",
    ]
    if payload.get("output_path"):
        lines.append(f"PNG: {payload['output_path']}")
    return "\n".join(lines)


def format_generation(payload: dict[str, Any]) -> str:
    """Render one batch-generation summary for terminal display."""

    return "\n".join(
        [
            f"Generated {payload['count']} {payload['level']} examples",
            f"Images: {payload['images_dir']}",
            f"Manifest: {payload['manifest_path']}",
            f"Arrays: {payload['dataset_path']}",
            f"Target column: {payload['target_name']}",
        ]
    )


def format_inference(payload: dict[str, Any]) -> str:
    """Render one inference payload for terminal display."""

    lines = [
        f"Level: {payload['level']}",
        f"Example: {payload['example']['title']} ({payload['example']['id']})",
        f"Preset: {payload['preset']}",
        f"Prediction: {_prediction_text(payload['prediction'])}",
        f"Confidence: {payload['confidence']:.4f}",
        f"Explanation: {payload['explanation']}",
    ]
    if payload.get("top_classes"):
        lines.append("Top classes:")
        for entry in payload["top_classes"]:
            lines.append(f"- {entry['label']}: {entry['p']:.4f}")
    if payload.get("result_image_uri"):
        lines.append("Result image: available in JSON output or the web app.")
    return "\n".join(lines)


def format_visualization(payload: dict[str, Any]) -> str:
    """Render one visualization payload for terminal display."""

    visualization = payload["visualization"]
    lines = [f"Level: {payload['level']}", f"Preset: {visualization['preset']}", f"Visualization: {visualization['kind']}"]
    if visualization["kind"] == "feature_maps":
        for item in visualization["items"]:
            lines.append(f"- {item['segment']}: {len(item['maps'])} maps")
    else:
        for item in visualization["items"]:
            lines.append(f"- {item['label']}")
    export = payload.get("export")
    if export:
        lines.append(f"Exported {export['count']} files to {export['out_dir']}")
    return "\n".join(lines)


def format_training_list(payload: dict[str, Any]) -> str:
    """Render the available training presets for terminal display."""

    lines = ["Training presets:"]
    for preset in payload["presets"]:
        lines.append(
            f"- {preset['name']} [{preset['level']}] "
            f"{preset['epochs']} epochs, batch {preset['batch_size']}, "
            f"train={preset['train_size']}, test={preset['test_size']}"
        )
    return "\n".join(lines)


def format_training_run(payload: dict[str, Any]) -> str:
    """Render one completed training run summary for terminal display."""

    lines = [
        f"Preset: {payload['preset']}",
        f"Level: {payload['level']}",
        f"Artifact: {payload['artifact_path']}",
    ]
    evaluation = payload.get("evaluation") or {}
    if evaluation:
        metrics = ", ".join(f"{key}={value:.4f}" for key, value in sorted(evaluation.items()))
        lines.append(f"Evaluation: {metrics}")
    return "\n".join(lines)


def _format_metadata(metadata: dict[str, Any]) -> str:
    """Render one metadata mapping as a stable comma-separated string."""

    parts = [f"{key}={value}" for key, value in sorted(metadata.items())]
    return ", ".join(parts)


def _prediction_text(prediction: dict[str, Any]) -> str:
    """Build a concise human-readable description for one prediction mapping."""

    if "digit" in prediction:
        return f"digit {prediction['digit']}"
    if "value" in prediction:
        return f"value {prediction['value']:02d} from {prediction['left_digit']} and {prediction['right_digit']}"
    return (
        f"{prediction['left_digit']} {prediction['operator_symbol']} {prediction['right_digit']} "
        f"= {prediction['result']}"
    )
