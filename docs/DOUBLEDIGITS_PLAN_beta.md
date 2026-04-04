# Double-digits Standalone and AIX-Arm Plan
# *Phase Beta: The "Migration Ledger"*
# **notebooks -> ledger -> Gamma execution**

## Summary
- Convert the current notebook-level migration notes into a complete working ledger that tracks every relevant notebook-derived capability, its current `dd` status, its target destination, and its eventual terminal exposure.
- Keep Beta organizational only: no new runtime behavior, no `dd_cli` package yet, and no additional notebook extraction in this phase.
- Use Beta to remove ambiguity before Gamma starts. Any non-deferred migration item must already have one destination, one status, one planned test surface, and one docstring expectation.

## Beta deliverables
- `docs/DOUBLEDIGITS_PLAN_beta.md`
  - freezes Beta scope
  - defines the ledger rules and statuses
  - assigns one role to each legacy notebook
  - states the planned CLI contract for terminal use
- `docs/migration_inventory.md`
  - becomes the working migration ledger
  - groups work by subsystem instead of by notebook
  - deduplicates repeated notebook helper families into canonical migration rows
  - records both current `dd` coverage and remaining Gamma work

## Working status taxonomy
- `done`
  - the capability already exists in `dd` in the accepted canonical location and is covered well enough to serve as the Gamma baseline
- `partial`
  - the capability exists in some form, but Gamma still needs parity cleanup, destination cleanup, richer docs, or CLI/test integration
- `pending`
  - the capability is in scope for Gamma but does not yet exist in its planned canonical form
- `docs-only`
  - the notebook material will survive as documentation, narrative, provenance, or comparison text rather than as live product code
- `deferred`
  - the material is intentionally preserved in the ledger but pushed past Gamma so it does not silently disappear

## Ledger contract
Every item in `migration_inventory.md` must include:
- source notebook(s)
- source helper, section, or experiment lineage
- current `dd` state/path
- target destination
- CLI exposure mode: `web+cli`, `web-only`, `cli-only`, `docs-only`, or `deferred`
- docs or UI destination
- planned test surface
- docstring obligation
- Gamma action

## Notebook role register
| Notebook | Beta role | Primary migration emphasis |
|---|---|---|
| `double_digits_with_MNIST.ipynb` | main extraction source | double-digit composition, dataset assembly, early dense-model flow, answer reporting lineage |
| `minimal_convolution_double_digits.ipynb` | main extraction source | minimalist convnet framing, feature-view ideas, prediction inspection lineage |
| `digits_project.ipynb` | main extraction source | arithmetic narrative, mixed-model comparisons, training and visualization lineage |
| `arithmetic_double_digits.ipynb` | main extraction source | operator drawing logic, arithmetic scene generation, arithmetic experiments, result semantics lineage |
| `digits_classifier.ipynb` | docs-only reference | single-digit tutorial language, Estimator-era comparison framing, layer-inspection language |
| `double_digits_classifier.ipynb` | docs-only reference | two-digit tutorial language, Estimator-era comparison framing, dataset parsing/input pipeline lineage |
| `introduction-to-ensembling-stacking-in-python.ipynb` | deferred reference | future alternative-model and stacking direction only |

Checkpoint notebooks under `.ipynb_checkpoints/` are explicitly excluded from the ledger.

## Canonical destinations
- `dd_core`
  - dataset loading, normalization, composition, operator rendering, example catalogs, notebook-lineage compatibility shims
- `dd_models`
  - baseline inference wrappers, artifact loading, future model export/import utilities
- `dd_visuals`
  - feature-map style payloads, prototype/coefficient views, future learned-activation adapters
- `dd_web`
  - guided lab pages, JSON APIs, runtime wiring, and AIX-facing standalone app behavior
- `dd_cli`
  - future stable terminal interface for end-user and engineer access from a regular command line
- `docs`
  - narrative salvage, provenance, design notes, migration decisions, and comparison material
- `scripts`
  - one-off internal utilities only; not the public or stable user-facing command surface

## Planned terminal contract
The first stable terminal interface is shell-neutral and starts with `python -m dd_cli`, not a PowerShell-specific wrapper.

Reserved command families:
- `python -m dd_cli examples`
  - list or emit curated/generated scenarios by level
- `python -m dd_cli infer`
  - run inference on an example id or structured input
- `python -m dd_cli visualize`
  - emit visualization payloads or image artifacts for a chosen scenario
- `python -m dd_cli serve`
  - launch the local Flask lab with the same config surface currently exposed through `run.py`

Beta does not implement these commands. It only reserves them so Gamma can build them without revisiting the interface shape.

## Gamma handoff rule
Gamma may implement only from ledger rows that are decision-complete. For each non-deferred row, the ledger must already answer:
- what notebook material is being kept
- what notebook material is being dropped or rewritten
- which repo location becomes canonical
- whether the feature is exposed in web, CLI, docs, or some combination
- how parity will be tested
- which docstrings are required when code is touched

If a row cannot answer those questions, Gamma must treat it as a Beta gap rather than making a fresh design decision during implementation.

## Acceptance checks for Beta
- A reviewer can start from any legacy notebook helper or section and find its ledger row without reopening the notebook.
- A reviewer can distinguish current coverage from remaining work by scanning statuses alone.
- A reviewer can tell whether a capability belongs in `dd_core`, `dd_models`, `dd_visuals`, `dd_web`, `dd_cli`, or docs without guessing.
- A reviewer can infer the future terminal surface from the ledger without inventing new subcommands.
- Gamma can begin implementation with no unresolved questions about migration ownership, target location, or documentation standard.

## Assumptions
- The current package split remains intact; Beta adds planning clarity, not architectural churn.
- `dd_cli` is the future canonical terminal surface even though it is not implemented yet.
- Existing `run.py` remains the current local serve entrypoint until Gamma folds that behavior into `python -m dd_cli serve`.
- Estimator-era notebook code is preserved only as documentation or comparison context, not as active product code.
- Stacking, division, retraining workflows, handwriting input, and handwritten-output polish remain visible in the ledger but outside Gamma's default implementation scope.
- Gamma applies full docstring coverage to every touched module, class, and function, with extra care on notebook-derived helpers and CLI commands.
