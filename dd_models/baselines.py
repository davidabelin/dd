"""Lightweight baseline models for the Double-digits lab."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

from dd_core.constants import ARITHMETIC_LEVEL, DIGIT_SIZE, DOUBLE_LEVEL, OPERATORS, SINGLE_LEVEL
from dd_core.dataset import downscale_digit, load_digit_bank
from dd_core.examples import Example, ExampleCatalog, get_results
from dd_core.render import operator_canvas, to_data_uri


@dataclass(slots=True)
class InferenceResult:
    level: str
    prediction: dict[str, Any]
    confidence: float
    top_classes: list[dict[str, Any]]
    segments: dict[str, np.ndarray]
    explanation: str
    result_image_uri: str | None = None


class OperatorTemplateModel:
    def __init__(self) -> None:
        self._templates = {
            operator: operator_canvas(operator).astype(np.float32)
            for operator in OPERATORS
        }

    def predict(self, image_28x28: np.ndarray) -> tuple[str, dict[str, float]]:
        image = image_28x28.astype(np.float32)
        scores = {}
        for operator, template in self._templates.items():
            mse = float(np.mean((image - template) ** 2))
            scores[operator] = 1.0 / (1.0 + mse)
        total = sum(scores.values()) or 1.0
        probabilities = {operator: score / total for operator, score in scores.items()}
        best = max(probabilities.items(), key=lambda item: item[1])[0]
        return best, probabilities

    def template(self, operator: str) -> np.ndarray:
        return np.array(self._templates[operator], copy=True)


class SingleDigitLogRegModel:
    def __init__(self, *, models_dir: str, cache_artifact: bool = True) -> None:
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.artifact_path = self.models_dir / "single_digit_logreg.joblib"
        self.cache_artifact = bool(cache_artifact)
        self._model: LogisticRegression | None = None
        self._bank = load_digit_bank()
        self._class_means = self._bank["class_means"]

    @property
    def model(self) -> LogisticRegression:
        if self._model is not None:
            return self._model
        if self.cache_artifact and self.artifact_path.exists():
            self._model = joblib.load(self.artifact_path)
            return self._model
        features = self._bank["images_8x8"].reshape((-1, 64))
        labels = self._bank["labels"]
        model = LogisticRegression(
            max_iter=2000,
            multi_class="multinomial",
            solver="lbfgs",
            random_state=7,
        )
        model.fit(features, labels)
        if self.cache_artifact:
            joblib.dump(model, self.artifact_path)
        self._model = model
        return model

    def predict(self, image_28x28: np.ndarray) -> tuple[int, float, list[dict[str, Any]]]:
        features = downscale_digit(image_28x28).reshape(1, -1)
        probabilities = self.model.predict_proba(features)[0]
        order = np.argsort(probabilities)[::-1]
        prediction = int(order[0])
        confidence = float(probabilities[prediction])
        top_classes = [
            {"label": int(index), "p": round(float(probabilities[index]), 4)}
            for index in order[:3]
        ]
        return prediction, confidence, top_classes

    def class_mean(self, digit: int) -> np.ndarray:
        return np.array(self._class_means[int(digit)], copy=True)

    def coefficient_map(self, digit: int) -> np.ndarray:
        coef = self.model.coef_[int(digit)].reshape(8, 8)
        normalized = coef - coef.min()
        max_value = float(normalized.max() or 1.0)
        normalized = (normalized / max_value) * 255.0
        from dd_core.dataset import _resize_to_28  # local reuse of the same resize path

        return _resize_to_28(normalized.astype(np.uint8) / 255.0 * 16.0)


class BaselineRuntime:
    """One unified inference contract for the guided Double-digits app."""

    def __init__(self, *, models_dir: str, cache_artifact: bool = True) -> None:
        self.examples = ExampleCatalog()
        self.single_model = SingleDigitLogRegModel(models_dir=models_dir, cache_artifact=cache_artifact)
        self.operator_model = OperatorTemplateModel()

    def infer_from_example(self, example: Example) -> InferenceResult:
        if example.level == SINGLE_LEVEL:
            prediction, confidence, top_classes = self.single_model.predict(example.image)
            return InferenceResult(
                level=example.level,
                prediction={"digit": prediction},
                confidence=confidence,
                top_classes=top_classes,
                segments={"digit": example.image},
                explanation=f"Predicted digit {prediction} from one handwritten input.",
            )
        if example.level == DOUBLE_LEVEL:
            left_img = example.image[:, : DIGIT_SIZE[1]]
            right_img = example.image[:, DIGIT_SIZE[1] :]
            left_pred, left_conf, left_top = self.single_model.predict(left_img)
            right_pred, right_conf, right_top = self.single_model.predict(right_img)
            value = left_pred * 10 + right_pred
            return InferenceResult(
                level=example.level,
                prediction={"left_digit": left_pred, "right_digit": right_pred, "value": value},
                confidence=float(left_conf * right_conf),
                top_classes=[
                    {"label": f"{left_pred}{right_pred}", "p": round(float(left_conf * right_conf), 4)},
                    {"label": f"{left_top[0]['label']}{right_top[1]['label']}", "p": round(float(left_top[0]["p"] * right_top[1]["p"]), 4)},
                ],
                segments={"left": left_img, "right": right_img},
                explanation=f"Recognized the left half as {left_pred} and the right half as {right_pred}, giving {value:02d}.",
            )
        left_img = example.image[:, : DIGIT_SIZE[1]]
        operator_img = example.image[:, DIGIT_SIZE[1] : DIGIT_SIZE[1] * 2]
        right_img = example.image[:, DIGIT_SIZE[1] * 2 :]
        left_pred, left_conf, _ = self.single_model.predict(left_img)
        right_pred, right_conf, _ = self.single_model.predict(right_img)
        operator_pred, operator_probs = self.operator_model.predict(operator_img)
        arithmetic = get_results(left_pred, right_pred, operator_pred)
        operator_conf = float(operator_probs[operator_pred])
        return InferenceResult(
            level=example.level,
            prediction={
                "left_digit": left_pred,
                "right_digit": right_pred,
                "operator": operator_pred,
                "operator_symbol": OPERATORS[operator_pred]["symbol"],
                "result": arithmetic["result"],
            },
            confidence=float(left_conf * right_conf * operator_conf),
            top_classes=[
                {
                    "label": f"{left_pred} {OPERATORS[operator_pred]['symbol']} {right_pred}",
                    "p": round(float(left_conf * right_conf * operator_conf), 4),
                }
            ],
            segments={"left": left_img, "operator": operator_img, "right": right_img},
            explanation=arithmetic["display_text"],
            result_image_uri=ExampleCatalog.render_result_image(arithmetic["result"]),
        )
