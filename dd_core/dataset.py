"""Digit sample loading and rendering helpers."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np
from PIL import Image
from sklearn.datasets import load_digits

from dd_core.constants import DIGIT_SIZE


def _resize_to_28(image_8x8: np.ndarray) -> np.ndarray:
    scaled = np.clip((image_8x8 / 16.0) * 255.0, 0, 255).astype(np.uint8)
    pil_image = Image.fromarray(scaled, mode="L")
    resized = pil_image.resize((DIGIT_SIZE[1], DIGIT_SIZE[0]), resample=Image.Resampling.BICUBIC)
    return np.array(resized, dtype=np.uint8)


@lru_cache(maxsize=1)
def load_digit_bank() -> dict[str, Any]:
    dataset = load_digits()
    images_8x8 = dataset.images.astype(np.float32)
    labels = dataset.target.astype(int)
    images_28 = np.stack([_resize_to_28(image) for image in images_8x8], axis=0)
    by_digit: dict[int, list[np.ndarray]] = {digit: [] for digit in range(10)}
    by_digit_8: dict[int, list[np.ndarray]] = {digit: [] for digit in range(10)}
    for image_8x8, image_28, label in zip(images_8x8, images_28, labels, strict=False):
        by_digit[int(label)].append(image_28)
        by_digit_8[int(label)].append(image_8x8.astype(np.float32))
    class_means = {
        digit: np.mean(np.stack(samples, axis=0), axis=0).astype(np.float32)
        for digit, samples in by_digit.items()
    }
    return {
        "images_8x8": images_8x8,
        "images_28": images_28,
        "labels": labels,
        "by_digit": by_digit,
        "by_digit_8": by_digit_8,
        "class_means": class_means,
    }


def digit_variant(digit: int, variant_index: int = 0, *, size: str = "28") -> np.ndarray:
    bank = load_digit_bank()
    source = bank["by_digit"] if size == "28" else bank["by_digit_8"]
    samples = source[int(digit)]
    index = int(variant_index) % len(samples)
    return np.array(samples[index], copy=True)


def downscale_digit(image_28x28: np.ndarray) -> np.ndarray:
    image = Image.fromarray(np.clip(image_28x28, 0, 255).astype(np.uint8), mode="L")
    downsized = image.resize((8, 8), resample=Image.Resampling.BICUBIC)
    return (np.array(downsized, dtype=np.float32) / 255.0) * 16.0
