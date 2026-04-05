"""Deterministic example construction for the Double-digits lab.

This module is the canonical source of scene semantics. It turns raw MNIST
records into curated, structured, and generated ``Example`` objects for the
``single``, ``double``, and ``arithmetic`` levels.

Important invariants
--------------------
- ``single`` scenes remain raw ``28x28`` MNIST digits.
- ``double`` and ``arithmetic`` scenes are composed whole-scene ``28x56``
  images.
- arithmetic semantics intentionally preserve notebook behavior, including
  larger-minus-smaller subtraction and the ``99`` divide-by-zero sentinel.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from dd_core.constants import ARITHMETIC_LEVEL, CURATED_EXAMPLES, DOUBLE_LEVEL, LEVELS, OPERATORS, SINGLE_LEVEL
from dd_core.dataset import digit_variant_record, load_digit_bank, mnist_sample
from dd_core.render import compose_pair, number_to_image, operator_canvas, overlay_operator_scene, to_data_uri


def get_results(left_digit: int, right_digit: int, operator: str) -> dict[str, Any]:
    """Return notebook-style arithmetic result metadata.

    Parameters
    ----------
    left_digit : int
        Left operand digit.
    right_digit : int
        Right operand digit.
    operator : str
        Arithmetic operator token. Supported values are the keys of
        ``dd_core.constants.OPERATORS``.

    Returns
    -------
    dict[str, Any]
        Dictionary with ``result`` and ``display_text`` fields.

    Notes
    -----
    This helper deliberately preserves notebook arithmetic semantics:

    - subtraction uses larger-minus-smaller so results stay non-negative
    - division uses larger-divided-by-smaller
    - division by zero yields the notebook sentinel value ``99``
    """

    left = int(left_digit)
    right = int(right_digit)
    normalized = str(operator).strip().lower()
    if normalized == "add":
        result = left + right
        explanation = f"{left} + {right} = {result}"
    elif normalized == "subtract":
        larger = max(left, right)
        smaller = min(left, right)
        result = larger - smaller
        explanation = f"{larger} - {smaller} = {result}"
    elif normalized == "multiply":
        result = left * right
        explanation = f"{left} × {right} = {result}"
    elif normalized == "divide":
        larger = max(left, right)
        smaller = min(left, right)
        result = 99 if smaller == 0 else int(round(larger / smaller))
        explanation = f"{larger} ÷ {smaller} = {result}" if smaller else f"{larger} ÷ 0 = 99"
    else:
        raise ValueError(f"Unsupported operator: {operator}")
    return {
        "result": int(result),
        "display_text": explanation,
    }


def doubleDigits(
    left_digit: int,
    right_digit: int,
    *,
    left_variant: int = 0,
    right_variant: int = 0,
    split: str = "test",
) -> np.ndarray:
    """Compose two MNIST digits into one two-digit notebook scene."""

    left = digit_variant_record(left_digit, left_variant, split=split)
    right = digit_variant_record(right_digit, right_variant, split=split)
    return compose_pair(left.image, right.image)


def getDoubleDigits(how_many: int = 6) -> list[dict[str, Any]]:
    """Return a deterministic slice of curated two-digit example specs."""

    return [
        CURATED_EXAMPLES[DOUBLE_LEVEL][index % len(CURATED_EXAMPLES[DOUBLE_LEVEL])]
        for index in range(int(how_many))
    ]


def getOperator(operator: str) -> np.ndarray:
    """Return the notebook-style operator overlay scene for one arithmetic token."""

    return operator_canvas(operator)


@dataclass(slots=True)
class Example:
    """One resolved guided-lab example.

    Attributes
    ----------
    id : str
        Stable example identifier used by the web API and CLI.
    level : str
        One of ``single``, ``double``, or ``arithmetic``.
    title : str
        Human-readable title for the guided UI.
    image : numpy.ndarray
        Backing grayscale image array for the example scene.
    metadata : dict[str, Any]
        Level-specific structured metadata that downstream serializers preserve.
    explanation : str
        Human-readable explanation of what the example represents.
    display_cmap : str, default="binary_r"
        Preferred display colormap when serialized for browser or CLI output.
    comparison_sources : list[dict[str, Any]]
        Supporting images used by the comparison visualization.
    """

    id: str
    level: str
    title: str
    image: np.ndarray
    metadata: dict[str, Any]
    explanation: str
    display_cmap: str = "binary_r"
    comparison_sources: list[dict[str, Any]] = field(default_factory=list)

    def to_summary(self) -> dict[str, Any]:
        """Serialize one example into the API summary shape."""

        return {
            "id": self.id,
            "level": self.level,
            "title": self.title,
            "metadata": self.metadata,
            "image_uri": to_data_uri(self.image, cmap=self.display_cmap),
            "explanation": self.explanation,
        }


class ExampleCatalog:
    """Build guided examples and structured notebook-style MNIST scenarios.

    Notes
    -----
    This is the canonical scene-construction layer for both the standalone DD
    app and the AIX-mounted `/doubledigits` lab. New scene semantics should be
    centralized here rather than split between the web and CLI surfaces.
    """

    def list_examples(self, level: str, *, count: int | None = None) -> list[dict[str, Any]]:
        """List curated examples for one supported level."""

        normalized = self._normalize_level(level)
        entries = CURATED_EXAMPLES[normalized]
        if count is not None:
            entries = entries[: int(count)]
        return [self.example_from_spec(normalized, entry).to_summary() for entry in entries]

    def example_from_id(self, level: str, example_id: str) -> Example:
        """Look up one curated example by id within the requested level."""

        normalized = self._normalize_level(level)
        for entry in CURATED_EXAMPLES[normalized]:
            if entry["id"] == example_id:
                return self.example_from_spec(normalized, entry)
        raise KeyError(f"Unknown example id '{example_id}' for level '{normalized}'.")

    def mnist_example(self, *, split: str = "test", index: int = 0) -> Example:
        """Return one raw MNIST sample as a single-level guided example."""

        record = mnist_sample(index, split=split)
        return Example(
            id=f"single_{record.split}_{record.index}",
            level=SINGLE_LEVEL,
            title=f"MNIST {record.digit}",
            image=record.image,
            metadata={
                "digit": record.digit,
                "split": record.split,
                "mnist_index": record.index,
            },
            explanation=f"Raw MNIST {record.split} sample {record.index} labeled {record.digit}.",
            comparison_sources=[
                {
                    "label": f"{record.split} sample {record.index}",
                    "image": record.image,
                    "cmap": "binary_r",
                }
            ],
        )

    def structured_example(self, level: str, payload: dict[str, Any]) -> Example:
        """Build one synthetic example from a structured request payload."""

        normalized = self._normalize_level(level)
        if normalized == SINGLE_LEVEL:
            if payload.get("mnist_index") is not None:
                return self.mnist_example(split=str(payload.get("split", "test")), index=int(payload["mnist_index"]))
            digit = int(payload.get("digit", 0))
            variant = int(payload.get("variant", 0))
            split = str(payload.get("split", "test"))
            spec = {
                "id": f"single_structured_{split}_{digit}_{variant}",
                "digit": digit,
                "variant": variant,
                "split": split,
                "title": f"Digit {digit}",
            }
            return self.example_from_spec(normalized, spec)
        if normalized == DOUBLE_LEVEL:
            left = int(payload.get("left", 1))
            right = int(payload.get("right", 2))
            left_variant = int(payload.get("left_variant", 0))
            right_variant = int(payload.get("right_variant", 1))
            split = str(payload.get("split", "test"))
            spec = {
                "id": f"double_structured_{split}_{left}{right}",
                "left": left,
                "right": right,
                "left_variant": left_variant,
                "right_variant": right_variant,
                "split": split,
                "title": f"{left}{right}",
            }
            return self.example_from_spec(normalized, spec)
        left = int(payload.get("left", 3))
        right = int(payload.get("right", 4))
        operator = str(payload.get("operator", "add"))
        left_variant = int(payload.get("left_variant", 0))
        right_variant = int(payload.get("right_variant", 1))
        split = str(payload.get("split", "test"))
        spec = {
            "id": f"arith_structured_{split}_{operator}_{left}_{right}",
            "left": left,
            "right": right,
            "operator": operator,
            "left_variant": left_variant,
            "right_variant": right_variant,
            "split": split,
            "title": f"{left} {OPERATORS[operator]['symbol']} {right}",
        }
        return self.example_from_spec(normalized, spec)

    def generated_example(self, level: str, index: int) -> Example:
        """Build one deterministic generated example for dataset export and CLI previews."""

        normalized = self._normalize_level(level)
        return self.example_from_spec(normalized, self._generated_spec(normalized, int(index)))

    def generate_examples(self, level: str, count: int) -> list[Example]:
        """Build a deterministic generated batch for one supported level."""

        normalized = self._normalize_level(level)
        return [self.generated_example(normalized, index) for index in range(max(0, int(count)))]

    def example_from_spec(self, level: str, spec: dict[str, Any]) -> Example:
        """Materialize one ``Example`` from a curated or synthetic spec."""

        split = str(spec.get("split", "test"))
        if level == SINGLE_LEVEL:
            if "mnist_index" in spec:
                return self.mnist_example(split=split, index=int(spec["mnist_index"]))
            digit = int(spec["digit"])
            variant = int(spec.get("variant", 0))
            record = digit_variant_record(digit, variant, split=split)
            return Example(
                id=str(spec["id"]),
                level=level,
                title=str(spec["title"]),
                image=record.image,
                metadata={
                    "digit": digit,
                    "variant": variant,
                    "split": record.split,
                    "mnist_index": record.index,
                },
                explanation=f"MNIST digit {digit} from the {record.split} split.",
                comparison_sources=[
                    {
                        "label": f"ground truth {digit}",
                        "image": record.image,
                        "cmap": "binary_r",
                    }
                ],
            )

        if level == DOUBLE_LEVEL:
            left = int(spec["left"])
            right = int(spec["right"])
            left_variant = int(spec.get("left_variant", 0))
            right_variant = int(spec.get("right_variant", 0))
            left_record = digit_variant_record(left, left_variant, split=split)
            right_record = digit_variant_record(right, right_variant, split=split)
            image = compose_pair(left_record.image, right_record.image)
            value = left * 10 + right
            return Example(
                id=str(spec["id"]),
                level=level,
                title=str(spec["title"]),
                image=image,
                metadata={
                    "left": left,
                    "right": right,
                    "value": value,
                    "left_variant": left_variant,
                    "right_variant": right_variant,
                    "split": split,
                    "left_mnist_index": left_record.index,
                    "right_mnist_index": right_record.index,
                },
                explanation=f"Two MNIST digits compose the number {value:02d}.",
                comparison_sources=[
                    {
                        "label": f"left ground truth {left}",
                        "image": left_record.image,
                        "cmap": "binary_r",
                    },
                    {
                        "label": f"right ground truth {right}",
                        "image": right_record.image,
                        "cmap": "binary_r",
                    },
                ],
            )

        left = int(spec["left"])
        right = int(spec["right"])
        operator = str(spec["operator"])
        left_variant = int(spec.get("left_variant", 0))
        right_variant = int(spec.get("right_variant", 0))
        left_record = digit_variant_record(left, left_variant, split=split)
        right_record = digit_variant_record(right, right_variant, split=split)
        image = overlay_operator_scene(left_record.image, right_record.image, operator)
        result = get_results(left, right, operator)
        return Example(
            id=str(spec["id"]),
            level=level,
            title=str(spec["title"]),
            image=image,
            metadata={
                "left": left,
                "right": right,
                "operator": operator,
                "operator_symbol": OPERATORS[operator]["symbol"],
                "result": result["result"],
                "left_variant": left_variant,
                "right_variant": right_variant,
                "split": split,
                "left_mnist_index": left_record.index,
                "right_mnist_index": right_record.index,
            },
            explanation=result["display_text"],
            comparison_sources=[
                {
                    "label": f"left ground truth {left}",
                    "image": left_record.image,
                    "cmap": "binary_r",
                },
                {
                    "label": f"right ground truth {right}",
                    "image": right_record.image,
                    "cmap": "binary_r",
                },
                {
                    "label": f"operator {OPERATORS[operator]['symbol']}",
                    "image": operator_canvas(operator),
                    "cmap": "binary_r",
                },
            ],
        )

    @staticmethod
    def render_result_image(result: int) -> str:
        """Render one arithmetic result value into a displayable image URI."""

        return to_data_uri(number_to_image(result), cmap="binary_r")

    @staticmethod
    def _normalize_level(level: str) -> str:
        """Validate and normalize one supported level token."""

        normalized = str(level or SINGLE_LEVEL).strip().lower()
        if normalized not in LEVELS:
            raise ValueError(f"Unsupported level: {level}")
        return normalized

    @staticmethod
    def _generated_spec(level: str, index: int) -> dict[str, Any]:
        """Build one deterministic generated-example spec for the requested level."""

        seed = max(0, int(index))
        split = "train"
        if level == SINGLE_LEVEL:
            digit = seed % 10
            variant = ExampleCatalog._normalize_variant(digit, seed * 5 + 1, split=split)
            return {
                "id": f"single_generated_{seed:04d}",
                "digit": digit,
                "variant": variant,
                "split": split,
                "title": f"Generated digit {digit}",
            }
        if level == DOUBLE_LEVEL:
            left = (seed * 3 + 1) % 10
            right = (seed * 7 + 2) % 10
            left_variant = ExampleCatalog._normalize_variant(left, seed * 2, split=split)
            right_variant = ExampleCatalog._normalize_variant(right, seed * 2 + 1, split=split)
            return {
                "id": f"double_generated_{seed:04d}",
                "left": left,
                "right": right,
                "left_variant": left_variant,
                "right_variant": right_variant,
                "split": split,
                "title": f"Generated {left}{right}",
            }
        operators = tuple(OPERATORS)
        operator = operators[seed % len(operators)]
        left = (seed * 3 + 1) % 10
        right = (seed * 5 + 2) % 10
        left_variant = ExampleCatalog._normalize_variant(left, seed * 3, split=split)
        right_variant = ExampleCatalog._normalize_variant(right, seed * 3 + 1, split=split)
        return {
            "id": f"arithmetic_generated_{seed:04d}",
            "left": left,
            "right": right,
            "operator": operator,
            "left_variant": left_variant,
            "right_variant": right_variant,
            "split": split,
            "title": f"Generated {left} {OPERATORS[operator]['symbol']} {right}",
        }

    @staticmethod
    def _normalize_variant(digit: int, variant_index: int, *, split: str = "test") -> int:
        """Normalize a requested variant index into the available range for one digit."""

        bank = load_digit_bank()
        by_digit = bank["train_by_digit"] if str(split).strip().lower() == "train" else bank["test_by_digit"]
        sample_count = len(by_digit[int(digit)])
        return int(variant_index) % sample_count
