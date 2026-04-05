# Sub-Project DD: Classic MNIST-Derived Double-Digits Lab

Double-digits guided lab for AIX, now restored to an MNIST-first runtime derived from the legacy notebooks.

## Current scope
- Guided three-level lab:
  - raw single-digit MNIST
  - direct 28x56 two-digit classification
  - direct 28x56 arithmetic scenes with embedded notebook-style operators
- Notebook-faithful web app with anchored single/double/arithmetic sections, advanced preset browsing, and notebook-derived comparison/prototype/feature-map panels
- Bundled `data/mnist.npz` archive so curated examples and cloud cold starts do not depend on live Keras dataset downloads
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

To test the mounted AIX path locally:

```powershell
$env:APP_BASE_PATH = "/doubledigits"
python run.py
```

Then open `http://127.0.0.1:5003/doubledigits/`.

## Web and API surface

- `GET /`
  - notebook-style guided lab page with explicit run buttons and advanced preset panels
- `GET /healthz`
  - lightweight service health payload that does not load model weights
- `GET /api/v1/examples?level=<single|double|arithmetic>`
  - curated example summaries for one level
- `GET /api/v1/presets?level=<single|double|arithmetic>`
  - notebook-derived preset metadata for the browser advanced panel
- `POST /api/v1/infer`
  - shared-runtime inference for a curated or structured payload, with optional `preset`
- `GET /api/v1/visualizations/<feature_maps|prototype|comparison>`
  - visualization payloads for the same shared-runtime example flow, with optional `preset`

When mounted under AIX, the same routes live under `/doubledigits/...`; the frontend reads server-rendered `mountBase` and `apiBase` values and never hard-codes root-relative API paths.

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

Override the active notebook preset when needed:

```sh
python -m dd_cli infer --level single --example-id single_5 --preset single_mnist_dense
python -m dd_cli visualize --kind prototype --level arithmetic --example-id arith_mul_34 --preset arithmetic_modelx
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

Disable auto-training with:
- `DOUBLEDIGITS_ALLOW_TRAINING=0`

That is the default cloud posture. The App Engine deployment ships the checked-in `.keras` artifacts, points `DOUBLEDIGITS_MODELS_DIR` at `/srv/models`, and keeps browser inference read-only.
The same deployment ships `data/mnist.npz` and points `DOUBLEDIGITS_DATA_DIR` at `/srv/data` so lightweight example routes stay off the Keras download path.

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

## Cloud deployment notes

- `app.aix.yaml` is the dedicated App Engine config for the mounted `/doubledigits` service.
- Delta tested `instance_class: F2`, but live cold-inference smoke still exceeded its memory ceiling. The production fix is `instance_class: F4`, which now serves the mounted `/doubledigits/` home, examples, and inference routes successfully.
- `KERAS_HOME` and `MPLCONFIGDIR` are directed into `/tmp` for writable runtime caches in App Engine Standard.
- Torch and BLAS thread counts are pinned to `1` in cloud to reduce cold-path memory overhead.

## Known issue

- On Windows with Python 3.14, pytest runs that exercise the Keras torch backend can still print a post-success fatal access-violation trace during interpreter shutdown. The DD test suites pass before that trace appears, and equivalent non-pytest inference scripts exit cleanly, so this is currently tracked as an environment/runtime issue rather than a DD deployment blocker.
