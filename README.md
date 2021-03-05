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

### Local personalizations

Aliases that are private or machine specific can be put in `~/.bash_aliases.local`, that is sourced automatically.
Notice that it is sourced first, _before_ the symlinked files.
If additional aliases need to be set after sourcing all the others, write them in `~/.bash_aliases.after.local`, that is sourced last.

Private git configs can be put in `~/.gitconfig.local`, that is included by `git/gitconfig.symlink`.

Additional vim settings can be saved in `~/.vimrc.local`, that is sourced at the _end_ of `vim.symlink/vimrc`

### install.py

Runs with python, version `>=3.6`.

Install everything with

```bash
python3 install.py
```

The backup directory name can be set with the option `--backup_dir`, the default is `.rcback`, so the old configuration will be backed up in `~/.rcbackNN`, and `NN` is automatically chosen to produce an unique dirname.
