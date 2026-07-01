---
status: done
---

# Phase 1 - Resolve open questions & decisions

## Overview

Before touching any vim config or install script, the four forking questions
in [`00_start.md`](00_start.md#open-questions-need-the-users-decision-before-phases-3-can-be-planned)
need answers, because they determine whether phases 2-5 are "small cleanups
on the current stack" or "rewrite around Neovim + LSP." No code changes
happen in this phase - it's a conversation, then a write-up.

## Goals

1. Get the user's answer on vim vs Neovim.
2. Get the user's answer on the completion/linting replacement for syntastic
   (none / ALE / coc.nvim / native LSP), consistent with (1).
3. Get the user's answer on plugin manager (keep vim-plug / switch), which is
   only a live question if (1) leans Neovim.
4. For each of the four dead-mapping cases (Black, YouCompleteMe, vim-go,
   vim-latex): does the user still want that tool? Re-enable, or delete the
   plugin remnant + mapping entirely?

## Plan

- Asked the four questions directly, plus a fifth that surfaced while
  scoping question 1 (where the Neovim config should live, given
  `install.py`'s folder-symlink limitation).
- Recorded each answer, and the rejected alternative with why, in the
  "Open questions - resolved" section of `00_start.md`.
- Rewrote the phase breakdown in `tracking.md` to match the now-confirmed
  scope (Neovim migration, not an in-place vim cleanup) - 7 phases instead
  of the original 5.

## Out of scope

- Any actual edit to `vimrc`, `gvimrc`, `after/ftplugin/*`, or
  `install_vim.sh` - those start in phase 2 onward. `install.py`'s fix is
  tracked separately in
  [`../01-install-script-refactor/`](../01-install-script-refactor/).

## Done when

- [x] All five open questions have a recorded answer in `00_start.md`.
- [x] `tracking.md`'s phase table reflects the confirmed scope, with
  statuses updated accordingly.
