---
status: draft
---

# Phase 5 - Test coverage for target-path/nesting logic

## Overview

`install.py` has no tests today. The highest-value, lowest-effort target
is the logic phase 1 touches directly: resolving a `.symlink` entry
(topic- or item-level) to its final home-directory path, including
`__` → `/` nesting - plus the surrounding safety behavior (already-linked
skip, divergence guard, backup, `--dry-run`). Lives in
`dotfiles/install/tests/`, run via `uv run pytest` from within
`install/`, now that phase 4 has given it a real project to run in. See
[`00_start.md`](00_start.md) → "Tests" for why this comes after the move
rather than before (avoids writing tests against a layout that's about to
change).

## Goals

1. The target-path resolution helper(s) that phase 1 factors out (shared
   between the topic- and item-level cases) are covered for: no `__` in
   the name (flat `~/.foo`), one level of nesting, multiple levels,
   files vs. directories.
2. `backup()`'s behavior is covered: backs up an existing real file/dir,
   backs up a dangling symlink, no-ops when nothing exists at the target,
   respects `--dry-run` (no filesystem change).
3. The "already correctly linked" skip and the divergence-guard warning
   (real file differing from repo source) are each covered by a case that
   would fail loudly if the guard regressed.
4. Tests run against a `tmp_path`-based fake `home_dir` and a fake
   dotfiles source tree - never touching the real `$HOME` or this
   machine's actual dotfiles checkout.

## Plan

- (Detail once phase 1's refactor lands and the shared target-path helper
  has a concrete signature to test against.)
- Likely needs `run_install`'s `home_dir` and `dotfiles_dir` to become
  parameters (or the relevant logic extracted into functions that take
  them as arguments) rather than reading `Path.home()` / the
  `__file__`-relative computation from phase 4 inline - a small
  testability refactor, not a restructuring.

## Out of scope

- Testing `add_source` / `~/.bash_aliases` generation end-to-end (lower
  value, more filesystem/state to fake) unless it falls out naturally
  from the `home_dir` parameterization above.
- Any change to `install.py`'s actual behavior - this phase adds tests
  for existing behavior (plus phases 1-4's changes), it doesn't change
  what the script does.

## Done when

- `uv run pytest` (from `install/`) passes and covers every bullet in
  Goals.
- A deliberate regression in the target-path nesting logic (tested
  manually while writing the suite, not left in the repo) fails at least
  one test, confirming the suite would actually catch it.
