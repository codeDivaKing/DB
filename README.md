DB
===

Small collection of Python utility modules and unit tests.

Key files
- `arch_design/user_command.py` — small thread-based `CommandEngine` and minimal `Future` implementation.
- `delete_intervals.py` — interval manipulation logic.
- `UnitTests/test_delete_intervals.py` — unit tests using Python `unittest`.

Quick start

1. Run the example that uses `CommandEngine`:

```bash
cd /Users/kingsley/Documents/coding/databricks
python - <<'PY'
from arch_design.user_command import CommandEngine

def compute():
    return sum(range(1000000))

engine = CommandEngine()
f = engine.submit(compute)
f.add_done_callback(lambda r: print('Done:', r))
PY
```

2. Run tests:

```bash
cd /Users/kingsley/Documents/coding/databricks
python -m unittest UnitTests.test_delete_intervals -v
```

Notes
- This repo relies on the Python standard library. Use Python 3.10+ or 3.12 where available.
- If you add third-party dependencies, create a `requirements.txt`.
