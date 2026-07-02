---
status: done
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

Read the current `install_basics.sh` (`~/bootstrap/install_basics.sh`,
not in this repo) top to bottom and fetched the live installer
(`curl -LsSf https://astral.sh/uv/install.sh`) to confirm the PATH
mechanics rather than assuming them:

- Current script, relevant excerpt:
  ```bash
  sudo apt -y install python3-pip
  git clone https://github.com/Pitrified/dotfiles.git ~/dotfiles
  python3 ~/dotfiles/install.py
  mkdir ~/.local
  mkdir ~/.local/bin
  echo "export PATH=\$PATH:~/.local/bin" >> ~/.bash_aliases.local
  ```
  No `set -e` anywhere in the script, confirmed by reading it end to
  end - a failing `mkdir` (e.g. dir already exists) just prints an
  error to stderr and the script continues, so ordering changes here
  can't newly abort the run.
- The installer writes a `~/.local/bin/env` (POSIX) and `env.fish`
  script and appends a line sourcing it to shell rc files, to persist
  PATH for *future* shells - it cannot and does not modify the PATH of
  the already-running `install_basics.sh` process. Confirmed on this
  box: `uv` has been installed for a while, yet `~/.local/bin/env`
  doesn't exist here - whether that file even gets written depends on
  how the installer infers the install layout (XDG vars, forced
  install dir, etc.) at run time, so sourcing it isn't reliable to
  depend on in a portable bootstrap script. A direct `export` is
  simpler and always correct.
- New ordering:
  ```bash
  sudo apt -y install python3-pip

  # install uv, and make it usable for the rest of *this* script run
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"

  git clone https://github.com/Pitrified/dotfiles.git ~/dotfiles
  # (invocation line changes to `uv run ...` in phase 4)
  ```
- Leave the later `mkdir ~/.local && mkdir ~/.local/bin` +
  `.bash_aliases.local` PATH-export block untouched: it's a different
  concern (persisting PATH into dotfiles' own bash startup for the
  *next* login shell), not the current-script PATH problem being fixed
  here. `mkdir` on an already-existing dir just warns, as established
  above.
- Update `bootstrap/README.md`'s `install_basics` bullet list to add
  `uv`.

## Out of scope

- Anything inside `dotfiles/` - that's phase 4.
- Changing what `install_python.sh` does.

## Done when

- A shell run of `install_basics.sh` from scratch (or its `uv`-install +
  clone + invoke portion in isolation) successfully calls `uv run
  ~/dotfiles/install/install.py` (once phase 4 lands) in the same script
  execution, no manual `source`/shell restart required.
