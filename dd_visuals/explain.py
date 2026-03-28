"""Visualization payload builders for Double-digits inference scenes."""

from __future__ import annotations

from typing import Any

import numpy as np

from dd_core.constants import DIGIT_SIZE, OPERATORS
from dd_core.render import to_data_uri
from dd_models.baselines import BaselineRuntime, InferenceResult


FILTERS = {
    "vertical": np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32),
    "horizontal": np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32),
    "diagonal": np.array([[2, 1, 0], [1, 0, -1], [0, -1, -2]], dtype=np.float32),
    "center": np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32),
}


def _convolve(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    padded = np.pad(image.astype(np.float32), 1, mode="edge")
    output = np.zeros_like(image, dtype=np.float32)
    for row in range(image.shape[0]):
        for col in range(image.shape[1]):
            patch = padded[row : row + 3, col : col + 3]
            output[row, col] = float(np.sum(patch * kernel))
    output -= output.min()
    max_value = float(output.max() or 1.0)
    output = (output / max_value) * 255.0
    return output.astype(np.uint8)


def feature_maps(image: np.ndarray) -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "image_uri": to_data_uri(_convolve(image, kernel)),
        }
        for name, kernel in FILTERS.items()
    ]


def build_visualization(kind: str, *, runtime: BaselineRuntime, inference: InferenceResult) -> dict[str, Any]:
    normalized = str(kind or "feature_maps").strip().lower()
    if normalized == "feature_maps":
        return {
            "kind": normalized,
            "items": [
                {
                    "segment": segment_name,
                    "maps": feature_maps(image),
                }
                for segment_name, image in inference.segments.items()
            ],
        }
    if normalized == "prototype":
        items = []
        if "digit" in inference.prediction:
            digit = int(inference.prediction["digit"])
            items.append(
                {
                    "label": f"Prototype {digit}",
                    "image_uri": to_data_uri(runtime.single_model.class_mean(digit)),
                    "coefficient_uri": to_data_uri(runtime.single_model.coefficient_map(digit)),
                }
            )
        if "left_digit" in inference.prediction:
            left_digit = int(inference.prediction["left_digit"])
            items.append(
                {
                    "label": f"Left prototype {left_digit}",
                    "image_uri": to_data_uri(runtime.single_model.class_mean(left_digit)),
                    "coefficient_uri": to_data_uri(runtime.single_model.coefficient_map(left_digit)),
                }
            )
        if "right_digit" in inference.prediction:
            right_digit = int(inference.prediction["right_digit"])
            items.append(
                {
                    "label": f"Right prototype {right_digit}",
                    "image_uri": to_data_uri(runtime.single_model.class_mean(right_digit)),
                    "coefficient_uri": to_data_uri(runtime.single_model.coefficient_map(right_digit)),
                }
            )
        if "operator" in inference.prediction:
            operator = str(inference.prediction["operator"])
            items.append(
                {
                    "label": f"Operator template {OPERATORS[operator]['symbol']}",
                    "image_uri": to_data_uri(runtime.operator_model.template(operator)),
                }
            )
        return {"kind": normalized, "items": items}
    if normalized == "comparison":
        items = []
        for name, image in inference.segments.items():
            items.append({"label": f"{name} input", "image_uri": to_data_uri(image)})
        if inference.result_image_uri:
            items.append({"label": "predicted result", "image_uri": inference.result_image_uri})
        return {"kind": normalized, "items": items}
    raise ValueError(f"Unsupported visualization kind: {kind}")
