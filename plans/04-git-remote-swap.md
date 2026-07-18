# git remote swap transport type

## draft

we often have something like this in our repos

```bash
$ ~/bootstrap (master)$ git remote -v
origin  https://github.com/Pitrified/bootstrap.git (fetch)
origin  https://github.com/Pitrified/bootstrap.git (push)
```

and we want to swap to ssh

```
git@github.com:Pitrified/bootstrap.git
```

we can create a new `.bash` in `/home/pmn/dotfiles/git`


## plan

### where it lives

Create `~/dotfiles/git/remote_swap.bash`.
`install.py` auto-sources every `.bash` file in a topic dir into `~/.bash_aliases`
(see `install.py:264-270`), so after adding the file rerun `~/dotfiles/install/install.py`
to wire it up (bash_aliases is generated, not edited by hand).
Match the existing style in `aliases.bash`: bare function, short mnemonic, usage echo on bad args.

### the conversion

Only the transport prefix changes; user/repo/`.git` are untouched.

```
https://github.com/Pitrified/bootstrap.git   ->   git@github.com:Pitrified/bootstrap.git
```

So the swap is a single substitution: `https://github.com/` -> `git@github.com:`
(note `/` becomes `:` after the host). Reverse direction flips it back.

### function: `git_remote_swap`

Explicit name over a short mnemonic: this is a one-off, not a daily command,
so clarity beats brevity.

Behavior:

1. Read the current `origin` url with `git remote get-url origin`
   (fail with a message if not in a repo / no origin).
2. Detect current transport:
   - starts with `https://github.com/` -> swap to ssh.
   - starts with `git@github.com:` -> swap to https (so the function toggles).
   - anything else (non-github host, ssh with different user) -> print the url and bail,
     do not guess.
3. Build the new url with a `sed -E` substitution.
4. Print old -> new, then apply with `git remote set-url origin "$new"`.
5. Echo the result of `git remote -v` so the change is visible.

Sketch:

```bash
git_remote_swap () {
    old=$(git remote get-url origin 2>/dev/null) || {
        echo "Not a git repo or no 'origin' remote."
        return 1
    }

    if [[ "$old" == https://github.com/* ]]; then
        new=$(echo "$old" | sed -E 's#^https://github.com/#git@github.com:#')
    elif [[ "$old" == git@github.com:* ]]; then
        new=$(echo "$old" | sed -E 's#^git@github.com:#https://github.com/#')
    else
        echo "Unrecognized github remote, leaving it alone:"
        echo "  $old"
        return 1
    fi

    echo "  old: $old"
    echo "  new: $new"
    git remote set-url origin "$new"
    git remote -v
}
```

### decisions (settled)

- Name: `git_remote_swap`, explicit over a mnemonic.
- Direction: toggle (https<->ssh), the natural inverse.
- Remote: `origin` only, hardcoded. No speculative `$1` for a remote name.
- Host scope: github.com only. Other hosts bail out rather than guess the ssh user.

### steps

1. Write `~/dotfiles/git/remote_swap.bash` with the `git_remote_swap` function above.
2. Run `~/dotfiles/install/install.py` (or `--dry-run` first) to regenerate `~/.bash_aliases`.
3. `source ~/.bash_aliases` (or new shell), `cd` into a repo, run `git_remote_swap`, verify with `git remote -v`.
4. Optionally note the function in `git/README.md` alongside the other git helpers.
