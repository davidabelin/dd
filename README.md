## dd

Double-digits guided lab for AIX, exposed publicly as `doubledigits`.

### Scope of this initial implementation
- Guided three-level web lab:
  - single-digit recognition
  - two-digit composition
  - controlled arithmetic
- Notebook logic migrated into clean Python modules and docs
- Lightweight baseline inference and visualization pipeline
- Standalone Flask app that mounts cleanly into AIX under `/doubledigits`

### Layout
- `dd_core/`
- `dd_models/`
- `dd_visuals/`
- `dd_web/`
- `tests/`
- `docs/`
- `scripts/`
- `data/`
- `models/`

### Local run
```powershell
pip install -r requirements.txt
python run.py
```

Then open `http://127.0.0.1:5003/`.
