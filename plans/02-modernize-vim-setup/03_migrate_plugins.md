---
status: draft
---

# Phase 3 - Migrate plugins to lazy.nvim, delete dead mappings

## Overview

Port the working plugin list from `vimrc`'s vim-plug block into lazy.nvim
specs, and - per phase 1's decision - delete the four dead plugin remnants
(Black, YouCompleteMe, vim-go, vim-latex) and their live `after/ftplugin`
mappings entirely, rather than porting them forward. See
[`00_start.md`](00_start.md#dead-code-plugins-disabled-but-their-mappingsconfig-still-live)
for the exact mappings to remove.

## Goals

1. Every currently-live, kept plugin (tpope suite, fzf/fzf.vim, ultisnips +
   vim-snippets, vim-skeleton, vim-autoformat, rainbow, easymotion,
   vim-regedit, auto-pairs, vim-polyglot, splitjoin.vim, vim-which-key) has
   a lazy.nvim spec and works under Neovim. Confirm each still functions
   under Neovim (most are plain vimscript plugins with no vim-only
   assumptions, but verify rather than assume).
2. Syntastic is **not** ported - superseded by phase 4's LSP diagnostics.
3. Delete: the four dead `Plug` remnants, `after/ftplugin/python/general.vim`'s
   `<leader>bb`/`<leader>bf` (Black) and `<leader>gd` (YcmCompleter)
   mappings, `after/ftplugin/go/general.vim`'s Go mappings, and
   `after/ftplugin/tex/mapping.vim`'s `IMAP(...)` calls.
4. Resolve the `<leader>bb` conflict (global `:Autoformat` vs. the deleted
   python-specific `:Black` override) - after deleting the Black mapping,
   `<leader>bb` should consistently mean `:Autoformat` everywhere, confirm
   no other filetype re-overrides it.

## Plan

- (Detail once phase 2's scaffold exists to migrate plugins into.)

## Out of scope

- LSP/completion plugins (nvim-lspconfig, mason.nvim, nvim-cmp) - phase 4,
  even though they're also "plugins," they get their own phase given the
  amount of configuration involved.

## Done when

- lazy.nvim reports all kept plugins installed and loading with no errors.
- `grep` for `Black\|YcmCompleter\|GoBuild\|GoDef\|GoInfo\|GoMetaLinter\|IMAP(`
  across the new config returns nothing.
- `<leader>bb` behaves identically in a `.py` file and in any other filetype.
