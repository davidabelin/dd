# Double-digits Design Notes

Status refresh: 2026-04-05

> Archival reference: the canonical maintainer documentation now lives in [docs/maintainer/README.md](maintainer/README.md). Use this file for historical design context, not as the primary maintainer entrypoint.

## Current product shape
- The project is a guided lab plus a notebook-fidelity CLI, not a notebook host.
- The runtime has been moved back onto MNIST rather than the temporary sklearn digits fallback.
- The web app is now a single notebook-style scroll with anchored sections for single digits, double digits, and arithmetic scenes.
- The mounted and standalone web builds share the same UI logic and runtime code, with server-rendered `mountBase` and `apiBase` config instead of hard-coded root paths.
- The repo now ships a local `data/mnist.npz` archive so example browsing and cloud cold starts do not depend on runtime dataset downloads.
- The three levels now map to notebook-derived data shapes:
  - single: raw `28x28` MNIST
  - double: direct `28x56` two-digit scenes
  - arithmetic: direct `28x56` arithmetic scenes with embedded operators
- The browser exposes read-only preset switching in advanced panels; training and artifact generation stay CLI-only.

## CLI surface
- `python -m dd_cli dataset show`
  - inspect raw MNIST by split and absolute index
- `python -m dd_cli examples list|show|generate`
  - inspect curated scenes or generate deterministic labeled batches
- `python -m dd_cli infer`
  - run notebook-derived inference directly from the local runtime
- `python -m dd_cli visualize`
  - build activation, prototype, and comparison payloads
- `python -m dd_cli infer --preset ...` and `python -m dd_cli visualize --preset ...`
  - override the active notebook-derived preset without changing the default registry mapping
- `python -m dd_cli train list|run`
  - inspect and train notebook-derived Keras presets
- `python -m dd_cli serve`
  - run the standalone Flask app

## Model strategy
- The runtime no longer decomposes double/arithmetic scenes into separate digit predictions plus templates.
- Double and arithmetic scenes are classified directly as whole notebook-style `28x56` images.
- The active default presets are dense notebook models because they line up best with the original notebook training flow and weight-viewing patterns.
- Alternative notebook presets remain available through `dd_cli train`.
- The heavy notebook runtime is now lazy-loaded; home, examples, presets, and health checks stay lightweight until inference or visualization is requested.
- Cloud deployment is read-only: shipped `.keras` artifacts are loaded from `/srv/models`, and missing artifacts do not trigger browser-side retraining.
- The App Engine service ended up on `F4`, not `F2`: live smoke showed that F2 still OOMed on the first inference request, so the measured production fix was a larger instance class plus bundled MNIST data and single-threaded torch/BLAS settings.

## Visualization semantics
- `feature_maps`
  - real activations from the selected notebook-derived model, rendered with `viridis`
- `prototype`
  - MNIST class means and first-layer weight maps, rendered with `binary_r` and `bone`
- `comparison`
  - generated scene plus the MNIST source digits and arithmetic-result context
- The web app surfaces all three visualization families for every level instead of limiting the browser to a partial subset.

## Batch export contract
- Generated batches remain deterministic and level-specific.
- The export bundle is still:
  - `images/`
  - `manifest.csv`
  - `dataset.npz`
- Batch exports intentionally avoid train/validation/test splitting; the training CLI owns training concerns.

## Deferred after Delta
- Estimator-era TensorFlow flows remain documentation/provenance only.
- Stacking and broader research-only notebook experiments are not part of the active runtime path yet.
- Handwriting input and browser-side training remain intentionally deferred beyond Delta.
