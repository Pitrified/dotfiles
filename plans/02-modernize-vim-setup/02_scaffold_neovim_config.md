---
status: draft
---

# Phase 2 - Scaffold the Neovim config

## Overview

With `install.py` able to place a nested folder symlink (tracked
separately in
[`../01-install-script-refactor/`](../01-install-script-refactor/)), create
the new config topic - e.g. `config__nvim.symlink/` → `~/.config/nvim` - and
migrate the editor-level settings from `vimrc` into `init.lua`. This phase
is structure and settings only; plugin migration is phase 3, LSP/completion
is phase 4.

## Goals

1. New topic folder (name TBD, e.g. `config__nvim.symlink/`) with
   `init.lua` as the entry point.
2. Port the non-plugin-specific settings from `vimrc`'s "miscellaneous
   options" and "optics" sections (listed in
   [`00_start.md`](00_start.md#editor-choice-and-rendering)): swap/undo/
   backup dirs, wildmenu/wildignore, tabs/indent, scrolloff, listchars,
   statusline, clipboard, `termguicolors` (now unconditionally on, since
   Neovim in a modern terminal supports true color - resolves the old
   `has('gui_running')` gate).
3. Port the mapping sections (leader key, window/split/terminal navigation,
   toggles, session mgmt, `gcy`/`gcp`/`gcP` commentary helpers) and the
   custom functions (`ResCur`, `UpdateTodoKeywords`, the terminal-scroll
   `ExitNormalMode`/`EnterNormalMode` pair) into Lua, preserving behavior.
4. Decide `gvimrc`'s fate: GUI vim's `gvimrc` isn't read by Neovim or by
   Neovim GUIs (e.g. Neovide) the same way - port the relevant bits (font,
   chrome stripping) into `init.lua` guarded by `vim.g.neovide` (or drop
   entirely if no GUI frontend is in use) rather than carrying a dead file
   forward.
5. Colorscheme: port `colors/gruvbox-bootleg.vim` and the other custom
   colorschemes (antares, hotpot, spacecamp) - these are plain vimscript
   colorscheme files and load unchanged under Neovim, no rewrite needed.

## Plan

- (Detail once
  [`../01-install-script-refactor/`](../01-install-script-refactor/) lands
  and confirms the exact topic folder name/path.)

## Out of scope

- Plugin list migration to lazy.nvim (phase 3).
- LSP/completion (phase 4).
- `after/ftplugin/*` content beyond what's needed to confirm it still loads
  under the new folder (Neovim reads `after/ftplugin` the same way vim
  does - the folder should carry over largely unchanged, dead mappings
  aside, handled in phase 3).

## Done when

- Opening Neovim with the new config loads with no errors, no plugins yet,
  and all ported mappings/settings/colorscheme behave the same as the old
  vimrc did for the equivalent feature.
