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
| 2  | Migrate Claude skill symlinks to folder-based ones         | [`02_migrate_claude_skill_symlinks.md`](02_migrate_claude_skill_symlinks.md)   | done    |
| 3  | Reorder `bootstrap` to install `uv` before cloning dotfiles | [`03_bootstrap_install_uv_first.md`](03_bootstrap_install_uv_first.md)         | done    |
| 4  | Move `install.py` into `install/` with a minimal `pyproject.toml` | [`04_restructure_install_subfolder.md`](04_restructure_install_subfolder.md) | done    |
| 5  | Test coverage for target-path/nesting logic                | [`05_add_tests.md`](05_add_tests.md)                                          | done    |
| 6  | Clean up untracked leftovers in the `bootstrap` repo       | [`06_bootstrap_repo_cleanup.md`](06_bootstrap_repo_cleanup.md)                | done    |
| 7  | Migrate the exa aliases to eza                             | [`07_exa_to_eza_migration.md`](07_exa_to_eza_migration.md)                    | done    |

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
- 2026-07-02 : implemented phase 2. `git mv`'d both skills'
  `claude__skills__<name>__SKILL.md.symlink` into
  `claude__skills__<name>.symlink/SKILL.md`; confirmed with `--dry-run`
  then a real `install.py` run that `~/.claude/skills/{caveman,
  tracked_development}` are now directory symlinks straight to the repo
  folder (old file-symlink layout backed up, content unchanged, verified
  by `cat`). No `install.py` changes needed, as expected. Updated
  `README.md`'s nesting example to show the new folder-symlink form.
- 2026-07-02 : follow-up to phase 2, at the user's request. The IDE's
  skill linter flagged `tracked_development`'s frontmatter `name` for
  using an underscore (Agent Skills spec: lowercase/numbers/hyphens
  only, must match the resolved directory name) - a pre-existing issue,
  unrelated to phase 2, surfaced by editing the file through its new
  folder-symlink path. Renamed end-to-end to `tracked-development`:
  dotfiles folder/symlink, frontmatter `name`, `README.md`, this plan's
  phase 2 file, `00_start.md`, and the one reference in
  `linux-box-cloudflare/configs/claude/rules/local-box.md`. Installed
  command changes from `/tracked_development` to `/tracked-development`.
  Verified via `install.py`. `caveman`'s `name` field was already spec-
  compliant, left unchanged.
- 2026-07-02 : fleshed out phases 3-5 from draft to planned, at the
  user's request, by resolving the placeholders each had deferred.
  Read `~/bootstrap/install_basics.sh`/`install_python.sh` for real
  (phase 3 was written from memory before). Fetched the live `uv`
  installer script and confirmed by reading it that it only persists
  PATH via shell-rc sourcing for *future* shells, never the running
  script - so `install_basics.sh` needs an explicit `export PATH=...`
  right after the `uv` install line, not just reordering. Ran a real
  scratch `uv` project locally (`uv 0.11.24`) and confirmed
  `[tool.uv] package = false` lets a `pyproject.toml` skip
  `[build-system]`/`hatchling`/`src/` entirely while `uv run
  <script>.py` and `uv run --group dev pytest` both still work -
  concretized phase 4's `pyproject.toml` around that instead of the
  vague "minimal" placeholder, and matched `requires-python =
  "==3.14.*"` to `tg-central-hub-bot`/`repomgr`'s existing convention.
  Also found, by testing directly, that `uv run <absolute-script-path>`
  does not discover a project's `pyproject.toml` unless invoked from
  within (or under) that project's directory - it silently falls back
  to an ad hoc environment instead. Harmless for `install.py` itself
  (no runtime deps either way) but means the planned bootstrap
  invocation needed `uv run --project ~/dotfiles/install
  ~/dotfiles/install/install.py`, not a bare path - updated phase 4's
  Goals/Plan/Done-when accordingly. For phase 5, corrected the earlier
  draft's assumption that `home_dir`/`dotfiles_dir` needed to become
  parameters before tests were possible: phase 1's `link_config()` and
  `backup()` already take `home_dir`/`backup_dir` as explicit
  arguments, so no further testability refactor is needed for either
  Goal - only `run_install()` itself (out of scope) still reads
  `Path.home()` inline. Wrote out the concrete test-case list against
  the real function signatures instead. No code changed in this pass -
  planning only; all three phases remain unimplemented.
- 2026-07-02 : implemented phase 3, in the `bootstrap` repo (not this
  one). Moved the `uv` install one-liner (from `install_python.sh`)
  into `install_basics.sh`, right after `python3-pip` and before the
  `dotfiles` clone, followed by `export PATH="$HOME/.local/bin:$PATH"`
  per the plan's finding that the installer's rc-file sourcing doesn't
  reach the already-running script. Left the `python3
  ~/dotfiles/install.py` invocation line untouched - switching it to
  `uv run` is phase 4's change, since it depends on the `install/`
  move. `install_python.sh` left as-is (standalone reinstall path, per
  plan). Added `uv` to `bootstrap/README.md`'s `install_basics` bullet
  list. Verified with `bash -n install_basics.sh` (syntax only - not
  run for real, since it does system-wide `apt`/`sudo` work on a real
  box). Nothing committed in `bootstrap` - that repo's changes are
  uncommitted, left for the user to review/commit.
- 2026-07-02 : implemented phase 4. `git mv install.py
  install/install.py`; `dotfiles_dir` now
  `Path(__file__).resolve().parent.parent`, closing the old `# MAYBE`
  comment. Added `install/pyproject.toml` exactly as planned
  (`[tool.uv] package = false`, `requires-python = "==3.14.*"`, `dev`
  group with `pytest`/`ruff`) - `uv run install.py` and `uv run --group
  dev pytest`/`ruff check` all resolve and run cleanly from within
  `install/`. Also updated `setup_env()`'s cosmetic `recap` string
  (`python3 install.py` → `uv run install.py`) - not in the original
  plan text, but it's a display-only string that would otherwise lie
  about how to repeat the run; small enough to fold in here rather than
  opening a new phase for it. Updated `bootstrap/install_basics.sh`'s
  invocation line to `uv run --project ~/dotfiles/install
  ~/dotfiles/install/install.py`, and confirmed by running it directly
  from `/tmp` that `--project` makes the project resolve correctly
  regardless of cwd (without it, per phase 3/4 planning, `uv` silently
  ignores the project). Updated `README.md`'s install.py section (new
  path, both invocation forms) and removed `TODO.md`'s stale "Poetry /
  pyenv" line (with the now-empty `## Python` heading, since nothing
  else was under it). Verified via `--dry-run` against the real
  dotfiles tree - matches phase-1/2's already-linked output, no
  regressions; the new `install/` folder itself shows up as an inert
  "Topic: install" with no `.symlink`/`.bash` children, as expected.
  `uv`'s own `.venv/.gitignore` (written by `uv` itself, containing
  `*`) already keeps `install/.venv/` out of git with no changes needed
  to the repo's own `.gitignore`; `install/uv.lock` is new and
  untracked, meant to be committed alongside the rest. Tests (phase 5)
  intentionally not written yet - `pytest` currently collects 0 items,
  as expected. Nothing committed - left staged/unstaged for the user to
  review.
- 2026-07-02 : implemented phase 5. Added `install/tests/test_install.py`
  (17 tests) covering every bullet in the plan's Plan section:
  `link_config()` (flat/one-level/multi-level nesting, directory
  sources, the already-linked skip with an empty-backup-dir assertion,
  the divergence warning both firing on differing content and staying
  silent on identical content while still relinking either way, and
  `dry_run` making zero filesystem changes), `backup()` (file, dir,
  dangling symlink, no-op, `dry_run`), and `find_free_dir()`/
  `is_conf_dir()` as the low-cost additions the plan allowed. Needed
  one addition beyond the plan text: `[tool.pytest.ini_options]
  pythonpath = ["."]` in `pyproject.toml`, so `import install` resolves
  in `install/tests/` without a `src/` layout or `conftest.py` path
  hack. Confirmed the suite actually catches regressions, per the
  phase's Done-when: temporarily reverted the `__` → `/` replace in
  `link_config()`, reran - exactly the two nesting tests failed, the
  rest stayed green - then restored the file and reran clean (17
  passed). `uv run --group dev ruff check .` passes on the new test
  file too. Also added a repo-root `.gitignore` (was empty) with just
  `__pycache__/` - pytest/uv's own cache dirs (`.pytest_cache/`,
  `install/.venv/`) already self-exclude via a `.gitignore` written
  inside themselves, but `__pycache__/` doesn't get that treatment and
  showed up untracked after running pytest. Nothing committed - left
  for the user to review. This closes out all 5 phases of the plan.
- 2026-07-18 : added phases 6-7 (planned, not implemented) after the
  user flagged `~/bootstrap`'s dirty working tree. Investigated the
  untracked files: `exa-linux-x86_64-v0.10.1.zip` + `bin/`/
  `completions/`/`man/` are a duplicate of the manual exa install that
  also lives in `~/setup_bootstrap/` (the intended download dir) - run
  once from the wrong cwd; `bin/exa` is byte-identical to the installed
  `~/.local/bin/exa` v0.10.1. `t.sh` is a 2-line scratch duplicating
  `install_tools.sh`'s `mkdir/cd ~/setup_bootstrap`; `install_backup.sh`
  is a markdown note holding one rclone mount command. Also found that
  `install_tools.sh` now installs `eza` (exa's maintained fork) while
  `dotfiles/bash/aliases_exa.bash` still calls `exa` - a fresh box would
  get broken aliases; this box only works via the stale manual binary.
  Phase 6 deletes the leftovers and keeps the rclone note; phase 7
  installs eza via the real bootstrap path, renames the aliases to eza,
  and removes `~/.local/bin/exa`. The user resolved the open decisions
  in-file: `install_backup.sh` becomes a clean rclone install script
  with a `README.md` bullet; no `.gitignore` (future messes should be
  visible and fixed, not ignored); no `exa=eza` compat alias (`le`/`lt`
  are the muscle-memory entry points).
- 2026-07-18 : implemented phases 6 and 7. Phase 6: deleted the exa zip,
  `bin/`/`completions/`/`man/`, and `t.sh` from `~/bootstrap`; rewrote
  `install_backup.sh` as a clean rclone install script keeping the
  mount command as a comment; added the `install_backup` bullet to
  `README.md` and flipped `install_tools`'s `exa` bullet to `eza`.
  Phase 7: installed eza 0.23.5 from the gierens apt repo via
  sudo-handoff (Claude's shell has no TTY for the password; commands run
  by the user, verified from `~/handoff-logs/07a-07f`). `git mv`'d
  `bash/aliases_exa.bash` to `bash/aliases_eza.bash` with `exa` → `eza`
  throughout. Hit the predicted stale-environment snag in a new place:
  the aliases still didn't load because `~/.bash_aliases` is
  *generated* by `install.py` with per-file paths, and its `[ -f ... ]`
  guard silently skipped the renamed file - reran `install.py` to
  regenerate it, aliases then resolved. Verified `le`/`lt` exit 0 in a
  fresh interactive shell and the full tree flag set
  (`--long --git --all --tree --level --ignore-glob`) directly against
  eza. Removed `~/.local/bin/exa`; `which exa` finds nothing. Remaining
  `exa` mentions are only `colors_wsl.md`'s historical build notes, per
  plan. `~/bootstrap` git status now shows only the intended changes
  (`README.md` modified, clean `install_backup.sh` untracked); commits
  left to the user. `~/handoff-logs/` can be deleted.
