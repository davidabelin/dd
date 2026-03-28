"""Deterministic example generation for the guided Double-digits lab."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from dd_core.constants import ARITHMETIC_LEVEL, CURATED_EXAMPLES, DOUBLE_LEVEL, LEVELS, OPERATORS, SINGLE_LEVEL
from dd_core.dataset import digit_variant
from dd_core.render import compose_arithmetic, compose_pair, number_to_image, operator_canvas, to_data_uri


def get_results(left_digit: int, right_digit: int, operator: str) -> dict[str, Any]:
    left = int(left_digit)
    right = int(right_digit)
    if operator == "add":
        result = left + right
        explanation = f"{left} + {right} = {result}"
    elif operator == "subtract":
        larger = max(left, right)
        smaller = min(left, right)
        result = larger - smaller
        explanation = f"{larger} - {smaller} = {result}"
    elif operator == "multiply":
        result = left * right
        explanation = f"{left} × {right} = {result}"
    else:
        raise ValueError(f"Unsupported operator: {operator}")
    return {
        "result": result,
        "display_text": explanation,
    }


def doubleDigits(left_digit: int, right_digit: int, *, left_variant: int = 0, right_variant: int = 0) -> np.ndarray:
    return compose_pair(digit_variant(left_digit, left_variant), digit_variant(right_digit, right_variant))


def getDoubleDigits(how_many: int = 6) -> list[dict[str, Any]]:
    items = []
    for index in range(int(how_many)):
        spec = CURATED_EXAMPLES[DOUBLE_LEVEL][index % len(CURATED_EXAMPLES[DOUBLE_LEVEL])]
        items.append(spec)
    return items


def getOperator(operator: str) -> np.ndarray:
    return operator_canvas(operator)


@dataclass(slots=True)
class Example:
    id: str
    level: str
    title: str
    image: np.ndarray
    metadata: dict[str, Any]
    explanation: str

    def to_summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "level": self.level,
            "title": self.title,
            "metadata": self.metadata,
            "image_uri": to_data_uri(self.image),
            "explanation": self.explanation,
        }


class ExampleCatalog:
    """Build guided examples and structured scenarios for the Double-digits lab."""

    def list_examples(self, level: str, *, count: int | None = None) -> list[dict[str, Any]]:
        normalized = self._normalize_level(level)
        entries = CURATED_EXAMPLES[normalized]
        if count is not None:
            entries = entries[: int(count)]
        return [self.example_from_spec(normalized, entry).to_summary() for entry in entries]

    def example_from_id(self, level: str, example_id: str) -> Example:
        normalized = self._normalize_level(level)
        for entry in CURATED_EXAMPLES[normalized]:
            if entry["id"] == example_id:
                return self.example_from_spec(normalized, entry)
        raise KeyError(f"Unknown example id '{example_id}' for level '{normalized}'.")

    def structured_example(self, level: str, payload: dict[str, Any]) -> Example:
        normalized = self._normalize_level(level)
        if normalized == SINGLE_LEVEL:
            digit = int(payload.get("digit", 0))
            variant = int(payload.get("variant", 0))
            spec = {"id": f"single_structured_{digit}_{variant}", "digit": digit, "variant": variant, "title": f"Digit {digit}"}
            return self.example_from_spec(normalized, spec)
        if normalized == DOUBLE_LEVEL:
            left = int(payload.get("left", 1))
            right = int(payload.get("right", 2))
            left_variant = int(payload.get("left_variant", 0))
            right_variant = int(payload.get("right_variant", 1))
            spec = {
                "id": f"double_structured_{left}{right}",
                "left": left,
                "right": right,
                "left_variant": left_variant,
                "right_variant": right_variant,
                "title": f"{left}{right}",
            }
            return self.example_from_spec(normalized, spec)
        left = int(payload.get("left", 3))
        right = int(payload.get("right", 4))
        operator = str(payload.get("operator", "add"))
        left_variant = int(payload.get("left_variant", 0))
        right_variant = int(payload.get("right_variant", 1))
        spec = {
            "id": f"arith_structured_{operator}_{left}_{right}",
            "left": left,
            "right": right,
            "operator": operator,
            "left_variant": left_variant,
            "right_variant": right_variant,
            "title": f"{left} {OPERATORS[operator]['symbol']} {right}",
        }
        return self.example_from_spec(normalized, spec)

    def example_from_spec(self, level: str, spec: dict[str, Any]) -> Example:
        if level == SINGLE_LEVEL:
            digit = int(spec["digit"])
            variant = int(spec.get("variant", 0))
            image = digit_variant(digit, variant)
            return Example(
                id=str(spec["id"]),
                level=level,
                title=str(spec["title"]),
                image=image,
                metadata={"digit": digit, "variant": variant},
                explanation=f"Single handwritten digit {digit}.",
            )
        if level == DOUBLE_LEVEL:
            left = int(spec["left"])
            right = int(spec["right"])
            left_variant = int(spec.get("left_variant", 0))
            right_variant = int(spec.get("right_variant", 0))
            image = doubleDigits(left, right, left_variant=left_variant, right_variant=right_variant)
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
                },
                explanation=f"Two separate digit images compose the number {value:02d}.",
            )
        left = int(spec["left"])
        right = int(spec["right"])
        operator = str(spec["operator"])
        left_variant = int(spec.get("left_variant", 0))
        right_variant = int(spec.get("right_variant", 0))
        left_image = digit_variant(left, left_variant)
        right_image = digit_variant(right, right_variant)
        operator_image = getOperator(operator)
        image = compose_arithmetic(left_image, operator_image, right_image)
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
            },
            explanation=result["display_text"],
        )

    @staticmethod
    def render_result_image(result: int) -> str:
        return to_data_uri(number_to_image(result))

    @staticmethod
    def _normalize_level(level: str) -> str:
        normalized = str(level or SINGLE_LEVEL).strip().lower()
        if normalized not in LEVELS:
            raise ValueError(f"Unsupported level: {level}")
        return normalized
