"""MNIST loading and sample-selection helpers for Double-digits."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path
from typing import Any

import numpy as np


def _bundled_mnist_path() -> Path:
    """Resolve the preferred on-disk MNIST archive path."""

    configured_dir = str(os.getenv("DOUBLEDIGITS_DATA_DIR", "")).strip()
    if configured_dir:
        return Path(configured_dir) / "mnist.npz"
    return Path(__file__).resolve().parents[1] / "data" / "mnist.npz"


def _load_mnist_arrays() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load raw MNIST arrays from the bundled archive or fall back to Keras."""

    archive_path = _bundled_mnist_path()
    if archive_path.exists():
        with np.load(archive_path, allow_pickle=False) as archive:
            return (
                np.asarray(archive["x_train"], dtype=np.uint8),
                np.asarray(archive["y_train"], dtype=np.int64),
                np.asarray(archive["x_test"], dtype=np.uint8),
                np.asarray(archive["y_test"], dtype=np.int64),
            )

    from dd_models.keras_backend import keras

    (train_images, train_labels), (test_images, test_labels) = keras.datasets.mnist.load_data()
    train_images = np.asarray(train_images, dtype=np.uint8)
    train_labels = np.asarray(train_labels, dtype=np.int64)
    test_images = np.asarray(test_images, dtype=np.uint8)
    test_labels = np.asarray(test_labels, dtype=np.int64)

    try:
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            archive_path,
            x_train=train_images,
            y_train=train_labels,
            x_test=test_images,
            y_test=test_labels,
        )
    except OSError:
        pass

    return train_images, train_labels, test_images, test_labels


@dataclass(frozen=True, slots=True)
class MnistRecord:
    """One resolved MNIST sample with split, index, label, and image data."""

    split: str
    index: int
    digit: int
    image: np.ndarray


def _group_indices(labels: np.ndarray) -> dict[int, np.ndarray]:
    """Group image indices by digit label for fast deterministic lookup."""

    return {
        digit: np.flatnonzero(labels == digit).astype(np.int32)
        for digit in range(10)
    }


@lru_cache(maxsize=1)
def load_digit_bank() -> dict[str, Any]:
    """Load the raw MNIST train/test splits and digit-wise lookup tables."""

    train_images, train_labels, test_images, test_labels = _load_mnist_arrays()
    combined_images = np.concatenate([train_images, test_images], axis=0)
    combined_labels = np.concatenate([train_labels, test_labels], axis=0)

    return {
        "train_images": train_images,
        "train_labels": train_labels,
        "test_images": test_images,
        "test_labels": test_labels,
        "train_by_digit": _group_indices(train_labels),
        "test_by_digit": _group_indices(test_labels),
        "class_means": {
            digit: combined_images[combined_labels == digit].mean(axis=0).astype(np.float32)
            for digit in range(10)
        },
    }


def normalize_images(images: np.ndarray) -> np.ndarray:
    """Scale one image array or image batch into the notebook 0..1 range."""

    return np.asarray(images, dtype=np.float32) / 255.0


def mnist_split(split: str = "test") -> tuple[np.ndarray, np.ndarray]:
    """Return one named MNIST split as ``(images, labels)`` arrays."""

    normalized = str(split or "test").strip().lower()
    bank = load_digit_bank()
    if normalized == "train":
        return bank["train_images"], bank["train_labels"]
    if normalized == "test":
        return bank["test_images"], bank["test_labels"]
    raise ValueError(f"Unsupported MNIST split: {split}")


def mnist_sample(index: int, *, split: str = "test") -> MnistRecord:
    """Return one MNIST sample resolved by absolute index within a split."""

    images, labels = mnist_split(split)
    actual_index = int(index) % len(images)
    return MnistRecord(
        split=str(split).strip().lower(),
        index=actual_index,
        digit=int(labels[actual_index]),
        image=np.array(images[actual_index], copy=True),
    )


def digit_variant_record(digit: int, variant_index: int = 0, *, split: str = "test") -> MnistRecord:
    """Return one deterministic digit sample chosen from a digit-specific bank."""

    target_digit = int(digit)
    normalized = str(split or "test").strip().lower()
    bank = load_digit_bank()
    if normalized == "train":
        images = bank["train_images"]
        labels = bank["train_labels"]
        by_digit = bank["train_by_digit"]
    elif normalized == "test":
        images = bank["test_images"]
        labels = bank["test_labels"]
        by_digit = bank["test_by_digit"]
    else:
        raise ValueError(f"Unsupported MNIST split: {split}")

    candidates = by_digit[target_digit]
    actual_index = int(candidates[int(variant_index) % len(candidates)])
    return MnistRecord(
        split=normalized,
        index=actual_index,
        digit=int(labels[actual_index]),
        image=np.array(images[actual_index], copy=True),
    )


def digit_variant(digit: int, variant_index: int = 0, *, split: str = "test") -> np.ndarray:
    """Return one digit image chosen deterministically by label and variant."""

    return digit_variant_record(digit, variant_index, split=split).image
