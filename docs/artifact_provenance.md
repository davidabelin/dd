# Double-digits Model and Artifact Provenance

## Current data source
- The live runtime is now MNIST-only.
- `dd_core.dataset` loads the raw `train` and `test` MNIST splits through standalone Keras.
- Single-digit examples are raw `28x28` MNIST samples.
- Two-digit scenes are notebook-style `28x56` composites made by concatenating two MNIST digits.
- Arithmetic scenes are also `28x56`; the operator is drawn directly into the center of the composed scene, matching `arithmetic_double_digits.ipynb`.

## Current runtime artifacts
- The sklearn logistic-regression path is gone.
- The active runtime uses notebook-derived Keras presets cached as `.keras` artifacts in `models/`.
- Default presets are:
  - `single_mnist_dense`
  - `double_project_modelx`
  - `arithmetic_modelx`
- Additional notebook presets are exposed through `python -m dd_cli train`.

## Why the runtime uses Keras on torch
- The legacy notebooks were written for TensorFlow/Keras in Colab.
- The current local Python 3.14 environment does not provide a practical TensorFlow install path.
- The migrated runtime therefore keeps the notebook-style Keras layer/model definitions but executes them through standalone Keras with the torch backend.

## Export artifacts
- `python -m dd_cli examples generate` writes:
  - `images/`
  - `manifest.csv`
  - `dataset.npz`
- `manifest.csv` is the authoritative metadata table.
- `dataset.npz` stores aligned `images`, `targets`, `ids`, and `metadata_json`.

## Visualization provenance
- `feature_maps` now come from real model activations rather than fixed image filters.
- `prototype` views combine MNIST class means with notebook-style first-layer weight maps.
- `comparison` views show the generated scene against the underlying MNIST ground-truth source digits and, for arithmetic, the notebook operator/result context.

## Notebook color conventions
- Raw MNIST-style scenes use `binary_r`.
- Activation maps use `viridis`.
- First-layer notebook weight views use `bone`.
