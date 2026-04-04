# Double-digits Migration Inventory

Status refresh: 2026-04-04

This is the working ledger for notebook-to-`dd` migration. It is grouped by capability so later phases can answer where each notebook feature now lives without reopening the notebooks.

## Source repos
- Legacy source: `C:\Users\David\Documents\Repositories\double-digits`
- New app target: `C:\Users\David\Documents\Local_Python\dd`

## Status legend
- `done`: migrated into the accepted canonical location
- `partial`: present but still needs follow-on product polish
- `pending`: in scope but not yet implemented
- `docs-only`: preserved in documentation rather than live code
- `deferred`: intentionally held for a later phase

## Exposure legend
- `web+cli`: stable in both the web lab and `python -m dd_cli`
- `web-only`: belongs in the web app, not as a terminal command
- `cli-only`: belongs in terminal tooling, not the guided web lab
- `docs-only`: documentation only
- `deferred`: not on the current product surface

## Notebook source register

| Notebook | Role | Primary ledger sections |
|---|---|---|
| `double_digits_with_MNIST.ipynb` | main extraction source | core data; inference/models; training |
| `minimal_convolution_double_digits.ipynb` | main extraction source | models; visuals; training |
| `digits_project.ipynb` | main extraction source | arithmetic; models; visuals; narrative |
| `arithmetic_double_digits.ipynb` | main extraction source | arithmetic; models; training; deferred tracks |
| `digits_classifier.ipynb` | extraction/reference source | models; visuals; narrative |
| `double_digits_classifier.ipynb` | extraction/reference source | models; visuals; narrative |
| `introduction-to-ensembling-stacking-in-python.ipynb` | deferred reference | experimental/deferred |

`.ipynb_checkpoints/` duplicates are intentionally ignored.

## Master capability ledger

### Core composition and data

- [x] Canonical MNIST loading and split access
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `digits_project.ipynb`
  - Source lineage: MNIST import, normalization, reshape, `scale_array`
  - Current `dd` state/path: `dd_core/dataset.py`
  - Target destination: keep MNIST loading and helper access in `dd_core.dataset`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, `docs/artifact_provenance.md`
  - Planned tests: dataset-shape coverage in `tests/test_core.py` and CLI coverage for `dataset show`
  - Docstring requirement: full module and function docstrings on split access, normalization, and record helpers
  - Gamma action: keep MNIST as the only active digit bank

- [x] Notebook-style scene composition and operator placement
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: `doubleDigits`, arithmetic scene assembly, `getOperator`
  - Current `dd` state/path: `dd_core/examples.py`, `dd_core/render.py`, `dd_core/legacy_api.py`
  - Target destination: keep composition helpers in `dd_core.examples` and rendering primitives in `dd_core.render`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `docs/doubledigits_design.md`
  - Planned tests: scene-shape coverage in `tests/test_core.py` and CLI parity through `examples show`
  - Docstring requirement: document 28x28 and 28x56 scene assumptions plus operator overlay rules
  - Gamma action: preserve notebook layout exactly

- [x] Curated catalog and structured example generation
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: `getDoubleDigits`, `getDDs`, curated selection cells
  - Current `dd` state/path: `dd_core/examples.py`, `dd_core/constants.py`
  - Target destination: keep example generation in `dd_core.examples.ExampleCatalog`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, `docs/doubledigits_design.md`
  - Planned tests: example coverage in `tests/test_core.py` and CLI coverage for `examples list` and `examples show`
  - Docstring requirement: document curated versus structured generation and notebook-lineage example IDs
  - Gamma action: use the same catalog from both CLI and web runtime

- [x] Batch export with `images/`, `manifest.csv`, and `dataset.npz`
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `digits_classifier.ipynb`, `double_digits_classifier.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: `get_new_data`, dataset assembly loops, export-oriented notebook flows
  - Current `dd` state/path: `dd_core/export.py`, `dd_cli/app.py`
  - Target destination: keep export helpers in `dd_core.export`, exposed through `dd_cli examples generate`
  - CLI exposure: `cli-only`
  - Docs/UI destination: `README.md`, `docs/doubledigits_design.md`
  - Planned tests: `tests/test_cli.py` coverage for file counts, manifest schema, and row alignment
  - Docstring requirement: full docstrings for export layout and alignment guarantees
  - Gamma action: keep the export contract stable

- [x] Notebook-lineage helper compatibility shims
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: `doubleDigits`, `getDoubleDigits`, `getOperator`, `get_results`
  - Current `dd` state/path: `dd_core/legacy_api.py`
  - Target destination: keep notebook-name compatibility in `dd_core.legacy_api`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `docs/migration_inventory.md`
  - Planned tests: smoke coverage through existing core/runtime tests
  - Docstring requirement: module-level rationale plus clear compatibility notes
  - Gamma action: preserve notebook-era naming continuity without duplicating implementations

### Arithmetic semantics and operators

- [x] Notebook arithmetic rules, including division
  - Status: `done`
  - Source notebook(s): `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: arithmetic rule cells, `get_results`, division branch
  - Current `dd` state/path: `dd_core/examples.py`, `dd_core/constants.py`, `dd_cli/app.py`
  - Target destination: keep canonical arithmetic evaluation in `dd_core.examples.get_results`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, `docs/doubledigits_design.md`
  - Planned tests: arithmetic assertions in `tests/test_core.py` plus CLI division coverage
  - Docstring requirement: explicitly document subtraction flooring, rounded division, and the notebook `99` divide-by-zero sentinel
  - Gamma action: preserve notebook arithmetic semantics exactly

- [x] Operator glyph rendering and result rasterization
  - Status: `done`
  - Source notebook(s): `arithmetic_double_digits.ipynb`, `digits_project.ipynb`
  - Source lineage: `getOperator`, operator overlay cells, result-display helpers
  - Current `dd` state/path: `dd_core/render.py`, `dd_core/examples.py`
  - Target destination: keep glyph rendering and result image generation in `dd_core.render`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `docs/artifact_provenance.md`
  - Planned tests: result-image coverage in `tests/test_core.py` and visualization parity checks
  - Docstring requirement: document `binary_r` rendering, operator placement, and current result-image limits
  - Gamma action: keep the rendered result image simple but notebook-aligned

### Inference, models, and artifacts

- [x] Unified runtime contract across all three levels
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: notebook prediction, inspection, and answer-reporting flows
  - Current `dd` state/path: `dd_models/baselines.py`, `dd_web/runtime.py`
  - Target destination: keep the canonical contract in `dd_models.baselines.InferenceResult` and `BaselineRuntime`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, `docs/artifact_provenance.md`
  - Planned tests: core/app/CLI parity coverage
  - Docstring requirement: preserve schema and payload docstrings on the runtime contract
  - Gamma action: keep CLI and web behavior on the same runtime objects

- [x] Notebook-derived Keras backend and cached artifacts
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: notebook Keras model definitions, optimizer settings, saved-model flows
  - Current `dd` state/path: `dd_models/keras_backend.py`, `dd_models/baselines.py`, generated `.keras` and `.json` files under `models/`
  - Target destination: keep Keras backend setup and artifact caching in `dd_models`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, `docs/artifact_provenance.md`
  - Planned tests: cache reuse coverage plus CLI training smoke coverage
  - Docstring requirement: full docstrings on backend selection, artifact metadata, and cache reuse behavior
  - Gamma action: keep notebook-style model code active while leaving runtime artifacts local

- [x] Notebook preset registry and whole-scene classifiers
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`, `digits_classifier.ipynb`, `double_digits_classifier.ipynb`
  - Source lineage: single-digit dense model, double-digit `modelX`, minimal conv variants, mixed model lineage, arithmetic CNN families
  - Current `dd` state/path: `dd_models/baselines.py`
  - Target destination: keep preset registration in `dd_models.baselines.PRESETS`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `docs/doubledigits_design.md`, `docs/artifact_provenance.md`
  - Planned tests: inference coverage plus preset-list coverage
  - Docstring requirement: document preset names, notebook lineage, label semantics, and whole-scene inference behavior
  - Gamma action: keep direct whole-scene classification as the canonical path

- [x] Notebook-derived training routines and artifact production
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`, `digits_classifier.ipynb`, `double_digits_classifier.ipynb`
  - Source lineage: `create_model`, `train_model`, `train`, model-family build cells, ad hoc retraining flows
  - Current `dd` state/path: `dd_models/baselines.py`, `dd_cli/app.py`, `dd_cli/formatting.py`
  - Target destination: keep training logic in `dd_models` and expose it through `dd_cli train`
  - CLI exposure: `cli-only`
  - Docs/UI destination: `README.md`, `docs/artifact_provenance.md`
  - Planned tests: `train list` coverage and smoke coverage for `train run` under tiny overrides
  - Docstring requirement: full docstrings on builders, presets, training overrides, and force-retrain behavior
  - Gamma action: keep notebook preset training explicit and terminal-driven

- [x] Prediction sampling and answer-reporting helpers
  - Status: `done`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: `guessing`, `getAnswers`, notebook tables, reporting helpers
  - Current `dd` state/path: `dd_models/baselines.py`, `dd_cli/formatting.py`, `dd_web/runtime.py`
  - Target destination: keep reporting semantics in shared runtime/model helpers and CLI formatting utilities
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`
  - Planned tests: inference-format coverage in `tests/test_cli.py` and runtime parity checks
  - Docstring requirement: full docstrings on reporting helpers and CLI serializers
  - Gamma action: keep text concise and `--json` stable

- [ ] Estimator-era dataframe parsing and training stack
  - Status: `docs-only`
  - Source notebook(s): `digits_classifier.ipynb`, `double_digits_classifier.ipynb`
  - Source lineage: feature-column helpers and Estimator training utilities
  - Current `dd` state/path: intentionally not ported as live code
  - Target destination: keep this lineage documented as historical context only
  - CLI exposure: `docs-only`
  - Docs/UI destination: `docs/artifact_provenance.md`, `docs/doubledigits_design.md`
  - Planned tests: documentation review only
  - Docstring requirement: N/A because this stack stays documentation-only
  - Gamma action: do not reintroduce Estimator compatibility layers

### Visuals and explainability

- [x] Learned activation maps with notebook color conventions
  - Status: `done`
  - Source notebook(s): `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`
  - Source lineage: `showOutput`, conv-visualization cells, layer inspection
  - Current `dd` state/path: `dd_visuals/explain.py`, `dd_models/baselines.py`
  - Target destination: keep activation extraction in `dd_models` and rendering in `dd_visuals`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, `docs/doubledigits_design.md`
  - Planned tests: visualization coverage in core/app tests plus CLI parity for `feature_maps`
  - Docstring requirement: document layer-selection behavior and `viridis` rendering
  - Gamma action: keep `feature_maps` as real learned activations

- [x] Prototype, weight, and comparison views
  - Status: `done`
  - Source notebook(s): `digits_project.ipynb`, `arithmetic_double_digits.ipynb`, `digits_classifier.ipynb`, `double_digits_classifier.ipynb`
  - Source lineage: `showWeights`, prototype views, class means, comparison framing
  - Current `dd` state/path: `dd_visuals/explain.py`, `dd_models/baselines.py`, `dd_core/examples.py`
  - Target destination: keep `prototype` and `comparison` payloads in `dd_visuals.explain`
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, `docs/artifact_provenance.md`
  - Planned tests: parity coverage across core, app, and CLI for `prototype` and `comparison`
  - Docstring requirement: document `binary_r`, `bone`, and the included MNIST ground-truth source tiles
  - Gamma action: keep comparison grounded in notebook-style MNIST provenance

- [ ] Training-history and learning-curve plots
  - Status: `deferred`
  - Source notebook(s): `double_digits_with_MNIST.ipynb`, `digits_project.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: `plot_curve`, `plotLearningCurves`
  - Current `dd` state/path: not present as a stable product surface
  - Target destination: future training-reporting utilities after the CLI training surface settles
  - CLI exposure: `deferred`
  - Docs/UI destination: `docs/doubledigits_design.md`
  - Planned tests: future plot-generation coverage only if activated
  - Docstring requirement: full docstrings if implemented later
  - Gamma action: keep deferred

### Web, API, runtime, and CLI

- [x] Guided three-level web shell
  - Status: `done`
  - Source notebook(s): `digits_project.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_classifier.ipynb`, `double_digits_classifier.ipynb`
  - Source lineage: tutorial progression from raw digits to composition to arithmetic
  - Current `dd` state/path: `dd_web/templates/pages/home.html`, `dd_web/static/js/doubledigits.js`
  - Target destination: keep the guided shell in `dd_web`
  - CLI exposure: `web-only`
  - Docs/UI destination: live web UI, `README.md`
  - Planned tests: `tests/test_app.py::test_home_page_renders`
  - Docstring requirement: comments only where frontend logic is non-obvious
  - Gamma action: leave major UI refinement to Delta

- [x] Runtime/API parity and local serving
  - Status: `done`
  - Source notebook(s): notebook behavior normalized into product endpoints
  - Source lineage: examples, inference, visualization, and local-run flows
  - Current `dd` state/path: `dd_web/runtime.py`, `dd_web/blueprints/api.py`, `dd_web/serve.py`, `run.py`
  - Target destination: keep runtime assembly in `dd_web` and serving in shared helpers
  - CLI exposure: `web+cli`
  - Docs/UI destination: `README.md`, `app.aix.yaml`
  - Planned tests: endpoint coverage in `tests/test_app.py` plus serve-runner coverage in `tests/test_cli.py`
  - Docstring requirement: preserve endpoint, runtime, and serve-helper docstrings
  - Gamma action: keep API, CLI, and local serve behavior aligned

- [x] Canonical `dd_cli` command surface
  - Status: `done`
  - Source notebook(s): all notebook-driven terminal needs are normalized here
  - Source lineage: Gamma CLI contract and notebook execution needs
  - Current `dd` state/path: `dd_cli/__main__.py`, `dd_cli/app.py`, `dd_cli/formatting.py`
  - Target destination: keep stable commands in `dd_cli`: `dataset`, `examples`, `infer`, `visualize`, `serve`, `train`
  - CLI exposure: `cli-only`
  - Docs/UI destination: `README.md`, command help text
  - Planned tests: CLI help, invalid-input, JSON/text mode, export, and training coverage in `tests/test_cli.py`
  - Docstring requirement: full module and command docstrings across the CLI surface
  - Gamma action: keep `python -m dd_cli` as the shell-neutral interface and reserve `scripts/` for internal utilities

### Narrative, provenance, and explicit deferrals

- [x] README, design notes, provenance notes, and migration plans updated to MNIST
  - Status: `done`
  - Source notebook(s): all notebook groups inform this layer
  - Source lineage: migration explanation, notebook restoration rationale, CLI documentation
  - Current `dd` state/path: `README.md`, `docs/doubledigits_design.md`, `docs/artifact_provenance.md`, `docs/DOUBLEDIGITS_PLAN_gamma.md`
  - Target destination: keep notebook-restoration narrative in docs rather than code comments
  - CLI exposure: `docs-only`
  - Docs/UI destination: the files listed above
  - Planned tests: documentation review only
  - Docstring requirement: N/A for prose docs
  - Gamma action: keep docs aligned to the actual MNIST runtime, not the temporary sklearn detour

- [ ] Guided web copy and notebook exercise prose refinement
  - Status: `partial`
  - Source notebook(s): `digits_classifier.ipynb`, `double_digits_classifier.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`
  - Source lineage: tutorial prompts and comparison language
  - Current `dd` state/path: only partially reflected in `dd_web/templates/pages/home.html`
  - Target destination: finish the copy pass during Delta
  - CLI exposure: `docs-only`
  - Docs/UI destination: web templates and future inline help
  - Planned tests: manual content review only
  - Docstring requirement: N/A for prose
  - Gamma action: leave detailed web narrative polish to Delta

- [x] Migration provenance ledger
  - Status: `done`
  - Source notebook(s): all seven notebooks
  - Source lineage: Alpha, Beta, and Gamma planning plus notebook extraction rationale
  - Current `dd` state/path: `docs/DOUBLEDIGITS_PLAN_alpha.md`, `docs/DOUBLEDIGITS_PLAN_beta.md`, `docs/DOUBLEDIGITS_PLAN_gamma.md`, `docs/migration_inventory.md`
  - Target destination: keep migration decision history in docs
  - CLI exposure: `docs-only`
  - Docs/UI destination: the planning docs and this ledger
  - Planned tests: documentation review and ledger completeness review
  - Docstring requirement: N/A for prose docs
  - Gamma action: keep the ledger current as implementation changes land

- [ ] Stacking and ensembling experiments
  - Status: `deferred`
  - Source notebook(s): `introduction-to-ensembling-stacking-in-python.ipynb`
  - Source lineage: stacking references and exploratory ensembling work
  - Current `dd` state/path: intentionally excluded from live product code
  - Target destination: future experimental branch under `dd_models`
  - CLI exposure: `deferred`
  - Docs/UI destination: `docs/doubledigits_design.md`
  - Planned tests: future benchmark coverage only if this becomes active scope
  - Docstring requirement: full docstrings if implemented later
  - Gamma action: keep deferred

- [ ] Handwriting input and handwritten-output polish
  - Status: `deferred`
  - Source notebook(s): later product goals plus result-display polish ideas from `arithmetic_double_digits.ipynb`
  - Source lineage: post-migration product requirements rather than core notebook code
  - Current `dd` state/path: intentionally omitted from the active product surface
  - Target destination: future `dd_web` input layer and render refinements
  - CLI exposure: `deferred`
  - Docs/UI destination: `docs/DOUBLEDIGITS_PLAN_alpha.md`, `docs/doubledigits_design.md`
  - Planned tests: future browser-input, rasterization, and rendering regression coverage
  - Docstring requirement: full docstrings if implemented later
  - Gamma action: defer until after Delta

- [ ] Notebook-only execution scaffolding
  - Status: `docs-only`
  - Source notebook(s): `minimal_convolution_double_digits.ipynb`, `arithmetic_double_digits.ipynb`
  - Source lineage: `clear`, `mg`, reload/display helpers, Colab scaffolding
  - Current `dd` state/path: intentionally not ported
  - Target destination: mention only in migration/provenance docs when useful
  - CLI exposure: `docs-only`
  - Docs/UI destination: `docs/migration_inventory.md`
  - Planned tests: none
  - Docstring requirement: N/A because this remains documentation-only
  - Gamma action: do not port notebook execution scaffolding into modules, scripts, or CLI commands
