"""Visualization payload builders for notebook-derived Double-digits scenes.

The model layer produces activations, class means, and weight maps. This module
packages those outputs into stable JSON-friendly structures used by the web API
and CLI export flows.
"""

from __future__ import annotations

from typing import Any

from dd_core.render import to_data_uri
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dd_models.baselines import BaselineRuntime, InferenceResult


VISUALIZATION_KINDS = ("feature_maps", "prototype", "comparison")


def build_visualization(kind: str, *, runtime: BaselineRuntime, inference: InferenceResult) -> dict[str, Any]:
    """Build one supported visualization payload.

    Parameters
    ----------
    kind : str
        Requested visualization family. Supported values are listed in
        ``VISUALIZATION_KINDS``.
    runtime : BaselineRuntime
        Shared runtime used to recover the classifier associated with the
        inference preset.
    inference : InferenceResult
        Canonical inference payload for the selected example.

    Returns
    -------
    dict[str, Any]
        JSON-friendly visualization payload consumed by the web API and CLI
        export flows.
    """

    normalized = str(kind or "feature_maps").strip().lower()
    classifier = runtime.classifier_for_level(inference.level, preset=inference.preset_name)

    if normalized == "feature_maps":
        return {
            "kind": normalized,
            "items": [
                {
                    "segment": "scene",
                    "maps": [
                        {"name": item["name"], "image_uri": to_data_uri(item["image"], cmap="viridis")}
                        for item in classifier.activation_maps(inference.input_image)
                    ],
                }
            ],
        }

    if normalized == "prototype":
        items: list[dict[str, Any]] = []
        if "digit" in inference.prediction:
            digit = int(inference.prediction["digit"])
            items.append(
                {
                    "label": f"MNIST mean {digit}",
                    "image_uri": to_data_uri(classifier.class_mean(digit), cmap="binary_r"),
                }
            )
        if "left_digit" in inference.prediction:
            left_digit = int(inference.prediction["left_digit"])
            items.append(
                {
                    "label": f"Left mean {left_digit}",
                    "image_uri": to_data_uri(classifier.class_mean(left_digit), cmap="binary_r"),
                }
            )
        if "right_digit" in inference.prediction:
            right_digit = int(inference.prediction["right_digit"])
            items.append(
                {
                    "label": f"Right mean {right_digit}",
                    "image_uri": to_data_uri(classifier.class_mean(right_digit), cmap="binary_r"),
                }
            )
        for item in classifier.first_layer_weight_maps(limit=6):
            items.append(
                {
                    "label": item["label"],
                    "image_uri": to_data_uri(item["image"], cmap="bone"),
                }
            )
        return {"kind": normalized, "items": items}

    if normalized == "comparison":
        items = [
            {
                "label": "generated scene",
                "image_uri": to_data_uri(inference.input_image, cmap="binary_r"),
            }
        ]
        for source in inference.example.comparison_sources:
            items.append(
                {
                    "label": str(source["label"]),
                    "image_uri": to_data_uri(source["image"], cmap=str(source.get("cmap", "binary_r"))),
                }
            )
        if inference.result_image_uri:
            items.append({"label": "predicted result", "image_uri": inference.result_image_uri})
        return {"kind": normalized, "items": items}

    raise ValueError(f"Unsupported visualization kind: {kind}")
