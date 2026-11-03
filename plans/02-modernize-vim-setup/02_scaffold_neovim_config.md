---
status: planned
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
6. Colorscheme: gruvbox.nvim with the bootleg file's one tweak (closed-fold background) as an override;
   the local colorschemes are not carried over (decision 24).
7. `vim.symlink/` is left untouched in this phase: it is the source being ported, and is removed in phase 6.

Test bed: Neovim 0.12.6 from the upstream tarball in `~/.local`, installed on this box ahead of phase 5
(system note `~/repos/plans/2026-11-03_01_neovim_0_12_tarball.md`).
The scaffold targets 0.12 APIs.

## Plan

Facts checked on this box before writing (Neovim 0.12.6, `nvim --clean --headless`):
many old `vimrc` options are now Neovim defaults; the default `backupdir` starts with `.` (so `set backup` alone would write backups next to the files);
`gruvbox-bootleg.vim` is morhetz's 2017 gruvbox with one change (closed-fold background `bg0` instead of `bg1`) and defines both gui and cterm colors, so it works with `termguicolors`.

### Decisions for this phase

Settled with the user 2026-11-03 (`00_start.md` decisions 24-27):

1. **Colorscheme:** ellisonleao/gruvbox.nvim, with an override setting `Folded`'s background to gruvbox's `bg0` to keep the one bootleg tweak.
   It is the first lazy.nvim spec, so lazy.nvim boots in this phase. antares, hotpot, spacecamp and `gruvbox-bootleg.vim` are not carried over.
2. **`<leader>rs`:** `:source %` (source the file being edited), since lazy.nvim does not support re-sourcing `init.lua`.
3. **Local override file:** `~/.nvim.local.lua`, Lua only.
4. **Branch:** executed on `master`.

### Steps

1. **Skeleton.** In `~/dotfiles/nvim/config__nvim.symlink/`:

   ```
   init.lua
   lua/config/options.lua
   lua/config/keymaps.lua
   lua/config/autocmds.lua
   lua/config/lazy.lua
   lua/plugins/colorscheme.lua
   after/ftplugin/*.lua
   ```

   `init.lua` only sets `mapleader` (before anything maps keys), then requires the `config.*` modules in order, then runs `~/.nvim.local.lua` if readable.
   `lua/config/lazy.lua` clones lazy.nvim into `stdpath('data')` on first run (the documented bootstrap), and `lazy-lock.json` is committed in the config folder.
2. **`options.lua`.** Carry over only what differs from the 0.12 defaults:
   - kept: `viewoptions=folds,options,cursor,unix,slash`, `virtualedit=onemore`, `gdefault`, `showmatch`, `matchtime=3`, `ignorecase`, `smartcase`,
     `wildmode=list:longest,full`, `wildignore+=*.pyc,*.class`, `wildignorecase`, `splitright`, `splitbelow`, `nowrap`, `scrolloff=8`, `listchars`,
     `number`, `relativenumber`, `numberwidth=3`, `signcolumn=number`, `cursorline`, `showmode`, the 4-space tab settings, `mouse=a`,
     `backup` with `backupdir` set to `stdpath('state')/backup//` only (drops the default leading `.`), `undofile`,
     `clipboard=unnamed,unnamedplus`, `termguicolors` (unconditional), `background=dark`, the statusline without the syntastic flag, the two netrw globals.
   - dropped because 0.12's default is the same or better: `encoding`, `history` (default 10000), `hidden`, `incsearch`, `hlsearch`, `wildmenu`, `nojoinspaces`, `backspace`, `laststatus`, `showcmd`, `undolevels`, `undoreload`, `directory`, `undodir`.
   - dropped as GUI- or Vim-only: `linespace`, `t_Co`, every `has(...)` guard.
3. **`keymaps.lua`.** Port the non-plugin mappings with `vim.keymap.set` and a `desc` on each (which-key reads them in phase 3):
   - as-is: `jk`/`jK`/`kj`, `j`/`k` ↔ `gj`/`gk`, visual `J`/`K`, `<leader>w`/`q`, the `<leader>n*` toggles (`nh`, `nc`, `nw`, `nl`, `ns`), `<leader>ya`, `<leader>cf`/`cc`,
     window split/navigate/move (`<leader>d`/`s`/`h`/`j`/`k`/`l`/`m*`), `<leader>es`, `gcy`/`gcp`/`gcP` on the built-in `gcc`.
   - changed: `<leader>re` opens `init.lua` from `stdpath('config')`; `<leader>rs` runs `:source %`; `<leader>ms`/`mr` use `stdpath('state')/sessions` (created on first use) instead of `~/.vim/sessions`;
     `<F5>` calls a Lua port of `strip_trailing_whitespace`; the terminal-mode `<leader><leader>*` mappings are rewritten for Neovim's terminal (`<C-\><C-n>` then the window command, since Vim's `<C-w>` passthrough does not exist there).
   - dropped as now default: `Y` (= `y$` since 0.6), visual `*`/`#` (search the selection since 0.10).
   - dropped as obsolete: `<leader>np` (`paste` toggle; Neovim handles bracketed paste) and the scroll-wheel `EnterNormalMode`/`ExitNormalMode` hack (Neovim's terminal scrolls its scrollback with the mouse; checked during verification).
   - left for phase 3: `[l`/`]l`/`[q`/`]q` (wrap helper), `<leader>nr`, `<leader>bb`, `<leader>f*`, the which-key `<leader>` popup; `<leader>ue` and `<leader>bs` for phase 4.
4. **`autocmds.lua`.** One augroup:
   - `FileType vim` → `foldmethod=marker`.
   - restore the last cursor position on `BufReadPost` (port of `ResCur`), skipping `gitcommit`/`gitrebase`, which replaces the separate COMMIT_EDITMSG autocmd.
   - `.html` always `html`, never `htmldjango`, via `vim.filetype.add` instead of the five-event autocmd.
   - `UpdateTodoKeywords` ported to Lua on the `Syntax` event (NOTE, MAYBE, YES, NO, QUESTION).
     It relies on regex syntax, which treesitter turns off, so phase 3 revisits it.
5. **Colorscheme:** `lua/plugins/colorscheme.lua` with gruvbox.nvim and the `Folded` override, loaded eagerly at high priority so it is set before anything draws.
6. **`after/ftplugin/` in Lua, live content only.** Dead mappings are never copied, so phase 3's delete step becomes a check:
   - `python.lua`: `textwidth=88`, the `@r`/`@t`/`@s` macros via `vim.fn.setreg`; the `GetFold` foldexpr carried as-is (phase 3 compares it with treesitter folds).
   - `go.lua`, `html.lua`, `cpp.lua`, `java.lua`: `foldmethod=syntax` (window-local; the old go file used a global `set`).
   - `markdown.lua`: `g:markdown_folding`.
   - `tex.lua`: `g:tex_flavor` and the abbreviations; no `IMAP` calls.
7. **Link.** `uv run install/install.py --dry-run`, read the plan it prints, then the real run.
   This creates `~/.config/nvim`, regenerates `~/.bash_aliases` and writes a backup folder, as every install run does.
8. **Verify:**
   - `nvim --headless +qa` exits 0 with nothing on stderr; same for opening a `.py`, `.go`, `.tex`, `.md` file.
   - headless `lua print(...)` spot checks of the kept options, including `backupdir`.
   - `:verbose nmap <leader>w` (and a sample of the others) shows the mapping coming from `keymaps.lua`.
   - by hand, the user: colors, statusline, terminal-mode mappings, mouse scroll in `:terminal`, clipboard over SSH (Neovim falls back to OSC 52 there; paste through OSC 52 depends on the terminal and zellij).

## Out of scope

- Plugin list migration to lazy.nvim (phase 3).
- LSP/completion (phase 4).
- Deleting `vim.symlink/` and the shell/git references to vim outside it (phase 6).

## Done when

- Opening Neovim with the new config loads with no errors, lazy.nvim with gruvbox.nvim as its only plugin,
  and all ported mappings/settings/colorscheme behave the same as the old
  vimrc did for the equivalent feature.
