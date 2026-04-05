# Models And Artifacts

## Runtime Strategy

The live DD runtime keeps notebook-style model definitions but runs them through standalone Keras on the torch backend. This preserves notebook lineage while avoiding a TensorFlow dependency path that is not practical in the current local environment.

Important decisions:

- shipped runtime remains Keras-based
- double-digit and arithmetic tasks are direct whole-scene classifiers
- browser inference prefers prebuilt artifacts and is read-only in cloud

## Preset Registry

The canonical registry lives in `dd_models.baselines.PRESETS`.

### Single-Level Presets

| Preset | Notebook lineage | Input mode | Labels | Default |
| --- | --- | --- | --- | --- |
| `single_mnist_dense` | `digits_classifier.ipynb` | `channels` | `0..9` digit classes | yes |

### Double-Level Presets

| Preset | Notebook lineage | Input mode | Labels | Default |
| --- | --- | --- | --- | --- |
| `double_with_mnist_dense` | `double_digits_with_MNIST.ipynb` | `image` | `0..99` whole-scene values | no |
| `double_project_minimal` | `digits_project.ipynb` | `channels` | `0..99` whole-scene values | no |
| `double_project_cnn` | `digits_project.ipynb` | `channels` | `0..99` whole-scene values | no |
| `double_project_mixed` | `digits_project.ipynb` | `channels` | `0..99` whole-scene values | no |
| `double_project_modelx` | `digits_project.ipynb` | `channels` | `0..99` whole-scene values | yes |
| `double_minimal_conv` | `minimal_convolution_double_digits.ipynb` | `channels` | `0..99` whole-scene values | no |
| `double_minimal_stack` | `minimal_convolution_double_digits.ipynb` | `channels` | `0..99` whole-scene values | no |
| `double_classifier_diy_conv` | `digits_classifier.ipynb` | `channels` | `0..99` whole-scene values | no |
| `double_classifier_dense` | `digits_classifier.ipynb` | `channels` | `0..99` whole-scene values | no |

### Arithmetic-Level Presets

| Preset | Notebook lineage | Input mode | Labels | Default |
| --- | --- | --- | --- | --- |
| `arithmetic_cnn` | `arithmetic_double_digits.ipynb` | `channels` | `0..99` result values | no |
| `arithmetic_new_model` | `arithmetic_double_digits.ipynb` | `channels` | `0..99` result values | no |
| `arithmetic_modelx` | `arithmetic_double_digits.ipynb` | `channels` | `0..99` result values | yes |

## Label Semantics

### Single

- prediction is a digit class
- `prediction["digit"]` is the top class id

### Double

- prediction class is the entire two-digit value
- `value = left_digit * 10 + right_digit`
- runtime serialization expands that value into:
  - `left_digit`
  - `right_digit`
  - `value`

### Arithmetic

- scene metadata stores:
  - left digit
  - right digit
  - operator token
  - operator symbol
- prediction class is the arithmetic result value only
- `result_image_uri` is derived from that predicted result value

Important invariant:

- arithmetic models do not separately predict the operator or operand digits
- those fields come from the constructed example metadata

## Artifact Layout

Each cached preset produces two files in `models/`:

- `<artifact_name>.keras`
  - serialized Keras model
- `<artifact_name>.json`
  - training metadata written by `NotebookClassifier.train`

Metadata JSON records include:

- `preset`
- `level`
- `source_notebook`
- `train_size`
- `test_size`
- `epochs`
- `batch_size`
- `evaluation`
- `history`

## Default Versus Override Behavior

Default runtime presets come from `DEFAULT_PRESETS`:

- `single` -> `single_mnist_dense`
- `double` -> `double_project_modelx`
- `arithmetic` -> `arithmetic_modelx`

These may be overridden:

- globally by environment variable
- per request through the web API
- per command through the CLI

Validation rules:

- preset name must exist in `PRESETS`
- preset level must match the requested level

## Training Policy

`NotebookClassifier.train` owns the canonical training path.

Key rules:

- if artifact caching is enabled and the artifact already exists, training can short-circuit unless `force=True`
- if training is disabled and the artifact is missing, runtime usage must fail clearly
- training-size and epoch overrides may come from CLI arguments or level-specific environment variables

The CLI is the explicit maintainer surface for training:

```powershell
python -m dd_cli train list
python -m dd_cli train run --preset arithmetic_modelx
```

## Explainability Artifacts

The model layer also exposes inspection helpers used by `dd_visuals`:

- activation maps
- first-layer weight maps
- class means
- notebook-style guessing/reporting helpers

These outputs are part of the documentation contract because the web and CLI surfaces depend on them for visualization payloads and export behavior.

## Read-Only Cloud Posture

The App Engine deployment uses a read-only inference posture.

Expected cloud behavior:

- `.keras` and `.json` artifacts are shipped with the service
- `DOUBLEDIGITS_MODELS_DIR=/srv/models`
- `DOUBLEDIGITS_DATA_DIR=/srv/data`
- `DOUBLEDIGITS_ALLOW_TRAINING=0`
- browser requests must not trigger training

This matters for both reliability and memory behavior. Cold-path model training is not part of the mounted AIX production contract.
