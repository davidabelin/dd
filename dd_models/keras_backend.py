"""Shared Keras bootstrap helpers for notebook-derived MNIST models.

This module centralizes backend selection and thread-count defaults so the same
runtime posture is used during local development, CLI training, tests, and the
App Engine deployment mounted through AIX.
"""

from __future__ import annotations

import os

os.environ.setdefault("KERAS_BACKEND", "torch")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import keras
from keras import Model, Sequential, layers
from keras.optimizers import Adam

try:
    import torch

    _TORCH_THREADS = int(os.getenv("DOUBLEDIGITS_TORCH_THREADS", "1"))
    torch.set_num_threads(_TORCH_THREADS)
    torch.set_num_interop_threads(_TORCH_THREADS)
except (ImportError, RuntimeError, ValueError):
    pass


def set_random_seed(seed: int = 7) -> None:
    """Seed Keras and its backend for deterministic local experiments."""

    keras.utils.set_random_seed(int(seed))


__all__ = ["Adam", "Model", "Sequential", "keras", "layers", "set_random_seed"]
