# DD Plan Delta: Notebook-Faithful Web App and AIX Online Integration

Status refresh: 2026-04-05

## Summary
- Fidelity source stays locked to the legacy notebook set: `double_digits_with_MNIST.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`, and `arithmetic_double_digits.ipynb`.
- Gamma landed on April 4, 2026 and restored the MNIST-first shared runtime, CLI, and notebook-derived model flow, but it intentionally left the main web pass unfinished.
- Delta closes the remaining non-deferred web gaps: the page is now notebook-like, `comparison` is surfaced in the UI, divide is available in structured arithmetic, browser preset switching is implemented, frontend API calls are mount-safe, and the public mounted DD route is healthy again.
- The production `doubledigits` App Engine service that was failing on April 5, 2026 (`20260405t113241`) has been replaced by live version `20260405t141616`, serving at `https://aix-labs.uw.r.appspot.com/doubledigits/`.
- The original Delta target of `instance_class: F2` was tested and rejected by live smoke. The measured production fix is `F4`, plus bundled `data/mnist.npz`, lazy runtime loading, and single-threaded torch/BLAS settings.

## Public Interfaces
- `GET /api/v1/presets?level=<single|double|arithmetic>`
  - implemented for the advanced notebook-style preset panel
- `POST /api/v1/infer`
  - now accepts optional `preset`
- `GET /api/v1/visualizations/<kind>`
  - now accepts optional `preset`
- `GET /healthz`
  - lightweight and does not load model weights
- Server-rendered frontend config
  - `mountBase` and `apiBase` are injected into the page and used by the browser client
- Browser preset switching
  - implemented as read-only state; training and artifact generation remain CLI-only

## Milestones
- [x] M1: Fidelity lock and cleanup.
  - Delivered a retro notebook-style scroll with anchored single/double/arithmetic sections, IBM Plex typography, grid-paper background, notebook captions, and notebook-derived prose.
- [x] M2: Shared-runtime web parity.
  - Kept examples, inference, visuals, arithmetic semantics, and preset metadata on shared runtime code.
  - Surfaced `comparison`, added divide controls, and exposed advanced preset switching in the browser.
- [x] M3: Responsive mounted UI.
  - Added explicit loading/success/error states and server-rendered mount-safe API config.
  - Verified local standalone, local `/doubledigits` mount, and deployed `/doubledigits` routing behavior.
- [x] M4: Cloud stabilization.
  - Made home, examples, presets, and health lightweight.
  - Vendored `data/mnist.npz` to keep example routes off the Keras dataset-download path.
  - Tested `F2`, observed live cold-inference OOMs, and corrected the production service to `F4`.
  - Verified public `GET /doubledigits/`, `GET /doubledigits/api/v1/examples?level=single`, and `POST /doubledigits/api/v1/infer` return `200` on live version `20260405t141616`.
- [x] M5: Verification hardening.
  - Added DD and AIX coverage for presets, optional preset selection, divide support, comparison rendering, mount-safe frontend config, and `APP_BASE_PATH`.
  - Investigated the Windows post-`pytest` access violation and documented it as a runtime issue rather than a DD-specific blocker.
- [x] M6: Docs and release close-out.
  - Updated `README.md`, `docs/migration_inventory.md`, `docs/doubledigits_design.md`, and this Delta plan file.
  - Gamma’s web-copy/UI-refinement carry-over is now closed, while handwriting input, browser training, and ensembling remain explicit deferrals.

## Test Plan
- Standalone DD:
  - `python -m pytest tests/test_cli.py tests/test_app.py tests/test_core.py`
  - result: passed locally
- Mounted AIX:
  - `python -m pytest tests/test_hub_routes.py`
  - result: passed locally
- Base-path behavior:
  - covered by `tests/test_app.py::test_build_local_app_respects_app_base_path`
- Cloud smoke:
  - deployed DD version `20260405t141616`
  - verified `200` on mounted public home, examples, and inference
  - checked logs for the live version and found no `503` or hard-memory-limit entries after the final `F4` deploy

## Assumptions
- Canonical public DD routing remains the dedicated App Engine service behind `/doubledigits`; no AIX `dispatch.yaml` change is planned unless smoke tests prove current routing is wrong.
- Delta keeps training and batch export as CLI-only even though preset selection becomes browser-visible.
- Preset selection is page-local state; Delta does not add saved preferences or deep-link query-state for every control.
- Unrelated dirty-worktree changes in AIX remain untouched unless they are directly required for DD mount tests or deploy verification.

## Known issue
- On Windows with Python 3.14, pytest runs that exercise the Keras torch backend can still print a fatal access-violation trace during interpreter shutdown after the tests themselves pass. Minimal non-pytest inference scripts exit cleanly, so this remains documented as an environment/runtime issue rather than a DD product blocker.
