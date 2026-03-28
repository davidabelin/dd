"""Runtime service for the Double-digits guided lab."""

from __future__ import annotations

from typing import Any

from dd_core.constants import ARITHMETIC_LEVEL, DOUBLE_LEVEL, LEVELS, SINGLE_LEVEL
from dd_models.baselines import BaselineRuntime
from dd_visuals.explain import build_visualization


class DoubleDigitsService:
    """Expose example, inference, and visualization flows for the web app."""

    def __init__(self, *, models_dir: str, cache_artifact: bool = True) -> None:
        self.runtime = BaselineRuntime(models_dir=models_dir, cache_artifact=cache_artifact)

    def list_examples(self, *, level: str, count: int | None = None) -> dict[str, Any]:
        """Return curated example summaries for the requested difficulty level."""

        return {
            "level": self._normalize_level(level),
            "examples": self.runtime.examples.list_examples(level, count=count),
        }

    def infer(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Run baseline inference for one example or structured payload."""

        level = self._normalize_level(payload.get("level", SINGLE_LEVEL))
        example = self._resolve_example(level, payload)
        inference = self.runtime.infer_from_example(example)
        return {
            "level": level,
            "example": example.to_summary(),
            "prediction": inference.prediction,
            "confidence": round(float(inference.confidence), 4),
            "top_classes": inference.top_classes,
            "explanation": inference.explanation,
            "result_image_uri": inference.result_image_uri,
        }

    def visualization(self, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Build one visualization payload for the requested example."""

        level = self._normalize_level(payload.get("level", SINGLE_LEVEL))
        example = self._resolve_example(level, payload)
        inference = self.runtime.infer_from_example(example)
        return build_visualization(kind, runtime=self.runtime, inference=inference)

    def _resolve_example(self, level: str, payload: dict[str, Any]):
        """Resolve one explicit example id or structured example payload."""

        example_id = str(payload.get("example_id", "")).strip()
        if example_id:
            return self.runtime.examples.example_from_id(level, example_id)
        return self.runtime.examples.structured_example(level, payload)

    @staticmethod
    def _normalize_level(level: str) -> str:
        """Validate and normalize one Double-digits level token."""

        normalized = str(level or SINGLE_LEVEL).strip().lower()
        if normalized not in LEVELS:
            raise ValueError(f"Unsupported level: {level}")
        return normalized
