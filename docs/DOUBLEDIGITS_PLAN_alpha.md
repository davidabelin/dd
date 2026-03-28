# Double-digits Standalone AIX Arm Plan

## Summary
- Build `dd` as a standalone Flask-based lab that follows the AIX sibling-arm pattern, but use the public AIX slug `doubledigits` rather than `dd` so the arm reads clearly in the hub and routes.
- Make v1 a guided interactive lab, not just a calculator and not a research console: Level 1 covers single digits, Level 2 covers two-digit composition, and Level 3 introduces controlled arithmetic.
- Keep the first migration inference-first: extract reusable notebook logic, ship curated models and visual diagnostics, and defer full training workflows and touch-canvas handwriting input to later milestones.
- Treat the legacy notebook repo as source material only: extract all useful code, data-generation logic, narrative, and exercises into the new `dd` repo, then retire the notebooks from the live product path.

## Key Changes
- Create a new `dd` package layout around four runtime concerns: `dd_core` for image composition and label semantics, `dd_models` for baseline model wrappers and artifact loading, `dd_visuals` for activation/feature-map views, and `dd_web` for pages and APIs. Keep `scripts/`, `tests/`, `docs/`, `data/`, and `models/` beside them.
- Run a notebook-to-module migration pass with an explicit inventory:
  - Convert `doubleDigits`, `getDoubleDigits`, `getOperator`, `get_results`, `showOutput`, `show_layer_output`, and similar helpers into pure Python modules with tests.
  - Treat `double_digits_with_MNIST.ipynb`, `minimal_convolution_double_digits.ipynb`, `digits_project.ipynb`, and `arithmetic_double_digits.ipynb` as the main code-extraction sources.
  - Treat `digits_classifier.ipynb` and `double_digits_classifier.ipynb` as narrative/comparison sources; rewrite their useful exercises into docs/UI copy, but do not port TensorFlow Estimator-era code as live product code.
  - Defer `introduction-to-ensembling-stacking-in-python.ipynb` to a future “other designs” extension rather than part of the first app.
- Standardize all migrated model code on `tf.keras`-style artifacts and one clean inference contract. Do not keep mixed Estimator/Keras execution paths in the new app.
- Build the first public UI as a guided lab shell with three pages or modes:
  - Single-digit lab: curated examples, baseline prediction, confidence view, and first-layer/activation visual explanations.
  - Double-digit lab: show how two digits are composed into one wider image, how labels map to `00-99`, and how baseline models separate composition from recognition.
  - Arithmetic lab: use curated or programmatically generated operand/operator examples first, explain the operator overlay logic, and show predicted result plus model confidence.
- For v1 input, use curated examples, random scenario generation, and simple structured controls instead of freehand canvas drawing. Reserve touch/mouse handwriting capture and handwritten output rendering for phase 2.
- Keep v1 storage lightweight and mostly file-based: model artifacts, example manifests, and generated demo assets live under `models/` and `data/`. Do not introduce a database until the lab needs training jobs, user sessions, or artifact history.
- Define a small public API surface for the standalone app:
  - `GET /` landing page and level navigation.
  - `GET /api/v1/examples` for curated/generated scenarios by level.
  - `POST /api/v1/infer` for inference over a selected scenario or structured digit/operator input.
  - `GET /api/v1/visualizations/<kind>` for activation-map, feature, or comparison payloads tied to the current scenario.
- Add one migration-documentation layer in the new repo so the old repo can be abandoned cleanly:
  - notebook inventory and salvage matrix
  - extracted narrative/exercise register
  - model/artifact provenance notes
  Raw `.ipynb` files should not become active product assets in the new repo.
- Integrate into AIX only after the standalone app works locally:
  - add an AIX adapter pointing at `../dd`
  - register the `doubledigits` lab in the hub and TOC
  - add dispatch/service wiring consistent with the other mounted arms
- Reserve phase 2 for the handwriting surface:
  - touch/mouse canvas for two operands and an operator
  - optional handwritten-style rendered result
  - mobile-friendly input workflow
  - same inference API extended to accept stroke/raster payloads

## Test Plan
- Migration tests: extracted generators produce the expected image shapes, label ranges, and operator encodings for single-digit, double-digit, and arithmetic scenarios.
- Model wrapper tests: baseline model loaders return stable predictions on fixed fixtures and expose intermediate activations in a consistent shape.
- API tests: example generation, inference, and visualization endpoints return deterministic schemas and fail clearly on malformed requests.
- UI tests: each guided lab level loads, switches scenarios without state corruption, and renders prediction plus explanatory visuals.
- AIX smoke tests: the standalone app mounts under `/doubledigits`, hub metadata renders correctly, and the mounted page still serves the standalone lab chrome.
- Acceptance scenarios:
  - A user can walk through Levels 1 and 2 without training anything.
  - A user can run a controlled arithmetic example in Level 3 and understand how the operator/result pipeline works.
  - An engineer can identify every notebook-derived feature in the migration inventory and confirm whether it was extracted, rewritten as docs, or explicitly deferred.

## Assumptions
- Public naming stays meaningful: repo folder is `dd`, but the arm slug, service name, and AIX route should be `doubledigits`.
- The first useful release is guided and educational, not notebook-hosting, and not a full training console.
- Inference-first means curated baseline artifacts ship with the app; retraining, artifact generation, and “other model designs” come after the interactive lab is solid.
- Mouse/touch handwriting input is important, but it is explicitly a phase-2 milestone rather than a blocker for the first public lab.
- The old `double-digits` repo remains a temporary excavation site only until the new repo contains the extracted code, narrative, exercises, and migration record.
