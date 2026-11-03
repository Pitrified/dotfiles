---
status: in progress
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
4. Snippets: the built-in `vim.snippet` via blink, friendly-snippets for the stock set.
   The 8 own snippets (`UltiSnips/{python,go}.snippets`) are not ported (decision 37): their code patterns are no longer used.
   Keys kept from UltiSnips: `<C-j>` expand / jump forward, `<C-p>` jump back.
5. Diagnostics UI via `vim.diagnostic.config`: signs in the number column (the old `signcolumn=number`), virtual text, a float on demand.
   `<leader>bs` fills the location list (replaces `:SyntasticCheck`), so the ported `[l`/`]l` wrap helper walks it.
6. Mappings: the 0.12 LSP defaults (`grn`, `gra`, `grr`, `gri`, `K`) plus `gd` for definition; `K` replaces the old YCM GetDoc mapping.
   The old vim-go mappings (`<leader>gb`/`gd`/`gi`/`gl`/`gr`) are not recreated. All mappings carry `desc` for which-key.

## Plan

Facts checked before writing (docs, sources and this box, 2026-11-03):

- On this box: go 1.27.3 (`GOBIN=~/go/bin`, on PATH), Dart 3.13.5 in `~/flutter/bin`, shellcheck in `/usr/bin`, ruff 0.17.3.
  Missing: basedpyright, gopls, lua-language-server, node/npm, bash-language-server, shfmt.
  apt candidates: nodejs 22.22.1, npm 9.2.0, shfmt 3.12.0; lua-language-server is not in apt (latest GitHub release 3.19.2).
- nvim-lspconfig's `lsp/*.lua` names: `ruff`, `basedpyright`, `lua_ls`, `gopls`, `dartls` (`dart language-server --protocol=lsp`, root `pubspec.yaml`), `bashls` (filetypes `bash`, `sh`).
  With lazy.nvim the plugin only has to be on the runtimepath; `vim.lsp.enable{...}` picks the configs up.
- basedpyright's lspconfig defaults: `diagnosticMode = "openFilesOnly"`, no `typeCheckingMode`, so basedpyright's own default applies, documented as `recommended` (its strictest level but `all`; to confirm on the installed version in step 7); a project's `pyproject.toml` overrides the editor setting.
- Neovim 0.12 defaults (checked headless): `virtual_text = false`, `signs = true`, `float = true`, `jump.wrap = true`, `severity_sort = false`;
  LSP mappings `grn`, `gra`, `grr`, `gri`, `grt` (type definition), `grx` (codelens), `gO` (document symbols), `K`, `<C-s>` in insert (signature); `]d`/`[d` and `<C-w>d` for diagnostics.
- blink.cmp v1.10.2 (2026-04-04), spec `version = "1.*"`: on a release tag it downloads the prebuilt Rust matcher from the GitHub release and checks it against the release's `.sha256` file (`fuzzy/download/files.lua`); the Lua fallback lacks typo resistance and frecency.
  friendly-snippets loads automatically when installed; own snippets go in `<config>/snippets/` with a `package.json` manifest.
  The default keymap preset uses `<C-y>` accept, `<C-n>`/`<C-p>` select, `<Tab>`/`<S-Tab>` snippet jumps, `<C-space>` show, `<C-e>` hide, `<C-k>` signature.
- The "0.12 blink shows no LSP completions" report (discussion #2123) was a `vim.pack` setup mistake, not a blink bug; nothing to work around.
- lazydev.nvim (Neovim 0.10+) gives lua_ls the Neovim runtime and plugin types, and has a blink source.
- nvim-autopairs needs no blink glue: blink adds brackets after functions itself (`completion.accept.auto_brackets`, on by default); the integration phase 3 deferred here is nil.
- The old snippets: 7 Python (`deflog`, `logg`, `newobscb`, `deflogfmtcn`, `varflog`, `tyD`, `tyL`), 1 Go (`funcs`).
  UltiSnips' `b` flag (expand only at line start) has no vscode equivalent; `tyD`/`tyL` expand to `ty.Dict[...]`/`ty.List[...]`, the pre-3.9 typing form.
  `<leader>ue` opened `:UltiSnipsEdit`.
- Old syntastic: `always_populate_loc_list`, `auto_loc_list` (the list opened by itself on errors), check on open, a statusline flag, `<leader>bs` to check.

### Open questions for this phase

All six are settled (`00_start.md`, decisions 34-39); question 4 ended with all 8 snippets dropped after the review.
The text below is the proposal as asked; the decisions record the answers.

1. **Tools on this box now?** basedpyright (`uv tool`), gopls (`go install`), lua-language-server (release tarball into `~/.local/opt`, linked from `~/.local/bin`, sha256 checked), apt `nodejs npm shfmt` (sudo-handoff), bash-language-server from npm with `--prefix ~/.local` (binary lands in `~/.local/bin`, no PATH change, no root).
   Recommended: yes, with a system note, as in phase 3; phase 5 reuses the same choices for bootstrap.
2. **basedpyright strictness?** Its default `recommended` flags missing annotations, `Any`, unused call results and more; the old setup had no type checker.
   Recommended: `typeCheckingMode = "standard"` (pyright's normal level), which projects can raise in `pyproject.toml`.
3. **Snippet keys.** `<C-j>` maps to "jump forward if in a snippet, else accept the selected item" (accepting a snippet item expands it).
   `<C-p>` is blink's "select previous" in the menu; recommended: "jump back if in a snippet, else select previous", so both old keys work. The rest of the default preset stays (`<Tab>`/`<S-Tab>` also jump).
4. **The own snippets.** Recommended: port all 8, with `tyD`/`tyL` rewritten to `dict[...]`/`list[...]`; `<leader>ue` opens the snippet JSON for the buffer's filetype.
5. **Diagnostics on screen.** Recommended: virtual text on (current line only is an option), signs in the number column, `severity_sort`, a statusline count like `E2 W1` in place of the syntastic flag, and no location list opening by itself (`<leader>bs` fills it on demand).
6. **blink's fuzzy matcher.** Recommended: the prebuilt Rust binary (checksum-checked download, `prefer_rust_with_warning`); the alternative is `lua`, with no download.

### Steps

1. **Tools** per the system note `~/repos/plans/2026-11-03_03_lsp_servers.md` (pinned versions and the tarball digest are there): basedpyright with `uv tool`, gopls with `go install`, the lua-language-server tarball, the user's apt install (log `11a-apt-node-shfmt.log`), bash-language-server with `npm --prefix ~/.local`; check each binary resolves and prints a version.
2. **LSP** (`lua/plugins/lsp.lua`): nvim-lspconfig (`lazy = false`, configs only) and lazydev (`ft = "lua"`).
   `vim.lsp.config` overrides: basedpyright `typeCheckingMode` (question 2); ruff with hover off so `K` shows basedpyright's.
   `vim.lsp.enable{ "ruff", "basedpyright", "lua_ls", "gopls", "dartls", "bashls" }`.
   An `LspAttach` autocmd sets `gd` to `vim.lsp.buf.definition` (buffer-local, with `desc`); the 0.12 defaults stay as they are.
3. **Diagnostics** (`lua/config/diagnostics.lua`, required from `init.lua`): `vim.diagnostic.config` per question 5; `<leader>bs` runs `vim.diagnostic.setloclist()`; the statusline count added to the phase 2 statusline in `options.lua`.
4. **Completion** (`lua/plugins/blink.lua`): blink.cmp `version = "1.*"`, friendly-snippets, sources `lazydev`, `lsp`, `path`, `snippets`, `buffer`; keymap the default preset plus `<C-j>`/`<C-p>` per question 3; fuzzy per question 6.
   `appearance` set for no Nerd Font (checkhealth showed no icon font in use).
5. **Formatting:** `shfmt` for `sh`/`bash` in `conform.lua`; Lua and Dart already fall back to their LSP.
6. **which-key:** `gr` group label "LSP".
7. **Verify:**
   - headless: each server attaches in a sample file of its language (`vim.lsp.get_clients{ bufnr = 0 }`); `:checkhealth vim.lsp` and `:checkhealth blink.cmp` with no errors.
   - headless: ruff reports F841 on an unused local and nothing on a long line; basedpyright reports a type error; `gd` jumps to a definition; `<leader>bs` fills the location list and `]l` walks it; `<leader>bb` formats a `.sh` file; lua_ls knows `vim.api` (no "undefined global vim").
   - headless: blink's menu lists an LSP item and a friendly-snippets Python snippet with placeholders; accepting it fills them, `<C-j>`/`<C-p>` move between them.
   - by hand, the user: the menu while typing, the docs window, virtual text and signs, the statusline count, `K` on a Python name.

## Out of scope

- Re-litigating "native LSP vs coc.nvim" - phase 1 already decided that.
- Servers for yaml, json, ts/tsx, markdown and LaTeX (decision 20).
- ty as the Python type checker, until it reaches 1.0 (decision 22).

## Done when

- `:checkhealth vim.lsp` shows each of the five servers attaching in a file of its language.
- Opening a `.py` file shows ruff diagnostics equivalent to the old syntastic+flake8 setup,
  and blink.cmp shows completions from basedpyright and the snippet sources.
- `<C-j>` expands and walks a friendly-snippets snippet.
