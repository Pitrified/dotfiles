---
status: planned
---

# Phase 4 - Move `install.py` into `install/` with a minimal `pyproject.toml`

## Overview

Relocate `dotfiles/install.py` to `dotfiles/install/install.py` and give
it a minimal `pyproject.toml` there, now that `uv` is a guaranteed
prerequisite (phase 3). Single script, not a `src/`-layout package - see
[`00_start.md`](00_start.md) → "Single script vs `src/` package, in a
dedicated `install/` subfolder" for the full assessment and why a `src/`
package was rejected.

## Goals

1. `install.py` lives at `dotfiles/install/install.py`; nothing else
   about its logic changes in this phase beyond the item below.
2. `dotfiles_dir` is computed as `Path(__file__).resolve().parent.parent`
   instead of the hardcoded `home_dir / "dotfiles"`, closing the
   existing `# MAYBE get the folder as parent of the current file`
   comment. `home_dir` (for symlink *targets*) stays `Path.home()` -
   only the *source* repo root changes how it's found.
3. `dotfiles/install/pyproject.toml`: `requires-python = "==3.14.*"`
   (matching the box's other Python projects, see Plan), no
   `[project.dependencies]` (the script stays stdlib-only at runtime),
   `[tool.uv] package = false` (no `[build-system]`/`src/` layout
   needed), a `dev` dependency group with `pytest` and `ruff` for
   phase 5 and lint.
4. `bootstrap/install_basics.sh`'s invocation line becomes
   `uv run --project ~/dotfiles/install ~/dotfiles/install/install.py`
   (was `python3 ~/dotfiles/install.py`) - the explicit `--project` is
   required, not cosmetic; see the cwd-discovery finding in Plan.
5. `dotfiles/README.md`'s "install.py" section is updated: new path, new
   invocation (`uv run --project install install/install.py` from the
   repo root, or equivalent), and that `uv`/`pyproject.toml` here are
   unrelated to how the topic-folder symlinking itself works (still
   zero runtime deps).
6. `dotfiles/TODO.md`'s stale "Python: Poetry / pyenv" line is removed or
   rewritten to point at this plan/the new `install/` setup.

## Plan

- `git mv install.py install/install.py`; change
  `dotfiles_dir = home_dir / "dotfiles"` to
  `dotfiles_dir = Path(__file__).resolve().parent.parent`. No other
  path in the script assumes a particular cwd or script location
  (re-read end to end to confirm) - `home_dir = Path.home()` is
  unrelated and stays as-is (it's the symlink *target* root, not the
  repo root).
- `dotfiles/install/pyproject.toml`. Verified locally (scratch `uv`
  project, `uv 0.11.24`) that a non-packaged project needs no
  `[build-system]`/`hatchling` at all: `[tool.uv] package = false`
  is enough for `uv run <script>.py` and `uv run --group dev pytest`
  to both work with a plain `[project]` table and no `src/` layout -
  this is what actually delivers the "single script, not a package"
  decision in `00_start.md`, rather than just informally not adding a
  `src/` folder while still carrying hatchling/package metadata:
  ```toml
  [project]
  name = "dotfiles-install"
  version = "0.1.0"
  description = "Symlinks dotfiles topics into $HOME"
  requires-python = "==3.14.*"
  dependencies = []

  [tool.uv]
  package = false

  [dependency-groups]
  dev = [
      { include-group = "lint" },
      { include-group = "test" },
  ]
  test = [
      "pytest>=8.3.4",
  ]
  lint = [
      "ruff>=0.9.6",
  ]
  ```
  `requires-python = "==3.14.*"` matches the exact-pin convention
  already used by `tg-central-hub-bot`/`repomgr` (both
  `requires-python = "==3.14.*"`) rather than keeping the README's
  stale `>=3.6` claim - `uv` will download that interpreter itself if
  the box doesn't have it, so pinning costs nothing and the script's
  actual stdlib usage (`argparse`, `pathlib`, `logging`, `timeit`) has
  no compatibility reason to stay loose. `dependencies = []` because
  the script itself stays stdlib-only at runtime, per the existing
  decision - only the `dev` group carries `pytest`/`ruff`.
- **Non-obvious finding, tested directly:** `uv run <absolute-path>`
  only auto-discovers a project's `pyproject.toml` by walking up from
  the *current working directory*, not from the script's own
  directory. Ran `uv run /path/to/project/hello.py` from `/tmp` (script
  lives in a project dir with a `pyproject.toml` two levels up from
  nowhere near `/tmp`) - `uv` silently ignored the project entirely and
  ran the script with an ad hoc uv-managed interpreter instead of the
  project's `.venv`. Inconsequential for `install.py` itself (zero
  runtime deps, so which interpreter/env `uv` picks doesn't matter
  functionally), but it means a bare
  `uv run ~/dotfiles/install/install.py` in `install_basics.sh` (run
  from an arbitrary cwd during bootstrap) never actually touches
  `install/pyproject.toml` - `uv` is being used purely as a
  Python-version-agnostic launcher there, not as the project runner.
  Confirmed `uv run --help` has a `--project <PROJECT>` flag
  ("Discover a project in the given directory") for exactly this case.
  Use it explicitly in the bootstrap invocation so behavior doesn't
  silently depend on cwd, and so this keeps working if a real
  dependency ever gets added:
  `uv run --project ~/dotfiles/install ~/dotfiles/install/install.py`.
  (`uv run pytest` for phase 5 doesn't have this problem - it's always
  invoked with cwd inside `install/`, per that phase's plan.)

## Out of scope

- Any change to the symlinking/backup/nesting logic itself (that's
  phase 1, already done by the time this phase starts).
- Writing tests (phase 5) - this phase only makes `uv run pytest`
  *possible*, doesn't add the suite.
- Restructuring into a `src/` package - rejected, see `00_start.md`.

## Done when

- `uv run --project ~/dotfiles/install ~/dotfiles/install/install.py
  --dry-run` succeeds from a freshly cloned `dotfiles` with only `uv`
  present (no other setup), invoked from an arbitrary cwd.
- `dotfiles_dir` resolves correctly regardless of the current working
  directory the script is invoked from.
- `bootstrap/install_basics.sh` and `dotfiles/README.md` reference the
  new path and invocation; `TODO.md` no longer has the stale Poetry/pyenv
  line.
