# dd

Double-digits guided lab for AIX, now restored to an MNIST-first runtime derived from the legacy notebooks.

## Current scope
- Guided three-level lab:
  - raw single-digit MNIST
  - direct 28x56 two-digit classification
  - direct 28x56 arithmetic scenes with embedded notebook-style operators
- Shell-neutral CLI at `python -m dd_cli`
- Notebook-derived Keras model presets with cached `.keras` artifacts
- Deterministic batch export with image files, a pandas-readable manifest, and aligned NumPy arrays
- Notebook-style visualizations using `binary_r`, `viridis`, and `bone`

## Install
```sh
python -m pip install -r requirements.txt
```

The modern runtime uses standalone Keras on the torch backend. That keeps the notebook-style model definitions while avoiding the old sklearn fallback.

## Local web run
```sh
python run.py
```

Or:

```sh
python -m dd_cli serve
```

Then open `http://127.0.0.1:5003/`.

## CLI usage

Show one raw MNIST sample:

```sh
python -m dd_cli dataset show --split test --index 0 --out out/mnist_0.png
```

Inspect a curated arithmetic scene:

```sh
python -m dd_cli examples show --level arithmetic --example-id arith_div_84
```

Inspect a single-level example directly from the MNIST split:

```sh
python -m dd_cli examples show --level single --mnist-index 0 --split test
```

Run inference from structured notebook-style input:

```sh
python -m dd_cli infer --level arithmetic --left 8 --right 4 --operator divide
```

Inspect learned activations or comparison views:

```sh
python -m dd_cli visualize --kind feature_maps --level double --example-id double_12 --write-dir out/feature_maps
python -m dd_cli visualize --kind comparison --level arithmetic --example-id arith_div_84
```

Generate a labeled batch export:

```sh
python -m dd_cli examples generate --level double --count 12 --out out/double_batch
```

List and train notebook-derived presets:

```sh
python -m dd_cli train list
python -m dd_cli train run --preset double_project_modelx
```

Use `--json` with `dataset show`, `examples`, `infer`, `visualize`, and `train` commands for scripting.

## First-run model behavior

If a cached `.keras` artifact is missing, the runtime trains the default notebook-derived preset for that level and stores it in `models/`.

Default presets:
- `single_mnist_dense`
- `double_project_modelx`
- `arithmetic_modelx`

Override them with:
- `DOUBLEDIGITS_SINGLE_PRESET`
- `DOUBLEDIGITS_DOUBLE_PRESET`
- `DOUBLEDIGITS_ARITHMETIC_PRESET`

Training-size overrides are also supported per level:
- `DOUBLEDIGITS_TRAIN_SIZE_SINGLE`, `DOUBLEDIGITS_TEST_SIZE_SINGLE`, `DOUBLEDIGITS_EPOCHS_SINGLE`
- `DOUBLEDIGITS_TRAIN_SIZE_DOUBLE`, `DOUBLEDIGITS_TEST_SIZE_DOUBLE`, `DOUBLEDIGITS_EPOCHS_DOUBLE`
- `DOUBLEDIGITS_TRAIN_SIZE_ARITHMETIC`, `DOUBLEDIGITS_TEST_SIZE_ARITHMETIC`, `DOUBLEDIGITS_EPOCHS_ARITHMETIC`

## Batch export layout

`python -m dd_cli examples generate` writes:
- `images/`
- `manifest.csv`
- `dataset.npz`

`manifest.csv` is the authoritative metadata table. Row order matches `dataset.npz`.

## Visualization kinds

- `feature_maps`
  - learned activation maps rendered with `viridis`
- `prototype`
  - MNIST class means and first-layer notebook-style weight maps rendered with `binary_r` and `bone`
- `comparison`
  - the generated scene, its MNIST ground-truth source tiles, the notebook operator overlay when applicable, and the predicted arithmetic result image
