"""Runtime service for the Double-digits guided lab."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dd_core.constants import LEVELS, SINGLE_LEVEL
from dd_core.examples import ExampleCatalog


class DoubleDigitsService:
    """Expose example, preset, inference, and visualization flows for the web app."""

    def __init__(self, *, models_dir: str, cache_artifact: bool = True, allow_training: bool = True) -> None:
        self.examples = ExampleCatalog()
        self.models_dir = str(models_dir)
        self.cache_artifact = bool(cache_artifact)
        self.allow_training = bool(allow_training)
        self._runtime = None

    def list_examples(self, *, level: str, count: int | None = None) -> dict[str, Any]:
        """Return curated example summaries for the requested difficulty level."""

        normalized = self._normalize_level(level)
        return {
            "level": normalized,
            "examples": self.examples.list_examples(normalized, count=count),
        }

    def list_presets(self, *, level: str) -> dict[str, Any]:
        """Return preset metadata for one level without loading model weights."""

        normalized = self._normalize_level(level)
        from dd_models.baselines import DEFAULT_PRESETS, PRESETS, list_training_presets

        items = []
        for item in list_training_presets(level=normalized):
            spec = PRESETS[item["name"]]
            artifact_path = Path(self.models_dir) / f"{spec.artifact_name}.keras"
            items.append(
                {
                    **item,
                    "default": item["name"] == DEFAULT_PRESETS[normalized],
                    "artifact_ready": artifact_path.exists(),
                    "artifact_filename": artifact_path.name,
                }
            )
        return {
            "level": normalized,
            "default_preset": DEFAULT_PRESETS[normalized],
            "presets": items,
        }

    def infer(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Run baseline inference for one example or structured payload."""

        level = self._normalize_level(payload.get("level", SINGLE_LEVEL))
        example = self._resolve_example(level, payload)
        preset = self._normalize_preset(payload.get("preset"))
        inference = self._runtime_instance().infer_from_example(example, preset=preset)
        return {
            "level": level,
            "preset": inference.preset_name,
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
        preset = self._normalize_preset(payload.get("preset"))
        inference = self._runtime_instance().infer_from_example(example, preset=preset)
        from dd_visuals.explain import build_visualization

        visualization = build_visualization(kind, runtime=self._runtime_instance(), inference=inference)
        visualization["level"] = level
        visualization["preset"] = inference.preset_name
        return visualization

    def health(self) -> dict[str, Any]:
        """Return a lightweight health payload that does not force model loading."""

        return {
            "status": "ok",
            "runtime_loaded": self._runtime is not None,
            "cache_artifact": self.cache_artifact,
            "allow_training": self.allow_training,
            "models_dir": self.models_dir,
            "levels": list(LEVELS),
        }

    def _resolve_example(self, level: str, payload: dict[str, Any]):
        """Resolve one explicit example id or structured example payload."""

        example_id = str(payload.get("example_id", "")).strip()
        if example_id:
            return self.examples.example_from_id(level, example_id)
        return self.examples.structured_example(level, payload)

    def _runtime_instance(self):
        """Build and cache the heavy notebook runtime only when needed."""

        if self._runtime is None:
            from dd_models.baselines import BaselineRuntime

            self._runtime = BaselineRuntime(
                models_dir=self.models_dir,
                cache_artifact=self.cache_artifact,
                allow_training=self.allow_training,
            )
        return self._runtime

    @staticmethod
    def _normalize_level(level: str) -> str:
        """Validate and normalize one Double-digits level token."""

        normalized = str(level or SINGLE_LEVEL).strip().lower()
        if normalized not in LEVELS:
            raise ValueError(f"Unsupported level: {level}")
        return normalized

    @staticmethod
    def _normalize_preset(preset: object) -> str | None:
        """Normalize an optional preset token from query or JSON payloads."""

        value = str(preset or "").strip()
        return value or None
