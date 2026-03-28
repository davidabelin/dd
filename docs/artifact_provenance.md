# Double-digits Model and Artifact Provenance

## V1 baseline artifacts

The first app release uses lightweight baseline classifiers and deterministic generators so the lab is interactive immediately and does not depend on heavyweight notebook-era training infrastructure.

### Inputs
- `sklearn.datasets.load_digits()` provides the base handwritten digit samples
- digit samples are resized into `28x28` grayscale canvases for guided visualization
- double-digit and arithmetic scenes are composed programmatically from those base digits

### Baseline inference
- single-digit recognition uses a cached scikit-learn logistic regression model
- double-digit recognition composes two single-digit predictions
- arithmetic recognition composes two digit predictions plus operator template matching, then computes the controlled result

### Why this differs from the notebook era
- notebook-era TensorFlow experiments mixed tutorial code, exploratory code, and product ideas
- v1 standardizes on one clean inference contract first
- future phases may replace or augment the baselines with exported `tf.keras` artifacts once the interactive lab flow is stable
