---
status: done
---

# Phase 2 - Migrate Claude skill symlinks to folder-based ones

## Overview

Convert each `claude/claude__skills__<name>__SKILL.md.symlink` (an
item-level *file* symlink) into `claude/claude__skills__<name>.symlink/`
(an item-level *directory* symlink containing `SKILL.md`). See
[`00_start.md`](00_start.md) → "Claude skill folder-symlink migration -
not actually blocked by phase 1": the item-level `.symlink` path already
handles directories (`target_is_directory=config_at_dot.is_dir()`), so
this needs **no `install.py` change** and doesn't depend on phase 1.
Independent phase, sequenced here only because it's small and the
motivation (multi-file skills showing up later) is fresh context.

## Goals

1. Both current skills (`caveman`, `tracked-development`) move from
   `claude/claude__skills__<name>__SKILL.md.symlink` to
   `claude/claude__skills__<name>.symlink/SKILL.md`.
2. `~/.claude/skills/<name>/SKILL.md` resolves identically after
   `install.py` re-runs (same file content, now reached through a
   directory symlink instead of a file symlink).
3. `dotfiles/README.md`'s Claude-skills bullet examples are updated to
   show the new folder-symlink form.

## Plan

- For each skill: `git mv claude/claude__skills__<name>__SKILL.md.symlink
  claude/claude__skills__<name>.symlink/SKILL.md` (create the directory,
  move the file in).
- Run `install.py --dry-run` to confirm both entries resolve to the same
  `~/.claude/skills/<name>` target as before (as a directory symlink now,
  not a file symlink two levels down).
- Run `install.py` for real, confirm the old file symlinks at
  `~/.claude/skills/<name>/SKILL.md` are backed up and replaced by
  `~/.claude/skills/<name>` as a directory symlink.
- Update the README's example bullets under "A `__` in a `*.symlink`
  filename expands to..." to show a folder-symlink skill example
  alongside the existing file-symlink ones (e.g. `claude/claude__rules__
  python.md.symlink` stays a file example; add
  `claude/claude__skills__tracked-development.symlink/` as the folder
  example).

## Out of scope

- Any change to skill *content* (`SKILL.md` bodies) - pure relocation.
- `install.py` code changes - none needed for this phase.

## Done when

- `find dotfiles/claude -iname '*skill*'` shows two `.symlink` folders,
  no `.symlink` files, each containing a `SKILL.md`.
- A real `install.py` run leaves `~/.claude/skills/caveman` and
  `~/.claude/skills/tracked-development` as directory symlinks pointing
  at the corresponding `dotfiles/claude/...symlink/` folders, with old
  content backed up, not lost.

## Follow-up: `tracked_development` -> `tracked-development`

The Agent Skills spec requires the frontmatter `name` to be lowercase
letters/numbers/hyphens only (no underscores) and to match the resolved
directory name. `tracked_development`'s underscore predated this phase
and was unrelated to it, but got fixed in the same sitting since the
folder was already being touched: renamed the dotfiles folder, symlink,
and frontmatter `name` to `tracked-development`; the installed command is
now `/tracked-development`.
