# 00 - start: modernize the vim setup

## Origin

The vim configuration has accumulated cruft over the years across two repos:
`dotfiles/vim.symlink/` (the actual config, symlinked to `~/.vim`) and
`bootstrap/install_vim.sh` (the machine-setup script that installs vim and
its dependencies and triggers the first plugin install). The ask is to polish
and modernize both, starting with an assessment before touching any code.

## Current state (as read from the files)

### Plugin manager and plugin list (`vim.symlink/vimrc`)

- Plugin manager is `vim-plug`, self-bootstrapping via `curl` at the top of
  `vimrc` (auto-installs `plug.vim` and runs `PlugInstall --sync` on first run).
- Live plugins: tpope suite (surround, repeat, commentary, unimpaired), fzf +
  fzf.vim, ultisnips + vim-snippets, vim-skeleton, vim-autoformat,
  vim-syntastic/syntastic, rainbow, easymotion, vim-regedit, auto-pairs,
  vim-polyglot, splitjoin.vim, vim-which-key.
- syntastic is effectively unmaintained upstream (last meaningful activity
  ~2018); the ecosystem moved to ALE, coc.nvim, or native LSP years ago. It's
  still configured here with real flake8 args and a mode_map, so it's not
  dead weight, just aging infrastructure.
- There is no LSP client anywhere (no coc.nvim, no ALE, no native LSP client).
  The only "intelligence" plugins are UltiSnips (snippets, not completion) and
  a fully commented-out YouCompleteMe.

### Dead code: plugins disabled but their mappings/config still live

This is the single biggest correctness issue in the current setup - four
separate cases of a `Plug` line being commented out while something
downstream still calls the disabled plugin's commands:

- **Black**: `Plug 'psf/black', ...` is commented out, but
  `after/ftplugin/python/general.vim` still maps `<leader>bb` and `<leader>bf`
  to `:Black<CR>` - these mappings error/no-op today.
- **YouCompleteMe**: fully commented out (`Plug 'Valloric/YouCompleteMe'` and
  the YCM-Generator line), but the same python ftplugin file still maps
  `<leader>gd` to `:YcmCompleter GetDoc<CR>`.
- **vim-go**: `Plug 'fatih/vim-go', ...` is commented out, but
  `after/ftplugin/go/general.vim` still has live `GoBuild`/`GoDef`/`GoInfo`/
  `GoMetaLinter` mappings.
- **vim-latex**: `Plug 'vim-latex/vim-latex'` is commented out, but
  `after/ftplugin/tex/mapping.vim` still calls `IMAP(...)`, a function that
  plugin provides.

None of these fail loudly - they just silently do nothing (or error quietly)
the moment someone opens a python/go/tex file and hits the mapping. Cleaning
this up (either re-enable the plugin, or delete the dead mapping) is
low-risk, high-value, and doesn't require deciding anything about the bigger
LSP/completion question below.

### A real conflict, not just dead code

`vimrc` sets `nnoremap <leader>bb :Autoformat<CR>` globally (line 330), but
the python ftplugin overrides `<leader>bb` to `:Black<CR>` for python files
specifically. So `<leader>bb` means "run vim-autoformat" everywhere except
python files, where it means "run a plugin that isn't loaded." This is an
actual behavioral inconsistency across filetypes, not just leftover cruft.

### Editor choice and rendering

- Vanilla Vim (`vim-gtk3`, installed by bootstrap), not Neovim.
- `termguicolors` is only set when `has('gui_running')` - true color is never
  enabled in terminal vim, it falls back to `t_Co=256`. Most terminals people
  actually use today support true color, so this is leaving color fidelity on
  the table for no clear reason.
- Colorscheme in actual use is a local file, `colors/gruvbox-bootleg.vim`;
  four alternatives (kuroi, antares, gruvbox proper, solarized) are commented
  out as options. Custom colorschemes (antares, hotpot, spacecamp) plus
  `gruvbox-bootleg` are working and low-risk to keep as-is.

### `bootstrap/install_vim.sh`

- Installs `vim-gtk3`, `libcanberra-gtk-module`/`libcanberra-gtk3-module`,
  `python3-venv`, and `build-essential`/`cmake`/`python3-dev`. The last three
  exist only to compile YouCompleteMe, which is disabled - likely dead
  dependencies now.
- Creates `~/.myvim/{swap,undo,backup}` with plain `mkdir` (no `-p`, no
  existence check), so re-running the script on a machine that already has
  the setup fails outright instead of being a no-op.
- Ends with `vim +PlugInstall` and a `# TODO this needs to be manually
  closed` comment - it's not scriptable/automatable, unlike vimrc's own
  self-bootstrap which uses `PlugInstall --sync`.
- Has a commented-out line to compile YouCompleteMe via
  `install.py --clang-completer --go-completer` - dead code since the Plug
  line for YCM is already disabled.
- No Neovim path at all; the whole script assumes vanilla vim.

### Documentation

- `vim.symlink/README.md` is almost entirely a personal vim tips/cheatsheet
  (marks, motions, terminal mode mappings) rather than documentation of *this
  setup* (what's installed, why, how to add a plugin, how `.vimrc.local`
  fits in). Worth separating "how to use vim in general" notes from "how
  this config is put together" docs, so the latter can actually orient a
  future reader (including future-me).
- `dotfiles/README.md` documents the general symlink install system
  (`topic.symlink/` dirs, `__` nesting for files inside `~/.claude/`,
  `.local` override files). Relevant constraint for any vim rework: because
  `vim.symlink` is symlinked as a whole directory (not per-file via
  `install.py`), and `~/.vimrc.local` is sourced at the very end of
  `vimrc` for machine-specific overrides, both mechanisms need to keep
  working through any restructuring.

## Things that are fine and should not be touched without reason

- Custom colorschemes, `autoload/wrap_command.vim`,
  `autoload/strip_trailing_whitespace.vim`, `templates/skel.py`, UltiSnips
  snippets for go/python, the leader-key mapping scheme, window/split/terminal
  navigation mappings, the fold-related autocmds, `ResCur()` /
  `UpdateTodoKeywords()` helper functions. These work and aren't part of the
  "modernize" ask.

## Additional finding: install.py's folder-symlink asymmetry

Discovered while scoping where a Neovim config would live: `install.py`'s
topic-level whole-folder symlink path doesn't support the same `__`-nesting
that the item-level path already has, which blocks landing a Neovim config
at `~/.config/nvim`. Not a vim-specific problem (also blocks nested Claude
skill-folder symlinks), so the fix is tracked as its own plan:
[`../01-install-script-refactor/`](../01-install-script-refactor/) (full
write-up of the asymmetry in that plan's `00_start.md`). This plan only
needs the *result* once that lands.

## Open questions - resolved

1. **Vanilla Vim vs Neovim?** → **Neovim.** Native LSP client and Lua config
   support are worth the migration; the plugin ecosystem has largely moved
   there too. Rejected: staying on vim-gtk3 (smaller diff, but keeps
   building on an aging completion/LSP story with no real upgrade path).
2. **Completion/linting replacement for syntastic?** → **Native LSP**
   (`nvim-lspconfig`), which also replaces the disabled YouCompleteMe as the
   completion story. Rejected: ALE (fine, but a lateral move, not a real
   upgrade); coc.nvim (extension-based, Node.js dependency, less idiomatic
   Neovim than native LSP).
3. **Plugin manager?** → **lazy.nvim.** Current standard for Neovim
   (lazy-loading, lockfile, Lua-native). Rejected: keep vim-plug (would work,
   but Vim-vs-Neovim is already decided, so no reason to keep a
   cross-editor-compatible manager); packer.nvim (in maintenance mode,
   effectively superseded by lazy.nvim).
4. **Dead mappings (Black/YCM/vim-go/vim-latex): re-enable or delete?** →
   **Delete all four.** None are in active day-to-day use; remove the
   commented `Plug` remnants and their live `after/ftplugin` mappings
   entirely rather than re-enabling.
5. **Where should the Neovim config folder live, given install.py's
   folder-symlink limitation?** → **Extend and clean up `install.py`**: add
   `__` nesting support to the topic-level folder-symlink path (matching
   what item-level symlinks already do), so a topic folder can target a
   nested path like `~/.config/nvim`. This is a small, well-scoped
   consistency fix (bring the topic-level code path in line with the
   item-level one that already supports this), and it also unblocks
   symlinking whole Claude skill folders instead of file-by-file. Tracked
   as its own plan,
   [`../01-install-script-refactor/`](../01-install-script-refactor/),
   since it's a general symlink-mechanism fix, not vim-specific. Rejected:
   `~/.nvim` + `NVIM_APPNAME` (works without touching install.py, but leaves
   the asymmetry in place and doesn't help the Claude-skills case).
