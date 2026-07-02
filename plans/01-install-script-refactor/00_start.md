# 00 - start: install.py topic-level folder-symlink nesting refactor

## Origin

Split out of [`../02-modernize-vim-setup/`](../02-modernize-vim-setup/)
(see that plan's `00_start.md` → "Additional finding: install.py's
folder-symlink asymmetry" and "Open questions - resolved" #5). While
scoping where a Neovim config would live, found that `install.py`'s
topic-level whole-folder symlink path doesn't support the same
`__`-nesting that the item-level path already has. Fixing `install.py`
isn't inherently a vim task, so it gets its own plan; the vim plan only
needs the *result* (a Neovim config folder can land at `~/.config/nvim`),
not to own the mechanism.

## Current state (as read from `install.py`)

- **Topic-level** (a whole `foo.symlink/` folder as one of the top-level
  dotfiles dirs, e.g. `vim.symlink`): target is computed as
  `home_dir / f".{topic_at_dot.stem}"` - always lands at `~/.<stem>`, no
  `__` nesting support. `install.py:203-218`.
- **Item-level** (a `.symlink` file *or folder* inside a topic dir, e.g.
  `claude/claude__rules__python.md.symlink`): target is computed as
  `home_dir / f".{config_at_dot.stem.replace('__', '/')}"` - already
  supports `__` → `/` nesting, and already handles directories
  (`target_is_directory=config_at_dot.is_dir()`), not just files.
  `install.py:230-282`.

So nesting already works for item-level entries, just not for a
whole-topic folder.

## Why this matters beyond vim

1. The Neovim config needs to land at `~/.config/nvim`, not `~/.nvim`
   ([`../02-modernize-vim-setup/`](../02-modernize-vim-setup/)) - this is
   the topic-level case, and it's what actually needs the fix below.
2. **Correction from the original write-up:** the Claude skills
   currently symlinked file-by-file (e.g.
   `claude__skills__tracked_development__SKILL.md.symlink`) do *not*
   need this fix at all. The item-level path (`install.py:230-282`)
   already handles directories, not just files
   (`target_is_directory=config_at_dot.is_dir()`) - it already has both
   nesting *and* directory support. Migrating a skill from a file
   symlink to a folder symlink is a pure data reorganization, doable
   today with zero `install.py` changes. See "Claude skill folder-symlink
   migration" below - it's independent of phase 1, not blocked by it.

## Decision

Extend the topic-level folder-symlink path to support `__` nesting,
matching the item-level path that already has it, rather than working
around the limitation per-consumer (e.g. `~/.nvim` + `NVIM_APPNAME` for
vim specifically). This was decided while scoping the vim plan, before
the split; full reasoning and the rejected alternative are recorded there:
[`../02-modernize-vim-setup/00_start.md`](../02-modernize-vim-setup/00_start.md#open-questions-resolved)
→ "Open questions - resolved" #5.

## Broadening the scope

Second and third planning passes, once the folder split above had
settled. Four threads, tied together below: why `install.py` no longer
needs to stay `uv`-free, whether it should move into its own subfolder
and what should live there, the Claude skill-symlink migration this
unblocks (or rather, was never blocked), and tests.

### uv as a guaranteed prerequisite, not dev-only

First pass concluded `install.py` had to stay `uv`-free at runtime,
because `bootstrap/install_basics.sh` clones `dotfiles` and runs
`python3 ~/dotfiles/install.py` with the system interpreter very early,
before `uv` (installed by a separate `bootstrap/install_python.sh`) was
guaranteed present.

User correction: `install_basics.sh` already installs things inline
immediately before it needs them (`sudo apt -y install python3-pip`
right before the `git clone` of `dotfiles`), and `install_python.sh` is
already down to a single line: `curl -LsSf
https://astral.sh/uv/install.sh | sh`. There's no reason that line can't
move earlier and run inline in `install_basics.sh`, the same way
`python3-pip` does. That removes the ordering constraint entirely.

**Decision:** reorder `bootstrap/install_basics.sh` to install `uv`
(the same one-liner `install_python.sh` already uses) immediately before
the `git clone` of `dotfiles`, then invoke the installer via `uv run`
instead of bare `python3`. `install_python.sh` stays as-is, for a
standalone reinstall/upgrade path - duplicating one line costs less than
restructuring script boundaries between the two `bootstrap` scripts.
This is a `bootstrap`-repo change (phase 3), a prerequisite for moving
`install.py` (phase 4).

### Single script vs `src/` package, in a dedicated `install/` subfolder

With `uv` guaranteed present, `install.py` can get a real `pyproject.toml`
without needing a dev-only-dependency-group workaround. Putting that
project in a `dotfiles/install/` subfolder (rather than at the repo
root) keeps `pyproject.toml` / `tests/` / `uv.lock` out of the
topic-folder root, so `dotfiles/` still reads as "a pile of
`topic.symlink/` dirs" at a glance instead of picking up Python-project
furniture next to `vim.symlink/` and `bash/`.

Assessed, within `install/`: a single script vs. a `src/`-layout package
(the convention this box uses for actual services, documented in
`copilot-instructions.md` - Config/Params/Paths/webapp layers, a
`get_..._params()` singleton, etc.).

**Decision: single script, `install/install.py`.** ~300 lines, no
reuse-as-a-library need, no public API surface, no config/params/webapp
layers to speak of - it is what the user called it, "a renamer." The
`install/` subfolder itself already delivers the organizational win
(`pyproject.toml`, `tests/`, `uv`-managed dependency groups, all out of
the topic-folder root); a `src/` layout on top of that buys nothing here.

Rejected: `src/dotfiles_install/` package with a `[project.scripts]`
entry point. Matches the box's "modern Python package" convention, but
that convention exists for services with real runtime configuration
surfaces. A single CLI script gains nothing from it and picks up a
build-backend + packaging-metadata tax for no reason - the
overengineering the user explicitly ruled out ("no bloat and no
overengineering... in the end it's a renamer").

One real fix falls out of the move, not just relocation: `run_install()`
currently hardcodes `dotfiles_dir = home_dir / "dotfiles"`, with a
`# MAYBE get the folder as parent of the current file` comment already
flagging it as a wart. Once the script lives at `install/install.py`,
deriving the dotfiles repo root as `Path(__file__).resolve().parent.parent`
is strictly more correct than assuming the clone landed at `~/dotfiles` -
this finally closes that old `MAYBE`.

### Claude skill folder-symlink migration - not actually blocked by phase 1

Per the corrected finding above ("Why this matters beyond vim" #2): the
item-level `.symlink` path already supports directories, so migrating
`claude/claude__skills__<name>__SKILL.md.symlink` (a file) to
`claude/claude__skills__<name>.symlink/SKILL.md` (a directory) needs
**zero `install.py` changes** - it's independent of phase 1, not gated
on it. Only two skills exist today (`caveman`, `tracked-development`),
both single-file, so the migration itself is small. Doing it now, while
this folder is already being restructured, sets the folder-per-skill
pattern before a multi-file skill (with a `references/` dir, scripts,
etc.) shows up and makes it urgent. Added as phase 2 - sequenced right
after the mechanical fix, ahead of the heavier `uv`/subfolder work, since
it has no dependency on any other phase here.

### Tests

Unchanged in spirit from the first pass: pytest coverage for the
target-path/nesting logic, `backup()`, the already-linked skip, and the
divergence guard. Now living in `install/tests/`, run via `uv run
pytest` from within `install/`, after the move (phase 4) rather than at
the old flat location, to avoid writing tests against a layout that's
about to change. Still dev-only in the ordinary sense (not part of what
a fresh machine needs to install), independent of the runtime-dependency
question above - the script stays stdlib-only at execution time either
way.

`dotfiles/TODO.md`'s stale "Python: Poetry / pyenv" line predates all of
this; it gets removed/updated once the `install/` `pyproject.toml` lands
(phase 4) - `uv` gives the same "proper Python tooling" outcome that old
TODO wanted, with far less setup than Poetry/pyenv would have needed.

## Scope for now

Five phases: the mechanical nesting fix (1, already planned), the Claude
skill folder-symlink migration (2, independent of 1), reordering
`bootstrap` to install `uv` before cloning `dotfiles` (3), moving
`install.py` into `install/` with a minimal `pyproject.toml` and the
`__file__`-relative `dotfiles_dir` fix (4), and pytest coverage in
`install/tests/` (5).
