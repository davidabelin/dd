# DD Maintainer Documentation and Docstring Plan

## Summary
- Produce a full maintainer-facing documentation suite for `dd` using in-repo Markdown plus NumPy-style Python docstrings.
- Treat `dd` as both a standalone lab and the AIX-mounted `/doubledigits` service; every major subsystem should document its AIX-facing contract, not just its local behavior.
- Preserve runtime behavior. The production code already has broad docstring coverage; the real work is standardization, deeper semantic coverage, cross-references, and canonical maintainer docs.
- Use the current historical docs as source material and lineage appendices, but move the canonical maintainer path to a new `docs/maintainer/` set and make the repo root docs point there.
- Keep the plan grounded in the current verified baseline: `20` tests pass in `tests/test_core.py`, `tests/test_cli.py`, and `tests/test_app.py`, with only Keras/NumPy deprecation-warning noise.

## Implementation Changes
- Refresh the root README so it becomes the maintainer entrypoint: project purpose, package map, quick local run/test commands, AIX relationship, and links into the canonical maintainer docs.
- Add a canonical maintainer doc set under `docs/maintainer/` with five fixed pages: `overview`, `architecture`, `interfaces`, `models-and-artifacts`, and `operations`.
- `overview` should explain repo purpose, the three lab levels, package responsibilities (`dd_core`, `dd_models`, `dd_visuals`, `dd_web`, `dd_cli`), and how this repo fits into the broader AIX umbrella.
- `architecture` should document the concrete flow `data/mnist.npz` -> dataset helpers -> example/render composition -> runtime/model inference -> visualization/export -> web/CLI surfaces -> AIX adapter, with one dependency diagram and one request-flow diagram.
- `interfaces` should document the stable contracts for HTTP endpoints, CLI commands, dataclasses, payload shapes, environment variables, legacy compatibility helpers, and generated export layouts.
- `models-and-artifacts` should document all registered presets, their notebook lineage, input modes, label semantics, default-vs-override behavior, cached `.keras`/`.json` artifacts, training metadata, read-only cloud posture, and the fact that double/arithmetic are whole-scene classifiers rather than stitched digit pipelines.
- `operations` should document local serving, test execution, artifact retraining, model replacement, App Engine deployment assumptions, `APP_BASE_PATH=/doubledigits`, AIX bridge expectations, and the current Windows Python 3.14 Keras-torch warning/shutdown caveat.
- Keep the existing design, provenance, migration, and phase-plan docs as archival/reference material; update them so they point to the new maintainer docs instead of acting as competing primary entrypoints.
- Standardize production docstrings to NumPy style across modules, dataclasses, public functions, route handlers, CLI handlers, runtime services, and the important internal helpers that encode notebook semantics or cross-module contracts.
- Expand module docstrings so each production module states: responsibility, key dependencies, upstream/downstream callers, notebook lineage, AIX relevance, and any important invariants.
- Deepen docstrings where maintainers need real semantics, especially around image shapes (`28x28`, `28x56`), dtype/normalization boundaries, arithmetic rules, divide-by-zero sentinel `99`, label spaces (`0..9`, `0..99`), preset selection, lazy runtime loading, artifact caching, and mount-safe frontend config injection.
- Fill the remaining undocumented production-callable gaps explicitly: constructor/config boundaries, path-prefix middleware setup, lazy runtime/service constructors, and template-global injection.
- Add targeted inline comments only in the few notebook-fidelity areas where the code is intentionally non-obvious, especially operator drawing, mixed-model training, and activation-map shaping. Avoid comment noise elsewhere.
- Document the frontend as part of the maintainer story: server-rendered `mountBase`/`apiBase`, `home.html` lab-section structure, and the JS fetch/render lifecycle for examples, inference, presets, and visualizations.
- Document the AIX contract without moving scope into the sibling repo: explain the external adapter path, expected environment variables, mounted route prefix, and the fact that `dd` is owned here while AIX only bridges and hosts it.

## Public Interfaces and Types
- No runtime API changes are planned; the work makes the existing public contracts explicit and maintainable.
- Treat these as stable documented contracts: `MnistRecord`, `Example`, `InferenceResult`, `ModelPreset`, `PreparedDataset`, `BaselineRuntime`, `NotebookClassifier`, `DoubleDigitsService`, and the notebook-lineage helpers exposed through `legacy_api`.
- Treat these as stable documented surfaces: `GET /`, `GET /healthz`, `GET /api/v1/examples`, `GET /api/v1/presets`, `POST /api/v1/infer`, `GET /api/v1/visualizations/<kind>`, and `python -m dd_cli dataset|examples|infer|visualize|serve|train`.
- Treat these as stable documented operational contracts: `DOUBLEDIGITS_*`, `AIX_HUB_URL`, `APP_BASE_PATH`, `models/*.keras`, `models/*.json`, and generated example bundles containing `images/`, `manifest.csv`, and `dataset.npz`.

## Test Plan
- Re-run the current behavioral baseline after documentation edits: `python -m pytest tests/test_core.py tests/test_cli.py tests/test_app.py -q`.
- Add one lightweight docs-contract test module under `tests/` that enforces docstring coverage for production packages and verifies the canonical maintainer index links every required maintainer page.
- Add module docstrings to the test suite and fixture documentation in `conftest.py`, but do not add verbose per-test docstrings unless a test encodes a subtle contract.
- Perform a manual docs-only acceptance pass for three end-to-end scenarios: single-digit, double-digit, and arithmetic. A maintainer should be able to trace each flow from input source through runtime/model choice to output payloads and exported artifacts using the docs alone.
- Manually verify that the AIX integration docs explain mounted operation, path-prefix behavior, and read-only cloud artifact usage without requiring code changes in the `aix` repo.

## Assumptions and Defaults
- Canonical output format is Markdown in the repo, not Sphinx or MkDocs.
- Python docstrings use NumPy style.
- Scope is the `dd` repo; AIX is documented as an external integration contract, not rewritten here.
- Notebook lineage stays prominent. Each major docs section should connect current code to the notebook family it came from and explain what was preserved, normalized, or intentionally deferred.
- Existing production docstrings should be preserved when accurate and upgraded when thin; this is a standardization-and-context pass, not a blanket rewrite for style alone.
- No notebook files are being vendored into `dd`; lineage is documented by notebook name and by the existing migration/provenance docs.
