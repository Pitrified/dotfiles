---
status: draft
---

# Phase 3 - Migrate plugins to lazy.nvim, delete dead mappings

## Overview

Replace every kept plugin from `vimrc`'s vim-plug block with its modern Neovim equivalent (a built-in, a Lua plugin, or a few lines of our own Lua),
and - per phase 1's decision - delete the four dead plugin remnants
(Black, YouCompleteMe, vim-go, vim-latex) and their live `after/ftplugin`
mappings entirely, rather than porting them forward. See
[`00_start.md`](00_start.md#dead-code-plugins-disabled-but-their-mappingsconfig-still-live)
for the exact mappings to remove.
Legacy code is rewritten where the modern replacement needs it; it is not kept just because it works.
Decisions behind the mapping: `00_start.md` → "Plugin decisions - resolved 2026-11-03".

## Goals

1. Each kept plugin is replaced as follows, with a lazy.nvim spec in `lua/plugins/` where a plugin remains:

   | Old | New | Notes |
   | --- | --- | --- |
   | vim-surround + vim-repeat | nvim-surround | same `ys`/`cs`/`ds` keys; dot-repeat built in, so vim-repeat goes |
   | vim-commentary | built-in `gc`/`gcc` | `gcy`/`gcp`/`gcP` rewritten on top of the built-in |
   | vim-unimpaired | built-in `[q` `]q` `[b` `]b` `[l` `]l` ... | the wrap-around `[l`/`]l`/`[q`/`]q` helper (`autoload/wrap_command.vim`, `plugin/wrap_command.vim`) ported to Lua |
   | fzf + fzf.vim | fzf-lua | reuses `~/.fzf`; the `<leader>f*` mappings kept; `:Ag` becomes `live_grep` on ripgrep |
   | ultisnips + vim-snippets | engine chosen in phase 4 with completion, plus friendly-snippets | the 8 own snippets (`UltiSnips/{python,go}.snippets`) use only tabstops and are rewritten in the engine's format |
   | vim-skeleton | own autocmd, no plugin | `BufNewFile *.py` reads `templates/skel.py` and fills `@BASENAME@` |
   | vim-autoformat | conform.nvim | `<leader>bb`; ruff format for Python, LSP fallback |
   | rainbow | rainbow-delimiters.nvim | `<leader>nr` toggle kept |
   | easymotion | flash.nvim | on `s`/`S` (flash defaults; replaces the built-in `s`, use `cl`) |
   | auto-pairs | nvim-autopairs | |
   | vim-polyglot | nvim-treesitter (`main` branch) | highlight, indent, folds; needs Neovim 0.12+ and tree-sitter-cli 0.26.1+ |
   | splitjoin.vim | treesj | mapped to the old `gS`/`gJ` |
   | vim-which-key | which-key.nvim | `<leader>` popup; mappings get `desc` fields so it has labels |

2. Not ported: syntastic (superseded by phase 4's LSP diagnostics) and vim-regedit (no longer used).
3. Delete: the four dead `Plug` remnants, `after/ftplugin/python/general.vim`'s
   `<leader>bb`/`<leader>bf` (Black) and `<leader>gd` (YcmCompleter)
   mappings, `after/ftplugin/go/general.vim`'s Go mappings (phase 4 brings LSP equivalents),
   `after/ftplugin/tex/mapping.vim`'s `IMAP(...)` calls,
   `.ycm_extra_conf.py`, and the `g:pythoh_highlight_all` line (a typo that never took effect).
   Kept: the python macros `@r`/`@t`/`@s`, `textwidth=88`, and the tex abbreviations.
4. Resolve the `<leader>bb` conflict (global `:Autoformat` vs. the deleted
   python-specific `:Black` override) - after deleting the Black mapping,
   `<leader>bb` runs conform.nvim everywhere, confirm
   no other filetype re-overrides it.
5. Folding: the hand-written python `foldexpr` (`after/ftplugin/python/folding.vim`) and the `foldmethod=syntax` ftplugins are checked against treesitter folds; keep whichever behaves as expected, delete the other.

## Plan

- (Detail once phase 2's scaffold exists to migrate plugins into.)

## Out of scope

- LSP/completion plugins and the snippet engine - phase 4,
  even though they're also "plugins," they get their own phase given the
  amount of configuration involved.

## Done when

- lazy.nvim reports all kept plugins installed and loading with no errors, and `:checkhealth` shows no errors for them.
- `grep` for `Black\|YcmCompleter\|GoBuild\|GoDef\|GoInfo\|GoMetaLinter\|IMAP(\|Regedit`
  across the new config returns nothing.
- `<leader>bb` behaves identically in a `.py` file and in any other filetype.
