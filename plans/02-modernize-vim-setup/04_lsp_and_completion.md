---
status: draft
---

# Phase 4 - LSP, diagnostics & completion setup

## Overview

Per phase 1's decision, replace syntastic and the disabled YouCompleteMe
with Neovim's native LSP client. The standard modern stack for this is
`nvim-lspconfig` (server configuration) + `mason.nvim` (installs/manages
the language servers themselves) + `nvim-cmp` with `cmp-nvim-lsp` (the
completion popup UI - native LSP alone gives diagnostics/go-to-definition
but not an autocomplete menu). This combination wasn't asked about
explicitly in phase 1 (only "native LSP vs coc.nvim" was); flagging it here
since it's an implementation detail of "native LSP," not a new fork - worth
a quick confirmation with the user when this phase starts, not a silent
assumption.

## Goals

1. `nvim-lspconfig` + `mason.nvim` installed and configured for at least the
   languages the old syntastic config targeted: Python (flake8 today - see
   the ignore list in
   [`00_start.md`](00_start.md#plugin-manager-and-plugin-list-vimsymlinkvimrc)),
   and whichever others are still in active use.
2. Decide the Python linter/formatter under LSP: `ruff-lsp` or `pylsp` are
   the common choices, either can carry over an equivalent to the current
   `--ignore=E501,E266,E203,W503` flake8 args.
3. Completion UI: `nvim-cmp` + `cmp-nvim-lsp`, and decide whether UltiSnips
   stays as the snippet engine (via `cmp-ultisnips`) or moves to
   `luasnip`/`cmp-luasnip` - UltiSnips still works fine under Neovim, so
   this is "keep unless there's a reason to switch," not a required change.
4. True color / diagnostics UI (signs, virtual text, floating windows) is
   configured, not left at vim-era defaults.

## Plan

- (Detail once phases 2-3 land; this phase's shape depends on what's still
  in the plugin list by the time it starts.)

## Out of scope

- Re-litigating "native LSP vs coc.nvim" - phase 1 already decided that.

## Done when

- Opening a `.py` file shows LSP diagnostics equivalent to the old
  syntastic+flake8 setup (same ignore list, or a documented reason it
  changed), and `nvim-cmp` shows completions from the LSP server.
