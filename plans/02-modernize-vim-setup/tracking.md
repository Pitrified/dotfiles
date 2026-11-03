# modernize vim setup - tracking

Migrate the vim configuration in `dotfiles/vim.symlink/` to Neovim, and
update the install flow currently in `bootstrap/install_vim.sh` to match.
Analysis, inventory, and the decisions behind this scope are in
[`00_start.md`](00_start.md).

## Key decisions

- **Editor:** move from vanilla Vim to Neovim.
- **Plugin manager:** lazy.nvim.
- **Completion/diagnostics:** native LSP (`nvim-lspconfig`), replacing both
  syntastic and the already-disabled YouCompleteMe.
- **Dead plugin remnants** (Black, YouCompleteMe, vim-go, vim-latex): delete
  outright, don't re-enable.
- **`install.py`:** needs the topic-level folder-symlink path extended to
  support `__` nesting (matching the item-level path that already has it),
  so the new Neovim config can land at `~/.config/nvim` instead of
  `~/.nvim`. Not vim-specific, so it's tracked as its own plan:
  [`../01-install-script-refactor/`](../01-install-script-refactor/). This
  plan only needs the result.
- **Config location:** `nvim/config__nvim.symlink/` → `~/.config/nvim`, using the install.py nesting from plan 01 (done).
- **All machines move to Neovim:** `vim.symlink/` is removed once ported; the pull ships the new config, the updated `~/bootstrap` script and a migration guide together.
- **Config shape:** short `init.lua` plus `lua/config/` and `lua/plugins/` modules; Neovim default state dirs; a machine-local override hook kept; `gvimrc` dropped (terminal only).
- **Tools:** ruff via `uv tool`; other system tools in `~/bootstrap`, only if the config needs them.
- **Neovim 0.12.6** from the upstream tarball plus the `tree-sitter` CLI, under `~/.local` (apt is too old for nvim-treesitter `main`); lazy.nvim kept over 0.12's experimental `vim.pack`.
- **LSP:** native 0.12 `vim.lsp.config`/`enable` for Python (ruff server + basedpyright), Lua, Go, Dart, Bash; servers system-installed, no mason; blink.cmp with built-in `vim.snippet`.
- **Plugins:** every kept plugin ported to its modern equivalent (table in `03_migrate_plugins.md`); vim-regedit dropped; flash.nvim on `s`/`S`; which-key.nvim over mini.clue.
- Full reasoning and rejected alternatives for each: `00_start.md` → "Open
  questions - resolved", "Scaffold decisions", "Plugin decisions", "LSP decisions" and "Phase 2 decisions" (all resolved 2026-11-03).

## Phases

| #  | Phase                                                | Plan                                                          | Status |
| -- | ----------------------------------------------------- | ---------------------------------------------------------------- | ------ |
| 1  | Resolve open questions & decisions                    | [`01_resolve_decisions.md`](01_resolve_decisions.md)               | done   |
| 2  | Scaffold the Neovim config (init.lua, lazy.nvim boot) | [`02_scaffold_neovim_config.md`](02_scaffold_neovim_config.md)     | done   |
| 3  | Migrate plugins + delete dead mappings                | [`03_migrate_plugins.md`](03_migrate_plugins.md)                   | in progress |
| 4  | LSP, diagnostics & completion setup                   | [`04_lsp_and_completion.md`](04_lsp_and_completion.md)             | in progress |
| 5  | Modernize the install script for Neovim               | [`05_modernize_install_script.md`](05_modernize_install_script.md) | draft  |
| 6  | Docs, migration guide, remove `vim.symlink`           | [`06_docs_cleanup.md`](06_docs_cleanup.md)                         | draft  |

Status values: draft / planned / in progress / done / superseded / discarded.

`install.py`'s nested-folder-symlink fix, which phase 2 depends on, is
tracked separately in
[`../01-install-script-refactor/`](../01-install-script-refactor/) (split
out on 2026-07-02, see Log).

## Log

- 2026-07-02 : read `bootstrap/install_vim.sh` and the full
  `dotfiles/vim.symlink/` tree (vimrc, gvimrc, after/ftplugin/*, READMEs,
  install.py's symlink docs); wrote the initial assessment in `00_start.md`
  and bootstrapped this tracking folder. No code changed yet.
- 2026-07-02 : phase 1 - walked through the four open questions with the
  user: move to Neovim, native LSP (nvim-lspconfig) over ALE/coc.nvim,
  lazy.nvim as plugin manager, delete all four dead plugin remnants
  (Black/YCM/vim-go/vim-latex) rather than re-enabling. While scoping where
  the Neovim config would live, found that `install.py`'s topic-level
  folder-symlink path lacks the `__`-nesting support the item-level path
  already has; user chose to extend/clean up `install.py` as a preliminary
  step (also unblocks nested Claude-skill-folder symlinks). Rewrote the
  phase breakdown (now 7 phases) to reflect the Neovim migration scope, up
  from the original "small in-place cleanup" framing. Phase 1 done; phase 2
  (install.py) planned next.
- 2026-07-02 : split the `install.py` nesting fix out into its own plan,
  [`../01-install-script-refactor/`](../01-install-script-refactor/), since
  it's a general symlink-mechanism fix rather than a vim-specific task.
  This folder renamed from `01-modernize-vim-setup` to
  `02-modernize-vim-setup` to make room for the new plan at `01`; the old
  phase 2 file was removed here and phases 3-7 renumbered to 2-6. No scope
  change beyond the split - the install.py plan isn't being expanded yet,
  that's a later planning pass.
- 2026-11-03 : plan 01 is done, so phase 2 is unblocked.
  Checked the box: no vim or nvim installed (`~/.vim` still links to `vim.symlink`), apt offers neovim 0.11.6, no node/ruff/ripgrep/fd.
  Settled the scaffold questions with the user (decisions 6-13 in `00_start.md`) and folded them into phases 2, 5 and 6.
  Neovim install on this box handed to the user, system note `~/repos/plans/2026-11-03_00_install_neovim.md`.
  Phases 3-6 still to be assessed against Neovim 0.11 before detailing.
- 2026-11-03 : apt `neovim` 0.11.6 installed and verified (logs `~/handoff-logs/08a`, `08b`).
  Assessing phase 3 found that nvim-treesitter's `main` branch needs Neovim 0.12+ and tree-sitter-cli 0.26.1+, newer than apt has.
  User chose Neovim 0.12.6 from the tarball plus the tree-sitter CLI under `~/.local` (decision 14, supersedes the apt install), and settled the plugin mapping (decisions 15-19).
  Rewrote `03_migrate_plugins.md` goals with the old-to-new table; updated phases 2 and 5 for the 0.12 install.
  System note for the switch: `~/repos/plans/2026-11-03_01_neovim_0_12_tarball.md`, not yet executed.
  Phase 4 still to be assessed.
- 2026-11-03 : executed `~/repos/plans/2026-11-03_01_neovim_0_12_tarball.md`.
  Both downloads matched their release sha256 digests; Neovim 0.12.6 in `~/.local/opt/nvim-0.12.6`, linked from `~/.local/bin/nvim`; `tree-sitter` 0.27.1 in `~/.local/bin`.
  The user removed the apt `neovim`/`neovim-runtime` (log `~/handoff-logs/09a-apt-remove-neovim.log`); `nvim` now resolves only to `~/.local/bin/nvim`, v0.12.6.
- 2026-11-03 : assessed phase 4 against Neovim 0.12 (native LSP API and default mappings, nvim-lspconfig as configs only, `ruff-lsp` deprecated, ruff defaults cover the old flake8 ignores).
  User settled decisions 20-23: LSP for Python, Lua, Go, Dart and Bash (node joins bootstrap for bash-language-server), system installs over mason, basedpyright over ty, blink.cmp over native completion.
  Rewrote `04_lsp_and_completion.md` goals; added the server installs to phase 5; phase 3's snippet row now points at blink + `vim.snippet`.
  All six phases are now assessed; next is detailing phase 2's Plan section.
- 2026-11-03 : drafted phase 2's Plan section after checking 0.12 option defaults headless (many old options are now defaults; default `backupdir` starts with `.`) and the colorscheme (`gruvbox-bootleg.vim` is 2017 gruvbox with one fold-background tweak).
  Four open questions in the plan: colorscheme (gruvbox.nvim recommended), `<leader>rs` under lazy.nvim, local override file name, branch.
  Phase 3: dead-mapping delete became a check, added the treesitter revisit of `UpdateTodoKeywords`. Phase 6: added the `gvimdiff` references in bash and git config.
- 2026-11-03 : user settled phase 2's open questions (decisions 24-27): gruvbox.nvim with the `Folded` override, the other colorschemes dropped; `<leader>rs` is `:source %`; `~/.nvim.local.lua`; execute on `master`.
  Phase 2 is now `planned`.
- 2026-11-03 : executed phase 2 steps 1-8 on `master`.
  New `nvim/config__nvim.symlink/`: `init.lua`, `lua/config/{options,keymaps,autocmds,lazy}.lua`, `lua/plugins/colorscheme.lua`, `after/ftplugin/{python,tex,go,html,cpp,java}.lua`, `after/ftplugin/python/folding.vim` (carried as-is), `lazy-lock.json`.
  `install.py` dry run then real run linked `~/.config/nvim` (backup folder `~/.rcback03`); `Lazy! sync` installed lazy.nvim and gruvbox.nvim.
  Headless checks pass: clean startup with no stderr for none/py/go/tex/md/html files, option values, filetypes and fold methods, `Folded` bg `#282828`, mappings and descs, `@s` macro, `<F5>`, `gcy`, `pythonTodo` on NOTE, backups in the state dir, cursor restore, `:checkhealth lazy` with no errors or warnings.
  Changes from the plan: `markdown_folding`/`tex_flavor` set in `options.lua` (load-order fix), tex abbreviations buffer-local, macros set charwise (setreg guessed linewise for `@s`), lazy's luarocks support disabled (no plugin needs it).
  Headless tests in `/tmp` showed no backup and no restored cursor: Neovim's defaults `backupskip=/tmp/*` and `shada` `r/tmp/`, working as intended; rechecked outside `/tmp`.
  Left for the user by hand: colors, statusline, terminal-mode mappings, mouse scroll in `:terminal`, clipboard over SSH. Phase 2 stays `in progress` until then.
- 2026-11-03 : manual check by the user: `<Space>` in `:terminal` waited for the `<leader><leader>*` terminal mappings.
  Moved them to a `<C-w>` prefix (decision 28); headless check: no terminal mapping starts with `<Space>`, `<C-w>h` from a terminal leaves terminal mode and moves to the left window.
- 2026-11-03 : added terminal-mode `jk` → `<C-\><C-n>` at the user's request; checked with real input events: mode goes from `t` to `nt`.
- 2026-11-03 : manual checks by the user, in a local terminal on this box: colors fine (markdown only gets the plain regex syntax until treesitter in phase 3), statusline shows path, flags, `:b<n>`, filetype and position, mouse scroll works in `:terminal` (the old scroll hack is not needed), `yy` reaches the system clipboard through `xclip` (Wayland session, via XWayland).
  Not tested: pasting from another app into Neovim, and the clipboard over SSH (OSC 52), which matters only when Neovim runs remotely.
  Phase 2 done; phase 3 next.
- 2026-11-03 : drafted phase 3's Plan section from the current plugin READMEs and sources (nvim-treesitter `main` setup, flash keys and `char` mode, treesj default keys clashing with leader, fzf-lua's `fdfind` detection, todo-comments).
  Five open questions in the plan: tools now (ripgrep, fd-find, ruff), flash `char` mode, TODO keywords under treesitter, parser list, `<leader>fs` on a folder missing here.

- 2026-11-03 : user settled phase 3 questions 1, 3, 4, 5 (decisions 29-32): tools now, todo-comments.nvim, parser list without dart, `<leader>fs` dropped.
  Wrote the system note `~/repos/plans/2026-11-03_02_ripgrep_fd_ruff.md`. Flash `char` mode still open.
- 2026-11-03 : user settled the last phase 3 question (decision 33): flash `char` mode on. Phase 3 is now `planned`.
- 2026-11-03 : executing phase 3 on `master`.
  ruff 0.17.3 installed with `uv tool`; the apt ripgrep and fd-find install is handed to the user (log `10a-apt-ripgrep-fd.log`), not yet run.
  New specs in `lua/plugins/`: treesitter, surround, autopairs, treesj, flash, rainbow, todo-comments, conform, which-key, fzf; `templates/skel.py`; wrap helper in `keymaps.lua`; skeleton autocmd in `autocmds.lua`, replacing `UpdateTodoKeywords`; `g:markdown_folding` removed.
  Changes from the plan: only `after/ftplugin/{go,html}.lua` deleted; cpp and java have no parser, so they keep regex syntax and their syntax folds.
  todo-comments pattern is `.{-}<(KEYWORDS)>` (non-greedy, very magic): the greedy `.*` picked the last keyword on a line; it highlights one keyword per line and carries it onto following comment lines (default `multiline`).
  Headless checks pass: 22 parsers installed; treesitter highlight and fold expr in py/go/md/lua, cpp on syntax folds; checkhealth with no errors (flash, surround, todo-comments ship none; optional icon and image-preview warnings); conform formats py (ruff) and go (gofmt); `ysiw)`/`ds)`, `gS`/`gJ`, autopairs, `]q`/`[q` wrap and quiet on an empty list, skeleton fills `@BASENAME@`, rainbow toggle, dead-name grep empty, clean startup.
  Python folds: treesitter's foldexpr wins over `folding.vim` (the autocmd runs after the ftplugin); `GetFold` stays defined for the comparison.
- 2026-11-03 : the user installed ripgrep 15.1.0 and fd-find 10.3.0 (log `~/handoff-logs/10a-apt-ripgrep-fd.log`); `/usr/bin/rg`, `/usr/bin/fdfind`, `~/.local/bin/ruff` resolve; fzf-lua's checkhealth finds `rg` and `fdfind`.
  Phase 3 waits on the user's manual checks and the python fold choice.
- 2026-11-03 : the user cannot run phase 3's manual checks for now and asked to go on; phase 3 stays `in progress` until they are done.
  Drafted phase 4's Plan section from the nvim-lspconfig configs, the blink.cmp docs and its v1.10.2 source (the prebuilt matcher is checked against the release's `.sha256`), lazydev, and 0.12's headless diagnostic and LSP-mapping defaults.
  The "0.12 blink shows no LSP completions" report turned out to be a `vim.pack` setup mistake, so no workaround is planned.
  Six open questions in the plan: tools now, basedpyright strictness, the `<C-j>`/`<C-p>` snippet keys against blink's `<C-p>`, the own snippets, diagnostics on screen, blink's fuzzy matcher.
- 2026-11-03 : user settled phase 4 questions 1, 2, 3, 5, 6 (decisions 34-36, 38, 39): tools now, basedpyright `standard`, the `<C-j>`/`<C-p>` keys, diagnostics on screen, the Rust matcher.
  Question 4 (decision 37) waits on the user's review of the 8 own snippets.
  Wrote the system note `~/repos/plans/2026-11-03_03_lsp_servers.md` and ran its unprivileged steps 1-4: basedpyright 1.40.2 (it brings its own node through `nodejs-wheel-binaries` 24.19.0), gopls v0.24.0 in `~/go/bin`, lua-language-server 3.19.2 (tarball sha256 matched) in `~/.local/opt`, working through the `~/.local/bin` symlink without a wrapper.
  The apt `nodejs npm shfmt` install is handed to the user (log `11a-apt-node-shfmt.log`); bash-language-server follows it.
  For the snippet review: `~/repos` has 232 Python files on `from loguru import logger`, 2 on `import logging`, none with the snippets' `logging.getLogger(f"c.`, `fmt_cn`, `Observable` or `ty.Dict`/`ty.List`.
- 2026-11-03 : the user installed nodejs 22.22.1, npm 9.2.0 and shfmt 3.12.0 (log `~/handoff-logs/11a-apt-node-shfmt.log`, no `E:` lines); bash-language-server 5.8.1 installed with `npm --prefix ~/.local`, no `~/.npmrc` written.
  All tools of the system note resolve and print their versions.
  User dropped all 8 own snippets after the review (decision 37); step 5 (snippet JSON) removed from the plan.
  Phase 4 is now `planned`.
- 2026-11-03 : executing phase 4 on `master`.
  New `lua/plugins/lsp.lua` (nvim-lspconfig, configs only; lazydev), `lua/plugins/blink.lua` (blink.cmp v1.10.2, friendly-snippets), `lua/config/diagnostics.lua`; shfmt in `conform.lua`; `gr` label in which-key; statusline count.
  blink's prebuilt matcher matches the release asset's GitHub digest; my first headless run quit mid-download, which made the next start download again; a completed download stays put.
  Changes from the plan:
  the statusline count uses 0.12's `vim.diagnostic.status()` (`E:1 W:1`, redrawn on `DiagnosticChanged`) instead of an own helper;
  blink's command-line completion is off, so `:` keeps the wildmenu setup from phase 2;
  LSP Keyword items get `score_offset - 4`: blink ranks snippets 3 lower, so basedpyright's `for`/`try` keywords beat the friendly-snippets of the same name and `<C-j>` accepted the bare word.
  Headless checks pass: all six servers attach (ruff + basedpyright, gopls, dartls, bashls, lua_ls); ruff F841 and no E501, basedpyright `standard` reports the type error; ruff hover off; `gd`; `<leader>bs` fills the location list and `]l` wraps; shfmt via `<leader>bb`; lua_ls resolves `vim.diagnostic` to the runtime with no diagnostics in the config; `os.pa` lists basedpyright items; `for` + `<C-j>` expands, `<C-j>`/`<C-p>` walk the placeholders; checkhealth: no errors (lazydev ships no health check; notes: gopls's `gotmpl` filetype is unknown to Neovim, ruff UTF-8 vs basedpyright UTF-16 position encodings); clean startup on none/py/go/dart/sh/lua/md.
  Found: with an expr fold (treesitter or the old `GetFold`) and `foldlevel=0`, the inserted snippet lands in a closed fold, the placeholder selection covers the whole fold and typing replaces the whole snippet; correct with `foldlevel=99` or `nofoldenable`. Fix waits on the user.
  Test artifacts: a swap file and blink's frecency data from my own runs, both removed; later runs used a scratch `XDG_STATE_HOME`.
- 2026-11-03 : user chose to turn folds off during a snippet. blink's `snippets.expand` now sets `nofoldenable` in the window and restores it on the next settled normal mode (scheduled check: `vim.snippet` passes through normal mode on its way to select mode).
  Headless at `foldlevel=0`: `for` + `<C-j>`, then `<C-j>`/`<C-p>` walk the placeholders to `for x in things:` / `print(x)`; folds are back on after `<Esc>`.
  Noted, unchanged: after `<Esc>` the new block shows as a closed fold, the same as a block typed by hand at `foldlevel=0`.
  Phase 4 waits on the user's manual checks.
