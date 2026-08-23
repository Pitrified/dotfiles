# Fix sudo-guard false positives: skip heredoc bodies

## Status

**Nothing is installed.** The live hook on g7 is the unchanged original
(`claude/claude__hooks__sudo-guard.sh.symlink`, the regex below).

Two temporary changes were made and reverted while investigating on 2026-08-23: the python
matcher was installed live, and later the hook entry was removed from `settings.json` outright.
Both are back to `HEAD`; `sudo -n true` blocks as before.

Files here:

| File | What it is |
| --- | --- |
| `00_plan.md` | this note |
| `audit.py` | measures real denials from `~/.claude/projects/*.jsonl`; run on any box |
| `sudo_guard.py` | a full shell-aware matcher. **Rejected as over-built**, kept as evidence |
| `test_sudo_guard.py` | 20-case corpus for `sudo_guard.py`, `python3 -m pytest -q` here |

## What actually goes wrong

The hook matches a regex over the whole command string:

```
(^|[^[:alnum:]_./-])sudo([[:space:]]|$)
```

It is a substring test, so it cannot tell a sudo that runs from a sudo that is being written into
a file. Its own header calls this "acceptable, the deny message tells the model to rephrase".
Two reasons it is not.

**The skill causes it.** The `sudo-handoff` skill exists to make Claude write privileged commands
into plan notes and handoff blocks, and `local-box.md` makes the note mandatory *before* handing a
privileged command over. The documented workflow is "write a file containing the word sudo", which
is what the hook blocks.

**"Rephrase to avoid the word" damages the artifact.** In the g4 IPv4 outage note (2026-08-23,
`~/repos/plans/2026-08-23_00_ipv4_outage_ipv6_dns_workaround.md`) it produced command blocks with
`sudo` stripped off and a prose line "both `nmcli` lines need elevation" bolted on. A runbook that
omits the word from the command it tells you to paste is a worse runbook.

## Measured, not guessed

`audit.py` over every transcript on both boxes, including subagents. Hook installed 2026-07-16;
transcripts run 2026-07-23 to 2026-08-23.

| | g7 | g4 | total |
| --- | --- | --- | --- |
| transcripts | 12 | 41 | 53 |
| Bash calls | 1833 | 2012 | 3845 |
| guard denials | 9 | 4 | 13 |

Of the 13 denials: **6 real sudo, 6 false positives**, plus 1 that was not a match at all (the
exit-2 lockout described below).

So the false-positive rate is 6 in 5 weeks across 3845 Bash calls. Rare - but each one costs a
workaround, and the prescribed workaround degrades the output.

**Every false positive is a heredoc. All six.**

| Shape | Count |
| --- | --- |
| `python3 - <<'PY'` doing read/replace on a plan `.md` | 4 |
| `ssh host "cat > file" <<'EOF'` | 1 |
| `cat > file <<'EOF'` | 1 |

The dominant case is not hand-writing docs, it is Claude patching a markdown plan file with an
inline python script whose *replacement text* mentions sudo.

**Every true positive is caught by the plain regex.** Five of the six are `sudo -n true`
capability probes; the sixth is an `apt-get -s` line on g4. None needed tokenization, command
position tracking, wrapper handling or ssh-argument recursion.

## Decision: the narrow fix

Keep the bash script and keep the regex. Add one rule:

**Strip heredoc bodies before matching, unless the heredoc feeds a shell.**

That is 6/6 false positives fixed and 6/6 true positives kept, in roughly 15 lines of bash. It
stays in the existing script, keeps the `jq`-with-`python3`-fallback tolerance, adds no dependency,
and avoids the exit-2 trap below entirely.

The one subtlety: `ssh host "cat > f" <<'EOF'` mentions `ssh`, but the body is still data. The test
has to be "the last command word before `<<`, and if that is `ssh`, the command word of its quoted
argument" - not "does this line mention a shell". `_consumer_is_shell()` in `sudo_guard.py` is the
worked version of exactly this rule; port that function's logic, not the rest of the file.

### Why `sudo_guard.py` is rejected

It is ~140 lines that tokenize with `shlex`, track command position, expand wrappers
(`timeout`, `env`), and recurse into quoted ssh arguments. It scores 26/26 on a hand-written
corpus against 17/26 for the regex. But the corpus was hand-picked, and the measured traffic says
those extra rules never fire: no false positive in 5 weeks came from an `echo`, a `git commit -m`,
or a quoted string, and no true positive needed more than the regex. It is the right answer to a
problem that does not occur here.

It also introduces a hard `python3` dependency and, with it, the trap below.

## The exit-2 trap, if a python rewrite is ever revisited

Claude Code reads hook exit codes as: 0 = allow, **2 = block**, other non-zero = non-blocking
error. And:

```
$ python3 /nonexistent/x.py; echo $?
python3: can't open file '/nonexistent/x.py': [Errno 2] No such file or directory
2
```

python3's exit code for a missing script is 2, the same code that means "block". With
`settings.json` running `python3 ~/.claude/hooks/sudo-guard.py`, a missing or unreadable hook file
blocks **every Bash call in every session**. This happened on 2026-08-23 when `settings.json` was
pointed at the file before it existed; the shell was unusable until the file was created through
the Write tool, which no hook gates. A missing `.sh` gives bash 127 instead, which is only a
warning.

Related: nothing guarantees `python3` is on PATH. It comes from `python3-minimal`, priority
`important`, not `essential`. If absent the shell exits 127 and the guard fails open, which is the
acceptable direction.

If a python hook is ever wanted, use a shebang plus direct exec (`~/.claude/hooks/sudo-guard.py` as
the command) so both a missing file and a missing interpreter give 127, and create the file before
pointing `settings.json` at it.

## Steps, if adopted

1. In `claude/claude__hooks__sudo-guard.sh.symlink`, strip heredoc bodies from `$cmd` before the
   existing `grep -qE`, keeping bodies whose consumer is a shell (port `_consumer_is_shell`).
2. Rewrite the deny message: drop "rephrase the command to avoid the word", point at the Write tool
   for content that must contain it.
3. Update `claude__skills__sudo-handoff.symlink/SKILL.md`: privileged commands go into notes and
   handoff blocks verbatim; if Bash is blocked while only writing content, use Write, never elide.
4. Re-enable the hook entry in `settings.json`.
5. Verify with `audit.py`'s 13 real cases replayed through the script, then live: one `sudo -n true`
   (expect block), one `cat > f.md <<'EOF'` containing the word (expect pass).

## Rollback

```bash
cd ~/dotfiles && git checkout -- claude/claude__hooks__sudo-guard.sh.symlink claude/claude__settings.json.symlink
```

No symlink or settings path changes, so nothing to re-link and no lockout risk. Worst case, delete
the hook entry from `settings.json` - the skill and the `CLAUDE.md` pointer still carry the
procedure advisorily.
