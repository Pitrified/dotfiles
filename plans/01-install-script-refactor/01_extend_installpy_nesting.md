---
status: done
---

# Phase 1 - Extend `install.py` for nested folder symlinks

## Overview

Fix the asymmetry in `install.py` found while scoping
[`../02-modernize-vim-setup/`](../02-modernize-vim-setup/) (see
[`00_start.md`](00_start.md)): the topic-level whole-folder symlink path
(`install.py:203-218`) always targets `home_dir / f".{topic_at_dot.stem}"`,
with no `__`-nesting, while the item-level path (`install.py:230-282`)
already supports `__` → `/` nesting *and* already handles directories via
`target_is_directory=config_at_dot.is_dir()`. Bringing the topic-level path
in line with the item-level one is what lets a folder like
`config__nvim.symlink` land at `~/.config/nvim`.

## Goals

1. Topic-level folder symlinks support the same `__` → `/` nesting as
   item-level ones (e.g. a topic named `config__nvim.symlink` resolves to
   `~/.config/nvim`, creating `~/.config` first if needed).
2. No behavior change for existing topics without `__` in their name (e.g.
   `bash`, `git`, `tmux` keep resolving to `~/.bash`, `~/.git`... as today).
3. `--dry-run` output and backup behavior stay consistent with the existing
   item-level nested-target handling (parent dir creation, backup-before-
   relink, "already correctly linked" skip).

## Plan

- Read `install.py` end to end (not just the two symlink blocks) to confirm
  `is_conf_dir()` and the backup helper don't assume a flat `~/.<stem>`
  path elsewhere.
- Factor the nesting + parent-mkdir + backup + "already linked" logic that
  the item-level loop already has into something the topic-level block can
  reuse, rather than duplicating it - the two blocks are close to doing the
  same thing today.
- Add/update `--dry-run` coverage for a nested topic-level symlink.
- Rename `vim.symlink` to a `config__nvim.symlink` topic (or similar) as
  part of [`../02-modernize-vim-setup/`](../02-modernize-vim-setup/)'s
  Neovim-scaffold phase, not this phase - this phase only makes the
  mechanism work, it doesn't move vim's config.

## Out of scope

- Actually creating the Neovim config folder/content (that's
  [`../02-modernize-vim-setup/`](../02-modernize-vim-setup/)'s
  Neovim-scaffold phase).
- Migrating the existing Claude per-file skill symlinks to folder symlinks -
  useful once this lands, but not required by any current migration; leave
  as a follow-up, not a blocking goal here.

## Done when

- A dry-run and a real run of `install.py` correctly place a test topic
  folder named with `__` at its nested target, and existing non-nested
  topics are unaffected (verified by running install.py's existing
  behavior before/after on the current dotfiles tree).
