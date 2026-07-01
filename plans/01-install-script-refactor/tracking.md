# install.py folder-symlink nesting refactor - tracking

Extend `install.py`'s topic-level whole-folder symlink path to support
`__` → `/` nesting, matching the item-level path that already has it.
Split out of [`../02-modernize-vim-setup/`](../02-modernize-vim-setup/)
once it became clear the fix isn't a vim-specific concern. Background in
[`00_start.md`](00_start.md).

## Phases

| #  | Phase                                           | Plan                                                                | Status  |
| -- | ------------------------------------------------ | -------------------------------------------------------------------- | ------- |
| 1  | Extend `install.py` for nested folder symlinks  | [`01_extend_installpy_nesting.md`](01_extend_installpy_nesting.md) | planned |

Status values: draft / planned / in progress / done / superseded / discarded.

## Log

- 2026-07-02 : split out of `02-modernize-vim-setup` (formerly
  `01-modernize-vim-setup`) at the user's request, so the `install.py`
  mechanism fix has its own plan instead of being phase 2 of the vim
  migration. Moved the phase content over unchanged (renumbered to phase
  1 here); not expanding scope yet - that's a later planning pass.
