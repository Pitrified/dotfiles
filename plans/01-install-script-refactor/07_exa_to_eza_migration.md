---
status: done
---

# Phase 7 - Migrate the exa aliases to eza

## Overview

`bootstrap/install_tools.sh` now installs `eza` (the maintained fork of
the unmaintained `exa`) from the gierens apt repo, but
`dotfiles/bash/aliases_exa.bash` still calls `exa`.
On a fresh box the aliases (`le`, `lt`, ...) would all fail: `eza` gets
installed, `exa` never does.
This box only works because a manually installed `exa` v0.10.1 (from the
phase-6 zip leftovers) still sits in `~/.local/bin/exa`.

This phase makes the live box match what the bootstrap scripts would
produce, then switches the aliases to `eza`.

Cross-repo: touches `dotfiles` (aliases) and the live box (installing
eza, removing the stale binary). `bootstrap` itself needs no changes -
its eza install block is already correct.

## Goals

1. `eza` installed on this box via the same apt-repo commands
   `install_tools.sh` uses (keyring + gierens list + `apt install eza`),
   so the box exercises the real bootstrap path.
2. `bash/aliases_exa.bash` renamed to `bash/aliases_eza.bash` with every
   `exa` invocation changed to `eza`.
   Flag compatibility must be checked at implementation time against the
   installed eza's `--help` - the aliases use `--long --git --all --tree
   --level=N --ignore-glob=...`, all of which eza documents as supported,
   but verify rather than assume.
3. Stale `~/.local/bin/exa` removed once the eza aliases are verified
   working, so nothing on the box silently depends on the unmaintained
   binary.
4. `bootstrap/README.md`'s `install_tools` bullet updated from `exa` to
   `eza` (one-word change, folded in here rather than into phase 6 since
   it belongs to this switch).

## Plan

- Run the eza install block from `install_tools.sh` on this box.
- `git mv bash/aliases_exa.bash bash/aliases_eza.bash`, then
  `sed`-style replace `exa` with `eza` inside; review the diff by hand
  (the file also contains the word `exa` in comments).
- Open a fresh shell, confirm `le` and the `lt`/tree aliases work
  against a real directory.
  Be careful with the just-installed `eza`: a freshly installed binary
  may be missing from the current shell's environment (PATH/hash cache),
  so verify in a genuinely new shell, not the one that ran the install.
- `rm ~/.local/bin/exa`.
- Grep both repos for remaining `exa` references
  (`grep -rn exa ~/dotfiles ~/bootstrap --include='*.bash'
  --include='*.sh' --include='*.md'`) - `colors_wsl.md`'s historical
  exa-build notes may stay as history, everything functional must be
  eza.

## Decision point

Keeping a compatibility `alias exa=eza` was considered and rejected:
nothing in the repos would use it, and it hides exactly the kind of
stale reference this phase is meant to flush out. Confirmed not needed -
`le` and `lt` are the muscle-memory entry points, and they get updated
to eza by this phase.

## Out of scope

- Theming/dircolors work (`colors_wsl.md`) - historical notes, untouched.
- Any other tool in `install_tools.sh`.

## Done when

- Fresh shell: `le` and `lt` work, backed by apt-installed `eza`.
- `which exa` finds nothing; `~/.local/bin/exa` is gone.
- No functional `exa` reference remains in `dotfiles` or `bootstrap`.
