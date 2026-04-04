# Double-digits Design Notes

Status refresh: 2026-04-04

## Current product shape
- The project is a guided lab, not a notebook host and not a training console.
- The core teaching arc still runs through three levels:
  - single-digit recognition
  - two-digit composition
  - arithmetic scenes built from two digits and an operator
- Gamma adds a first-class terminal interface so the same lab concepts can be used from a regular command line as well as through the web app.

## Gamma command surface
- `python -m dd_cli examples list`
  - list curated examples for one level
- `python -m dd_cli examples show`
  - inspect one curated or structured example
- `python -m dd_cli examples generate`
  - generate a deterministic labeled batch for one level
- `python -m dd_cli infer`
  - run baseline inference for one example or structured input
- `python -m dd_cli visualize`
  - build one stable visualization payload and optionally export PNG artifacts
- `python -m dd_cli serve`
  - run the same standalone Flask app that `run.py` launches

The CLI is deliberately shell-neutral. Stable user-facing commands belong in `dd_cli`; `scripts/` stays reserved for ad hoc internal helpers.

## Batch export contract
- Generated batches are deterministic and level-specific.
- Gamma writes three artifacts together:
  - `images/` for direct inspection
  - `manifest.csv` as the authoritative metadata table
  - `dataset.npz` as the aligned numeric bundle
- Gamma does not introduce train/validation/test splitting or training workflows. Those remain future concerns for a training-focused phase.

## Visualization semantics
- `feature_maps`
  - proxy views created by fixed image filters over the current segments
- `prototype`
  - class-mean and coefficient-map views derived from the baseline classifier and operator templates
- `comparison`
  - the current input segments and the rendered arithmetic result when available

These are intentionally lightweight explanatory artifacts. They do not claim parity with notebook-era learned CNN activations. That learned-activation path remains deferred until the project has exported learned models worth inspecting.

## Deferred after Gamma
- Web-copy polish and broader frontend refinement move to Delta.
- Handwriting input, handwritten-style output polish, retraining flows, and alternative-model experiments stay outside Gamma.
- TensorFlow Estimator-era code remains documentation/provenance material rather than active runtime code.
