# Double-digits (`dd`)

Maintainer-facing home for the Double-digits lab: a notebook-faithful MNIST-derived project that runs as both a standalone Flask app and the AIX-mounted `/doubledigits` service.

## Canonical Maintainer Docs

The authoritative maintainer path now lives under [docs/maintainer/README.md](docs/maintainer/README.md).

- [Maintainer index](docs/maintainer/README.md)
- [Overview](docs/maintainer/overview.md)
- [Architecture](docs/maintainer/architecture.md)
- [Interfaces](docs/maintainer/interfaces.md)
- [Models and artifacts](docs/maintainer/models-and-artifacts.md)
- [Operations](docs/maintainer/operations.md)

Historical migration notes, provenance notes, and phase plans remain in `docs/` as archival references. They now supplement the maintainer docs instead of acting as the primary documentation set.

## Project Role In AIX

`dd` is the code-owning repository for the Double-digits lab. AIX does not reimplement the lab; it bridges this repo into the umbrella app and mounts it under `/doubledigits`.

- Standalone local run: `python run.py`
- Standalone CLI entrypoint: `python -m dd_cli`
- AIX mount path: `/doubledigits`
- AIX bridge adapter: `aix/aix_web/labs/doubledigits_adapter.py` in the sibling AIX repo

This repo therefore needs to document both:

- its local runtime and maintainership contracts
- the external contract AIX depends on when it imports and mounts `dd_web.create_app`

## Current Product Shape

The live project is a guided three-level lab derived from the legacy notebooks:

- `single`
  - raw `28x28` MNIST digit inspection and classification
- `double`
  - direct `28x56` whole-scene two-digit classification
- `arithmetic`
  - direct `28x56` arithmetic scenes with embedded notebook-style operators

The current runtime is MNIST-first, notebook-derived, and built around standalone Keras on the torch backend. Browser inference is read-only in cloud deployments and uses shipped `.keras` artifacts.

## Package Map

| Package | Responsibility |
| --- | --- |
| `dd_core` | Dataset loading, curated/generated example construction, rendering primitives, export helpers, legacy notebook-name compatibility |
| `dd_models` | Keras backend bootstrap, preset registry, artifact-backed training/inference runtime |
| `dd_visuals` | Explainability payload builders for feature maps, prototypes, and comparison strips |
| `dd_web` | Flask app factory, blueprints, lazy runtime service, local serving helpers, mount-safe frontend config |
| `dd_cli` | Shell-neutral interface for dataset inspection, examples, inference, visualizations, serving, and training |

## Quick Start

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the standalone web app:

```powershell
python run.py
```

Or:

```powershell
python -m dd_cli serve
```

Then open `http://127.0.0.1:5003/`.

Run the baseline tests:

```powershell
python -m pytest tests/test_core.py tests/test_cli.py tests/test_app.py -q
```

Test local mounted behavior:

```powershell
$env:APP_BASE_PATH = "/doubledigits"
python run.py
```

Then open `http://127.0.0.1:5003/doubledigits/`.

## CLI Surface

```powershell
python -m dd_cli dataset show --split test --index 0 --out out/mnist_0.png
python -m dd_cli examples show --level arithmetic --example-id arith_div_84
python -m dd_cli infer --level arithmetic --left 8 --right 4 --operator divide
python -m dd_cli visualize --kind comparison --level arithmetic --example-id arith_mul_34
python -m dd_cli train list
python -m dd_cli train run --preset double_project_modelx
```

Use `--json` with `dataset show`, `examples`, `infer`, `visualize`, and `train` for scripting.

## HTTP Surface

- `GET /`
  - notebook-style guided lab page
- `GET /healthz`
  - lightweight health payload that does not force model loading
- `GET /api/v1/examples?level=<single|double|arithmetic>`
  - curated example summaries
- `GET /api/v1/presets?level=<single|double|arithmetic>`
  - notebook-derived preset metadata without loading weights
- `POST /api/v1/infer`
  - inference for curated or structured payloads, with optional `preset`
- `GET /api/v1/visualizations/<feature_maps|prototype|comparison>`
  - explainability payloads for the same example flow, with optional `preset`

When mounted through AIX, these same routes live under `/doubledigits/...`.

## Model And Artifact Behavior

Default shipped presets:

- `single_mnist_dense`
- `double_project_modelx`
- `arithmetic_modelx`

Default override environment variables:

- `DOUBLEDIGITS_SINGLE_PRESET`
- `DOUBLEDIGITS_DOUBLE_PRESET`
- `DOUBLEDIGITS_ARITHMETIC_PRESET`

Training can be disabled with:

- `DOUBLEDIGITS_ALLOW_TRAINING=0`

The live App Engine deployment ships cached artifacts in `models/`, points `DOUBLEDIGITS_MODELS_DIR` at `/srv/models`, points `DOUBLEDIGITS_DATA_DIR` at `/srv/data`, and keeps browser inference read-only.

## Historical Reference Docs

These files remain useful for provenance and migration detail, but they are archival references rather than the primary maintainer path:

- [Design notes](docs/doubledigits_design.md)
- [Artifact provenance](docs/artifact_provenance.md)
- [Migration inventory](docs/migration_inventory.md)
- [Alpha plan](docs/DOUBLEDIGITS_PLAN_alpha.md)
- [Beta plan](docs/DOUBLEDIGITS_PLAN_beta.md)
- [Gamma plan](docs/DOUBLEDIGITS_PLAN_gamma.md)
- [Delta plan](docs/DOUBLEDIGITS_PLAN_delta.md)

## Known Environment Note

On Windows with Python `3.14`, pytest runs that exercise the Keras torch backend can emit a post-success shutdown trace even when the tests themselves pass. The current DD baseline treats that as an environment/runtime issue rather than a product regression.
