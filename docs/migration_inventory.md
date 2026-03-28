# Double-digits Notebook Migration Inventory

## Source repo
- Legacy source: `C:\Users\David\Documents\Repositories\double-digits`
- New app target: `C:\Users\David\Documents\Local_Python\dd`

## Salvage matrix

| Source notebook | Role in migration | What is extracted now | What is deferred |
|---|---|---|---|
| `double_digits_with_MNIST.ipynb` | main extraction source | digit-pair composition helpers, label semantics, basic recognition flow | original notebook execution environment |
| `minimal_convolution_double_digits.ipynb` | main extraction source | visualization ideas, comparison-oriented examples, feature-map style views | TensorFlow-specific convnet reproduction |
| `digits_project.ipynb` | main extraction source | arithmetic narrative, composition helpers, result logic | notebook-only training loops |
| `arithmetic_double_digits.ipynb` | main extraction source | operator overlay logic, arithmetic example generation, result rendering ideas | large experimental model variants |
| `digits_classifier.ipynb` | narrative/reference | teaching prompts, exercise framing, baseline comparison language | Estimator-era training code |
| `double_digits_classifier.ipynb` | narrative/reference | teaching prompts, exercise framing, visual inspection ideas | Estimator-era training code |
| `introduction-to-ensembling-stacking-in-python.ipynb` | deferred | none in v1 | future “other designs” branch |

## Extracted function lineage

The new repo preserves the spirit of these notebook helpers as tested modules:

- `doubleDigits` -> wide-image composition for two digits and arithmetic scenes
- `getDoubleDigits` -> deterministic batch example generation
- `getOperator` -> operator overlay templates for arithmetic examples
- `get_results` -> arithmetic result semantics and explanation text
- `showOutput` / `show_layer_output` / `show_layers` -> visualization payload builders and guided explanation panels

## Narrative and exercise themes carried forward

- Guided progression from single digits to double digits to arithmetic
- Comparison between representation, composition, and prediction
- Visualization of intermediate “what the model sees” views, adapted into lightweight feature maps and prototype panels
- Explicit explanation that v1 is inference-first and educational, not a training console

## Explicit non-goals for v1

- Raw `.ipynb` notebooks as live product assets
- TensorFlow Estimator compatibility layers
- In-browser or user-triggered retraining
- Touch/mouse handwriting canvas input
