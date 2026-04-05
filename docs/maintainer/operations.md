# Operations

## Local Development

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the local app:

```powershell
python run.py
```

Or:

```powershell
python -m dd_cli serve
```

Default local address:

- `http://127.0.0.1:5003/`

## Testing

Behavioral baseline:

```powershell
python -m pytest tests/test_core.py tests/test_cli.py tests/test_app.py -q
```

The baseline is intended to cover:

- core example and arithmetic semantics
- CLI behavior and export layout
- web routes, preset metadata, visualization payloads, and mount-safe path handling

## Artifact Retraining

Train a preset explicitly:

```powershell
python -m dd_cli train run --preset single_mnist_dense
python -m dd_cli train run --preset double_project_modelx
python -m dd_cli train run --preset arithmetic_modelx
```

Useful overrides:

```powershell
python -m dd_cli train run --preset arithmetic_modelx --train-size 512 --test-size 128 --epochs 2 --batch-size 64
```

Rules for maintainers:

- prefer CLI training over ad hoc scripting
- keep the matching `.json` metadata alongside any updated `.keras` artifact
- verify the target level and notebook lineage before replacing a shipped default artifact

## Replacing Model Artifacts

When replacing a shipped default artifact:

1. Train or generate the new `.keras` and `.json`.
2. Confirm the preset name still matches the registry entry.
3. Run the behavioral baseline tests.
4. Smoke the relevant web route or CLI path.
5. Preserve the read-only cloud posture if the artifact is intended for deployment.

## Mounted Execution Under AIX

DD must work both standalone and when mounted by AIX.

Key mount assumptions:

- AIX imports `dd_web.create_app`
- mounted path is `/doubledigits`
- local mount simulation uses `APP_BASE_PATH=/doubledigits`
- frontend API URLs must come from server-rendered config, not hard-coded root-relative paths

Local mount test:

```powershell
$env:APP_BASE_PATH = "/doubledigits"
python run.py
```

Then open:

- `http://127.0.0.1:5003/doubledigits/`

## App Engine Deployment Assumptions

The production manifest is `app.aix.yaml`.

Operational expectations from that manifest:

- service name is `doubledigits`
- mounted base path is `/doubledigits`
- instance class is `F4`
- entrypoint serves `run:app`
- model artifacts are read from `/srv/models`
- bundled MNIST archive is read from `/srv/data`
- `KERAS_HOME` and `MPLCONFIGDIR` point into `/tmp`
- torch and BLAS thread counts stay pinned to `1`

These settings are part of the measured production posture, not incidental local preferences.

## Browser And Frontend Maintenance Notes

The frontend depends on three server-side guarantees:

- `home.html` receives `dd_frontend_config`
- `mountBase` reflects `request.script_root`
- `apiBase` is derived from `url_for('api.list_examples')`

If any of those change, retest both:

- standalone root-path behavior
- mounted `/doubledigits` behavior

## Known Environment Caveat

On Windows with Python `3.14`, test runs that exercise the Keras torch backend can emit a post-success shutdown trace. Current DD practice treats this as an environment/runtime caveat when:

- the tests themselves pass
- equivalent non-pytest inference runs exit cleanly

Do not classify that caveat as a DD regression unless behavior changes before shutdown.
