# 06 - feat: promote project memories that are really global rules

## Goal

Two things, and the second is why the first came up.

1. Add a `~/.claude/rules/` file covering how to run and wait on long background jobs, because the
   lesson has now been learned three times in two projects and the note recording it cannot reach
   either of the other two.
2. Act on the sweep of every project memory on this box that found it, promoting the ones that are
   not about their project and correcting one that is filed in the wrong place.

## Why this class of thing needs promoting at all

Project memories live at `~/.claude/projects/<mangled-path>/memory/` and load only in that project.
That is right for most of them. It is wrong for a memory whose content is about **the user**, **the
box**, or **the harness**, because those are true in every repo and the repo you happen to be in
when you learn one is an accident.

The failure is quiet: the memory exists, it is correct, and the session that needed it never saw it.
The background-jobs lesson was learned in `snap_fit` in July, written down there, and then
rediscovered from scratch in `house-renderer` in September. Nobody was wrong at any point.

## The sweep, 2026-09-13

Seven memories across six projects.

| Memory | Project | Verdict |
| --- | --- | --- |
| `watchers-die-with-their-run` | `snap_fit` | content is global, file stays (it is that project's history) |
| `long-running-background-jobs` | `house-renderer` | delete once the rule exists; it is a hand copy of the above |
| `no-ask-question-tool` | `house-renderer` | **promote**, it is about the user |
| `chat-prose-style` | `genealogy-gramps-fn` | **promote**, it is about the user |
| `git-lfs-scope-fixes-per-repo` | `bootstrap` | **promote**, it is about this box and about global git config |
| `gemini-support-tracked-dev` | `linux-box-cloudflare` | **wrong project**, and possibly stale |
| `flutter-toolchain-on-box` | `flutter-setup-project` | leave, correctly scoped |

### 1. Background jobs and watchers

The new rule. Four sightings: `snap_fit` 2026-07-26 (watchers armed on a success string polled for
over 175 minutes after their jobs were killed, three times in one session, ten stragglers cleared at
once; and a self-matching `pkill` killed its own shell mid-command, so edits chained after it
silently never ran and the change looked applied); `house-renderer` 2026-09-13 (the same waits,
written from scratch, correct only because the failure alternation happened to be there);
`house-renderer` 2026-09-15, which is the one that adds a rule rather than repeating one.

That fourth sighting: two `until` loops waiting on a pair of Cycles renders, **patterns correctly
bracketed**, both polling for the rest of the session. `pgrep -f` reads the whole command line, and
the loop's line went on to report:

```sh
until ! pgrep -f "[i]ncasso_black"; do sleep 20; done; ls renders/incasso_black.png
```

The `ls` at the end is an unbracketed match on the watcher itself. The renders had finished and been
used; the watchers were found only because the user asked whether anything was still running. So the
bracketing rule as written was followed and was not enough, which is exactly the kind of gap that
justifies writing the reasons down beside the rules.

Draft content, reasons kept attached because the bare rules read as superstition and get dropped:

- **Bracket the first character of every `pgrep` and `pkill` pattern**: `pgrep -f "[m]y_script"`,
  never the bare name. Unbracketed, the pattern matches the shell running it: a `pgrep` watcher sees
  itself and never exits, a `pkill` kills its own shell.
- **Bracketing the pattern is not enough if the rest of the line names the job.** `pgrep -f` reads
  the whole command line, so a report chained after the loop - `; ls out/my_script.png` - is an
  unbracketed match on the watcher itself and the loop never ends. Either bracket every occurrence,
  or let the loop be the only thing on that line that names the job and report from a separate call.
- **Put a kill in its own call.** Never chain work after a `pkill` in one command.
- **Watch the process, not a success string.** `until ! pgrep -f "[m]y_script"; do sleep N; done`
  ends when the job ends, whatever happened to it.
- **A grep exit condition must trip on failure too**, a `Traceback|Error|FAILED|Killed` alternation,
  never a happy-path string alone. Same for waiting on a file: a producer that dies before flushing
  leaves it empty forever.
- **Stop a watcher in the same breath as its job.**
- **`ps` does not reliably see harness-managed background shells.** An empty sweep is not proof
  nothing is running; track background work by its task id.

### 2. `no-ask-question-tool` is about the user, not about `house-renderer`

"Do not use the AskUserQuestion tool with this user. Write the options and the recommendation in the
chat message and wait for the next reply." The reason given is the user's answering style: replies
are often several sentences that reject the premise rather than picking an option, and the tool's
input is a poor place to write that. Nothing in it is repo-specific, and the tool is offered in
every session.

### 3. `chat-prose-style` is about the user too

"Chat responses must follow the same prose rules as the repository." Named anti-patterns: negative
parallelism ("not X, it is Y"), setup lines that announce what is coming, punchline structures.
Asked for explicitly on 2026-08-31 in one repo, and independently written into `house-renderer`'s
own `.github/copilot-instructions.md` as "No fake drama". Two repos arriving at the same rule
separately is the signal that it belongs above both.

`~/.claude/CLAUDE.md` already has a Style section, so this is an addition to an existing home rather
than a new file. Note that it currently only governs files: the missing half is that it applies to
chat replies.

### 4. `git-lfs-scope-fixes-per-repo` is about this box

"Some repos on this box genuinely use git-lfs (`~/repos/lang-tools`); a global `git lfs install` or
`git config --global lfs.locksverify` silently affects them." Filed under `bootstrap`, which is the
repo that did *not* use LFS. The damage it prevents lands on a different repo entirely, and the
session most likely to cause it is one that has never heard of either.

It splits in two, and the halves want different homes:

- The principle: never change git config globally on this box, scope the fix to the repo
  (`git -C <repo> config ...`, `git lfs install --skip-repo`, `lfs.locksverify false` per repo).
  That is a rule.
- The fact: which repos here actually use LFS. That is a box fact and belongs with the other box
  facts, in `linux-box-cloudflare`'s `configs/claude/rules/local-box.md`.

### 5. `gemini-support-tracked-dev` is filed in the wrong project

It describes tracked development whose folder is `~/repos/llm-core/scratch_space/04_gemini_support/`
and whose work spans `llm-core` and `laife`. It is stored under `linux-box-cloudflare`, so a session
in either repo that actually does the work will not load it. Not a promotion: a move, or a copy into
both.

**Check it before trusting it.** It was written 2026-07-10 and says phase 1 of six is done. Two
months on, that is either accurate or badly stale, and a memory that reports stale phase state is
worse than none.

### 6. One box fact worth adding while here

Claude's shell is not a login shell, so `~/.bashrc` PATH exports do not apply. `python` is not on
PATH in a session on this box (`python3` and `uv run python` are), and the Flutter memory records the
same thing for `flutter` and `ANDROID_HOME`. One line in `local-box.md` covers both and a class of
others.

## Where things go

`~/dotfiles` owns the global Claude config through `claude/claude__*.symlink`, where `__` expands to
`/`. A new rule is one file and no script change: the installer globs `*.symlink`.

- `claude/claude__rules__harness.md.symlink` -> `~/.claude/rules/harness.md`, new, holding item 1.
- `claude/claude__rules__git.md.symlink` -> `~/.claude/rules/git.md`, new, holding item 4's principle.
- `claude/claude__CLAUDE.md.symlink`, edited, for items 2 and 3.
- `linux-box-cloudflare`'s `configs/claude/rules/local-box.md`, edited, for item 4's fact and item 6.
  Different repo, and it is already symlinked into `~/.claude/rules/`.

**No `paths:` frontmatter** on the two new files. `python.md` uses it so Python rules never reach a
Go session; these are about tool use rather than file types, and load unconditionally the way
`local-box.md` does.

**Budget.** Plan `00-feat-anti-superficiality-rules.md` recorded that instruction-following degrades
past roughly 80 lines in one file and that the answer is to prune as much as you add.
`~/.claude/CLAUDE.md` is at 65. So items 2 and 3 go in as a handful of lines, not paragraphs, and
everything longer goes to its own `rules/` file, where the budget is per file.

## Merged in

`~/repos/plans/2026-09-15_00_watcher_self_match_rule.md` was written box-wide the day the fourth
sighting happened, before this plan was found. Its content is folded in above and the file is
deleted rather than left to disagree with this one: two notes about one rule is the same failure the
plan is about. `~/repos/plans` keeps it in git history if anyone wants the original.

What that note had and this one did not: the self-match-via-the-rest-of-the-line rule, the fourth
sighting, and a short "if this becomes a skill" section. The last of those is the only part not
carried over, because this plan already answers it - the rule goes to `~/.claude/rules/harness.md`,
which loads unconditionally, and a skill is the heavier tool for something that needs to be in
context before the mistake rather than invoked after it.

## Steps

1. Write `claude/claude__rules__harness.md.symlink`.
2. Write `claude/claude__rules__git.md.symlink`.
3. Add items 2 and 3 to `claude/claude__CLAUDE.md.symlink`, tightly, and prune if it passes 80 lines.
4. `uv run --project ~/dotfiles/install ~/dotfiles/install/install.py`, confirm both symlinks resolve.
5. In `linux-box-cloudflare`, add the LFS fact and the non-login-shell fact to `local-box.md`.
6. Delete `house-renderer`'s `long-running-background-jobs.md` memory and its index line.
7. Verify the Gemini memory against its tracking folder, then move or copy it to `llm-core`.

## Rollback

Every step is a file in a git repo plus a symlink under `$HOME`. Revert the commit, delete the
symlink, re-run the installer. Nothing outside `$HOME`, no privileged command.

## Open questions

- Q1: one `harness.md` that accretes lessons about working with Claude Code, or one file per
  lesson? There is probably more of this kind of thing coming.
  Recommended: one file named for the general case, let it grow, split when it passes the budget.
  NEW_ANS:
- Q2: does promoting a memory mean deleting it from the project, or leaving it as that project's
  record of where the lesson came from? `snap_fit`'s carries its own history and links to
  `[[snap-fit-matching-phases]]`.
  Recommended: leave the original where it was learned, delete only hand copies made later.
  NEW_ANS:
- Q3: two of the seven memories link to memories that do not exist
  (`[[snap-fit-matching-phases]]`, `[[tracked-development-conventions]]`). The format allows that,
  a link is a note that something is worth writing. Is either worth writing now?
  NEW_ANS:
