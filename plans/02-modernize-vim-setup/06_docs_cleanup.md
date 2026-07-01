---
status: draft
---

# Phase 6 - Documentation cleanup

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
3. Update `dotfiles/README.md` only if phase 2 or
   [`../01-install-script-refactor/`](../01-install-script-refactor/)
   changed the symlink mechanism or topic naming enough to need it (e.g.
   documenting the new `__`-nesting support for topic-level folder
   symlinks).

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
