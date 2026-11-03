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

## Scaffold decisions - resolved 2026-11-03

Settled with the user once [`../01-install-script-refactor/`](../01-install-script-refactor/) was done, before detailing phase 2.

6. **Folder layout?** → **`nvim/config__nvim.symlink/`** → `~/.config/nvim`, an item-level folder symlink inside an `nvim/` topic.
   Matches `git/config__git__ignore.symlink` and the `claude/claude__skills__*.symlink/` folders, and leaves room in the topic for an `aliases.bash` and a README.
   Rejected: a top-level `config__nvim.symlink/` like `vim.symlink` (works, but gives the topic no home for its other files).
7. **Where to test?** → **Install Neovim on this box now**, ahead of phase 5.
   First done with apt `neovim` 0.11.6 (system note `~/repos/plans/2026-11-03_00_install_neovim.md`);
   **superseded the same day** by Neovim 0.12.6 from the upstream tarball plus the `tree-sitter` CLI, both under `~/.local`, see decision 14.
   System note: `~/repos/plans/2026-11-03_01_neovim_0_12_tarball.md`.
8. **Fate of `vim.symlink/`?** → **Remove it; every machine migrates to Neovim.**
   One pull brings the new dotfiles config together with the updated `~/bootstrap` install script, plus a migration guide for an existing machine (stale `~/.vim` link, `~/.myvim`, old packages).
   `vim.symlink/` stays in the tree only while it is the source being ported (phases 2-4).
9. **Lua structure?** → **Neat and clean**: a short `init.lua` that loads `lua/config/` modules (options, keymaps, autocmds) and lazy.nvim with specs in `lua/plugins/`.
   Rejected: one large `init.lua`.
10. **Swap, undo and backup dirs?** → **Neovim defaults** under `stdpath('state')` (`~/.local/state/nvim`), not `~/.myvim/*`.
    This also drops the `mkdir` step from the install script.
11. **Machine-local override (`~/.vimrc.local`)?** → **Keep** an equivalent hook, sourced at the end of the config when the file exists.
    Exact file name decided in phase 2.
12. **`gvimrc`?** → **Drop**; Neovim is used in the terminal only, no GUI frontend.
13. **System tools for the new setup?** → install whatever is needed:
    Python tools (ruff) via `uv tool`; anything else nvim needs (node, ripgrep, fd, ...) goes into the `~/bootstrap` repo, only if the final config actually uses it.

## Plugin decisions - resolved 2026-11-03

Settled with the user while assessing phase 3.

14. **Neovim version?** → **0.12.6 from the upstream release tarball**, installed under `~/.local` with no sudo, plus the `tree-sitter` CLI from its GitHub release in `~/.local/bin`; the apt `neovim` is removed.
    Why: the modern replacement for vim-polyglot, nvim-treesitter's `main` branch, needs Neovim 0.12+ and tree-sitter-cli 0.26.1+.
    Ubuntu 26.04 apt has Neovim 0.11.6 and tree-sitter-cli 0.25.9, and the Neovim stable PPA stopped at 22.04.
    `~/bootstrap` installs the same way on every machine (phase 5).
    Rejected: staying on 0.11 with nvim-treesitter's frozen `master` branch (not a modern port).
15. **Plugin manager, now that 0.12 ships `vim.pack`?** → **lazy.nvim stays** (decision 3).
    `vim.pack` is still marked experimental and has no lazy loading or UI.
16. **Port style?** → **Port everything to the modern equivalent**: a built-in, a Lua plugin, or own Lua code.
    Legacy code is rewritten where needed. The full old-to-new table is in [`03_migrate_plugins.md`](03_migrate_plugins.md).
17. **vim-regedit?** → **Drop**, no longer used.
18. **easymotion replacement keys?** → **flash.nvim on `s`/`S`**, its defaults.
    This gives up the built-in `s` (substitute character); `cl` does the same.
    Rejected: the old easymotion prefix `<leader><leader>`.
19. **Key-hint popup?** → **which-key.nvim.**
    It detects every mapping with no trigger list, so buffer-local LSP mappings from phase 4 cannot break it.
    Its last release was v3.17.0 (2025-02) and its last commit 2025-10, with no open bug about 0.12.
    Rejected: mini.clue (mature, in mini.nvim since 2023 with stable releases, but its triggers are opt-in buffer-local mappings that later buffer mappings such as an LSP `on_attach` can shadow).
    mini.clue is the fallback if which-key stops working on a later Neovim.

## LSP decisions - resolved 2026-11-03

Settled with the user while assessing phase 4.
Context: Neovim 0.12 ships `vim.lsp.config`/`vim.lsp.enable`, default LSP mappings (`grn`, `gra`, `grr`, `gri`, `K`) and a native `autocomplete` option whose only source is LSP;
nvim-lspconfig (v2.12.0) is now mainly a set of server configs in `lsp/*.lua`.
The repos on this box are mostly Python, then md/yaml/json, some ts/js, dart, go and sh; no `.tex`.

20. **Languages with an LSP?** → **Python, Lua, Go, Dart and Bash.**
    Lua is for editing the nvim config itself; Dart's server comes with the Flutter SDK (`dart language-server`).
    Bash's `bash-language-server` needs node, so node joins the bootstrap installs.
    Rejected for now: yaml, json, ts/tsx, markdown and LaTeX (texlab).
21. **How servers are installed?** → **System installs**, no mason.nvim, consistent with decision 13:
    `uv tool` for the Python tools, `go install` for gopls, everything else in `~/bootstrap`.
    Rejected: mason.nvim (a second package manager living inside nvim, outside bootstrap).
22. **Python servers?** → **`ruff server`** (lint and format) plus **basedpyright** (types, go-to-definition, hover), both via `uv tool`.
    Ruff's default rule set already leaves out the old flake8 ignores (E501, E266, E203; W503 does not exist in ruff) and keeps F841, so no extra rule config is needed.
    Rejected: `ruff-lsp` (deprecated); ty (Astral, 0.0.95 and still beta; a later swap once it reaches 1.0).
23. **Completion and snippets?** → **blink.cmp** (v1.10.2) with LSP, buffer, path and snippet sources.
    Snippets run on Neovim's built-in `vim.snippet` through blink, with friendly-snippets replacing vim-snippets; the 8 own UltiSnips snippets are rewritten as vscode-format JSON.
    Rejected: native `autocomplete` (LSP is its only source); nvim-cmp (superseded); LuaSnip and UltiSnips (not needed for tabstop-only snippets).
