---
status: draft
---

# Phase 5 - Modernize the install script for Neovim

## Overview

`bootstrap/install_vim.sh` needs both the decision-independent fixes noted
in the original assessment and an update for the Neovim move. See
[`00_start.md`](00_start.md#bootstrapinstall_vimsh).

## Goals

1. Install `neovim` instead of `vim-gtk3` (plus whatever `mason.nvim`
   expects to be present on the system for building language servers, e.g.
   a C compiler / Node.js, depending on phase 4's server choices).
2. Idempotent directory setup: `~/.myvim/{swap,undo,backup}` (or their
   Neovim-side equivalents, if paths changed as part of phase 2) created
   with `mkdir -p` / existence checks, so re-running the script is a no-op.
3. Non-interactive plugin bootstrap: lazy.nvim auto-installs itself and its
   plugins on first launch (`lazy.setup` handles this without a manual
   `PlugInstall` step), so the "needs to be manually closed" TODO can likely
   go away entirely rather than just being scripted better - confirm during
   this phase.
4. Drop the `build-essential`/`cmake`/`python3-dev` apt installs that only
   existed for YouCompleteMe (deleted in phase 3).
5. Rename the script (e.g. `install_neovim.sh`) if that matches the rest of
   the bootstrap repo's naming, or keep `install_vim.sh` if renaming churns
   references elsewhere - check `bootstrap/`'s other scripts for how they
   reference each other before deciding.

## Plan

- (Detail once phases 1-4 land and confirm what the script actually needs
  to install/configure.)

## Out of scope

- Anything inside `dotfiles/` - this phase only touches
  `bootstrap/install_vim.sh` (or its renamed successor).

## Done when

- Running the script twice in a row on a clean machine succeeds both times
  with no manual steps.
- No apt packages are installed for a plugin or feature that isn't enabled
  in the final config.
