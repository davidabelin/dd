"""Image composition and encoding helpers for Double-digits."""

from __future__ import annotations

import base64
from io import BytesIO
from typing import Any

import numpy as np
from PIL import Image

from dd_core.constants import ARITHMETIC_SCENE_SIZE, DIGIT_SIZE, DOUBLE_SCENE_SIZE
from dd_core.dataset import digit_variant


def compose_pair(left_image: np.ndarray, right_image: np.ndarray) -> np.ndarray:
    canvas = np.zeros(DOUBLE_SCENE_SIZE, dtype=np.uint8)
    canvas[:, : DIGIT_SIZE[1]] = left_image
    canvas[:, DIGIT_SIZE[1] :] = right_image
    return canvas


def operator_canvas(operator: str) -> np.ndarray:
    canvas = np.zeros(DIGIT_SIZE, dtype=np.uint8)
    mid = DIGIT_SIZE[0] // 2
    if operator == "add":
        canvas[mid - 1 : mid + 2, 7:21] = 220
        canvas[7:21, mid - 1 : mid + 2] = 220
    elif operator == "subtract":
        canvas[mid - 1 : mid + 2, 7:21] = 220
    elif operator == "multiply":
        for index in range(7, 21):
            offset = index - 7
            canvas[index, 7 + offset] = 220
            canvas[index, 20 - offset] = 220
    else:
        raise ValueError(f"Unsupported operator: {operator}")
    return canvas


def compose_arithmetic(left_image: np.ndarray, operator_image: np.ndarray, right_image: np.ndarray) -> np.ndarray:
    canvas = np.zeros(ARITHMETIC_SCENE_SIZE, dtype=np.uint8)
    canvas[:, : DIGIT_SIZE[1]] = left_image
    canvas[:, DIGIT_SIZE[1] : DIGIT_SIZE[1] * 2] = operator_image
    canvas[:, DIGIT_SIZE[1] * 2 :] = right_image
    return canvas


def number_to_image(number: int, *, variants: tuple[int, int] = (0, 1)) -> np.ndarray:
    value = abs(int(number))
    digits = [value] if value < 10 else [value // 10, value % 10]
    if len(digits) == 1:
        return digit_variant(digits[0], variants[0])
    return compose_pair(digit_variant(digits[0], variants[0]), digit_variant(digits[1], variants[1]))


def to_data_uri(image: np.ndarray, *, scale: int = 4) -> str:
    pil_image = Image.fromarray(np.clip(image, 0, 255).astype(np.uint8), mode="L")
    if scale > 1:
        pil_image = pil_image.resize((pil_image.width * scale, pil_image.height * scale), resample=Image.Resampling.NEAREST)
    buffer = BytesIO()
    pil_image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
