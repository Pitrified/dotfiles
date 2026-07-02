---
status: done
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

Phase 1 landed, so this is written against `link_config()`'s actual
signature rather than a hypothetical one:
`link_config(config_at_dot, home_dir, backup_dir, dry_run=False)` and
`backup(src_at_home, backup_dir, dry_run=False)` already take
`home_dir`/`backup_dir` as explicit arguments - neither reads
`Path.home()` internally. **Correction from the earlier draft:** no
testability refactor is needed for these two goals; only `run_install()`
itself (untested, out of scope - see below) still reads `Path.home()`
and the phase-4 `__file__`-relative `dotfiles_dir` inline.

- One test module, `install/tests/test_install.py` - mirrors the
  single-script decision in `00_start.md`; split later only if it
  actually grows unwieldy.
- Fixtures: `tmp_path` standing in for `home_dir`, a `backup_dir =
  tmp_path / ".rcback"` (created per-test, not shared), and small
  helper fixtures that write a fake dotfiles source file/dir under
  `tmp_path` to act as `config_at_dot` - never anything under the real
  `$HOME` or this checkout's actual `dotfiles/`.
- `link_config()` cases (Goal 1 + the already-linked/divergence-guard
  parts of Goal 3):
  - flat name (no `__`) → `~/.foo`.
  - one level of `__` nesting → `~/.a/b`, parent dir auto-created.
  - multiple levels (`a__b__c`) → `~/.a/b/c`.
  - source is a directory → `target_is_directory=True` is honored
    (assert the resulting symlink resolves to a directory).
  - already a correct symlink to `config_at_dot` → early return, *no*
    backup happens (assert `backup_dir` stays empty) - this is the
    idempotent-rerun behavior phase 1 added as a side effect.
  - real (non-symlink) file at the target with **different** content
    than the source → the divergence warning is logged (`caplog`) *and*
    the file still gets backed up and replaced - pin down that this
    warns but does not abort or skip.
  - real (non-symlink) file at the target with **identical** content →
    no warning, but it still gets backed up and replaced by a symlink
    (there is no "matches, leave alone" shortcut in the current code -
    worth a test precisely because that's non-obvious from reading
    `link_config()` alone).
  - `dry_run=True` → no filesystem change at all in any of the above
    (no symlink created, no backup dir entry, target untouched).
- `backup()` cases (Goal 2):
  - existing real file/dir at `src_at_home` → moved into `backup_dir`
    under the same name.
  - dangling symlink at `src_at_home` (target doesn't exist) → still
    backed up - `exists()` follows symlinks and would miss this, which
    is exactly why the current code also checks `is_symlink()`;
    regressing that check back to `exists()` alone should fail this
    test.
  - nothing at `src_at_home` → no-op, `backup_dir` stays empty.
  - `dry_run=True` → no move happens.
- `find_free_dir()` and `is_conf_dir()` are small enough to cover
  incidentally (free-dir picks an unused suffix; `is_conf_dir` rejects
  `.git` and non-directories) but aren't separate Goals - low-cost
  additions alongside the above, not a reason to expand scope.

## Out of scope

- Testing `add_source` / `~/.bash_aliases` generation end-to-end - lower
  value (string-append to a file), more filesystem/state to fake, and
  not one of the stated Goals.
- Testing `run_install()` itself end-to-end - it still reads
  `Path.home()` and (post phase 4) the `__file__`-relative
  `dotfiles_dir` directly rather than taking them as parameters, so
  exercising it would mean monkeypatching `Path.home`/`__file__` or a
  real subprocess run; `link_config()`/`backup()` already carry the
  actual logic worth pinning down, so this isn't worth the added
  complexity unless a real bug shows up there later.
- Any change to `install.py`'s actual behavior - this phase adds tests
  for existing behavior (plus phases 1-4's changes), it doesn't change
  what the script does.

## Done when

- `uv run pytest` (from `install/`) passes and covers every bullet in
  Goals.
- A deliberate regression in the target-path nesting logic (tested
  manually while writing the suite, not left in the repo) fails at least
  one test, confirming the suite would actually catch it.
