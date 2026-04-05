"""MNIST loading and sample-selection helpers for Double-digits.

Responsibility
--------------
Resolve raw MNIST data, prefer the bundled ``data/mnist.npz`` archive, and
expose deterministic sample-selection helpers that higher layers use to build
examples, scenes, class means, and training datasets.

Key dependencies
----------------
- ``numpy`` for array storage and transforms
- ``dd_models.keras_backend`` as a fallback loader when the bundled archive is
  absent

AIX relevance
-------------
The mounted AIX deployment relies on the same dataset contract as the
standalone app. In particular, lightweight example browsing should stay off the
live dataset-download path whenever ``data/mnist.npz`` is available.
"""

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
    """Load raw MNIST arrays.

    Returns
    -------
    tuple of numpy.ndarray
        ``(x_train, y_train, x_test, y_test)`` loaded from the bundled archive
        when available, otherwise from the Keras MNIST loader.

    Notes
    -----
    When the Keras fallback path is used, the function attempts to persist a
    compressed local archive for future lightweight reads. Failure to write that
    archive is non-fatal.
    """

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
    """One resolved MNIST sample.

    Attributes
    ----------
    split : str
        Source split name, normalized to ``"train"`` or ``"test"``.
    index : int
        Absolute sample index within the selected split.
    digit : int
        Ground-truth MNIST label in the ``0..9`` range.
    image : numpy.ndarray
        Unsigned ``28x28`` image array copied from the source split.
    """

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
    """Load the cached MNIST lookup bank.

    Returns
    -------
    dict[str, Any]
        Dictionary containing raw train/test arrays, per-digit index lookups
        for both splits, and cross-split MNIST class means used by the
        prototype views.
    """

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
    """Normalize images into the notebook ``0..1`` range.

    Parameters
    ----------
    images : numpy.ndarray
        One image or image batch stored in the notebook-style ``0..255``
        unsigned range.

    Returns
    -------
    numpy.ndarray
        Float32 array scaled into the ``0..1`` range.
    """

    return np.asarray(images, dtype=np.float32) / 255.0


def mnist_split(split: str = "test") -> tuple[np.ndarray, np.ndarray]:
    """Return one named MNIST split.

    Parameters
    ----------
    split : str, default="test"
        Requested split name.

    Returns
    -------
    tuple[numpy.ndarray, numpy.ndarray]
        ``(images, labels)`` arrays for the requested split.
    """

    normalized = str(split or "test").strip().lower()
    bank = load_digit_bank()
    if normalized == "train":
        return bank["train_images"], bank["train_labels"]
    if normalized == "test":
        return bank["test_images"], bank["test_labels"]
    raise ValueError(f"Unsupported MNIST split: {split}")


def mnist_sample(index: int, *, split: str = "test") -> MnistRecord:
    """Resolve one MNIST sample by absolute split index.

    Parameters
    ----------
    index : int
        Absolute index within the requested split. Values wrap by modulo so the
        helper stays deterministic for any integer input.
    split : str, default="test"
        Source split to query.

    Returns
    -------
    MnistRecord
        Resolved sample metadata and image data.
    """

    images, labels = mnist_split(split)
    actual_index = int(index) % len(images)
    return MnistRecord(
        split=str(split).strip().lower(),
        index=actual_index,
        digit=int(labels[actual_index]),
        image=np.array(images[actual_index], copy=True),
    )


def digit_variant_record(digit: int, variant_index: int = 0, *, split: str = "test") -> MnistRecord:
    """Resolve one deterministic sample for a requested digit label.

    Parameters
    ----------
    digit : int
        Target digit label in the ``0..9`` range.
    variant_index : int, default=0
        Variant selector within the label-specific sample bank. The value wraps
        by modulo so the helper remains deterministic for any integer input.
    split : str, default="test"
        Source split to query.

    Returns
    -------
    MnistRecord
        Resolved MNIST record for the selected label and variant.
    """

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
