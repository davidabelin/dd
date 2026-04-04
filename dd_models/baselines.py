"""Notebook-derived Keras models and runtime wrappers for Double-digits."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd

from dd_core.constants import ARITHMETIC_LEVEL, DIGIT_SIZE, DOUBLE_LEVEL, OPERATORS, SINGLE_LEVEL
from dd_core.dataset import load_digit_bank, mnist_split, normalize_images
from dd_core.examples import Example, ExampleCatalog, get_results
from dd_models.keras_backend import Adam, Model, keras, layers, set_random_seed


Builder = Callable[[], Model]


@dataclass(slots=True)
class InferenceResult:
    """Normalized inference payload shared by the web app and CLI."""

    level: str
    prediction: dict[str, Any]
    confidence: float
    top_classes: list[dict[str, Any]]
    explanation: str
    input_image: np.ndarray
    example: Example
    result_image_uri: str | None = None


@dataclass(frozen=True, slots=True)
class ModelPreset:
    """One notebook-derived model preset with training defaults and metadata."""

    name: str
    level: str
    source_notebook: str
    description: str
    artifact_name: str
    input_mode: str
    train_size: int
    test_size: int
    epochs: int
    batch_size: int
    learning_rate: float
    fit_mode: str
    builder_name: str
    from_logits: bool = False
    validation_split: float | None = None


@dataclass(slots=True)
class PreparedDataset:
    """Prepared train/test arrays for one supported Double-digits level."""

    level: str
    train_images: np.ndarray
    train_labels: np.ndarray
    test_images: np.ndarray
    test_labels: np.ndarray


def _compose_double_batch(images: np.ndarray, labels: np.ndarray, *, count: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Generate notebook-style two-digit images and 0..99 labels."""

    rng = np.random.default_rng(int(seed))
    left_index = rng.integers(0, len(images), size=int(count))
    right_index = rng.integers(0, len(images), size=int(count))
    left = images[left_index]
    right = images[right_index]
    composed = np.concatenate([left, right], axis=2)
    targets = labels[left_index] * 10 + labels[right_index]
    return composed.astype(np.uint8), targets.astype(np.int64)


def _apply_operator_overlay_batch(images: np.ndarray, operator_ids: np.ndarray) -> np.ndarray:
    """Overlay notebook-style arithmetic operators onto 28x56 MNIST scenes."""

    output = np.asarray(images, dtype=np.float32).copy()
    for index, operator_name in enumerate(operator_ids):
        scene = output[index]
        if operator_name == "multiply":
            for row in range(11, 18):
                scene[28 - row, row + 14] = 255
                scene[row, row + 14] = 255
                scene[row, row + 15] /= 2
                scene[row, row + 15] += 255 / row
                scene[row, row + 13] /= 2
                scene[row, row + 13] += 50 + 512 / row
                scene[28 - row, row + 13] /= 2
                scene[28 - row, row + 13] += 100 + 255 / (28 - row)
                scene[28 - row, row + 15] /= 2
                scene[28 - row, row + 15] += 512 / (28 - row)
        elif operator_name == "divide":
            for row in range(8, 21):
                scene[28 - row, row + 14] = 255
                scene[28 - row, row + 13] /= 2
                scene[28 - row, row + 13] += 60 + 255 / row
                scene[28 - row, row + 15] /= 2
                scene[28 - row, row + 15] += 512 / (28 - row)
        else:
            scene[14, 24:32] = 255
            if (scene[13, 24:32] > 156).any():
                scene[13, 24:32] /= 2
            scene[13, 24:32] += 99
            if (scene[15, 25:31] > 222).any():
                scene[15, 25:31] /= 2
            scene[15, 25:31] += 33
            if operator_name == "add":
                scene[10:18, 28] = 255
                if (scene[10:18, 27] > 156).any():
                    scene[10:18, 27] /= 2
                scene[10:18, 27] += 99
    return np.clip(output, 0, 255).astype(np.uint8)


def _compose_arithmetic_batch(images: np.ndarray, labels: np.ndarray, *, count: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Generate notebook-style arithmetic scenes and 0..99 result labels."""

    rng = np.random.default_rng(int(seed))
    left_index = rng.integers(0, len(images), size=int(count))
    right_index = rng.integers(0, len(images), size=int(count))
    operator_names = np.asarray(tuple(OPERATORS))[rng.integers(0, len(OPERATORS), size=int(count))]

    left_digits = labels[left_index].astype(np.int64)
    right_digits = labels[right_index].astype(np.int64)
    base = np.concatenate([images[left_index], images[right_index]], axis=2)
    composed = _apply_operator_overlay_batch(base, operator_names)

    results = np.zeros(int(count), dtype=np.int64)
    for index, operator_name in enumerate(operator_names):
        left = int(left_digits[index])
        right = int(right_digits[index])
        results[index] = int(get_results(left, right, str(operator_name))["result"])
    return composed, results


def _slice_limit(images: np.ndarray, labels: np.ndarray, limit: int | None) -> tuple[np.ndarray, np.ndarray]:
    """Return an optional leading slice of one image/label split."""

    if limit is None:
        return images, labels
    return images[: int(limit)], labels[: int(limit)]


def _prepare_single_digit_dataset(*, train_size: int | None, test_size: int | None) -> PreparedDataset:
    """Prepare raw MNIST data for the single-digit level."""

    train_images, train_labels = mnist_split("train")
    test_images, test_labels = mnist_split("test")
    train_images, train_labels = _slice_limit(train_images, train_labels, train_size)
    test_images, test_labels = _slice_limit(test_images, test_labels, test_size)
    return PreparedDataset(
        level=SINGLE_LEVEL,
        train_images=normalize_images(train_images)[..., np.newaxis],
        train_labels=train_labels,
        test_images=normalize_images(test_images)[..., np.newaxis],
        test_labels=test_labels,
    )


def _prepare_double_digit_dataset(*, train_size: int | None, test_size: int | None, seed: int = 7) -> PreparedDataset:
    """Prepare notebook-style 28x56 two-digit data for direct classification."""

    train_images, train_labels = mnist_split("train")
    test_images, test_labels = mnist_split("test")
    default_train = int(train_size) if train_size is not None else 10000
    default_test = int(test_size) if test_size is not None else 1000
    x_train, y_train = _compose_double_batch(train_images, train_labels, count=default_train, seed=seed)
    x_test, y_test = _compose_double_batch(test_images, test_labels, count=default_test, seed=seed + 1)
    return PreparedDataset(
        level=DOUBLE_LEVEL,
        train_images=normalize_images(x_train)[..., np.newaxis],
        train_labels=y_train,
        test_images=normalize_images(x_test)[..., np.newaxis],
        test_labels=y_test,
    )


def _prepare_arithmetic_dataset(*, train_size: int | None, test_size: int | None, seed: int = 7) -> PreparedDataset:
    """Prepare notebook-style arithmetic scenes with embedded operators."""

    train_images, train_labels = mnist_split("train")
    test_images, test_labels = mnist_split("test")
    default_train = int(train_size) if train_size is not None else 10000
    default_test = int(test_size) if test_size is not None else 1000
    x_train, y_train = _compose_arithmetic_batch(train_images, train_labels, count=default_train, seed=seed)
    x_test, y_test = _compose_arithmetic_batch(test_images, test_labels, count=default_test, seed=seed + 1)
    return PreparedDataset(
        level=ARITHMETIC_LEVEL,
        train_images=normalize_images(x_train)[..., np.newaxis],
        train_labels=y_train,
        test_images=normalize_images(x_test)[..., np.newaxis],
        test_labels=y_test,
    )


def _build_single_mnist_dense() -> Model:
    """Build a single-digit dense model in the style of the notebook dense stacks."""

    input_layer = layers.Input(shape=(28, 28, 1))
    x = layers.Flatten()(input_layer)
    x = layers.Dense(100, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(100, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Dense(100, activation="relu")(x)
    x = layers.Dropout(0.1)(x)
    output_layer = layers.Dense(10, activation="softmax")(x)
    model = Model(input_layer, output_layer, name="single_mnist_dense")
    model.compile(loss="sparse_categorical_crossentropy", optimizer=Adam(learning_rate=0.005), metrics=["acc"])
    return model


def _build_double_with_mnist_dense() -> Model:
    """Build the dense 28x56 classifier from `double_digits_with_MNIST.ipynb`."""

    model = keras.Sequential(
        [
            layers.Input(shape=(28, 56)),
            layers.Flatten(),
            layers.Dense(256, activation="relu"),
            layers.Dropout(0.3),
            layers.Dense(128, activation="relu"),
            layers.Dropout(0.2),
            layers.Dense(100, activation="softmax"),
        ],
        name="double_with_mnist_dense",
    )
    model.compile(loss="sparse_categorical_crossentropy", optimizer=Adam(learning_rate=0.001), metrics=["accuracy"])
    return model


def _build_double_project_minimal() -> Model:
    """Build the `minimalNN` classifier from `digits_project.ipynb`."""

    input_layer = layers.Input(shape=(28, 56, 1))
    output_layer = layers.Dense(100, activation="softmax")(layers.Flatten()(input_layer))
    model = Model(input_layer, output_layer, name="double_project_minimal")
    model.compile(loss="sparse_categorical_crossentropy", optimizer=Adam(learning_rate=0.005), metrics=["acc"])
    return model


def _build_double_project_cnn() -> Model:
    """Build the CNN classifier from `digits_project.ipynb`."""

    input_layer = layers.Input(shape=(28, 56, 1))
    x = layers.Conv2D(20, 2, padding="same", activation="relu")(input_layer)
    x = layers.AveragePooling2D(2)(x)
    x = layers.Conv2D(30, 3, activation="relu")(x)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Flatten()(x)
    output_layer = layers.Dense(100, activation="softmax")(x)
    model = Model(input_layer, output_layer, name="double_project_cnn")
    model.compile(loss="sparse_categorical_crossentropy", optimizer=Adam(learning_rate=0.005), metrics=["acc"])
    return model


def _build_double_project_modelx() -> Model:
    """Build the dense `modelX` classifier from `digits_project.ipynb`."""

    input_layer = layers.Input(shape=(28, 56, 1))
    x = layers.Flatten()(input_layer)
    x = layers.Dense(300, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(200, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    output_layer = layers.Dense(100, activation="softmax")(x)
    model = Model(input_layer, output_layer, name="double_project_modelx")
    model.compile(loss="sparse_categorical_crossentropy", optimizer=Adam(learning_rate=0.005), metrics=["acc"])
    return model


def _build_double_minimal_conv() -> Model:
    """Build the minimal-convolution logits model from `minimal_convolution_double_digits.ipynb`."""

    input_layer = layers.Input(shape=(28, 56, 1))
    x = layers.Conv2D(2, (3, 4), activation="relu")(input_layer)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Flatten()(x)
    x = layers.Dropout(0.25)(x)
    output_layer = layers.Dense(100)(x)
    model = Model(input_layer, output_layer, name="double_minimal_conv")
    model.compile(
        loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        optimizer=Adam(learning_rate=0.0075),
        metrics=["acc"],
    )
    return model


def _build_double_minimal_stack() -> Model:
    """Build the stacked minimal-convolution model from the same notebook."""

    input_layer = layers.Input(shape=(28, 56, 1))
    x = layers.Conv2D(4, 6, activation="relu")(input_layer)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Conv2D(3, 3, activation="relu", strides=2)(x)
    x = layers.Conv2D(1, 3, activation="relu", strides=2)(x)
    x = layers.Flatten()(x)
    x = layers.Dense(12, activation="relu")(x)
    x = layers.Dropout(0.1)(x)
    output_layer = layers.Dense(100)(x)
    model = Model(input_layer, output_layer, name="double_minimal_stack")
    model.compile(
        loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        optimizer=Adam(learning_rate=0.0075),
        metrics=["acc"],
    )
    return model


def _build_double_classifier_diy_conv() -> Model:
    """Build the deeper DIY convolutional classifier from the classifier notebook."""

    input_layer = layers.Input(shape=(28, 56, 1))
    x = layers.Conv2D(30, 7, activation="relu")(input_layer)
    x = layers.Conv2D(20, 5, activation="relu", padding="same")(x)
    x = layers.Conv2D(10, 3, activation="relu", padding="same")(x)
    x = layers.Flatten()(x)
    x = layers.Dense(20, activation="relu")(x)
    x = layers.Dropout(0.05)(x)
    x = layers.Dense(100, activation="relu")(x)
    x = layers.Dropout(0.1)(x)
    output_layer = layers.Dense(100, activation="softmax")(x)
    model = Model(input_layer, output_layer, name="double_classifier_diy_conv")
    model.compile(loss="sparse_categorical_crossentropy", optimizer=Adam(learning_rate=0.005), metrics=["acc"])
    return model


def _build_double_classifier_dense() -> Model:
    """Build the dense classifier from `digits_classifier.ipynb`."""

    input_layer = layers.Input(shape=(28, 56, 1))
    x = layers.Flatten()(input_layer)
    x = layers.Dense(100, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(100, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Dense(100, activation="relu")(x)
    x = layers.Dropout(0.1)(x)
    output_layer = layers.Dense(100, activation="softmax")(x)
    model = Model(input_layer, output_layer, name="double_classifier_dense")
    model.compile(loss="sparse_categorical_crossentropy", optimizer=Adam(learning_rate=0.005), metrics=["acc"])
    return model


def _build_arithmetic_cnn() -> Model:
    """Build the first arithmetic CNN from `arithmetic_double_digits.ipynb`."""

    input_layer = layers.Input(shape=(28, 56, 1))
    x = layers.Conv2D(10, 2, padding="same", activation="relu")(input_layer)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Conv2D(10, 2, padding="same", activation="relu")(x)
    x = layers.Flatten()(x)
    output_layer = layers.Dense(100, activation="softmax")(x)
    model = Model(input_layer, output_layer, name="arithmetic_cnn")
    model.compile(loss="sparse_categorical_crossentropy", optimizer=Adam(learning_rate=0.0025), metrics=["acc"])
    return model


def _build_arithmetic_new_model() -> Model:
    """Build the arithmetic `new_model` CNN-plus-dense head."""

    input_layer = layers.Input(shape=(28, 56, 1))
    x = layers.Conv2D(10, 2, padding="same", activation="relu")(input_layer)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Conv2D(10, 2, padding="same", activation="relu")(x)
    x = layers.Flatten()(x)
    x = layers.Dense(100, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    output_layer = layers.Dense(100, activation="softmax")(x)
    model = Model(input_layer, output_layer, name="arithmetic_new_model")
    model.compile(loss="sparse_categorical_crossentropy", optimizer=Adam(learning_rate=0.0025), metrics=["acc"])
    return model


def _build_arithmetic_modelx() -> Model:
    """Build the dense arithmetic `modelX` from the notebook."""

    input_layer = layers.Input(shape=(28, 56, 1))
    x = layers.Flatten()(input_layer)
    x = layers.Dense(100, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(100, activation="relu")(x)
    x = layers.Dropout(0.1)(x)
    output_layer = layers.Dense(100, activation="softmax")(x)
    model = Model(input_layer, output_layer, name="arithmetic_modelx")
    model.compile(loss="sparse_categorical_crossentropy", optimizer=Adam(learning_rate=0.0025), metrics=["acc"])
    return model


def _build_double_project_mixed(base_cnn: Model) -> Model:
    """Build the frozen-CNN mixed head from `digits_project.ipynb`."""

    for layer in base_cnn.layers:
        layer.trainable = False
    flatten_layer = next(layer for layer in base_cnn.layers if "flatten" in layer.name)
    x = layers.Dense(200, activation="relu")(flatten_layer.output)
    x = layers.Dropout(0.2)(x)
    output_layer = layers.Dense(100, activation="softmax")(x)
    model = Model(base_cnn.input, output_layer, name="double_project_mixed")
    model.compile(loss="sparse_categorical_crossentropy", optimizer=Adam(learning_rate=0.005), metrics=["acc"])
    return model


BUILDERS: dict[str, Builder] = {
    "single_mnist_dense": _build_single_mnist_dense,
    "double_with_mnist_dense": _build_double_with_mnist_dense,
    "double_project_minimal": _build_double_project_minimal,
    "double_project_cnn": _build_double_project_cnn,
    "double_project_modelx": _build_double_project_modelx,
    "double_minimal_conv": _build_double_minimal_conv,
    "double_minimal_stack": _build_double_minimal_stack,
    "double_classifier_diy_conv": _build_double_classifier_diy_conv,
    "double_classifier_dense": _build_double_classifier_dense,
    "arithmetic_cnn": _build_arithmetic_cnn,
    "arithmetic_new_model": _build_arithmetic_new_model,
    "arithmetic_modelx": _build_arithmetic_modelx,
}


PRESETS: dict[str, ModelPreset] = {
    "single_mnist_dense": ModelPreset(
        name="single_mnist_dense",
        level=SINGLE_LEVEL,
        source_notebook="digits_classifier.ipynb",
        description="Notebook-style dense stack adapted for direct 10-class MNIST use.",
        artifact_name="single_mnist_dense",
        input_mode="channels",
        train_size=10000,
        test_size=2000,
        epochs=5,
        batch_size=40,
        learning_rate=0.005,
        fit_mode="validation_data",
        builder_name="single_mnist_dense",
    ),
    "double_with_mnist_dense": ModelPreset(
        name="double_with_mnist_dense",
        level=DOUBLE_LEVEL,
        source_notebook="double_digits_with_MNIST.ipynb",
        description="Dense 28x56 classifier from the original MNIST notebook.",
        artifact_name="double_with_mnist_dense",
        input_mode="image",
        train_size=40000,
        test_size=4000,
        epochs=20,
        batch_size=500,
        learning_rate=0.001,
        fit_mode="validation_split",
        builder_name="double_with_mnist_dense",
        validation_split=0.1,
    ),
    "double_project_minimal": ModelPreset(
        name="double_project_minimal",
        level=DOUBLE_LEVEL,
        source_notebook="digits_project.ipynb",
        description="Minimal flatten-plus-softmax model from the project notebook.",
        artifact_name="double_project_minimal",
        input_mode="channels",
        train_size=10000,
        test_size=1000,
        epochs=10,
        batch_size=100,
        learning_rate=0.005,
        fit_mode="validation_data",
        builder_name="double_project_minimal",
    ),
    "double_project_cnn": ModelPreset(
        name="double_project_cnn",
        level=DOUBLE_LEVEL,
        source_notebook="digits_project.ipynb",
        description="Project CNN with average and max pooling.",
        artifact_name="double_project_cnn",
        input_mode="channels",
        train_size=10000,
        test_size=1000,
        epochs=10,
        batch_size=100,
        learning_rate=0.005,
        fit_mode="validation_data",
        builder_name="double_project_cnn",
    ),
    "double_project_mixed": ModelPreset(
        name="double_project_mixed",
        level=DOUBLE_LEVEL,
        source_notebook="digits_project.ipynb",
        description="Frozen-CNN mixed head from the project notebook.",
        artifact_name="double_project_mixed",
        input_mode="channels",
        train_size=10000,
        test_size=1000,
        epochs=10,
        batch_size=100,
        learning_rate=0.005,
        fit_mode="validation_data",
        builder_name="double_project_mixed",
    ),
    "double_project_modelx": ModelPreset(
        name="double_project_modelx",
        level=DOUBLE_LEVEL,
        source_notebook="digits_project.ipynb",
        description="Best dense `modelX` from the project notebook.",
        artifact_name="double_project_modelx",
        input_mode="channels",
        train_size=10000,
        test_size=1000,
        epochs=10,
        batch_size=100,
        learning_rate=0.005,
        fit_mode="validation_data",
        builder_name="double_project_modelx",
    ),
    "double_minimal_conv": ModelPreset(
        name="double_minimal_conv",
        level=DOUBLE_LEVEL,
        source_notebook="minimal_convolution_double_digits.ipynb",
        description="Minimal convolutional logits model.",
        artifact_name="double_minimal_conv",
        input_mode="channels",
        train_size=40000,
        test_size=4000,
        epochs=15,
        batch_size=40,
        learning_rate=0.0075,
        fit_mode="validation_data",
        builder_name="double_minimal_conv",
        from_logits=True,
    ),
    "double_minimal_stack": ModelPreset(
        name="double_minimal_stack",
        level=DOUBLE_LEVEL,
        source_notebook="minimal_convolution_double_digits.ipynb",
        description="Stacked minimal-convolution model with tiny dense head.",
        artifact_name="double_minimal_stack",
        input_mode="channels",
        train_size=40000,
        test_size=4000,
        epochs=15,
        batch_size=40,
        learning_rate=0.0075,
        fit_mode="validation_data",
        builder_name="double_minimal_stack",
        from_logits=True,
    ),
    "double_classifier_diy_conv": ModelPreset(
        name="double_classifier_diy_conv",
        level=DOUBLE_LEVEL,
        source_notebook="digits_classifier.ipynb",
        description="DIY convolutional classifier from the classifier notebook.",
        artifact_name="double_classifier_diy_conv",
        input_mode="channels",
        train_size=8000,
        test_size=1000,
        epochs=5,
        batch_size=100,
        learning_rate=0.005,
        fit_mode="validation_data",
        builder_name="double_classifier_diy_conv",
    ),
    "double_classifier_dense": ModelPreset(
        name="double_classifier_dense",
        level=DOUBLE_LEVEL,
        source_notebook="digits_classifier.ipynb",
        description="Dense 28x56 classifier from the classifier notebook.",
        artifact_name="double_classifier_dense",
        input_mode="channels",
        train_size=8000,
        test_size=1000,
        epochs=5,
        batch_size=40,
        learning_rate=0.005,
        fit_mode="validation_data",
        builder_name="double_classifier_dense",
    ),
    "arithmetic_cnn": ModelPreset(
        name="arithmetic_cnn",
        level=ARITHMETIC_LEVEL,
        source_notebook="arithmetic_double_digits.ipynb",
        description="Initial arithmetic CNN from the arithmetic notebook.",
        artifact_name="arithmetic_cnn",
        input_mode="channels",
        train_size=10000,
        test_size=1000,
        epochs=1,
        batch_size=1000,
        learning_rate=0.0025,
        fit_mode="validation_data",
        builder_name="arithmetic_cnn",
    ),
    "arithmetic_new_model": ModelPreset(
        name="arithmetic_new_model",
        level=ARITHMETIC_LEVEL,
        source_notebook="arithmetic_double_digits.ipynb",
        description="Arithmetic CNN with small dense head.",
        artifact_name="arithmetic_new_model",
        input_mode="channels",
        train_size=10000,
        test_size=1000,
        epochs=20,
        batch_size=100,
        learning_rate=0.0025,
        fit_mode="validation_data",
        builder_name="arithmetic_new_model",
    ),
    "arithmetic_modelx": ModelPreset(
        name="arithmetic_modelx",
        level=ARITHMETIC_LEVEL,
        source_notebook="arithmetic_double_digits.ipynb",
        description="Dense arithmetic `modelX` from the arithmetic notebook.",
        artifact_name="arithmetic_modelx",
        input_mode="channels",
        train_size=10000,
        test_size=1000,
        epochs=20,
        batch_size=100,
        learning_rate=0.0025,
        fit_mode="validation_data",
        builder_name="arithmetic_modelx",
    ),
}


DEFAULT_PRESETS = {
    SINGLE_LEVEL: "single_mnist_dense",
    DOUBLE_LEVEL: "double_project_modelx",
    ARITHMETIC_LEVEL: "arithmetic_modelx",
}


def list_training_presets(level: str | None = None) -> list[dict[str, Any]]:
    """Return serializable metadata for the available notebook-derived presets."""

    items = []
    for preset in PRESETS.values():
        if level and preset.level != str(level).strip().lower():
            continue
        items.append(
            {
                "name": preset.name,
                "level": preset.level,
                "source_notebook": preset.source_notebook,
                "description": preset.description,
                "train_size": preset.train_size,
                "test_size": preset.test_size,
                "epochs": preset.epochs,
                "batch_size": preset.batch_size,
            }
        )
    return items


class NotebookClassifier:
    """One cached notebook-derived Keras model with training and inference helpers."""

    def __init__(self, *, models_dir: str, preset_name: str, cache_artifact: bool = True) -> None:
        if preset_name not in PRESETS:
            raise KeyError(f"Unknown model preset: {preset_name}")
        self.spec = PRESETS[preset_name]
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.cache_artifact = bool(cache_artifact)
        self.model_path = self.models_dir / f"{self.spec.artifact_name}.keras"
        self.metadata_path = self.models_dir / f"{self.spec.artifact_name}.json"
        self._model: Model | None = None
        self._activation_model: Model | None = None

    @property
    def model(self) -> Model:
        """Load or train the cached model artifact for this preset."""

        if self._model is not None:
            return self._model
        if self.cache_artifact and self.model_path.exists():
            self._model = keras.saving.load_model(self.model_path)
            return self._model
        self.train()
        if self._model is None:
            raise RuntimeError(f"Failed to load or train model preset '{self.spec.name}'.")
        return self._model

    def train(
        self,
        *,
        train_size: int | None = None,
        test_size: int | None = None,
        epochs: int | None = None,
        batch_size: int | None = None,
        force: bool = False,
        seed: int = 7,
    ) -> dict[str, Any]:
        """Train this preset with notebook defaults or explicit overrides."""

        if not force and self.cache_artifact and self.model_path.exists():
            self._model = keras.saving.load_model(self.model_path)
            return self.training_metadata()

        set_random_seed(seed)
        dataset = self._prepare_dataset(train_size=train_size, test_size=test_size)
        model = self._build_model_for_training(dataset=dataset, seed=seed)
        fit_batch_size = int(batch_size) if batch_size is not None else self._override_value("batch_size", self.spec.batch_size)
        fit_epochs = int(epochs) if epochs is not None else self._override_value("epochs", self.spec.epochs)

        x_train = self._prepare_inputs(dataset.train_images)
        x_test = self._prepare_inputs(dataset.test_images)
        fit_kwargs: dict[str, Any] = {
            "x": x_train,
            "y": dataset.train_labels,
            "batch_size": fit_batch_size,
            "epochs": fit_epochs,
            "shuffle": True,
            "verbose": 0,
        }
        if self.spec.fit_mode == "validation_split":
            fit_kwargs["validation_split"] = self.spec.validation_split or 0.1
        else:
            fit_kwargs["validation_data"] = (x_test, dataset.test_labels)

        history = model.fit(**fit_kwargs)
        evaluation = model.evaluate(x=x_test, y=dataset.test_labels, batch_size=fit_batch_size, verbose=0, return_dict=True)
        if self.cache_artifact:
            model.save(self.model_path)
            self.metadata_path.write_text(
                json.dumps(
                    {
                        "preset": self.spec.name,
                        "level": self.spec.level,
                        "source_notebook": self.spec.source_notebook,
                        "train_size": int(dataset.train_labels.shape[0]),
                        "test_size": int(dataset.test_labels.shape[0]),
                        "epochs": fit_epochs,
                        "batch_size": fit_batch_size,
                        "evaluation": evaluation,
                        "history": {key: [float(value) for value in values] for key, values in history.history.items()},
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
        self._model = model
        self._activation_model = None
        return self.training_metadata()

    def training_metadata(self) -> dict[str, Any]:
        """Return saved metadata for this preset, if available."""

        if self.metadata_path.exists():
            return json.loads(self.metadata_path.read_text(encoding="utf-8"))
        return {
            "preset": self.spec.name,
            "level": self.spec.level,
            "source_notebook": self.spec.source_notebook,
            "artifact_path": str(self.model_path),
        }

    def predict(self, image: np.ndarray) -> tuple[int, float, list[dict[str, Any]], np.ndarray]:
        """Predict one class id plus top-class payloads and raw probabilities."""

        raw = np.asarray(self.model.predict(self._prepare_inputs(np.asarray(image)[None, ...]), verbose=0))
        scores = raw.reshape(-1)
        if self.spec.from_logits:
            probabilities = keras.ops.convert_to_numpy(keras.activations.softmax(scores)).astype(np.float32)
        else:
            probabilities = scores.astype(np.float32)
        order = np.argsort(probabilities)[::-1]
        prediction = int(order[0])
        top_classes = [
            {"label": int(index), "p": round(float(probabilities[index]), 4)}
            for index in order[:5]
        ]
        return prediction, float(probabilities[prediction]), top_classes, probabilities

    def activation_maps(self, image: np.ndarray) -> list[dict[str, Any]]:
        """Return notebook-style activation maps for the configured model."""

        activation_model = self._activation_model_for_model()
        outputs = activation_model.predict(self._prepare_inputs(np.asarray(image)[None, ...]), verbose=0)
        if not isinstance(outputs, list):
            outputs = [outputs]
        items: list[dict[str, Any]] = []
        for layer, activation in zip(self.model.layers[1:], outputs, strict=False):
            items.extend(self._activation_items_for_layer(layer.name, np.asarray(activation)))
        return items

    def first_layer_weight_maps(self, *, limit: int = 10) -> list[dict[str, Any]]:
        """Return notebook-style first-layer weight visualizations."""

        weights = self._first_dense_weights()
        if weights is None:
            return []
        maps = []
        for index, coef in enumerate(weights.T[: int(limit)]):
            maps.append({"label": f"Neuron {index}", "image": coef.reshape(self._image_shape())})
        return maps

    def class_mean(self, label: int) -> np.ndarray:
        """Return the MNIST class mean for one digit label."""

        bank = load_digit_bank()
        digit = int(label) % 10
        return np.array(bank["class_means"][digit], copy=True)

    def guessing(self, n: int = 1) -> tuple[list[int], list[int], list[float], list[float], np.ndarray]:
        """Replicate notebook-style `guessing()` output on generated test data."""

        dataset = self._prepare_dataset(
            train_size=self._override_value("train_size", self.spec.train_size),
            test_size=max(int(n), self._override_value("test_size", self.spec.test_size)),
        )
        x_test = self._prepare_inputs(dataset.test_images[: int(n)])
        predictions = np.asarray(self.model.predict(x_test, verbose=0))
        if self.spec.from_logits:
            predictions = keras.ops.convert_to_numpy(keras.activations.softmax(predictions))
        guesses = predictions.argmax(axis=1).astype(np.int64)
        answers = dataset.test_labels[: int(n)].astype(np.int64)
        p_guess = [float(predictions[index, guess]) * 100.0 for index, guess in enumerate(guesses)]
        p_answer = [float(predictions[index, answer]) * 100.0 for index, answer in enumerate(answers)]
        return answers.tolist(), guesses.tolist(), p_answer, p_guess, dataset.test_images[: int(n)]

    def get_results_frame(self, n: int = 10) -> pd.DataFrame:
        """Replicate notebook-style `get_results()` / `getAnswers()` tables."""

        answers, guesses, p_answer, p_guess, _ = self.guessing(n=n)
        return pd.DataFrame({"Answer": answers, "Guess": guesses, "P(A)": p_answer, "P(G)": p_guess})

    def _first_dense_weights(self) -> np.ndarray | None:
        """Return the first dense-layer kernel when it matches the input image size."""

        for layer in self.model.layers:
            if not isinstance(layer, layers.Dense):
                continue
            kernel = np.asarray(layer.get_weights()[0])
            image_shape = self._image_shape()
            if kernel.shape[0] == image_shape[0] * image_shape[1]:
                return kernel.astype(np.float32)
        return None

    def _activation_model_for_model(self) -> Model:
        """Build and cache a Keras model that exposes every non-input layer output."""

        if self._activation_model is None:
            outputs = [layer.output for layer in self.model.layers[1:]]
            self._activation_model = Model(self.model.input, outputs, name=f"{self.spec.name}_activations")
        return self._activation_model

    def _activation_items_for_layer(self, layer_name: str, activation: np.ndarray) -> list[dict[str, Any]]:
        """Convert one raw layer activation into displayable notebook-style images."""

        items: list[dict[str, Any]] = []
        image_shape = self._image_shape()
        if activation.ndim == 4:
            maps = activation[0]
            for index in range(min(maps.shape[-1], 10)):
                items.append({"name": f"{layer_name}:{index}", "image": maps[:, :, index]})
            return items
        flattened = activation.reshape((activation.shape[0], -1))[0]
        if "flatten" in layer_name and flattened.size == image_shape[0] * image_shape[1]:
            items.append({"name": layer_name, "image": flattened.reshape(image_shape)})
            return items
        items.append({"name": layer_name, "image": _reshape_vector_to_grid(flattened)})
        return items

    def _prepare_dataset(self, *, train_size: int | None, test_size: int | None) -> PreparedDataset:
        """Prepare level-appropriate training data for this preset."""

        resolved_train = train_size if train_size is not None else self._override_value("train_size", self.spec.train_size)
        resolved_test = test_size if test_size is not None else self._override_value("test_size", self.spec.test_size)
        if self.spec.level == SINGLE_LEVEL:
            return _prepare_single_digit_dataset(train_size=resolved_train, test_size=resolved_test)
        if self.spec.level == DOUBLE_LEVEL:
            return _prepare_double_digit_dataset(train_size=resolved_train, test_size=resolved_test)
        return _prepare_arithmetic_dataset(train_size=resolved_train, test_size=resolved_test)

    def _build_model_for_training(self, *, dataset: PreparedDataset, seed: int) -> Model:
        """Build the configured preset, including special handling for mixedNN."""

        if self.spec.name == "double_project_mixed":
            base_classifier = NotebookClassifier(
                models_dir=str(self.models_dir),
                preset_name="double_project_cnn",
                cache_artifact=self.cache_artifact,
            )
            base_classifier.train(
                train_size=int(dataset.train_labels.shape[0]),
                test_size=int(dataset.test_labels.shape[0]),
                epochs=self._override_value("epochs", PRESETS["double_project_cnn"].epochs),
                batch_size=self._override_value("batch_size", PRESETS["double_project_cnn"].batch_size),
                seed=seed,
            )
            return _build_double_project_mixed(base_classifier.model)
        return BUILDERS[self.spec.builder_name]()

    def _prepare_inputs(self, images: np.ndarray) -> np.ndarray:
        """Convert normalized image arrays into the shape expected by the preset."""

        if self.spec.input_mode == "image":
            return np.asarray(images, dtype=np.float32).reshape((-1, *self._image_shape()))
        return np.asarray(images, dtype=np.float32).reshape((-1, *self._image_shape(), 1))

    def _image_shape(self) -> tuple[int, int]:
        """Return the native input image shape for this preset."""

        return DIGIT_SIZE if self.spec.level == SINGLE_LEVEL else (28, 56)

    def _override_value(self, field_name: str, default: int) -> int:
        """Resolve a level-specific environment override for notebook training sizes."""

        env_name = f"DOUBLEDIGITS_{field_name.upper()}_{self.spec.level.upper()}"
        raw = os.getenv(env_name)
        return int(raw) if raw else int(default)


def _reshape_vector_to_grid(values: np.ndarray) -> np.ndarray:
    """Reshape one flat activation vector into the nearest rectangular grid."""

    size = int(values.size)
    cols = int(np.ceil(np.sqrt(size)))
    rows = int(np.ceil(size / cols))
    grid = np.zeros((rows, cols), dtype=np.float32)
    grid.flat[:size] = values.astype(np.float32)
    return grid


class BaselineRuntime:
    """Notebook-derived inference runtime for the guided Double-digits app."""

    def __init__(self, *, models_dir: str, cache_artifact: bool = True) -> None:
        self.examples = ExampleCatalog()
        self.single_model = NotebookClassifier(
            models_dir=models_dir,
            preset_name=os.getenv("DOUBLEDIGITS_SINGLE_PRESET", DEFAULT_PRESETS[SINGLE_LEVEL]),
            cache_artifact=cache_artifact,
        )
        self.double_model = NotebookClassifier(
            models_dir=models_dir,
            preset_name=os.getenv("DOUBLEDIGITS_DOUBLE_PRESET", DEFAULT_PRESETS[DOUBLE_LEVEL]),
            cache_artifact=cache_artifact,
        )
        self.arithmetic_model = NotebookClassifier(
            models_dir=models_dir,
            preset_name=os.getenv("DOUBLEDIGITS_ARITHMETIC_PRESET", DEFAULT_PRESETS[ARITHMETIC_LEVEL]),
            cache_artifact=cache_artifact,
        )

    def infer_from_example(self, example: Example) -> InferenceResult:
        """Run direct notebook-style inference for one prepared example."""

        if example.level == SINGLE_LEVEL:
            prediction, confidence, top_classes, _ = self.single_model.predict(example.image)
            return InferenceResult(
                level=example.level,
                prediction={"digit": prediction},
                confidence=confidence,
                top_classes=top_classes,
                explanation=f"Predicted digit {prediction} from the MNIST input.",
                input_image=example.image,
                example=example,
            )
        if example.level == DOUBLE_LEVEL:
            prediction, confidence, top_classes, _ = self.double_model.predict(example.image)
            return InferenceResult(
                level=example.level,
                prediction={"left_digit": prediction // 10, "right_digit": prediction % 10, "value": prediction},
                confidence=confidence,
                top_classes=top_classes,
                explanation=f"Predicted the whole 28x56 scene as {prediction:02d}.",
                input_image=example.image,
                example=example,
            )
        prediction, confidence, top_classes, _ = self.arithmetic_model.predict(example.image)
        return InferenceResult(
            level=example.level,
            prediction={
                "left_digit": int(example.metadata["left"]),
                "right_digit": int(example.metadata["right"]),
                "operator": str(example.metadata["operator"]),
                "operator_symbol": OPERATORS[str(example.metadata["operator"])]["symbol"],
                "result": prediction,
            },
            confidence=confidence,
            top_classes=top_classes,
            explanation=(
                f"Notebook-style arithmetic model predicted {prediction} for the scene "
                f"{example.metadata['left']} {example.metadata['operator_symbol']} {example.metadata['right']}."
            ),
            input_image=example.image,
            example=example,
            result_image_uri=ExampleCatalog.render_result_image(prediction),
        )

    def classifier_for_level(self, level: str) -> NotebookClassifier:
        """Return the level-appropriate classifier wrapper."""

        normalized = str(level).strip().lower()
        if normalized == SINGLE_LEVEL:
            return self.single_model
        if normalized == DOUBLE_LEVEL:
            return self.double_model
        if normalized == ARITHMETIC_LEVEL:
            return self.arithmetic_model
        raise ValueError(f"Unsupported level: {level}")
