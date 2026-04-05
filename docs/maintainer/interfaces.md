# Interfaces

## Stable Public Surface

The documentation work in this repo does not add new runtime APIs. It makes the current public contracts explicit so future maintainers can preserve them deliberately.

## HTTP Endpoints

### `GET /`

- Returns the notebook-style guided lab page.
- Renders server-provided frontend config:
  - `mountBase`
  - `apiBase`
- Must work both at `/` and under `/doubledigits/`.

### `GET /healthz`

- Returns lightweight service health metadata.
- Must not force heavy model loading.

Example response fields:

- `status`
- `runtime_loaded`
- `cache_artifact`
- `allow_training`
- `models_dir`
- `levels`

### `GET /api/v1/examples?level=<single|double|arithmetic>`

- Returns curated example summaries for one level.
- Optional query:
  - `count`

Response shape:

- `level`
- `examples`
  - list of serialized `Example` summaries

### `GET /api/v1/presets?level=<single|double|arithmetic>`

- Returns preset metadata without loading model weights.
- Used by the browser advanced panel and by maintainers inspecting artifact readiness.

Response shape:

- `level`
- `default_preset`
- `presets`
  - `name`
  - `level`
  - `source_notebook`
  - `description`
  - `train_size`
  - `test_size`
  - `epochs`
  - `batch_size`
  - `default`
  - `artifact_ready`
  - `artifact_filename`

### `POST /api/v1/infer`

- Accepts either:
  - a curated example selector
  - a structured scene payload
- Optional `preset` overrides the level default.

Accepted payload patterns:

| Level | Required fields |
| --- | --- |
| `single` curated | `level`, `example_id` |
| `single` structured | `level`, plus either `mnist_index` or `digit` |
| `double` curated | `level`, `example_id` |
| `double` structured | `level`, `left`, `right` |
| `arithmetic` curated | `level`, `example_id` |
| `arithmetic` structured | `level`, `left`, `right`, `operator` |

Response shape:

- `level`
- `preset`
- `example`
- `prediction`
- `confidence`
- `top_classes`
- `explanation`
- `result_image_uri`

### `GET /api/v1/visualizations/<kind>`

- Supported kinds:
  - `feature_maps`
  - `prototype`
  - `comparison`
- Accepts the same example-selection arguments as the inference flow.
- Optional `preset` overrides the level default.

Base response fields:

- `kind`
- `level`
- `preset`
- `items`

## CLI Surface

Canonical entrypoint:

```powershell
python -m dd_cli
```

Commands:

| Command | Purpose |
| --- | --- |
| `dataset show` | inspect one raw MNIST sample |
| `examples list` | list curated examples for a level |
| `examples show` | inspect one curated or structured example |
| `examples generate` | export a deterministic labeled batch |
| `infer` | run baseline inference on one example or structured payload |
| `visualize` | build one visualization payload and optionally export files |
| `serve` | run the local Flask app |
| `train list` | list available notebook-derived presets |
| `train run` | train one named preset and write artifacts |

CLI behavior rules:

- `--json` is the machine-readable contract for scripting
- example selection mirrors the web service payload rules
- `train` is CLI-only by design
- `visualize --write-dir` exports PNGs derived from the visualization payload

## Stable Types And Contracts

### `MnistRecord`

Represents one resolved MNIST sample.

Fields:

- `split`
- `index`
- `digit`
- `image`

### `Example`

Represents one resolved guided-lab example plus its serialized display metadata.

Fields:

- `id`
- `level`
- `title`
- `image`
- `metadata`
- `explanation`
- `display_cmap`
- `comparison_sources`

### `InferenceResult`

Canonical runtime inference payload used by visualization and serialization layers.

Fields:

- `level`
- `preset_name`
- `prediction`
- `confidence`
- `top_classes`
- `explanation`
- `input_image`
- `example`
- `result_image_uri`

### `ModelPreset`

Registry entry for one notebook-derived preset.

Fields include:

- lineage metadata
- artifact naming
- input mode
- default train/test sizes
- batch size and epochs
- logits vs probability behavior

### `PreparedDataset`

Level-specific training/test arrays after normalization and shape preparation.

### `NotebookClassifier`

Owns one preset's artifact files, training behavior, prediction helpers, activation extraction, and first-layer inspection logic.

### `BaselineRuntime`

Selects a level-appropriate classifier, applies default preset policy, and returns normalized inference contracts across all levels.

### `DoubleDigitsService`

Web-facing orchestration layer for examples, presets, inference, visualizations, and health.

## Legacy Compatibility Helpers

`dd_core.legacy_api` preserves notebook-era names:

- `doubleDigits`
- `getDoubleDigits`
- `getOperator`
- `get_results`

These are compatibility helpers, not the preferred implementation surface for new maintainers. New code should use `ExampleCatalog`, render helpers, and the runtime/service layers directly.

## Environment Variables

### Runtime And Paths

| Variable | Meaning |
| --- | --- |
| `DOUBLEDIGITS_MODELS_DIR` | directory containing `.keras` and `.json` model artifacts |
| `DOUBLEDIGITS_DATA_DIR` | directory containing `mnist.npz` |
| `AIX_HUB_URL` | base URL for AIX navigation links |
| `APP_BASE_PATH` | local path-prefix simulation, usually `/doubledigits` when testing mount behavior |

### Artifact And Training Policy

| Variable | Meaning |
| --- | --- |
| `DOUBLEDIGITS_ARTIFACT_CACHE` | whether trained models are reused from disk |
| `DOUBLEDIGITS_ALLOW_TRAINING` | whether missing artifacts may be trained in the current runtime |
| `DOUBLEDIGITS_SINGLE_PRESET` | override default single-level preset |
| `DOUBLEDIGITS_DOUBLE_PRESET` | override default double-level preset |
| `DOUBLEDIGITS_ARITHMETIC_PRESET` | override default arithmetic-level preset |

### Level-Specific Training Overrides

For each level `SINGLE`, `DOUBLE`, and `ARITHMETIC`:

- `DOUBLEDIGITS_TRAIN_SIZE_<LEVEL>`
- `DOUBLEDIGITS_TEST_SIZE_<LEVEL>`
- `DOUBLEDIGITS_EPOCHS_<LEVEL>`

### Backend Tuning

- `DOUBLEDIGITS_TORCH_THREADS`
- `OMP_NUM_THREADS`
- `MKL_NUM_THREADS`
- `OPENBLAS_NUM_THREADS`
- `NUMEXPR_NUM_THREADS`

These are part of the operational contract because cloud execution relies on conservative thread counts to reduce cold-path memory overhead.

## Generated Export Layout

`python -m dd_cli examples generate` writes:

- `images/`
- `manifest.csv`
- `dataset.npz`

Contract rules:

- `manifest.csv` is the authoritative metadata table
- row order matches `dataset.npz`
- `dataset.npz` stores aligned arrays:
  - `images`
  - `targets`
  - `ids`
  - `metadata_json`

`python -m dd_cli visualize --write-dir` writes PNGs derived from visualization payloads. The file naming is slug-based and visualization-kind-specific.
