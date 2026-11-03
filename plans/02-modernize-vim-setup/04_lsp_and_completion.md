---
status: draft
---

# Phase 4 - LSP, diagnostics & completion setup

## Overview

Per phase 1's decision, replace syntastic and the disabled YouCompleteMe with Neovim's native LSP client,
using the 0.12 API (`vim.lsp.config` + `vim.lsp.enable`) with nvim-lspconfig only as the source of server configs,
blink.cmp for completion, and the built-in `vim.snippet` engine for snippets.
Servers are system-installed, not managed from inside nvim.
Decisions behind the goals below: `00_start.md` → "LSP decisions - resolved 2026-11-03".

## Goals

1. Servers, enabled with `vim.lsp.enable` and installed outside nvim (the installs belong to phase 5):

   | Language | Server | Installed by |
   | --- | --- | --- |
   | Python | `ruff server` (lint, format) + basedpyright (types, definition, hover) | `uv tool` |
   | Lua | lua-language-server, aware of the Neovim runtime for the config itself | GitHub release in `~/bootstrap` |
   | Go | gopls | `go install` |
   | Dart | `dart language-server` | ships with the Flutter SDK |
   | Bash | bash-language-server (uses shellcheck) | npm in `~/bootstrap`, plus apt `shellcheck` |

   Python keeps parity with the old syntastic + flake8 setup: ruff's default rules already leave out E501/E266/E203 (W503 does not exist in ruff) and keep F841.
2. Formatting through conform.nvim (from phase 3) on `<leader>bb`: ruff format for Python, gofmt for Go, shfmt for Bash, LSP fallback for Lua and Dart.
3. Completion: blink.cmp with LSP, buffer, path and snippet sources.
   Watch for the reported 0.12 issue where blink returned no LSP completions; decide whether to allow blink's prebuilt Rust fuzzy-matcher download or use its Lua fallback.
4. Snippets: the built-in `vim.snippet` via blink, friendly-snippets for the stock set,
   and the 8 own snippets (`UltiSnips/{python,go}.snippets`) rewritten as vscode-format JSON in the config.
   Keys kept from UltiSnips: `<C-j>` expand / jump forward, `<C-p>` jump back.
5. Diagnostics UI via `vim.diagnostic.config`: signs in the number column (the old `signcolumn=number`), virtual text, a float on demand.
   `<leader>bs` fills the location list (replaces `:SyntasticCheck`), so the ported `[l`/`]l` wrap helper walks it.
6. Mappings: the 0.12 LSP defaults (`grn`, `gra`, `grr`, `gri`, `K`) plus `gd` for definition; `K` replaces the old YCM GetDoc mapping.
   The old vim-go mappings (`<leader>gb`/`gd`/`gi`/`gl`/`gr`) are not recreated. All mappings carry `desc` for which-key.

## Plan

- (Detail once phases 2-3 land.)

## Out of scope

- Re-litigating "native LSP vs coc.nvim" - phase 1 already decided that.
- Servers for yaml, json, ts/tsx, markdown and LaTeX (decision 20).
- ty as the Python type checker, until it reaches 1.0 (decision 22).

## Done when

- `:checkhealth vim.lsp` shows each of the five servers attaching in a file of its language.
- Opening a `.py` file shows ruff diagnostics equivalent to the old syntastic+flake8 setup,
  and blink.cmp shows completions from basedpyright and the snippet sources.
- `<C-j>` expands and walks one of the own snippets.
