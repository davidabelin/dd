"""Filesystem export helpers for Double-digits artifacts.

This module owns the stable on-disk contracts used by maintainer workflows:
generated example bundles and exported visualization images. The CLI is the
primary caller, but the exported shapes and filenames are part of the broader
maintainer documentation because downstream scripts may consume them directly.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd

from dd_core.constants import ARITHMETIC_LEVEL, DOUBLE_LEVEL, SINGLE_LEVEL
from dd_core.examples import Example
from dd_core.render import data_uri_to_png_bytes, write_png


def target_name_for_level(level: str) -> str:
    """Return the canonical target name for one generated batch level."""

    normalized = str(level).strip().lower()
    if normalized == SINGLE_LEVEL:
        return "digit"
    if normalized == DOUBLE_LEVEL:
        return "value"
    if normalized == ARITHMETIC_LEVEL:
        return "result"
    raise ValueError(f"Unsupported level: {level}")


def target_value_for_example(example: Example) -> int:
    """Return the canonical numeric target value for one exported example."""

    target_name = target_name_for_level(example.level)
    return int(example.metadata[target_name])


def export_example_batch(examples: Sequence[Example], out_dir: str | Path) -> dict[str, Any]:
    """Write one generated example batch as images, manifest CSV, and an NPZ bundle."""

    if not examples:
        raise ValueError("Expected at least one generated example to export.")

    output_dir = Path(out_dir)
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    images: list[np.ndarray] = []
    targets: list[int] = []
    ids: list[str] = []
    metadata_json: list[str] = []

    for index, example in enumerate(examples):
        filename = f"{index:04d}_{slugify(example.id)}.png"
        image_path = write_png(example.image, images_dir / filename, scale=1, cmap=example.display_cmap)
        target = target_value_for_example(example)
        metadata_text = json.dumps(example.metadata, sort_keys=True)

        row = {
            "row_index": index,
            "id": example.id,
            "level": example.level,
            "title": example.title,
            "filename": filename,
            "path": str(image_path),
            "target": target,
            "target_name": target_name_for_level(example.level),
            "explanation": example.explanation,
            "image_height": int(example.image.shape[0]),
            "image_width": int(example.image.shape[1]),
            "metadata_json": metadata_text,
        }
        row.update(example.metadata)
        rows.append(row)
        images.append(np.array(example.image, copy=True))
        targets.append(target)
        ids.append(example.id)
        metadata_json.append(metadata_text)

    manifest = pd.DataFrame(rows)
    manifest_path = output_dir / "manifest.csv"
    manifest.to_csv(manifest_path, index=False)

    dataset_path = output_dir / "dataset.npz"
    np.savez_compressed(
        dataset_path,
        images=np.stack(images, axis=0),
        targets=np.asarray(targets, dtype=np.int64),
        ids=np.asarray(ids, dtype=str),
        metadata_json=np.asarray(metadata_json, dtype=str),
    )

    return {
        "level": examples[0].level,
        "count": len(examples),
        "out_dir": str(output_dir),
        "images_dir": str(images_dir),
        "manifest_path": str(manifest_path),
        "dataset_path": str(dataset_path),
        "target_name": target_name_for_level(examples[0].level),
        "image_shape": list(images[0].shape),
        "files": [str(path) for path in sorted(images_dir.glob("*.png"))],
        "columns": list(manifest.columns),
    }


def export_visualization_payload(kind: str, payload: dict[str, Any], out_dir: str | Path) -> dict[str, Any]:
    """Write one visualization payload to disk as a directory of PNG files."""

    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    files: list[dict[str, Any]] = []
    normalized = str(kind or payload.get("kind", "")).strip().lower()

    if normalized == "feature_maps":
        for item in payload.get("items", []):
            segment = str(item.get("segment", "segment"))
            for feature in item.get("maps", []):
                name = str(feature.get("name", "map"))
                path = output_dir / f"{slugify(segment)}__{slugify(name)}.png"
                path.write_bytes(data_uri_to_png_bytes(str(feature["image_uri"])))
                files.append({"path": str(path), "label": f"{segment}:{name}", "type": "image"})
    elif normalized == "prototype":
        for index, item in enumerate(payload.get("items", [])):
            label = str(item.get("label", f"prototype-{index}"))
            image_path = output_dir / f"{index:02d}_{slugify(label)}.png"
            image_path.write_bytes(data_uri_to_png_bytes(str(item["image_uri"])))
            files.append({"path": str(image_path), "label": label, "type": "image"})
            coefficient_uri = item.get("coefficient_uri")
            if coefficient_uri:
                coefficient_path = output_dir / f"{index:02d}_{slugify(label)}__coefficient.png"
                coefficient_path.write_bytes(data_uri_to_png_bytes(str(coefficient_uri)))
                files.append({"path": str(coefficient_path), "label": f"{label} coefficient", "type": "coefficient"})
    elif normalized == "comparison":
        for index, item in enumerate(payload.get("items", [])):
            label = str(item.get("label", f"comparison-{index}"))
            path = output_dir / f"{index:02d}_{slugify(label)}.png"
            path.write_bytes(data_uri_to_png_bytes(str(item["image_uri"])))
            files.append({"path": str(path), "label": label, "type": "image"})
    else:
        raise ValueError(f"Unsupported visualization kind: {kind}")

    return {
        "kind": normalized,
        "out_dir": str(output_dir),
        "count": len(files),
        "files": files,
    }


def slugify(value: str) -> str:
    """Convert one arbitrary label into a filesystem-friendly slug."""

    text = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return text or "item"


def compact_example_summary(summary: dict[str, Any]) -> dict[str, Any]:
    """Strip image payloads from one example summary for concise CLI listing output."""

    return {
        "id": summary["id"],
        "level": summary["level"],
        "title": summary["title"],
        "metadata": summary["metadata"],
        "explanation": summary["explanation"],
    }


def summarize_examples(summaries: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build compact summaries for a sequence of example records."""

    return [compact_example_summary(summary) for summary in summaries]
