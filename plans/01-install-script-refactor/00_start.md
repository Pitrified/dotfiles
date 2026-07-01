# 00 - start: install.py topic-level folder-symlink nesting refactor

## Origin

Split out of [`../02-modernize-vim-setup/`](../02-modernize-vim-setup/)
(see that plan's `00_start.md` → "Additional finding: install.py's
folder-symlink asymmetry" and "Open questions - resolved" #5). While
scoping where a Neovim config would live, found that `install.py`'s
topic-level whole-folder symlink path doesn't support the same
`__`-nesting that the item-level path already has. Fixing `install.py`
isn't inherently a vim task, so it gets its own plan; the vim plan only
needs the *result* (a Neovim config folder can land at `~/.config/nvim`),
not to own the mechanism.

## Current state (as read from `install.py`)

- **Topic-level** (a whole `foo.symlink/` folder as one of the top-level
  dotfiles dirs, e.g. `vim.symlink`): target is computed as
  `home_dir / f".{topic_at_dot.stem}"` - always lands at `~/.<stem>`, no
  `__` nesting support. `install.py:203-218`.
- **Item-level** (a `.symlink` file *or folder* inside a topic dir, e.g.
  `claude/claude__rules__python.md.symlink`): target is computed as
  `home_dir / f".{config_at_dot.stem.replace('__', '/')}"` - already
  supports `__` → `/` nesting, and already handles directories
  (`target_is_directory=config_at_dot.is_dir()`), not just files.
  `install.py:230-282`.

So nesting already works for item-level entries, just not for a
whole-topic folder.

## Why this matters beyond vim

Two consumers want the same capability:

1. The Neovim config needs to land at `~/.config/nvim`, not `~/.nvim`
   ([`../02-modernize-vim-setup/`](../02-modernize-vim-setup/)).
2. The Claude skills currently symlinked file-by-file (e.g.
   `claude__skills__tracked_development__SKILL.md.symlink`) would be
   simpler as one nested *folder* symlink per skill once multi-file
   skills (with a `references/` dir, scripts, etc.) show up.

## Decision

Extend the topic-level folder-symlink path to support `__` nesting,
matching the item-level path that already has it, rather than working
around the limitation per-consumer (e.g. `~/.nvim` + `NVIM_APPNAME` for
vim specifically). This was decided while scoping the vim plan, before
the split; full reasoning and the rejected alternative are recorded there:
[`../02-modernize-vim-setup/00_start.md`](../02-modernize-vim-setup/00_start.md#open-questions-resolved)
→ "Open questions - resolved" #5.

## Scope for now

Per the user: split the folder now for clarity, don't expand the plan
yet. The only phase currently defined is the mechanical `install.py` fix
([`01_extend_installpy_nesting.md`](01_extend_installpy_nesting.md));
further phases (e.g. migrating the Claude skill symlinks to use it) are
not planned yet.
