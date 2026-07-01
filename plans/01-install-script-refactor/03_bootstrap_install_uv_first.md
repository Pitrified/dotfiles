---
status: draft
---

# Phase 3 - Reorder `bootstrap` to install `uv` before cloning dotfiles

## Overview

Move the `uv` install one-liner earlier in `bootstrap/install_basics.sh`
so it runs before `dotfiles` is cloned and `install.py` is invoked,
mirroring how the script already installs `python3-pip` inline
immediately before that same clone. This is the prerequisite that lets
phase 4 invoke the installer via `uv run` instead of bare `python3`. See
[`00_start.md`](00_start.md) → "uv as a guaranteed prerequisite, not
dev-only" for the reasoning and the rejected first-pass alternative
(keeping `install.py` `uv`-free).

This phase touches the `bootstrap` repo, not `dotfiles` - same
cross-repo shape as
[`../02-modernize-vim-setup/05_modernize_install_script.md`](../02-modernize-vim-setup/05_modernize_install_script.md).

## Goals

1. `bootstrap/install_basics.sh` installs `uv` (the same
   `curl -LsSf https://astral.sh/uv/install.sh | sh` line
   `bootstrap/install_python.sh` already uses) before the
   `git clone .../dotfiles` step.
2. `uv` is actually usable later in the *same* script run, not just in a
   fresh shell - the `uv` installer typically requires sourcing an env
   file or a `PATH` update to be picked up in the current shell session;
   confirm what `install_basics.sh` needs to do (e.g. source
   `"$HOME/.local/bin/env"` if the installed `uv` version writes one, or
   explicitly `export PATH="$HOME/.local/bin:$PATH"`) so the `uv run`
   call later in the same script (phase 4) works without a restart.
3. `bootstrap/install_python.sh` is left as-is (still just the one-liner)
   for a standalone reinstall/upgrade path - accept the one-line
   duplication rather than restructuring script boundaries between the
   two scripts.
4. `bootstrap/README.md`'s `install_basics` bullet list mentions `uv` is
   now installed as part of that step.

## Plan

- (Detail exact placement and the PATH/env-sourcing mechanics once this
  phase starts - depends on what the `uv` installer actually does on
  this box's Ubuntu version.)

## Out of scope

- Anything inside `dotfiles/` - that's phase 4.
- Changing what `install_python.sh` does.

## Done when

- A shell run of `install_basics.sh` from scratch (or its `uv`-install +
  clone + invoke portion in isolation) successfully calls `uv run
  ~/dotfiles/install/install.py` (once phase 4 lands) in the same script
  execution, no manual `source`/shell restart required.
