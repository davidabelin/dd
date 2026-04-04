# dd

Double-digits guided lab for AIX, exposed publicly as `doubledigits`.

## Current scope
- Guided three-level web lab:
  - single-digit recognition
  - two-digit composition
  - controlled arithmetic
- Shell-neutral CLI at `python -m dd_cli`
- Deterministic batch export with image files, a pandas-readable manifest, and aligned NumPy arrays
- Lightweight baseline inference plus documented proxy visualizations

## Layout
- `dd_cli/`
- `dd_core/`
- `dd_models/`
- `dd_visuals/`
- `dd_web/`
- `tests/`
- `docs/`
- `scripts/`
- `data/`
- `models/`

Stable user-facing terminal commands live in `dd_cli`. The `scripts/` directory remains reserved for one-off internal utilities.

## Install
```sh
python -m pip install -r requirements.txt
```

## Local web run
```sh
python run.py
```

Or use the CLI wrapper:

```sh
python -m dd_cli serve
```

Then open `http://127.0.0.1:5003/`.

## Terminal usage

List curated examples:

```sh
python -m dd_cli examples list --level double
```

Inspect one example:

```sh
python -m dd_cli examples show --level arithmetic --example-id arith_mul_34
```

Run inference from structured input:

```sh
python -m dd_cli infer --level arithmetic --left 6 --right 7 --operator multiply
```

Inspect visualization payloads and optionally write PNG artifacts:

```sh
python -m dd_cli visualize --kind comparison --level arithmetic --example-id arith_mul_34 --write-dir out/visuals
```

Generate a batch export:

```sh
python -m dd_cli examples generate --level double --count 12 --out out/double_batch
```

Use `--json` with `examples list`, `examples show`, `examples generate`, `infer`, and `visualize` for machine-readable output.

## Batch export layout

`python -m dd_cli examples generate` writes one level-specific directory containing:

- `images/`
  - one PNG per generated example
- `manifest.csv`
  - the authoritative metadata table, readable directly in pandas
- `dataset.npz`
  - aligned arrays for `images`, `targets`, `ids`, and `metadata_json`

Row order in `manifest.csv` matches array order in `dataset.npz`. Gamma does not create train/validation/test splits by default.

## Visualization kinds

The stable Gamma visualization set is:

- `feature_maps`
  - fixed-filter responses over the current image segments
- `prototype`
  - class-mean and coefficient-map views for the current prediction path
- `comparison`
  - the input segments and, when available, the rendered arithmetic result

These payloads are shared between the CLI and the web API.
