# Double-digits Migration Inventory

Status refresh: 2026-04-04

This file is the working migration ledger for notebook-to-`dd` transfer work. It is organized by capability, not by notebook, so Gamma can execute against one master check-off list.

## Source repos
- Legacy source: `C:\Users\David\Documents\Repositories\double-digits`
- New app target: `C:\Users\David\Documents\Local_Python\dd`

## Status legend
- `done`: already migrated into the accepted canonical location
- `partial`: present but still needs parity cleanup, richer tests/docs, or CLI alignment
- `pending`: in scope for Gamma but not implemented in canonical form yet
- `docs-only`: preserved as documentation, narrative, or provenance rather than live code
- `deferred`: explicitly retained in the ledger for later phases

## Exposure legend
- `web+cli`: stable behavior should be available both in the web lab and in `python -m dd_cli`
- `web-only`: behavior belongs in the web app, not as a first-class terminal command
- `cli-only`: behavior belongs in terminal tooling, not the guided web lab
- `docs-only`: preserved in documentation only
- `deferred`: not part of Gamma exposure

## Notebook source register

| Notebook | Role | Primary ledger sections |
|---|---|---|
| `double_digits_with_MNIST.ipynb` | main extraction source | core composition/data; inference/models/artifacts |
| `minimal_convolution_double_digits.ipynb` | main extraction source | inference/models/artifacts; visuals/explainability |
| `digits_project.ipynb` | main extraction source | arithmetic semantics/operators; inference/models/artifacts; visuals/explainability; narrative |
| `arithmetic_double_digits.ipynb` | main extraction source | arithmetic semantics/operators; inference/models/artifacts; training/experimental/deferred |
| `digits_classifier.ipynb` | docs-only reference | inference/models/artifacts; visuals/explainability; narrative |
| `double_digits_classifier.ipynb` | docs-only reference | inference/models/artifacts; visuals/explainability; narrative |
| `introduction-to-ensembling-stacking-in-python.ipynb` | deferred reference | training/experimental/deferred |

`.ipynb_checkpoints/` duplicates are intentionally ignored.

## Master capability ledger

### Core composition and data

- [x] Canonical digit-bank loading, resizing, and variant lookup
  - Status: `done`
  - Source notebook(s): `digits_project.ipynb`, `double_digits_with_MNIST.ipynb`
  - Source lineage: dataset setup cells, `scale_array`, notebook image reshaping and normalization steps
  - Current `dd` state/path: `dd_core/dataset.py`
  - Target destination: keep canonical loading and normalization in `dd_core.dataset`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, `docs/artifact_provenance.md`
  - Planned tests: keep and extend `tests/test_core.py` shape and variant coverage
  - Docstring requirement: preserve module and function docstrings for dataset helpers; add rationale when normalization assumptions change
  - Gamma action: verify notebook parity notes, then keep the current dataset module as the single source of truth

- [x] Two-digit image composition helper
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: `doubleDigits`
  - Current `dd` state/path: `dd_core/examples.py`, `dd_core/render.py`, `dd_core/legacy_api.py`
  - Target destination: keep notebook-lineage API in `dd_core.examples.doubleDigits`, backed by `dd_core.render.compose_pair`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `docs/doubledigits_design.md`, level-2 lab copy
  - Planned tests: retain deterministic shape tests in `tests/test_core.py`; add CLI parity checks when `dd_cli infer` lands
  - Docstring requirement: retain docstrings on the public helper and render path; add invariants if width or digit ordering changes
  - Gamma action: keep canonical helper names stable, document left/right ordering explicitly, and reuse in CLI inference flows

- [x] Deterministic curated example catalog for double-digit scenes
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`
  - Source lineage: `getDoubleDigits`, `getDDs`, notebook dataset assembly loops
  - Current `dd` state/path: `dd_core/examples.py`, `dd_core/constants.py`
  - Target destination: keep canonical example generation in `dd_core.examples.ExampleCatalog`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, level selectors in `dd_web/templates/pages/home.html`
  - Planned tests: keep example-shape coverage in `tests/test_core.py`; add example-list contract tests for future CLI output
  - Docstring requirement: document deterministic catalog behavior and level normalization rules
  - Gamma action: add explicit notes about curated versus structured generation and reuse the catalog directly from CLI commands

- [ ] Bulk synthetic dataset generation for future export and parity fixtures
  - Status: `pending`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `digits_classifier.ipynb`, `double_digits_classifier.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: `getDoubleDigits`, `getDDs`, `get_new_data`
  - Current `dd` state/path: not present as a dedicated export-oriented module
  - Target destination: add non-web dataset builders under `dd_core` or `scripts/` first, then expose stable fixture/export flows through `dd_cli examples`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `docs/doubledigits_design.md`
  - Planned tests: add deterministic fixture-generation tests and CLI snapshot/schema tests
  - Docstring requirement: full module, function, and parameter docstrings once extraction/export helpers exist
  - Gamma action: decide the smallest useful export surface for Gamma and avoid reintroducing notebook-only batching code

- [x] Notebook-lineage compatibility shim for canonical helper names
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: legacy helper names `doubleDigits`, `getDoubleDigits`, `getOperator`, `get_results`
  - Current `dd` state/path: `dd_core/legacy_api.py`
  - Target destination: keep compatibility imports in `dd_core.legacy_api` until Gamma no longer needs notebook-name continuity
  - CLI exposure: `web+cli`
  - Docs/UI destination: `docs/migration_inventory.md`
  - Planned tests: add one import/smoke test if Gamma expands compatibility usage
  - Docstring requirement: module docstring plus clear comment on why the shim exists
  - Gamma action: preserve the shim while inventory-driven migration is active; revisit only after notebook lineage is fully documented

### Arithmetic semantics and operators

- [x] Operator glyph rendering for arithmetic scenes
  - Status: `done`
  - Source notebook(s): `arithmetic_double_digits.ipynb`
  - Source lineage: `getOperator`
  - Current `dd` state/path: `dd_core/examples.py`, `dd_core/render.py`, `dd_core/constants.py`, `dd_core/legacy_api.py`
  - Target destination: keep canonical operator rendering in `dd_core.render.operator_canvas` with user-facing helper access from `dd_core.examples.getOperator`
  - CLI exposure: `web+cli`
  - Docs/UI destination: level-3 UI copy, `docs/doubledigits_design.md`
  - Planned tests: keep arithmetic scene shape coverage in `tests/test_core.py`; add CLI visualization checks once the terminal surface exists
  - Docstring requirement: retain operator-shape and supported-operator docstrings; document any intentional limits
  - Gamma action: keep `add`, `subtract`, and `multiply` as the supported Gamma operator set and document the omission of division

- [x] Arithmetic scene composition from left digit, operator, and right digit
  - Status: `done`
  - Source notebook(s): `arithmetic_double_digits.ipynb`, `digits_project.ipynb`
  - Source lineage: arithmetic-mode `doubleDigits`
  - Current `dd` state/path: `dd_core/render.py`, `dd_core/examples.py`
  - Target destination: keep canonical arithmetic scene assembly in `dd_core.render.compose_arithmetic`
  - CLI exposure: `web+cli`
  - Docs/UI destination: level-3 lab copy, `docs/doubledigits_design.md`
  - Planned tests: retain arithmetic fixture coverage in `tests/test_core.py`; add CLI infer/visualize parity tests
  - Docstring requirement: full docstrings on scene assembly and scene-size assumptions
  - Gamma action: document scene segmentation explicitly so web and CLI consumers share one contract

- [x] Arithmetic result semantics and explanation text
  - Status: `done`
  - Source notebook(s): `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: arithmetic rule cells; notebook arithmetic answer logic
  - Current `dd` state/path: `dd_core/examples.py`
  - Target destination: keep canonical rule evaluation in `dd_core.examples.get_results`
  - CLI exposure: `web+cli`
  - Docs/UI destination: level-3 result text, `docs/doubledigits_design.md`
  - Planned tests: keep arithmetic-result assertions in `tests/test_core.py`; extend with edge-case fixtures if Gamma broadens operators
  - Docstring requirement: preserve rule semantics, especially the non-negative subtraction policy
  - Gamma action: keep the current explanation contract and reference it in CLI output formatting

- [x] Rendered result image generation for arithmetic outputs
  - Status: `done`
  - Source notebook(s): `arithmetic_double_digits.ipynb`, `digits_project.ipynb`
  - Source lineage: result rendering ideas and handwritten-style result display intent
  - Current `dd` state/path: `dd_core/render.py`, `dd_core/examples.py`, `dd_models/baselines.py`
  - Target destination: keep simple result raster generation in `dd_core.render.number_to_image` and `ExampleCatalog.render_result_image`
  - CLI exposure: `web+cli`
  - Docs/UI destination: level-3 lab result panel, `docs/artifact_provenance.md`
  - Planned tests: retain arithmetic result image assertions in `tests/test_core.py`; add CLI file/stdout mode tests later
  - Docstring requirement: document the current raster style and note that handwritten-output polish is not yet implemented
  - Gamma action: keep the current result image as the baseline and separate any later handwriting polish into a deferred track

- [ ] Arithmetic extras beyond the current operator set
  - Status: `deferred`
  - Source notebook(s): `arithmetic_double_digits.ipynb`
  - Source lineage: division branch, broader operator experiments, alternate arithmetic policies
  - Current `dd` state/path: intentionally omitted from active code
  - Target destination: future arithmetic extension after Gamma, likely `dd_core.examples` plus CLI/web validation layers
  - CLI exposure: `deferred`
  - Docs/UI destination: `docs/doubledigits_design.md`
  - Planned tests: future arithmetic edge-case and policy tests only when scope is expanded
  - Docstring requirement: full docstrings if activated later; no Gamma code changes required
  - Gamma action: inventory only; do not implement division or alternate arithmetic policies in Gamma by default

### Inference, models, and artifacts

- [x] Unified example-to-inference contract for all three levels
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: notebook prediction flows normalized into one runtime contract
  - Current `dd` state/path: `dd_models/baselines.py`, `dd_web/runtime.py`
  - Target destination: keep one canonical inference contract in `dd_models.baselines.InferenceResult` and `BaselineRuntime`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, `docs/artifact_provenance.md`
  - Planned tests: retain `tests/test_core.py` inference coverage and add future CLI contract tests
  - Docstring requirement: preserve class and method docstrings; add schema notes when payloads change
  - Gamma action: build CLI on top of the current runtime contract rather than creating a separate inference path

- [x] Single-digit baseline classifier artifact and loader
  - Status: `done`
  - Source notebook(s): `digits_classifier.ipynb`, `double_digits_with_MNIST.ipynb`
  - Source lineage: baseline single-digit recognition concepts, notebook classifier lineage
  - Current `dd` state/path: `dd_models/baselines.py`, `models/single_digit_logreg.joblib` when cached
  - Target destination: keep baseline artifact caching and loading in `dd_models.baselines.SingleDigitLogRegModel`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `docs/artifact_provenance.md`
  - Planned tests: retain baseline runtime tests in `tests/test_core.py`; add cache/no-cache CLI smoke tests later
  - Docstring requirement: preserve artifact and cache behavior docstrings
  - Gamma action: keep the lightweight logistic-regression baseline as the active Gamma model path

- [x] Two-digit recognition by composing two single-digit predictions
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `double_digits_classifier.ipynb`
  - Source lineage: double-digit prediction flow and label semantics
  - Current `dd` state/path: `dd_models/baselines.py`
  - Target destination: keep the decomposition-first logic in `BaselineRuntime.infer_from_example`
  - CLI exposure: `web+cli`
  - Docs/UI destination: level-2 explanation copy, `docs/doubledigits_design.md`
  - Planned tests: retain two-digit inference assertions in `tests/test_core.py`; add CLI parity tests once `infer` exists
  - Docstring requirement: document label/value semantics and confidence composition
  - Gamma action: keep composition-first recognition as the canonical Gamma behavior

- [x] Arithmetic recognition by digit recognition plus operator template matching
  - Status: `done`
  - Source notebook(s): `arithmetic_double_digits.ipynb`, `digits_project.ipynb`
  - Source lineage: arithmetic recognition flow, operator overlay logic, result computation
  - Current `dd` state/path: `dd_models/baselines.py`
  - Target destination: keep the current arithmetic inference stack in `BaselineRuntime` and `OperatorTemplateModel`
  - CLI exposure: `web+cli`
  - Docs/UI destination: level-3 explanation copy, `docs/artifact_provenance.md`
  - Planned tests: retain arithmetic inference coverage in `tests/test_core.py`; add CLI and API parity checks later
  - Docstring requirement: document operator confidence calculation and result-image behavior
  - Gamma action: expose the same arithmetic path through CLI without adding a second implementation

- [ ] Prediction sampling and answer-reporting helpers
  - Status: `partial`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: `guessing`, notebook-table `get_results`, `getAnswers`, `no_guessing`, `no_get_results`
  - Current `dd` state/path: partly replaced by `dd_models/baselines.py`, `dd_web/runtime.py`, and API payload fields such as `prediction`, `confidence`, `top_classes`, and `explanation`
  - Target destination: normalize human-readable reporting in `dd_cli infer` and shared response-format helpers instead of notebook DataFrames
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, level result panels
  - Planned tests: add CLI output-schema tests and API/CLI parity assertions
  - Docstring requirement: full docstrings on any shared formatting helper and CLI command entrypoint
  - Gamma action: finish the reporting layer in terminal form and avoid reviving notebook-style ad hoc tables

- [ ] tf.keras training and export utilities for future learned artifacts
  - Status: `deferred`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: `create_model`, `train_model`, `train`, `plot_curve`, `plotLearningCurves`, model-family build cells
  - Current `dd` state/path: not present as active product code
  - Target destination: future `dd_models` training/export utilities plus optional `scripts/` or CLI training commands after Gamma
  - CLI exposure: `deferred`
  - Docs/UI destination: `docs/artifact_provenance.md`, `docs/doubledigits_design.md`
  - Planned tests: future artifact-export and deterministic-load tests only when the training path is activated
  - Docstring requirement: full module, class, and function docstrings when implemented later
  - Gamma action: keep in the ledger, but do not implement training/export utilities in Gamma's default scope

- [ ] Estimator-era dataframe parsing and training stack
  - Status: `docs-only`
  - Source notebook(s): `digits_classifier.ipynb`, `double_digits_classifier.ipynb`
  - Source lineage: `parse_dataset`, `parse_labels_and_features`, `construct_feature_columns`, `create_training_input_fn`, `create_predict_input_fn`, `train_linear_classification_model`, `train_nn_classification_model`
  - Current `dd` state/path: intentionally not ported as active code
  - Target destination: document why this stack is not part of the modern app; do not migrate the code path itself
  - CLI exposure: `docs-only`
  - Docs/UI destination: `docs/artifact_provenance.md`, `docs/doubledigits_design.md`
  - Planned tests: none beyond documentation review; no runtime parity expected
  - Docstring requirement: N/A for code because Gamma should not implement it; narrative text should explain the replacement path
  - Gamma action: write comparison/provenance notes only and keep the live app free of Estimator compatibility layers

### Visuals and explainability

- [x] Lightweight feature-map style explanation payloads
  - Status: `done`
  - Source notebook(s): `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`
  - Source lineage: `showOutput`, conv-visualization cells, intermediate-representation narrative
  - Current `dd` state/path: `dd_visuals/explain.py`
  - Target destination: keep lightweight visual payload builders in `dd_visuals`
  - CLI exposure: `web+cli`
  - Docs/UI destination: level visual panels, `docs/doubledigits_design.md`
  - Planned tests: retain visualization payload coverage in `tests/test_core.py`; add CLI visualize tests later
  - Docstring requirement: preserve visualization-kind docstrings and payload-shape descriptions
  - Gamma action: reuse the existing payload builders from both the web and CLI surfaces

- [ ] Learned-layer output viewers
  - Status: `partial`
  - Source notebook(s): `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`, `digits_classifier.ipynb`, `double_digits_classifier.ipynb`
  - Source lineage: `showOutput`, `show_layer_output`, `show_layers`
  - Current `dd` state/path: partially represented by `dd_visuals/explain.py` with synthetic feature-map and prototype views rather than real learned-layer activations
  - Target destination: keep current lightweight views for Gamma and optionally add a clearly named learned-activation adapter later if exported learned models arrive
  - CLI exposure: `web+cli`
  - Docs/UI destination: `docs/doubledigits_design.md`, level explanation copy
  - Planned tests: keep payload-shape tests; add learned-activation tests only if Gamma introduces real layer outputs
  - Docstring requirement: document exactly what is synthetic/proxy visualization versus true model activation output
  - Gamma action: clarify the current visualization semantics and avoid implying CNN-layer parity that the baseline model does not provide

- [ ] Weight and prototype inspection views
  - Status: `partial`
  - Source notebook(s): `digits_project.ipynb`, `arithmetic_double_digits.ipynb`, `digits_classifier.ipynb`, `double_digits_classifier.ipynb`
  - Source lineage: `showWeights`, prototype/weight-inspection cells
  - Current `dd` state/path: `dd_models/baselines.py` (`coefficient_map`), `dd_visuals/explain.py`
  - Target destination: keep coefficient/prototype inspection in `dd_visuals` backed by model helpers in `dd_models`
  - CLI exposure: `web+cli`
  - Docs/UI destination: visual explanation panels, `docs/artifact_provenance.md`
  - Planned tests: add explicit coefficient/prototype payload assertions when Gamma expands visualization coverage
  - Docstring requirement: full docstrings describing what each map represents and how it differs from notebook CNN weights
  - Gamma action: finish naming and documentation so the current views are presented honestly and consistently across web and CLI

- [ ] Training-history and learning-curve plots
  - Status: `deferred`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: `plot_curve`, `plotLearningCurves`
  - Current `dd` state/path: not present
  - Target destination: future training/reporting utilities after the project has an explicit training pipeline
  - CLI exposure: `deferred`
  - Docs/UI destination: `docs/doubledigits_design.md`
  - Planned tests: future plotting/serialization tests only after training flows exist
  - Docstring requirement: full docstrings if activated later
  - Gamma action: keep deferred; do not create learning-curve code without first adding a supported training path

### Web, API, and runtime

- [x] Guided three-level web shell
  - Status: `done`
  - Source notebook(s): `digits_project.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_classifier.ipynb`, `double_digits_classifier.ipynb`
  - Source lineage: the overall teaching progression from single digits to two-digit composition to arithmetic
  - Current `dd` state/path: `dd_web/templates/pages/home.html`, `dd_web/static/js/doubledigits.js`
  - Target destination: keep the guided shell in `dd_web` as the primary public interface
  - CLI exposure: `web-only`
  - Docs/UI destination: live web UI, `README.md`
  - Planned tests: retain `tests/test_app.py::test_home_page_renders`
  - Docstring requirement: template comments only where non-obvious; no code docstrings beyond JS/module-level notes if Gamma touches frontend logic
  - Gamma action: preserve the three-level progression while tightening narrative copy and parity with terminal commands

- [x] Examples API endpoint
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `digits_project.ipynb`
  - Source lineage: notebook dataset/example sampling flows
  - Current `dd` state/path: `dd_web/blueprints/api.py`, `dd_web/runtime.py`
  - Target destination: keep examples listing under `GET /api/v1/examples`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, future CLI help text
  - Planned tests: retain `tests/test_app.py::test_examples_endpoint_returns_curated_examples`
  - Docstring requirement: preserve endpoint and service docstrings; add request/response schema details if the payload evolves
  - Gamma action: map `python -m dd_cli examples` directly to the same catalog/runtime behavior

- [x] Inference API endpoint
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: notebook predict/guess/report flows
  - Current `dd` state/path: `dd_web/blueprints/api.py`, `dd_web/runtime.py`
  - Target destination: keep inference under `POST /api/v1/infer`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, future CLI help text
  - Planned tests: retain `tests/test_app.py::test_infer_endpoint_supports_example_and_structured_payloads`
  - Docstring requirement: preserve endpoint and service docstrings; add payload contract notes if structured input changes
  - Gamma action: use the runtime contract directly from CLI rather than wrapping the HTTP route

- [ ] Visualization API endpoint breadth and naming
  - Status: `partial`
  - Source notebook(s): `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`, `digits_classifier.ipynb`, `double_digits_classifier.ipynb`
  - Source lineage: notebook layer-output and feature-view helpers
  - Current `dd` state/path: `dd_web/blueprints/api.py`, `dd_web/runtime.py`, `dd_visuals/explain.py`
  - Target destination: keep visual payload delivery under `GET /api/v1/visualizations/<kind>` and align future CLI naming with the same kinds
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, `docs/doubledigits_design.md`
  - Planned tests: retain `tests/test_app.py::test_visualization_endpoint_returns_payload`; add coverage for every supported visualization kind if Gamma expands the set
  - Docstring requirement: document the supported `kind` values and payload semantics
  - Gamma action: finalize the supported visualization names and keep them identical between API and CLI

- [x] Standalone runtime and AIX-friendly app wiring
  - Status: `done`
  - Source notebook(s): none directly; required by Alpha migration architecture
  - Source lineage: migration architecture rather than notebook code
  - Current `dd` state/path: `dd_web/__init__.py`, `dd_web/runtime.py`, `run.py`
  - Target destination: keep app creation and runtime assembly in `dd_web`; keep the current standalone entrypoint until CLI serve is added
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, `app.aix.yaml`
  - Planned tests: current app smoke tests plus future CLI serve smoke tests
  - Docstring requirement: preserve app-factory and middleware docstrings
  - Gamma action: fold serve behavior into `dd_cli serve` without disrupting the existing Flask app factory

### CLI mapping

- [ ] Canonical `dd_cli` package and `python -m dd_cli` entrypoint
  - Status: `pending`
  - Source notebook(s): none directly; required terminal access layer for migrated features
  - Source lineage: Beta CLI contract
  - Current `dd` state/path: not present
  - Target destination: add a top-level `dd_cli` package with a `__main__.py` entrypoint
  - CLI exposure: `cli-only`
  - Docs/UI destination: `README.md`, command help text
  - Planned tests: add `tests/test_cli.py` for invocation, help output, and failure modes
  - Docstring requirement: full module, command, and argument docstrings
  - Gamma action: implement the package first so the rest of the terminal surface has one stable home

- [ ] `python -m dd_cli examples`
  - Status: `pending`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: `getDoubleDigits`, `getDDs`, curated example selection
  - Current `dd` state/path: behavior exists only through `ExampleCatalog` and `GET /api/v1/examples`
  - Target destination: expose catalog listing and optional structured generation through `dd_cli`
  - CLI exposure: `cli-only`
  - Docs/UI destination: `README.md`
  - Planned tests: CLI output-schema and level-filter tests
  - Docstring requirement: full command docstring plus argument semantics
  - Gamma action: build directly on `ExampleCatalog` or `DoubleDigitsService`, not on shelling out to HTTP

- [ ] `python -m dd_cli infer`
  - Status: `pending`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: `guessing`, notebook prediction tables, result inspection
  - Current `dd` state/path: behavior exists through `BaselineRuntime` and `POST /api/v1/infer`
  - Target destination: expose structured inference and example-id inference through `dd_cli`
  - CLI exposure: `cli-only`
  - Docs/UI destination: `README.md`
  - Planned tests: CLI inference schema tests plus parity checks against runtime outputs
  - Docstring requirement: full command docstring and shared result-format helper docstrings
  - Gamma action: implement terminal inference with stable machine-readable output and concise human-readable defaults

- [ ] `python -m dd_cli visualize`
  - Status: `pending`
  - Source notebook(s): `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`, `digits_classifier.ipynb`, `double_digits_classifier.ipynb`
  - Source lineage: `showOutput`, `show_layer_output`, `show_layers`, prototype/weight views
  - Current `dd` state/path: behavior exists only through `dd_visuals` and `GET /api/v1/visualizations/<kind>`
  - Target destination: expose visualization payloads through `dd_cli`
  - CLI exposure: `cli-only`
  - Docs/UI destination: `README.md`, `docs/doubledigits_design.md`
  - Planned tests: CLI visualization-kind tests and output-format tests
  - Docstring requirement: full command and payload docstrings
  - Gamma action: mirror API visualization names exactly to avoid split terminology

- [ ] `python -m dd_cli serve`
  - Status: `partial`
  - Source notebook(s): none directly; terminalization of the current standalone app entrypoint
  - Source lineage: Beta CLI contract plus current local serve behavior
  - Current `dd` state/path: `run.py` already launches the Flask app, but not through `dd_cli`
  - Target destination: move or wrap local serve behavior under `dd_cli serve` while keeping `run.py` backward-compatible if practical
  - CLI exposure: `cli-only`
  - Docs/UI destination: `README.md`
  - Planned tests: CLI serve smoke test and config/env passthrough checks
  - Docstring requirement: full command docstring plus environment/config notes
  - Gamma action: give terminal users one stable entrypoint without removing the current local dev flow abruptly

- [ ] Scripts policy for public versus one-off command surfaces
  - Status: `pending`
  - Source notebook(s): none directly; migration governance item
  - Source lineage: Beta CLI contract
  - Current `dd` state/path: `scripts/` exists but has no written policy
  - Target destination: document that stable user-facing commands live in `dd_cli`, while `scripts/` stays reserved for internal utilities
  - CLI exposure: `docs-only`
  - Docs/UI destination: `README.md`, `docs/DOUBLEDIGITS_PLAN_beta.md`
  - Planned tests: documentation review only
  - Docstring requirement: N/A until utility scripts are added; any new scripts should still carry module docstrings
  - Gamma action: codify the rule when the first CLI package lands

### Narrative, exercises, and provenance

- [ ] Guided three-level narrative thread
  - Status: `partial`
  - Source notebook(s): `digits_classifier.ipynb`, `double_digits_classifier.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`
  - Source lineage: tutorial progression from single digits to composition to arithmetic
  - Current `dd` state/path: `dd_web/templates/pages/home.html`, `README.md`, `docs/DOUBLEDIGITS_PLAN_alpha.md`
  - Target destination: keep the live narrative split between web copy and docs, with the design rationale in `docs/doubledigits_design.md`
  - CLI exposure: `docs-only`
  - Docs/UI destination: `README.md`, `docs/doubledigits_design.md`, future level copy refinement
  - Planned tests: manual content review only
  - Docstring requirement: N/A for prose; add concise comments only if frontend logic becomes non-obvious
  - Gamma action: tighten the wording so the teaching arc is consistent across home page, API docs, and CLI help text

- [ ] Notebook exercise prompts and comparison language
  - Status: `docs-only`
  - Source notebook(s): `digits_classifier.ipynb`, `double_digits_classifier.ipynb`, `minimal_convolution_double_digits.ipynb`
  - Source lineage: task prompts, comparison framing, tutorial copy
  - Current `dd` state/path: only partially reflected in `README.md` and the home page
  - Target destination: rewrite as docs and selective UI copy rather than porting notebook prose wholesale
  - CLI exposure: `docs-only`
  - Docs/UI destination: `docs/doubledigits_design.md`, `README.md`, future inline help
  - Planned tests: manual documentation review only
  - Docstring requirement: N/A for prose
  - Gamma action: salvage the useful teaching language, compress it, and avoid notebook-era instructional scaffolding that assumes Colab execution

- [ ] Migration provenance and salvage rationale
  - Status: `partial`
  - Source notebook(s): all seven notebooks
  - Source lineage: Beta and Alpha documentation layer
  - Current `dd` state/path: `docs/DOUBLEDIGITS_PLAN_alpha.md`, `docs/DOUBLEDIGITS_PLAN_beta.md`, `docs/migration_inventory.md`
  - Target destination: keep migration decision history in docs, not in code comments
  - CLI exposure: `docs-only`
  - Docs/UI destination: `docs/migration_inventory.md`, `docs/DOUBLEDIGITS_PLAN_alpha.md`, `docs/DOUBLEDIGITS_PLAN_beta.md`
  - Planned tests: documentation review and ledger completeness review
  - Docstring requirement: N/A for prose docs
  - Gamma action: update the ledger as implementation proceeds so provenance stays current rather than becoming stale again

- [x] Model and artifact provenance notes
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`, `digits_classifier.ipynb`, `double_digits_classifier.ipynb`
  - Source lineage: model-source justification and notebook-to-baseline replacement rationale
  - Current `dd` state/path: `docs/artifact_provenance.md`
  - Target destination: keep artifact rationale in `docs/artifact_provenance.md`
  - CLI exposure: `docs-only`
  - Docs/UI destination: `docs/artifact_provenance.md`
  - Planned tests: documentation review only
  - Docstring requirement: N/A for prose docs
  - Gamma action: update provenance notes if CLI or model artifacts change the delivery path, but keep the current baseline rationale intact

### Training, experimental tracks, and explicit deferrals

- [ ] Alternative-model exploration beyond the current baseline
  - Status: `deferred`
  - Source notebook(s): `digits_project.ipynb`, `minimal_convolution_double_digits.ipynb`, `introduction-to-ensembling-stacking-in-python.ipynb`
  - Source lineage: minimalist convnet variants, mixed model, modelX, stacking references, other-design questions
  - Current `dd` state/path: intentionally excluded from active code
  - Target destination: future design branch under `dd_models` plus dedicated evaluation tooling after Gamma
  - CLI exposure: `deferred`
  - Docs/UI destination: `docs/doubledigits_design.md`
  - Planned tests: future evaluation benchmarks only when alternative models become active scope
  - Docstring requirement: full docstrings if implemented later
  - Gamma action: keep visible in the ledger, but do not allow it to expand Gamma scope

- [ ] User-triggered retraining and artifact production
  - Status: `deferred`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: notebook training loops, ad hoc retraining cells, model rebuild flows
  - Current `dd` state/path: intentionally omitted from the app
  - Target destination: future training pipeline and artifact management layer after the guided lab and CLI are stable
  - CLI exposure: `deferred`
  - Docs/UI destination: `docs/doubledigits_design.md`, `docs/artifact_provenance.md`
  - Planned tests: future training job and artifact regression tests only when the workflow is supported
  - Docstring requirement: full docstrings if activated later
  - Gamma action: keep out of Gamma scope

- [ ] Handwriting canvas input and touch-first entry workflow
  - Status: `deferred`
  - Source notebook(s): none directly; derived from Alpha scope and later product goals
  - Source lineage: post-migration product requirement rather than notebook code
  - Current `dd` state/path: intentionally omitted
  - Target destination: future `dd_web` input layer plus CLI/image-ingest contract if needed
  - CLI exposure: `deferred`
  - Docs/UI destination: `docs/DOUBLEDIGITS_PLAN_alpha.md`, `docs/doubledigits_design.md`
  - Planned tests: future browser input and rasterization tests
  - Docstring requirement: full docstrings if implemented later
  - Gamma action: keep deferred until after the notebook-to-code migration is structurally complete

- [ ] Handwritten-style output polish beyond the current raster result image
  - Status: `deferred`
  - Source notebook(s): `arithmetic_double_digits.ipynb`
  - Source lineage: result rendering ideas and later polish goals
  - Current `dd` state/path: only a basic rendered result image exists
  - Target destination: future rendering extension in `dd_core.render` and UI presentation refinements
  - CLI exposure: `deferred`
  - Docs/UI destination: `docs/doubledigits_design.md`
  - Planned tests: future rendering regression tests only when visual style becomes a supported requirement
  - Docstring requirement: full docstrings if activated later
  - Gamma action: keep the current simple result raster for Gamma and defer stylistic output work

- [ ] Notebook-only convenience and execution-environment helpers
  - Status: `docs-only`
  - Source notebook(s): `minimal_convolution_double_digits.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: `clear`, `mg`, notebook reload/display cells, Colab-oriented execution scaffolding
  - Current `dd` state/path: intentionally not ported
  - Target destination: omit from product code and mention only in migration/provenance notes where needed
  - CLI exposure: `docs-only`
  - Docs/UI destination: `docs/migration_inventory.md`
  - Planned tests: none
  - Docstring requirement: N/A for code because Gamma should not implement these helpers
  - Gamma action: do not port notebook execution scaffolding into modules, scripts, or CLI commands
