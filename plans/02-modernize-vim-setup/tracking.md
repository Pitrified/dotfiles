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
- Full reasoning and rejected alternatives for each: `00_start.md` → "Open
  questions - resolved".

## Phases

| #  | Phase                                                | Plan                                                          | Status |
| -- | ----------------------------------------------------- | ---------------------------------------------------------------- | ------ |
| 1  | Resolve open questions & decisions                    | [`01_resolve_decisions.md`](01_resolve_decisions.md)               | done   |
| 2  | Scaffold the Neovim config (init.lua, lazy.nvim boot) | [`02_scaffold_neovim_config.md`](02_scaffold_neovim_config.md)     | draft  |
| 3  | Migrate plugins + delete dead mappings                | [`03_migrate_plugins.md`](03_migrate_plugins.md)                   | draft  |
| 4  | LSP, diagnostics & completion setup                   | [`04_lsp_and_completion.md`](04_lsp_and_completion.md)             | draft  |
| 5  | Modernize the install script for Neovim               | [`05_modernize_install_script.md`](05_modernize_install_script.md) | draft  |
| 6  | Documentation cleanup                                 | [`06_docs_cleanup.md`](06_docs_cleanup.md)                         | draft  |

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