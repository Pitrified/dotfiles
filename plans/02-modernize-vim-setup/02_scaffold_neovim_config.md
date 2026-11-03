---
status: draft
---

# Phase 2 - Scaffold the Neovim config

## Overview

With `install.py` able to place a nested folder symlink (done in
[`../01-install-script-refactor/`](../01-install-script-refactor/)), create
the new `nvim/` topic with `nvim/config__nvim.symlink/` → `~/.config/nvim`,
and migrate the editor-level settings from `vimrc` into Lua.
This phase is structure and settings only; plugin migration is phase 3, LSP/completion is phase 4.
Decisions behind the goals below: `00_start.md` → "Scaffold decisions - resolved 2026-11-03".

## Goals

1. New `nvim/` topic with `config__nvim.symlink/` holding a short `init.lua`
   that loads `lua/config/` modules (options, keymaps, autocmds) and lazy.nvim with specs in `lua/plugins/` (empty until phase 3).
   Keep it neat and clean: one concern per module, no leftover commented-out vimscript.
2. Port the non-plugin-specific settings from `vimrc`'s "miscellaneous
   options" and "optics" sections: wildmenu/wildignore, tabs/indent, scrolloff, listchars,
   statusline, clipboard, `termguicolors` (unconditionally on, since
   Neovim in a modern terminal supports true color - resolves the old
   `has('gui_running')` gate).
   Swap, undo and backup use Neovim's defaults under `stdpath('state')`; the `~/.myvim/*` paths are not carried over (only `undofile` and the backup behavior themselves are).
3. Port the mapping sections (leader key, window/split/terminal navigation,
   toggles, session mgmt, `gcy`/`gcp`/`gcP` commentary helpers) and the
   custom functions (`ResCur`, `UpdateTodoKeywords`, the terminal-scroll
   `ExitNormalMode`/`EnterNormalMode` pair) into Lua, preserving behavior.
4. Keep a machine-local override hook equivalent to `~/.vimrc.local`, sourced last when the file exists; pick its file name here.
5. `gvimrc` is dropped, not ported: Neovim is used in the terminal only.
6. Colorscheme: carry over `colors/gruvbox-bootleg.vim` and the other custom
   colorschemes (antares, hotpot, spacecamp) - these are plain vimscript
   colorscheme files and load unchanged under Neovim, no rewrite needed.
7. `vim.symlink/` is left untouched in this phase: it is the source being ported, and is removed in phase 6.

Test bed: Neovim 0.12.6 from the upstream tarball in `~/.local`, installed on this box ahead of phase 5
(system note `~/repos/plans/2026-11-03_01_neovim_0_12_tarball.md`).
The scaffold targets 0.12 APIs.

## Plan

- (To detail next, once phases 3-6 have been assessed against Neovim 0.11.)

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
