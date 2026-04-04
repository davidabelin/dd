# Double-digits Model and Artifact Provenance

## Current baseline inputs
- `sklearn.datasets.load_digits()` provides the handwritten source samples.
- Source samples are resized into `28x28` grayscale digit canvases for the current lab and CLI flows.
- Two-digit scenes and arithmetic scenes are composed programmatically from those digit tiles.

## Current runtime artifacts
- Single-digit recognition uses a cached scikit-learn logistic-regression model.
- Double-digit recognition composes two single-digit predictions rather than using a separate monolithic classifier.
- Arithmetic recognition composes two digit predictions with operator-template matching and then evaluates the controlled result.

## Gamma export artifacts
- `python -m dd_cli examples generate` writes:
  - `images/` for direct image inspection
  - `manifest.csv` as the authoritative metadata table
  - `dataset.npz` for aligned numeric workflows
- `manifest.csv` is intentionally pandas-readable without requiring notebook code or custom parsers.
- `dataset.npz` stores the aligned `images`, `targets`, `ids`, and `metadata_json` arrays for the same row order.

## Visualization provenance
- `feature_maps` are fixed-filter explanatory views, not learned CNN activations.
- `prototype` views combine logistic-regression class means and coefficient maps plus operator templates where relevant.
- `comparison` views expose the current input segments and the rendered arithmetic result image when one exists.

## Why this differs from the notebook era
- The notebooks mixed tutorial narrative, exploratory model work, Colab execution scaffolding, and product ideas in the same files.
- The migrated app and CLI standardize on one clean inference contract first.
- Estimator-era flows, retraining workflows, stacking experiments, and broader CNN research remain outside the active runtime path.
- Future phases may replace or augment the current baselines with exported learned artifacts once those models are stable enough to justify a richer inspection surface.
