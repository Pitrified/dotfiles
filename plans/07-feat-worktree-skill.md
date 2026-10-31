# 07 - feat: a general worktree skill, and a spin_worktree script each repo keeps

## Goal

Working a second branch in its own folder beside the main checkout is written up once, in `house-renderer/docs/worktrees.md`, as hand-run setup commands.
Lift the general part into a dotfiles skill, and replace the hand-run setup with a script each repo maintains for itself:

```sh
scripts/spin_worktree feat/NN_name
```

creates the folder, runs that repo's installs, and gives the command that starts a second Claude session there, in its own zellij session with Remote Control on, so it shows up in the web UI.
The session that ran the script keeps working in the main checkout.

Status: executed 2026-10-30 through step 8.3; see "Execution log". Waiting on the user for the commits (step 7 and the house-renderer branch) and the step 8.4 test.

## Source material

- `house-renderer/docs/worktrees.md`: opening, what the two checkouts share, the Claude session, closing.
- `house-renderer` plans `57`, `72`, `76`: worktrees used for a probe at an old commit, for a feature, and a feature handed back to the main checkout.
- The worktrees on g7 today, `git worktree list` in `house-renderer`: each carries the `.r2.env` symlink, and one is on a branch that does not follow `feat/NN_name`.
- `tracked-development` skill, "Branches and merging" and the spin-off section: the `feat/<NN_name>` branch convention and `plans.py branches` for a free number.
  Its `reference/plans-script.md` is the precedent for a script that lives in the skill and is copied into each repo.
- Claude Code docs, `code.claude.com/docs/en/memory`, `/permissions` and `/permission-modes`, read 2026-10-30 against Claude Code 2.1.311; quoted where used below.
- The zellij sessions on g7 (`zellij list-sessions`) are named `<repo>-g7-<n>`; the worktree sessions get their own `wt-` prefix so they sort apart.

## What is general and what is house-renderer's

General, goes in the skill:

- The folder is `../<repo>-<suffix>`, a sibling of the main checkout, on its own branch cut from the default branch.
- The main checkout is read-only to the session in the worktree: no edits, commits or build targets there.
- Each worktree installs its own environment (`.venv`, `node_modules`, ...); the build targets run from that folder.
- A gitignored secret is a symlink to the main checkout's file, so the box holds one copy. Never printed.
- Large ignored output the worktree needs is copied, not hard-linked: a write in place through a hard link changes the main checkout's file.
- Anything with one instance on the box is shared and needs a word between the two sessions: ports, a GPU, an external store keyed by path.
  Which ones apply is the repo's doc.
- Conflicts land in shared index-like files; keep edits there small, cut a stale cross-file claim rather than rewriting it, catch the prose up on the default branch after the merge.
- Claude Code state that is per repository and not per folder, so both sessions share it: auto memory, and `.claude/settings.local.json`.
  The docs: "The `<project>` path is derived from the git repository, so all worktrees and subdirectories within the same repo share one auto memory directory", and a saved permission rule goes to `.claude/settings.local.json` "at the root of the git repository, resolved through worktrees to the main checkout".
  The transcripts of the past `house-renderer` worktree sessions confirm the memory half: they read and wrote `~/.claude/projects/-home-pmn-repos-house-renderer/memory/`, and their own project folders have no `memory/`.
- The closing runbook (below).

House-renderer's own, stays in its `docs/worktrees.md` and its script:

- `uv sync`, the `.r2.env` link, the two `bucket-pull`s around the PNG `rsync`, and why.
- No bucket sweep while a branch with pushed renders is unmerged.
- One GPU on g7, the second viewer on `VIEWER_PORT=8094`, `house/catalogue.yaml` and `house/README.md` as the conflict files.
- Its section "The Claude session in it" says a worktree session does not see the main checkout's memories. That is wrong for the Claude Code on the box (see above) and goes in the adoption.

## Decisions, proposed

- **Skill** `claude/claude__skills__worktrees.symlink/`: `SKILL.md` with the general rules above, how a repo adopts the script, the closing runbook, and `scripts/spin_worktree`, the template.
  Name `worktrees` for now; `git-worktrees` if it reads as too generic in the skill list.
- **The script is per repo**, `scripts/spin_worktree` in the repo, copied from the template and then owned by the repo.
  The template has a generic core, two constants at the top (`REPO_SHORT`, the short name for the zellij session, and nothing else unless a case turns up), and one marked function, `setup_repo`, which the repo fills in (installs, secret links, output copies).
  The core may be refreshed from the template; `setup_repo` and the constants are the repo's.
- **Bash**, `set -euo pipefail`, no dependency beyond git and zellij; checked with `shellcheck`. A repo whose setup is Python calls into it from `setup_repo`.
  (The box rule against chains is about the Bash tool's calls; inside a script file `set -e` holds.)
- **What the core does**, in order, failing before it writes anything when a check fails:
  1. Refuse unless run from the main checkout (`git rev-parse --git-dir` equals `--git-common-dir`), so a worktree never spawns a worktree.
  2. Work out the folder: `feat/NN_name` gives `../<repo>-NN`; any other branch needs the suffix as a second argument. Refuse if the folder exists.
  3. If the branch exists locally, check it out there; otherwise create it from the default branch (`origin/HEAD` if set, else `main`). Refuse if the branch is already checked out in another worktree, naming the folder.
  4. `git worktree add`.
  5. `setup_repo` with the main checkout and the new folder as arguments, run from the new folder.
  6. Write the worktree session's Claude settings (the read-only guard below) into the worktree's own git dir, `<main>/.git/worktrees/<name>/claude-settings.json`: outside the working tree, so nothing to ignore, and removed by `git worktree remove`.
  7. Launch the Claude session (below), then print the absolute path of the new folder as the only line on stdout and the zellij session name on stderr.
- **Launch**, a new zellij session running Claude in the worktree with Remote Control named after it:

  ```sh
  env $(env | grep -o '^CLAUDE[A-Z_]*' | sed 's/^/-u /') zellij attach --create-background wt-house-NN-name
  zellij --session wt-house-NN-name run --cwd ../house-renderer-NN --name claude -- \
    claude --name wt-house-NN-name --remote-control wt-house-NN-name --settings <git-dir>/claude-settings.json
  ```

  `--remote-control <name>` sets the title in the web UI; `--name` sets the name other local sessions see in their peer list, which otherwise is taken from the folder (`<repo>-NN-<n>`). The user's own sessions are started with `--name`.
  The probe confirmed the web UI title: Claude's Remote Control entry for the probe session stores a title hash equal to `sha256` of the name passed.

  Session and Remote Control name `wt-<REPO_SHORT>-<NN>-<name>`, `<name>` being the branch's part after `NN_`; a non-feat branch gives `wt-<REPO_SHORT>-<suffix>`.
  The script runs it as its last step (Q6); the user only opens the session in the web UI.
  - **The `CLAUDE*` variables are stripped when the zellij server starts.** The server keeps the environment it was started with and hands it to every pane, so launched from a Claude session the new Claude inherits that session's ID, Remote Control bridge ID, messaging socket and `CLAUDE_CODE_CHILD_SESSION=1`, and shows a transcript-saving warning. Stripping on `run` alone is too late.
  - **The name is cut to fit.** zellij refuses a session name whose socket path passes the Unix limit: on g7, under `/run/user/1000/zellij/contract_version_1/`, 66 characters work and 67 do not. The script cuts `<name>` so the whole stays within 64 and says so on stderr.
  - **Trust is not a problem for a repo already trusted.** Claude records the trust answer on the main checkout's path, so a worktree of a trusted repo starts without the question. A repo never opened in Claude asks it in the pane, and the user answers it once, from the web UI or with `zellij attach`.
  - **Closing the zellij session ends Claude a few seconds later**, not at once; `kill-session` then `delete-session` is enough, nothing to kill by hand.
- **Read-only main checkout, partly enforced.** The settings file from step 6 holds `permissions.deny` rules `Edit(//<main>/**)` and `Write(//<main>/**)`.
  Changed at execution: `Edit(//<main>/**)` alone, since the docs say "`Edit` rules apply to all built-in tools that edit files"; the guard test below shows it stopping both the Edit tool and a Bash redirect.
  The docs: "Deny rules block in every mode, including `bypassPermissions`", and Edit deny rules cover the built-in file tools, the file commands Claude Code recognises in Bash (`sed`, `tee`, ...) and redirection targets.
  It is passed with `--settings` on the worktree session only, since a rule in `.claude/settings.local.json` would reach the main checkout's session too.
  Reads stay allowed; the PNG copy and `git` need them.
  The ceiling: the docs say these rules do not reach "arbitrary subprocesses that read or write files indirectly", so `cd <main>; make ...`, `git -C <main> commit` and a Python script writing there are not caught.
  The upgrade path, if the guard turns out to matter: a PreToolUse hook that refuses a Bash call whose working directory or `git -C` target resolves into the main checkout, or the sandbox's filesystem write list, which the docs give as the OS-level enforcement. Neither is built now; the user asked whether it can be enforced, not for it to be.
- **The hand-off prompt**, the skill's last section. After the script has run and the session is launched, the original session shows in chat, in one fenced code block ready to copy into the new session:
  1. The situation: this session runs in a worktree, its folder and branch; the main checkout's path and branch, which are read-only to it (no edits, commits or build targets there, edits denied by its settings); what the two share (memory and local settings, plus the shared resources the repo's worktree doc lists); the repo's worktree doc to read first; closing goes by the skill's runbook and is started from the main checkout's session.
  2. The task: the details the user gave in the message that asked for the worktree, kept in their words, with the plan folder to read when there is one.

  Draft shape, for `SKILL.md`:

  ````md
  ```text
  This session runs in a git worktree: <folder>, on <branch>.
  The main checkout is <main folder>, on <main branch>. It is read-only to this session:
  no edits, commits or build targets there; edits to it are denied by this session's settings.
  Shared with the main checkout's session: auto memory, .claude/settings.local.json,
  and what <repo worktree doc> lists. Read that doc first.
  Closing the worktree follows the worktrees skill's runbook and is started from the main checkout.

  The task:
  <the user's request, in their words>
  ```
  ````

  Below the block, the original session offers to send it to the new session with `SendMessage`, addressed by the `wt-...` name.
  It sends only on the user's yes, and sends the block as the user left it; a tweaked version pasted back replaces the draft.
  If the user would rather paste it, nothing is sent.
  The probe confirmed delivery both ways: a test message sent from the original session reached the probe session, and its reply came back.
- **Memory needs nothing.** Shared already, per the docs and the transcripts above.
- **No numbering logic in the script.** Picking a free `NN` is `tracked-development`'s `plans.py branches`; the skill points there.
- **No closing script.** The skill carries the closing runbook:
  1. In the worktree: merge the default branch into the feature branch, then the repo's checks.
  2. In the main checkout, on the default branch: `git merge --no-ff feat/NN_name`, then the checks.
  3. Push the default branch from the box that holds the GitHub key.
  4. The repo's own after-merge steps (for `house-renderer`, the bucket sweep), from its doc.
  5. Bring the prose deferred in the branch up to date on the default branch.
  6. End the Claude session in the worktree, and its zellij session: `zellij kill-session wt-...`, then `zellij delete-session wt-...`.
  7. In the main checkout: `git worktree remove ../<repo>-NN`, then `git branch -d feat/NN_name`.

  `remove` refuses modified or untracked files, `branch -d` refuses an unmerged branch, so the order cannot lose a commit.
  The worktree session's transcripts under `~/.claude/projects/` are kept: old sessions are mined for information, and closing never deletes them.

## Steps

1. This note, and the user's answers to the questions below.
2. `shellcheck` installed per `~/repos/plans/2026-10-30_00_install_shellcheck.md`. Done 2026-10-30, 0.11.0.
3. Write `claude/claude__skills__worktrees.symlink/SKILL.md` and `scripts/spin_worktree` (the template, `setup_repo` a no-op with a comment saying what goes there).
4. Test the core in a throwaway repo under the job's `tmp/`: a `feat/NN_name` branch, a non-feat branch with and without a suffix, an existing folder, an existing branch, a branch already checked out elsewhere, run from inside a worktree. `shellcheck` and `bash -n` on the file.
5. Launch from the template on the throwaway worktree, which the Q6 probe has already shown works by hand.
6. Symlink the skill into `~/.claude/skills/worktrees` by hand, the same result as `uv run install/install.py`, as plan 03 did.
7. Commit in dotfiles, when the user says so.
8. Adoption in `house-renderer`:
   1. Fast-forward `main` to `feat/81_impianti_rooms` (`main` is an ancestor, one commit behind). The main checkout stays on `feat/81_impianti_rooms` with its uncommitted work untouched.
   2. Spin `feat/87_spin_worktree` from `main` with the skill's template run from the main checkout, `setup_repo` empty, and the doc's hand steps run once in the new folder. That is the last time they are run by hand.
   3. In that worktree: `scripts/spin_worktree` with `REPO_SHORT=house` and `setup_repo` holding `uv sync`, the `.r2.env` link, the bucket pulls and the PNG copy; `docs/worktrees.md` cut to the house-specific rules and a pointer to the skill, the opening section the one command, the memory sentence corrected; `make check`.
   4. Tested by spinning a second real worktree with it, which writes a folder and a branch and runs two `bucket-pull`s: a deep probe, asked for separately.

## Rollback

- Remove `~/.claude/skills/worktrees` and revert the dotfiles commit.
- In a repo that adopted it, revert the commit adding `scripts/spin_worktree`; worktrees already made by it are ordinary worktrees and close by the runbook.
- `shellcheck`: the rollback line in its note.

## Execution log

- 2026-10-30 : step 3. `SKILL.md` and `scripts/spin_worktree` written. The template sets `set -Eeuo pipefail`: without `-E` the ERR trap does not fire inside `setup_repo`, found by the failing-setup test.
- 2026-10-30 : step 4. Eleven scenarios against a throwaway repo with zellij stubbed, all as expected: new and existing feat branch, branch held by another worktree, existing folder, non-feat branch with and without a suffix, existing zellij session, long name cut to 64, no arguments, run from a subfolder, run from a worktree. No `CLAUDE*` variable reached `zellij attach`. A failing `setup_repo` stops before the launch and prints the remove command. `bash -n` and `shellcheck` clean.
- 2026-10-30 : step 5. A real launch on the throwaway: the shell pane opens in the worktree, the Claude pane has no `CLAUDE*` variable and Remote Control on, the peer list shows `wt-repo-70-guard_check` (so `--name` works). The trust question showed, as expected for a repo never opened. The guard: asked by message to try, that session was denied an Edit-tool edit and a Bash `>>` on the main checkout's file and allowed one in its own folder; the files on disk agree.
- 2026-10-30 : step 6. `~/.claude/skills/worktrees` linked; the skill shows in the skill list.
- 2026-10-30 : step 8.1. `main` fast-forwarded to `feat/81_impianti_rooms` (`git fetch . feat/81_impianti_rooms:main`); the main checkout stays on `feat/81_impianti_rooms` with its uncommitted edit.
- 2026-10-30 : step 8.2. `feat/87_spin_worktree` spun with the template (`REPO_SHORT=house`, empty setup) into `../house-renderer-87`; Claude started there with no trust question. The doc's hand steps run once: both `bucket-pull`s downloaded nothing, the copy brought the PNGs across.
- 2026-10-30 : step 8.3. In the worktree: `scripts/spin_worktree` with house-renderer's `setup_repo`, core identical to the template; `docs/worktrees.md` cut to the house-specific rules, the wrong memory section gone. `shellcheck` clean, `make check` passed (750 tests). Not committed.
- 2026-10-30 : renamed at the user's word. The skill `worktrees` is now `sibling-worktree` (`claude/claude__skills__sibling-worktree.symlink/`, linked as `~/.claude/skills/sibling-worktree`). The original checkout is called the main worktree, the added one a linked worktree, as the git-worktree manual names them; "main checkout" in this note is the same thing. Template and house-renderer copy re-checked: `shellcheck` clean, cores identical, the eleven scenarios pass, `make check` passed.

## Open questions

- **Q1. A closing script too?** Answered 2026-10-30: no, a runbook of steps in order. Folded in above.
- **Q2. The `cd`.** Answered 2026-10-30: a turn of phrase. Superseded by the launch, which starts the new session in the folder; no shell function.
- **Q3. Which branch does the house-renderer adoption go on?** Answered 2026-10-30: fast-forward `main` to `feat/81_impianti_rooms`, spin the new branch off `main`. Step 8.
- **Q4. Memory across the two folders.** Answered 2026-10-30: wanted if trivial. It is already shared, per the docs and the past transcripts; nothing to build.
- **Q5. `shellcheck`.** Answered 2026-10-30: install it. Note at `~/repos/plans/2026-10-30_00_install_shellcheck.md`.
- **Q6. Can this session start the new one, or does the user paste the command?** Answered 2026-10-30 by the probe: the session can start it, with the `CLAUDE*` variables stripped. Findings folded into "Launch" above. The question as asked:
  a zellij server started from Claude's Bash tool inherits that session's environment (`CLAUDECODE` and the other `CLAUDE_*` variables), and the inner `claude` may refuse to start or misbehave, so the command may need `env -u` for them;
  a folder Claude has not seen asks the trust question on start, which may hold the session in the pane before Remote Control connects, so the user may have to `zellij attach` once to answer it;
  and a long `wt-...` name may hit zellij's session-name limit, unknown.
  The probe: launch on the throwaway worktree from step 4, check `zellij list-sessions` and the web UI, then kill and delete the zellij session. It writes a zellij session, a Remote Control session, a trust entry in `~/.claude.json` and a project folder under `~/.claude/projects/` for the throwaway path, and takes a few minutes. Asked for before it runs.
  If any of the three fails and cannot be worked around, the script prints the command and the user pastes it.
- **Q7. Which number for `feat/NN_spin_worktree`?** Answered 2026-10-30: 87, `feat/87_spin_worktree`.
- **Q8. Send the hand-off prompt instead of showing it?** The probe session appeared in the original session's `ListAgents` peer list, so `SendMessage` could deliver the prompt directly and the user would not paste it. Proposed: the copyable block, as asked; sending is a later change if pasting gets tedious.
  Answered 2026-10-30: both. The block stays so the user can tweak it, and the session offers to send it once it looks right. Folded into "The hand-off prompt".
