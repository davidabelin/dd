"""Shared Keras bootstrap helpers for notebook-derived MNIST models."""

from __future__ import annotations

import os

os.environ.setdefault("KERAS_BACKEND", "torch")

import keras
from keras import Model, Sequential, layers
from keras.optimizers import Adam


def set_random_seed(seed: int = 7) -> None:
    """Seed Keras and its backend for deterministic local experiments."""

    keras.utils.set_random_seed(int(seed))


__all__ = ["Adam", "Model", "Sequential", "keras", "layers", "set_random_seed"]
