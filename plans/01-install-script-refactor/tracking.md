# install.py folder-symlink nesting refactor - tracking

Extend `install.py`'s topic-level whole-folder symlink path to support
`__` → `/` nesting, matching the item-level path that already has it;
migrate the Claude skill symlinks to folder-based ones; make `uv` a
guaranteed prerequisite so `install.py` can move into a self-contained
`install/` subfolder with a real `pyproject.toml`; and add test coverage
for the target-path logic. Split out of
[`../02-modernize-vim-setup/`](../02-modernize-vim-setup/) once it became
clear the fix isn't a vim-specific concern. Background in
[`00_start.md`](00_start.md).

## Key decisions

- **`uv` becomes a guaranteed prerequisite.** `bootstrap/install_basics.sh`
  gets the one-line `uv` install (already used by `install_python.sh`)
  moved inline, immediately before cloning `dotfiles` - mirroring how it
  already installs `python3-pip` inline before that same clone. The
  installer is then invoked via `uv run`, not bare `python3`.
- **`install.py` moves into a dedicated `install/` subfolder**
  (`install/install.py`), single script, not a `src/`-layout package -
  the `install/` subfolder itself is what keeps `pyproject.toml`/`tests/`
  out of the topic-folder root; a `src/` layout on top buys nothing for
  a ~300-line script with no library surface. Per the user: "no bloat and
  no overengineering... in the end it's a renamer."
- **`dotfiles_dir` becomes `__file__`-relative** instead of the hardcoded
  `home_dir / "dotfiles"`, closing the old `# MAYBE get the folder as
  parent of the current file` comment already in the code - falls out of
  the move to `install/`.
- **The Claude skill-symlink migration doesn't need phase 1 at all** -
  the item-level `.symlink` path already supports directories, so
  converting `claude__skills__<name>__SKILL.md.symlink` to
  `claude__skills__<name>.symlink/SKILL.md` is a pure data move, zero
  `install.py` changes. Corrected from the original (wrong) write-up that
  implied it depended on the topic-level fix.
- **`dotfiles/TODO.md`'s old "Poetry / pyenv" line is superseded** by the
  `install/` `pyproject.toml`; update/remove it once phase 4 lands.
- Full reasoning and rejected alternatives: `00_start.md` → "Broadening
  the scope".

## Phases

| #  | Phase                                                     | Plan                                                                          | Status  |
| -- | ------------------------------------------------------------ | -------------------------------------------------------------------------------- | ------- |
| 1  | Extend `install.py` for nested folder symlinks            | [`01_extend_installpy_nesting.md`](01_extend_installpy_nesting.md)             | done    |
| 2  | Migrate Claude skill symlinks to folder-based ones         | [`02_migrate_claude_skill_symlinks.md`](02_migrate_claude_skill_symlinks.md)   | draft   |
| 3  | Reorder `bootstrap` to install `uv` before cloning dotfiles | [`03_bootstrap_install_uv_first.md`](03_bootstrap_install_uv_first.md)         | draft   |
| 4  | Move `install.py` into `install/` with a minimal `pyproject.toml` | [`04_restructure_install_subfolder.md`](04_restructure_install_subfolder.md) | draft   |
| 5  | Test coverage for target-path/nesting logic                | [`05_add_tests.md`](05_add_tests.md)                                          | draft   |

Status values: draft / planned / in progress / done / superseded / discarded.

## Log

- 2026-07-02 : split out of `02-modernize-vim-setup` (formerly
  `01-modernize-vim-setup`) at the user's request, so the `install.py`
  mechanism fix has its own plan instead of being phase 2 of the vim
  migration. Moved the phase content over unchanged (renumbered to phase
  1 here); not expanding scope yet - that's a later planning pass.
- 2026-07-02 : broadened scope at the user's request (first pass). Read
  `install.py`'s full git history (stdlib-only from the start) and
  `bootstrap/install_basics.sh` (runs `python3 ~/dotfiles/install.py`
  with the system interpreter before `uv` is guaranteed installed).
  Found a stale `TODO.md` line ("Python: Poetry / pyenv"). Initially
  decided to keep `install.py` runtime-dependency-free and add a
  dev-only `pyproject.toml` - superseded by the next entry.
- 2026-07-02 : broadened again at the user's request (second pass),
  correcting the first pass. The user pointed out `install_basics.sh`
  already installs things inline right before use (`python3-pip` before
  the `dotfiles` clone) and `install_python.sh` is already a single `uv`
  install line - so that line can just move earlier instead of treating
  `uv` as unavailable. Also pointed out the item-level `.symlink` path
  already supports directories, so the Claude skill-symlink migration
  isn't blocked by phase 1 as originally written - folded in as its own
  phase. And asked for an explicit single-script-vs-`src`-package
  assessment given a dedicated `install/` subfolder, which was decided in
  favor of the single script (see Key decisions). Replaced the old
  phases 2-3 (dev-only tooling, tests-in-place) with the current phases
  2-5: skill-symlink migration, `bootstrap` reorder, the `install/` move,
  then tests against the new layout.
- 2026-07-02 : implemented phase 1. Factored the topic-level and
  item-level `.symlink` handling in `install.py` into one shared
  `link_config()` (nesting, parent-mkdir, backup, already-linked skip,
  divergence guard) - topic-level folders now support `__` nesting and,
  as a side effect, are no longer needlessly re-backed-up/relinked on
  every run (the old topic-level code had no already-linked skip).
  Verified with a fake-`$HOME` fixture (flat topic, nested topic, nested
  item) covering dry-run, real run, and idempotent second run, plus a
  `--dry-run` pass against the real dotfiles tree showing no regressions.
  No test suite added yet - that's phase 5, sequenced after the `install/`
  move.
