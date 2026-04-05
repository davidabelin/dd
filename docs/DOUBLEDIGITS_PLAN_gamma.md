# Plan Gamma: CLI-First MNIST Execution

> Archival reference: the canonical maintainer documentation now lives in [docs/maintainer/README.md](maintainer/README.md). This phase plan is retained as implementation history.

## Summary
- Execute the migration as code and docs, not as another planning pass.
- Restore the runtime to MNIST-only behavior derived from the notebooks.
- Expose notebook-faithful retrieval, inference, visualization, serving, and training through `python -m dd_cli`.
- Leave broader web-app copy and UI refinement to Delta.

## Implemented scope
- Replace the temporary sklearn-based runtime with notebook-derived Keras models running on the torch backend.
- Keep the shell-neutral entrypoint at `python -m dd_cli`.
- Expose raw MNIST access with `dataset show`.
- Expose curated and structured scene workflows with `examples list`, `examples show`, and `examples generate`.
- Expose inference with `infer`, notebook-style explanations with `visualize`, and local serving with `serve`.
- Expose notebook-derived preset discovery and training with `train list` and `train run`.
- Keep batch export shared in core code, not embedded in CLI glue.

## Notebook fidelity rules
- Data source: MNIST only.
- Single digits and generated scenes render with `binary_r`.
- Learned activation maps render with `viridis`.
- Weight views render with `bone`.
- Double-digit and arithmetic scenes use the notebook 28x56 layout.
- Arithmetic preserves notebook operator placement and divide semantics, including the divide-by-zero sentinel.
- Model builders, presets, and default hyperparameters come from the notebooks and are registered explicitly in `dd_models`.

## Public interfaces
- `python -m dd_cli dataset show --split <train|test> --index N [--out PATH] [--json]`
- `python -m dd_cli examples list --level <single|double|arithmetic> [--count N] [--json]`
- `python -m dd_cli examples show --level ... [--example-id ID | --mnist-index N | structured args] [--json]`
- `python -m dd_cli examples generate --level ... --count N --out DIR [--json]`
- `python -m dd_cli infer --level ... [--example-id ID | structured args] [--json]`
- `python -m dd_cli visualize --kind <feature_maps|prototype|comparison> --level ... [--example-id ID | structured args] [--write-dir DIR] [--json]`
- `python -m dd_cli serve`
- `python -m dd_cli train list [--level ...] [--json]`
- `python -m dd_cli train run --preset <name> [--train-size N] [--test-size N] [--epochs N] [--batch-size N] [--force] [--json]`

## Shared implementation rules
- CLI commands call core/runtime/model code directly rather than wrapping HTTP.
- Text output is the human-readable default; `--json` is the scripting contract.
- Batch export writes `images/`, `manifest.csv`, and `dataset.npz`.
- `manifest.csv` aligns row-for-row with `dataset.npz`.
- Cached model artifacts live under `models/` as `.keras` plus metadata `.json`.
- Full docstrings are required on touched modules, classes, functions, and CLI handlers.

## Delta handoff
- Delta picks up web copy, template parity, and broader UI refinement.
- Gamma leaves the web shell operational but does not expand frontend polish beyond minimal parity.
