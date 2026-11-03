---
status: draft
---

# Phase 6 - Documentation, migration guide and vim removal

## Overview

`vim.symlink/README.md` (or its renamed successor once phase 2 picks the
new topic name) is currently a personal vim tips/cheatsheet, not
documentation of the setup itself. See
[`00_start.md`](00_start.md#documentation). Do this last, once phases 1-5
have settled what the setup actually looks like.

## Goals

1. Keep the general vim tips/cheatsheet content, clearly separated from
   setup documentation (either a distinct file, or a clearly labeled
   section boundary).
2. Add a "what's installed and why" section: lazy.nvim, the plugin list's
   intent, the LSP/mason/nvim-cmp setup from phase 4, where `.vimrc.local`'s
   Neovim-era equivalent fits (if one exists after phase 2), how to add a
   plugin or a new language server.
3. Update `dotfiles/README.md` for the new `nvim/` topic (it still names `vim.symlink` as the folder-symlink example).
4. Migration guide for an existing machine, shipped in the same pull as the new config and the updated `~/bootstrap` script:
   remove the stale `~/.vim` link and `~/.myvim`, uninstall `vim-gtk3` and the YouCompleteMe build packages,
   run the bootstrap script and `install.py`, first launch of `nvim`.
   Where it lives (the setup README or a separate file) is decided here.
5. Delete `vim.symlink/` from the repo once phases 2-4 have ported everything that is kept.
6. Update the vim references outside `vim.symlink/`:
   `bash/bash_aliases.bash` `gd()` calls `gvimdiff`, `git/gitconfig.symlink` sets `merge.tool = gvimdiff`
   (both become `nvim -d` / `nvimdiff`), and decide whether an `nvim/aliases.bash` (e.g. `alias vim=nvim`) is wanted.
   `vim.symlink/completion.bash` (commented out, but sourced from `~/.bash_aliases`) goes with the folder; re-run `install.py` so the generated file drops it.

## Plan

- Do last, once phases 1-5 have settled what the setup actually looks like.

## Out of scope

- Rewriting the vim tips/cheatsheet content itself - just relocate/label it.

## Done when

- A new reader can tell, from the setup's README alone, what's installed,
  why, and how to extend it, without reading `init.lua` line by line.
- `dotfiles/README.md` accurately describes the symlink mechanism after
  [`../01-install-script-refactor/`](../01-install-script-refactor/)'s
  changes.
