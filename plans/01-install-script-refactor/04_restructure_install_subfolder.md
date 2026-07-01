---
status: draft
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
3. `dotfiles/install/pyproject.toml`: `requires-python` matching what's
   actually needed (re-examine the currently-documented `>=3.6` claim -
   `uv`'s own minimum is far newer), no `[project.dependencies]` (the
   script stays stdlib-only at runtime), a dev dependency group with
   `pytest` and `ruff` for phase 5 and lint.
4. `bootstrap/install_basics.sh`'s invocation line becomes `uv run
   ~/dotfiles/install/install.py` (was `python3 ~/dotfiles/install.py`).
5. `dotfiles/README.md`'s "install.py" section is updated: new path, new
   invocation (`uv run install/install.py` from the repo root, or
   equivalent), and that `uv`/`pyproject.toml` here are unrelated to how
   the topic-folder symlinking itself works (still zero runtime deps).
6. `dotfiles/TODO.md`'s stale "Python: Poetry / pyenv" line is removed or
   rewritten to point at this plan/the new `install/` setup.

## Plan

- (Detail the exact `pyproject.toml` contents - project name,
  `requires-python`, dev-dependency-group syntax - once this phase
  starts; confirm against the `uv` version actually available on this
  box, per phase 3's findings.)
- `git mv install.py install/install.py`, adjust the `dotfiles_dir`
  computation, re-verify every other path in the script that assumes a
  particular working directory or script location still resolves
  correctly (e.g. relative imports, if any get added - none exist today).

## Out of scope

- Any change to the symlinking/backup/nesting logic itself (that's
  phase 1, already done by the time this phase starts).
- Writing tests (phase 5) - this phase only makes `uv run pytest`
  *possible*, doesn't add the suite.
- Restructuring into a `src/` package - rejected, see `00_start.md`.

## Done when

- `uv run ~/dotfiles/install/install.py --dry-run` succeeds from a
  freshly cloned `dotfiles` with only `uv` present (no other setup).
- `dotfiles_dir` resolves correctly regardless of the current working
  directory the script is invoked from.
- `bootstrap/install_basics.sh` and `dotfiles/README.md` reference the
  new path and invocation; `TODO.md` no longer has the stale Poetry/pyenv
  line.
