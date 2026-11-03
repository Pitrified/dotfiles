---
status: in progress
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
   | ultisnips + vim-snippets | built-in `vim.snippet` through blink.cmp, plus friendly-snippets (set up in phase 4) | the 8 own snippets (`UltiSnips/{python,go}.snippets`) use only tabstops and are rewritten as vscode-format JSON |
   | vim-skeleton | own autocmd, no plugin | `BufNewFile *.py` reads `templates/skel.py` and fills `@BASENAME@` |
   | vim-autoformat | conform.nvim | `<leader>bb`; ruff format for Python, LSP fallback |
   | rainbow | rainbow-delimiters.nvim | `<leader>nr` toggle kept |
   | easymotion | flash.nvim | on `s`/`S` (flash defaults; replaces the built-in `s`, use `cl`) |
   | auto-pairs | nvim-autopairs | |
   | vim-polyglot | nvim-treesitter (`main` branch) | highlight, indent, folds; needs Neovim 0.12+ and tree-sitter-cli 0.26.1+ |
   | splitjoin.vim | treesj | mapped to the old `gS`/`gJ` |
   | vim-which-key | which-key.nvim | `<leader>` popup; mappings get `desc` fields so it has labels |

2. Not ported: syntastic (superseded by phase 4's LSP diagnostics) and vim-regedit (no longer used).
3. Not carried over (phase 2 ports only live content, so this is a check that none of it reached the new config): the four dead `Plug` remnants, `after/ftplugin/python/general.vim`'s
   `<leader>bb`/`<leader>bf` (Black) and `<leader>gd` (YcmCompleter)
   mappings, `after/ftplugin/go/general.vim`'s Go mappings (phase 4 brings LSP equivalents),
   `after/ftplugin/tex/mapping.vim`'s `IMAP(...)` calls,
   `.ycm_extra_conf.py`, and the `g:pythoh_highlight_all` line (a typo that never took effect).
   Kept: the python macros `@r`/`@t`/`@s`, `textwidth=88`, and the tex abbreviations.
4. Resolve the `<leader>bb` conflict (global `:Autoformat` vs. the deleted
   python-specific `:Black` override) - after deleting the Black mapping,
   `<leader>bb` runs conform.nvim everywhere, confirm
   no other filetype re-overrides it.
5. Revisit what treesitter changes: `UpdateTodoKeywords` (ported in phase 2) uses regex `syntax keyword`, which does not run when treesitter highlights a buffer;
   find a treesitter-era way to highlight NOTE/MAYBE/YES/NO/QUESTION.
6. Folding: the hand-written python `foldexpr` (`after/ftplugin/python/folding.vim`) and the `foldmethod=syntax` ftplugins are checked against treesitter folds; keep whichever behaves as expected, delete the other.

## Plan

Facts checked before writing (current READMEs and sources, 2026-11-03):

- nvim-treesitter `main`: `lazy = false` (no lazy-loading), `build = ":TSUpdate"`, `require("nvim-treesitter").install{...}`.
  Highlighting (`vim.treesitter.start()`) and folds (`vim.treesitter.foldexpr()`) are Neovim features enabled per filetype; its indent is marked experimental.
  When treesitter highlights a buffer, regex syntax is off, so `foldmethod=syntax` and `syntax keyword` (the phase 2 `UpdateTodoKeywords`) stop working there.
- nvim-surround 4.x needs Neovim 0.12 (`version = "^4.0.0"`).
- flash.nvim: the README spec maps `s` (jump), `S` (treesitter select), `r` (remote, operator mode), `R` (treesitter search), `<C-s>` (toggle in `/` search).
  Its `char` mode is on by default and changes `f`/`t`/`F`/`T`/`;`/`,` (highlights and jump labels).
- treesj: default keys are `<space>m/j/s`, which clash with our leader; `use_default_keymaps = false` and own `gS`/`gJ`.
- fzf-lua: uses `fd`, else `fdfind` (Ubuntu's name), else `rg`, else `find`; `live_grep` needs `rg`.
- vim-skeleton's `@BASENAME@` is the file name without extension.
- todo-comments.nvim (maintained, last commit 2025-11) highlights keywords in comments only (treesitter) with a configurable vim-regex pattern.
- `~/snippet` does not exist on this box (target of `<leader>fs`); `~/ephem`, `~/repos`, `~/dotfiles` do.

### Open questions for this phase

All five are settled (`00_start.md`, decisions 29-33).

1. ~~Tools on this box now~~ → yes, in step 1 (decision 29). System note: `~/repos/plans/2026-11-03_02_ripgrep_fd_ruff.md`.
2. ~~flash `char` mode~~ → on, flash's default (decision 33).
3. ~~TODO keywords under treesitter~~ → todo-comments.nvim (decision 30).
4. ~~Parsers to install~~ → the proposed list without dart (decision 31).
5. ~~`<leader>fs` on `~/snippet`~~ → dropped (decision 32).

### Steps

1. **Tools** per the system note: the user installs ripgrep and fd-find from apt (sudo-handoff, log `10a-apt-ripgrep-fd.log`), then `uv tool install ruff`; check the three versions.
2. **Treesitter** (`lua/plugins/treesitter.lua`): the spec above, installing the decision 31 parsers.
   A `FileType` autocmd runs `pcall(vim.treesitter.start)`; when it succeeds, it sets the window's `foldmethod=expr` and `foldexpr=v:lua.vim.treesitter.foldexpr()`.
   Indent stays on the runtime indent scripts (treesitter indent is experimental, and the Python one is weaker than the runtime's).
   Delete `after/ftplugin/{go,html,cpp,java}.lua` (syntax folds, superseded) and `g:markdown_folding` from `options.lua`.
   Python: keep `after/ftplugin/python/folding.vim` for the side-by-side test in step 9, then delete the loser.
3. **Editing plugins**, one spec file each in `lua/plugins/`:
   nvim-surround (`version = "^4.0.0"`, defaults);
   nvim-autopairs (`event = "InsertEnter"`, defaults; blink.cmp integration in phase 4);
   treesj (`gS` split, `gJ` join, default keymaps off);
   flash (the README keys; `char` mode on, the default);
   rainbow-delimiters (defaults, `<leader>nr` toggles it for the buffer);
   todo-comments (decision 30).
4. **fzf-lua** (`lua/plugins/fzf.lua`), mappings kept from the old setup:
   `<leader>ff` files, `<leader>fp` files in `..`, `<leader>fd`/`fe`/`fr` files in `~/dotfiles`/`~/ephem`/`~/repos` (`<leader>fs` dropped),
   `<leader>fa` live grep (was `:Ag`), `<leader>fb` buffers, `<leader>fl` lines of open buffers (was `:Lines`).
5. **conform.nvim** (`lua/plugins/conform.lua`): `<leader>bb` formats with `lsp_format = "fallback"`; `ruff_format` for Python, `gofmt` for Go.
   No format-on-save (the old setup had none). shfmt joins in phase 4 with the Bash tools.
6. **which-key.nvim** (`lua/plugins/which-key.lua`): default preset; group labels for `<leader>f` find, `n` toggles, `m` windows/sessions, `r` config, `c` folds, `b` format.
   The phase 2 mappings already carry `desc`.
7. **Own Lua replacing plugins:**
   - wrap-around `[q`/`]q`/`[l`/`]l` in `keymaps.lua` (port of `wrap_command.vim`): run `cprevious`/`cnext` (`l` variants), on E553 wrap to `clast`/`cfirst`, stay quiet on E42/E776 (empty or no list).
   - skeleton: `BufNewFile *.py` reads `templates/skel.py` from the config folder (copied from `vim.symlink/templates/`) and fills `@BASENAME@`.
   - the phase 2 `UpdateTodoKeywords` autocmd is removed (replaced by todo-comments in step 3).
8. **Check** that no dead names reached the config: the grep in "Done when".
9. **Verify:**
   - headless: `Lazy! sync` installs everything; `:checkhealth` for lazy, nvim-treesitter, fzf-lua, conform, which-key with no errors; clean startup on py/go/md/lua files.
   - headless: treesitter active in a `.py` buffer, fold expr set; `<leader>bb` formats a messy `.py` (ruff) and `.go` (gofmt); `ysiw)`, `gS`, autopairs on `(`, the wrap helper on a two-entry quickfix list, the skeleton on a new `.py`.
   - by hand, the user: flash labels on `s`/`S` and `char` mode on `f`/`t`, which-key popup, the fzf pickers, rainbow colors, TODO keyword highlight, and Python folds: treesitter vs the old `GetFold`, keep one.

## Out of scope

- LSP, completion (blink.cmp) and snippets - phase 4,
  even though they're also "plugins," they get their own phase given the
  amount of configuration involved.

## Done when

- lazy.nvim reports all kept plugins installed and loading with no errors, and `:checkhealth` shows no errors for them.
- `grep` for `Black\|YcmCompleter\|GoBuild\|GoDef\|GoInfo\|GoMetaLinter\|IMAP(\|Regedit`
  across the new config returns nothing.
- `<leader>bb` behaves identically in a `.py` file and in any other filetype.
