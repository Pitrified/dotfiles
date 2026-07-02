# My dotfiles

I use these dotfiles to keep my Linux experience uniform across machines.

The project is heavily inspired by [holman's dotfiles](https://github.com/holman/dotfiles), that are far more comprehensive. Go check them out.

The install script is in python, that I find far more readable than bash.

## Structure

The repo is split in topics.

Anything with a `.symlink` extension will be symlinked in the home folder. Both folders and files can be linked.

Anything with a `.bash` extension will be sourced by `~/.bash_aliases`, that is generated automatically by the script.
The actual `bash_aliases` file is in `bash/bash_aliases.bash`

* `topic.symlink/`: symlink the folder (e.g. `vim.symlink` to `~/.vim`)
* `topic/*.symlink`: symlink the file (e.g. `tmux/tmux.conf.symlink` to `~/.tmux.conf`)
* `topic/*.bash`: source the file in the auto-generated  `~/.bash_aliases`

A `__` in a `*.symlink` name expands to a `/`, so the target can be nested
inside a dotfolder instead of landing directly in `~`. Missing parent folders are
created automatically, and this works for both files and folders. This is used to
track individual files and skill folders inside `~/.claude/` without symlinking
the whole folder (which holds credentials and session state):

* `claude/claude__CLAUDE.md.symlink` -> `~/.claude/CLAUDE.md`
* `claude/claude__rules__python.md.symlink` -> `~/.claude/rules/python.md`
* `claude/claude__settings.json.symlink` -> `~/.claude/settings.json`
* `claude/claude__skills__tracked-development.symlink/` -> `~/.claude/skills/tracked-development` (a folder, holding `SKILL.md` and any other skill assets)

### Local personalizations

Aliases that are private or machine specific can be put in `~/.bash_aliases.local`, that is sourced automatically.
Notice that it is sourced first, _before_ the symlinked files.
If additional aliases need to be set after sourcing all the others, write them in `~/.bash_aliases.after.local`, that is sourced last.

Private git configs can be put in `~/.gitconfig.local`, that is included by `git/gitconfig.symlink`.

Additional vim settings can be saved in `~/.vimrc.local`, that is sourced at the _end_ of `vim.symlink/vimrc`

### install.py

Lives at `install/install.py`, with its own `pyproject.toml` (`uv`-managed,
pinned to Python 3.14; no runtime dependencies, still stdlib-only). This is
unrelated to how the topic-folder symlinking itself works - it's just how
`install.py` runs and gets a `pytest`/`ruff` dev environment.

Install everything with

```bash
cd install
uv run install.py
```

or from anywhere, without changing directory first:

```bash
uv run --project ~/dotfiles/install ~/dotfiles/install/install.py
```

The backup directory name can be set with the option `--backup_dir`, the default is `.rcback`, so the old configuration will be backed up in `~/.rcbackNN`, and `NN` is automatically chosen to produce an unique dirname.

Pass `--dry-run` (`-n`) to print every move, write, and symlink the script would
make without touching the filesystem. Handy to check correctness before a real run.
