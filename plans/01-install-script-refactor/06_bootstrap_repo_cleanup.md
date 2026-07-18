---
status: done
---

# Phase 6 - Clean up untracked leftovers in the `bootstrap` repo

## Overview

`~/bootstrap` has been carrying untracked files for a long time:
`exa-linux-x86_64-v0.10.1.zip` plus the extracted `bin/`, `completions/`,
`man/` folders, a 2-line scratch `t.sh`, and `install_backup.sh` which is
a markdown note rather than a script.
This phase removes the leftovers and preserves the one useful note.

Same cross-repo shape as phase 3: touches `~/bootstrap`, not `dotfiles`.

## Findings

Established by inspection on 2026-07-18:

- The zip and `bin/`/`completions/`/`man/` are the extracted layout of
  the exa v0.10.1 release archive.
  `~/setup_bootstrap/` holds the *same* zip and the same extracted
  folders (alongside the go tarball, chrome/bat/gcm debs, `get-pip.py`),
  and `bin/exa` is byte-identical to the installed `~/.local/bin/exa`.
  Conclusion: the manual exa install was run once from `~/bootstrap`
  instead of `~/setup_bootstrap`, leaving a duplicate in the repo.
  Nothing references these repo-root copies.
- The manual-zip install method is obsolete anyway:
  `install_tools.sh` was since rewritten to install `eza` (exa's
  maintained fork) from the gierens apt repo, and it already does
  `mkdir ~/setup_bootstrap && cd ~/setup_bootstrap` before any download,
  so the current script cannot recreate this mess.
- `t.sh` contains only `mkdir ~/setup_bootstrap` + `cd ~/setup_bootstrap`,
  duplicating the lines already in `install_tools.sh`. Pure scratch.
- `install_backup.sh` contains a markdown snippet with one rclone command:
  `rclone --vfs-cache-mode writes mount onedrive: ~/OneDrive`.
  Worth keeping as a note, not as a fake `.sh`.

## Plan

1. Delete from `~/bootstrap` (plain `rm`, nothing is tracked):
   - `exa-linux-x86_64-v0.10.1.zip`
   - `bin/`, `completions/`, `man/`
   - `t.sh`
2. Preserve the rclone note: rewrite `install_backup.sh` as a clean
   script matching the other `install_*.sh` files
   (install `rclone`, with the mount command kept as a comment),
   and add an `install_backup` bullet to `README.md`.
3. No `.gitignore`. Considered and rejected: the current scripts already
   download into `~/setup_bootstrap`, so they cannot recreate this mess;
   any future mess should be *visible* in `git status` and lead to a
   fix, not be silently ignored.
4. `git status` must come back clean afterwards; commit is left to the
   user per repo convention.

## Out of scope

- `~/setup_bootstrap/` itself - it is outside the repo and is the
  *intended* dumping ground; its contents are harmless.
- The exa/eza alias mismatch in `dotfiles` - that's phase 7.
- Removing `~/.local/bin/exa` from the live box - also phase 7, since it
  only makes sense together with the eza switch.

## Done when

- `git status` in `~/bootstrap` reports a clean working tree.
- The rclone mount command is still findable in the repo, inside a
  proper `install_backup.sh`, with a `README.md` bullet.
