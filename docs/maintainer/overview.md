# Overview

## Purpose

`dd` is the code-owning repository for the Double-digits lab in the AIX Project. It takes legacy notebook ideas and turns them into a maintainable Python application with shared runtime logic, a guided web interface, and a shell-neutral CLI.

The repo has two deployment contexts:

- standalone local app for direct development and testing
- AIX-mounted lab under `/doubledigits`

That dual role is part of the product contract. Maintainers should preserve both paths whenever changing imports, configuration, routes, or frontend URL handling.

## Product Shape

The lab exposes three levels that share the same MNIST lineage but differ in scene construction and label semantics:

| Level | Image shape | Task | Canonical label space |
| --- | --- | --- | --- |
| `single` | `28x28` | classify one MNIST digit | `0..9` |
| `double` | `28x56` | classify a whole two-digit scene directly | `0..99` |
| `arithmetic` | `28x56` | classify the result of a handwritten arithmetic scene | `0..99` |

Important invariant:

- `double` and `arithmetic` are whole-scene classifiers.
- They do not decompose the scene into two independent digit predictions and then reconstruct the answer.

## Package Responsibilities

### `dd_core`

- owns raw data access from `data/mnist.npz`
- defines curated and generated examples
- preserves notebook-era arithmetic semantics and legacy helper names
- renders notebook-style scenes, glyphs, result rasters, PNGs, and export bundles

### `dd_models`

- bootstraps standalone Keras on the torch backend
- registers notebook-derived presets and their training defaults
- loads or trains cached `.keras` artifacts
- exposes shared inference and explainability helpers through `BaselineRuntime` and `NotebookClassifier`

### `dd_visuals`

- turns runtime/model outputs into browser- and CLI-friendly visualization payloads
- owns the `feature_maps`, `prototype`, and `comparison` payload families

### `dd_web`

- owns the Flask application factory and local serving helpers
- keeps the heavy runtime lazy so home, examples, presets, and health can remain lightweight
- injects `mountBase` and `apiBase` so the same frontend works both standalone and under `/doubledigits`

### `dd_cli`

- exposes a stable maintainable shell interface for dataset inspection, example browsing, inference, visualization, serving, and training
- reuses the same service/runtime layers as the web app where practical

## Relationship To AIX

The AIX repo imports this repo rather than copying it.

- AIX bridge variable: `AIX_DOUBLEDIGITS_REPO`
- AIX adapter target: `dd_web.create_app`
- Mounted route prefix: `/doubledigits`

The Double-digits repo therefore owns:

- the Flask app contract
- the API contract
- the artifact/runtime contract
- the mount-safe frontend behavior

AIX owns:

- repo discovery and import-path bridging
- umbrella navigation and deployment composition
- the parent route namespace in which DD is mounted

## Source Lineage

The current runtime remains explicitly notebook-derived. The main lineage sources are:

- `double_digits_with_MNIST.ipynb`
- `minimal_convolution_double_digits.ipynb`
- `digits_project.ipynb`
- `arithmetic_double_digits.ipynb`
- `digits_classifier.ipynb`
- `double_digits_classifier.ipynb`

Maintainers should keep that lineage visible in docs and docstrings because several product decisions are fidelity choices rather than generic ML defaults. The divide-by-zero sentinel `99`, the direct `28x56` classification path, and the notebook color conventions all fall into that category.
