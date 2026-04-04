# Double-digits Design Notes

Status refresh: 2026-04-04

## Current product shape
- The project is a guided lab plus a notebook-fidelity CLI, not a notebook host.
- The runtime has been moved back onto MNIST rather than the temporary sklearn digits fallback.
- The three levels now map to notebook-derived data shapes:
  - single: raw `28x28` MNIST
  - double: direct `28x56` two-digit scenes
  - arithmetic: direct `28x56` arithmetic scenes with embedded operators

## CLI surface
- `python -m dd_cli dataset show`
  - inspect raw MNIST by split and absolute index
- `python -m dd_cli examples list|show|generate`
  - inspect curated scenes or generate deterministic labeled batches
- `python -m dd_cli infer`
  - run notebook-derived inference directly from the local runtime
- `python -m dd_cli visualize`
  - build activation, prototype, and comparison payloads
- `python -m dd_cli train list|run`
  - inspect and train notebook-derived Keras presets
- `python -m dd_cli serve`
  - run the standalone Flask app

## Model strategy
- The runtime no longer decomposes double/arithmetic scenes into separate digit predictions plus templates.
- Double and arithmetic scenes are classified directly as whole notebook-style `28x56` images.
- The active default presets are dense notebook models because they line up best with the original notebook training flow and weight-viewing patterns.
- Alternative notebook presets remain available through `dd_cli train`.

## Visualization semantics
- `feature_maps`
  - real activations from the selected notebook-derived model, rendered with `viridis`
- `prototype`
  - MNIST class means and first-layer weight maps, rendered with `binary_r` and `bone`
- `comparison`
  - generated scene plus the MNIST source digits and arithmetic-result context

## Batch export contract
- Generated batches remain deterministic and level-specific.
- The export bundle is still:
  - `images/`
  - `manifest.csv`
  - `dataset.npz`
- Batch exports intentionally avoid train/validation/test splitting; the training CLI owns training concerns.

## Deferred after Gamma
- Web-copy and UI refinement still belong to Delta.
- Estimator-era TensorFlow flows remain documentation/provenance only.
- Stacking and broader research-only notebook experiments are not part of the active runtime path yet.
