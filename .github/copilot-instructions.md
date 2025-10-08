# Copilot / AI Agent Instructions (repo-specific)

Purpose: give an AI coding agent the exact, actionable knowledge to be productive in this repository.

Quick context
- Repo root: `databricks/`
- Small Python utility code and unit tests under `UnitTests/`.
- Key files: `arch_design/user_command.py` (simple concurrency helper), `delete_intervals.py` (interval manipulation logic), `UnitTests/test_delete_intervals.py` (unit tests).

Big picture
- This repository contains standalone Python utilities (no framework). Each module is designed to be run or imported directly. Tests are plain unittest files in `UnitTests/`.
- The code is synchronous by default; `arch_design/user_command.py` provides a tiny thread-based asynchronous helper (`CommandEngine`) and a minimal `Future` implementation used by examples.

Project-specific patterns and conventions
- Minimal dependencies: no requirements file present. Assume standard library only unless a test imports an external package.
- Tests use Python's builtin `unittest` and live under `UnitTests/`.
- Modules are simple scripts. Functions and classes are small and single-purpose. Keep changes minimal and well-tested.
- Threading conventions: `CommandEngine.submit(fn, *args, **kwargs)` starts a background thread and returns a `Future` with these methods:
  - `add_done_callback(fn)` — registers a callback to be called with the result once available. If already done, callback is invoked immediately.
  - `result()` — returns the result (no blocking implemented).
  - `done()` — returns True/False.
  Example usage from codebase:

```python
from arch_design.user_command import CommandEngine

def compute():
    return sum(range(1000000))

engine = CommandEngine()
f = engine.submit(compute)
f.add_done_callback(lambda r: print("Done:", r))
```

- Future implementation is intentionally minimal: it does not provide blocking `result(timeout)` semantics or exception handling. When modifying, preserve test expectations or expand tests when altering behavior.

Developer workflows (how to run/build/test/debug)
- Run tests from repo root (`databricks/`) with Python 3.12+ (tests import via relative sys.path manipulation in `UnitTests/test_delete_intervals.py`):

```bash
cd databricks
python -m unittest UnitTests.test_delete_intervals
```

- Run a single example script interactively by importing `arch_design.user_command.CommandEngine` as shown above. Because `CommandEngine` uses threads and callbacks, run examples in a script or interactive REPL and allow a small sleep when needed to let background threads finish.

Integration points and external dependencies
- No declared external dependencies in repository. If adding one, update a `requirements.txt` or add an install note in the README.
- No networked services or databases appear in the code — changes can be tested locally.

Files to inspect when changing behavior
- `arch_design/user_command.py` — small thread-based future/engine; central when adding async behavior.
- `delete_intervals.py` — algorithmic logic; unit tests in `UnitTests/test_delete_intervals.py` show expected outputs and edge cases.
- `UnitTests/test_delete_intervals.py` — canonical examples and expected outputs. Run these tests after edits.

How to propose changes (for AI agents)
- When editing logic in `delete_intervals.py`, also update or add unit tests under `UnitTests/` covering happy paths and edge cases. Keep API signatures stable unless tests are updated.
- Be conservative changing concurrency semantics in `arch_design/user_command.py`. If you add blocking `result()` or exception propagation, update tests or add new tests demonstrating the new behavior.

Examples of concrete tasks and guidance
- Add a timeout-capable `result(timeout)` to `Future`: implement with threading.Event and update tests to assert blocking behavior.
- Improve `CommandEngine` to use ThreadPoolExecutor: preserve `Future.add_done_callback` semantics.
- Add `requirements.txt` if external packages are introduced.

What not to change without confirmation
- Don't change the test expectations in `UnitTests/test_delete_intervals.py` unless you're intentionally fixing a bug and updating assertions.
- Avoid introducing new runtime dependencies without adding a manifest.

If you (human) are reviewing AI-generated changes
- Run the unit tests after every change. The repo is small so breakages are easy to find.
- Check that `arch_design/user_command.py` still behaves like a minimal Future: immediate callback invocation if the task is already done.

Questions for the repo owner
- Should `Future.result()` block until completion (and support timeouts), or remain non-blocking? This affects consumers.
- Is there an intended higher-level app or CI configuration that should run tests automatically?

End (short, actionable, repo-specific). Please tell me if you want the file to be adjusted (longer, more examples, or stricter rules).