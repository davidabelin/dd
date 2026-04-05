"""Image composition and encoding helpers for Double-digits.

This module converts MNIST digit tiles and model outputs into notebook-style
scene rasters, result rasters, PNG bytes, and browser-safe data URIs.

Important invariants
--------------------
- scene composition uses ``28x28`` digits and ``28x56`` composed scenes
- operator drawing intentionally follows notebook-era placement rules
- display serialization preserves the project color conventions:
  ``binary_r``, ``viridis``, and ``bone``
"""

from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

import numpy as np
from matplotlib import colormaps
from PIL import Image

from dd_core.constants import DIGIT_SIZE, DOUBLE_SCENE_SIZE
from dd_core.dataset import digit_variant


def compose_pair(left_image: np.ndarray, right_image: np.ndarray) -> np.ndarray:
    """Compose two MNIST digit tiles into the notebook-style 28x56 scene."""

    canvas = np.zeros(DOUBLE_SCENE_SIZE, dtype=np.float32)
    canvas[:, : DIGIT_SIZE[1]] = np.asarray(left_image, dtype=np.float32)
    canvas[:, DIGIT_SIZE[1] :] = np.asarray(right_image, dtype=np.float32)
    return np.clip(canvas, 0, 255).astype(np.uint8)


def operator_canvas(operator: str) -> np.ndarray:
    """Render one arithmetic operator onto a notebook-style 28x56 scene."""

    return _draw_operator(np.zeros(DOUBLE_SCENE_SIZE, dtype=np.float32), operator)


def overlay_operator_scene(left_image: np.ndarray, right_image: np.ndarray, operator: str) -> np.ndarray:
    """Compose a notebook-style arithmetic scene with the operator overlaid in the center."""

    image = compose_pair(left_image, right_image).astype(np.float32)
    return _draw_operator(image, operator)


def number_to_image(number: int, *, variants: tuple[int, int] = (0, 1), split: str = "test") -> np.ndarray:
    """Render one integer result value as one or two MNIST digit tiles."""

    value = abs(int(number))
    digits = [value] if value < 10 else [value // 10, value % 10]
    if len(digits) == 1:
        return digit_variant(digits[0], variants[0], split=split)
    return compose_pair(
        digit_variant(digits[0], variants[0], split=split),
        digit_variant(digits[1], variants[1], split=split),
    )


def apply_colormap(image: np.ndarray, *, cmap: str = "binary_r") -> np.ndarray:
    """Convert one grayscale image into an RGB image using a named Matplotlib colormap."""

    array = np.asarray(image, dtype=np.float32)
    if array.ndim == 3:
        return np.clip(array, 0, 255).astype(np.uint8)
    normalized = array - float(array.min())
    scale = float(normalized.max() or 1.0)
    mapped = colormaps[cmap](normalized / scale)[..., :3]
    return np.clip(mapped * 255.0, 0, 255).astype(np.uint8)


def to_png_bytes(image: np.ndarray, *, scale: int = 4, cmap: str | None = None) -> bytes:
    """Encode one image array as PNG bytes, optionally using a named colormap."""

    array = np.asarray(image)
    if cmap:
        array = apply_colormap(array, cmap=cmap)
        mode = "RGB"
    elif array.ndim == 3:
        array = np.clip(array, 0, 255).astype(np.uint8)
        mode = "RGB"
    else:
        array = np.clip(array, 0, 255).astype(np.uint8)
        mode = "L"
    pil_image = Image.fromarray(array, mode=mode)
    if scale > 1:
        pil_image = pil_image.resize((pil_image.width * scale, pil_image.height * scale), resample=Image.Resampling.NEAREST)
    buffer = BytesIO()
    pil_image.save(buffer, format="PNG")
    return buffer.getvalue()


def write_png(image: np.ndarray, path: str | Path, *, scale: int = 1, cmap: str | None = None) -> Path:
    """Write one image array to disk as a PNG file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(to_png_bytes(image, scale=scale, cmap=cmap))
    return output_path


def data_uri_to_png_bytes(data_uri: str) -> bytes:
    """Decode one PNG data URI into raw PNG bytes."""

    raw = str(data_uri or "")
    marker = "base64,"
    if marker not in raw:
        raise ValueError("Expected a base64 PNG data URI.")
    return base64.b64decode(raw.split(marker, maxsplit=1)[1].encode("ascii"))


def to_data_uri(image: np.ndarray, *, scale: int = 4, cmap: str | None = None) -> str:
    """Encode one image array as a PNG data URI."""

    encoded = base64.b64encode(to_png_bytes(image, scale=scale, cmap=cmap)).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _normalize_notebook_operator(operator: str) -> str:
    """Map runtime operator tokens onto the notebook operation names."""

    normalized = str(operator or "").strip().lower()
    mapping = {
        "add": "Add",
        "subtract": "Subtract",
        "multiply": "Multiply",
        "divide": "Divide",
        "+": "Add",
        "-": "Subtract",
        "x": "Multiply",
        "*": "Multiply",
        "×": "Multiply",
        "/": "Divide",
        "÷": "Divide",
    }
    if normalized not in mapping:
        raise ValueError(f"Unsupported operator: {operator}")
    return mapping[normalized]


def _draw_operator(image: np.ndarray, operator: str) -> np.ndarray:
    """Apply the notebook operator-drawing routine to one 28x56 scene image."""

    output = np.asarray(image, dtype=np.float32).copy()
    operation = _normalize_notebook_operator(operator)
    if operation == "Multiply":
        for row in range(11, 18):
            output[28 - row, row + 14] = 255
            output[row, row + 14] = 255
            output[row, row + 15] /= 2
            output[row, row + 15] += 255 / row
            output[row, row + 13] /= 2
            output[row, row + 13] += 50 + 512 / row
            output[28 - row, row + 13] /= 2
            output[28 - row, row + 13] += 100 + 255 / (28 - row)
            output[28 - row, row + 15] /= 2
            output[28 - row, row + 15] += 512 / (28 - row)
    elif operation == "Divide":
        for row in range(8, 21):
            output[28 - row, row + 14] = 255
            output[28 - row, row + 13] /= 2
            output[28 - row, row + 13] += 60 + 255 / row
            output[28 - row, row + 15] /= 2
            output[28 - row, row + 15] += 512 / (28 - row)
    else:
        output[14, 24:32] = 255
        if (output[13, 24:32] > 156).any():
            output[13, 24:32] /= 2
        output[13, 24:32] += 99
        if (output[15, 25:31] > 222).any():
            output[15, 25:31] /= 2
        output[15, 25:31] += 33
        if operation == "Add":
            output[10:18, 28] = 255
            if (output[10:18, 27] > 156).any():
                output[10:18, 27] /= 2
            output[10:18, 27] += 99
    return np.clip(output, 0, 255).astype(np.uint8)
