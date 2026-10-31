---
name: sibling-worktree
description: >-
  Work a second branch in its own git worktree beside the main worktree, with
  its own Claude session: open it with the repo's scripts/spin_worktree (which
  creates the folder, runs the repo's setup and starts a Claude session there in
  its own zellij session with Remote Control), hand the task over with a prompt,
  and close it by the runbook. Use when the user asks for a worktree, to work a
  feature "in parallel", "in its own folder" or "in a second session", when a
  repo has no spin_worktree and one is wanted, or when closing or merging a
  worktree.
---

# Sibling worktree

A feature branch can be worked in its own folder beside the main worktree, `git worktree`, by its own Claude session, so two sessions run at once without switching branches under each other.
The folder is `../<repo>-NN` for the branch `feat/NN_name`.
The terms are git's: the original checkout is the main worktree, each added one a linked worktree. The main worktree is not the `main` branch; it can be on any branch.
Each repo opens one with its own `scripts/spin_worktree`, copied from this skill's `scripts/spin_worktree` and filled in with that repo's setup.

## Opening one

1. The branch: `feat/NN_name`, `NN` the lowest number no branch has claimed.
   A repo using `tracked-development` lists the claimed ones with `plans.py branches`; take the lowest free one without asking.
   Any other branch name works too, with the folder suffix as a second argument.
2. From the main worktree:

   ```sh
   scripts/spin_worktree feat/NN_name
   ```

   It refuses from inside a worktree, over an existing folder or zellij session, and for a branch already checked out elsewhere, before it writes anything.
   Otherwise it adds the worktree (on the branch if it exists, else a new branch from the local default branch), runs the repo's `setup_repo` in it, writes the worktree session's settings, and starts `claude` in a new background zellij session.
   The session is `wt-<REPO_SHORT>-<NN>-<name>`, under that name in the web UI and in the local peer list.
   The new folder is the only line on stdout.
3. The hand-off prompt, below.

A repo without `scripts/spin_worktree` has not adopted it: offer to, rather than running the steps by hand.

The session that ran the script stays in the main worktree and keeps its own work.

## The hand-off prompt

After the script has run, show in chat one fenced block for the user to copy into the new session, and to tweak:

```text
This session runs in a git worktree: <folder>, on <branch>.
The main worktree is <main folder>, on <main branch>. It is read-only to this session:
no edits, commits or build targets there; edits to it are denied by this session's settings.
Shared with the main worktree's session: auto memory, .claude/settings.local.json,
and what <repo worktree doc> lists. Read that doc first.
Closing the worktree follows the sibling-worktree skill's runbook and is started from the main worktree.

The task:
<the user's request, in their words>
```

The task part is the details the user gave in the message that asked for the worktree, kept in their words, with the plan folder to read when there is one.

Below the block, offer to send it with `SendMessage` to the session's `wt-...` name.
Send only on the user's yes, the block as they left it; a tweaked version they paste back replaces the draft.
If they would rather paste it, send nothing.

## While a linked worktree is open

- The main worktree is read-only to the worktree session: no edits, commits or build targets there.
- Each worktree has its own environment (`.venv`, `node_modules`, ...), and build targets run from its folder.
- A gitignored secret is a symlink to the main worktree's file, so the box holds one copy. Never print it.
- Ignored output the worktree needs is copied, not hard-linked: a write in place through a hard link changes the main worktree's file.
- Anything with one instance on the box is shared and needs a word between the two sessions: ports, a GPU, an external store keyed by path. The repo's worktree doc says which apply.
- Conflicts land in shared index-like files. Keep edits there small, cut a stale cross-file claim rather than rewriting it, and bring the prose up to date on the default branch after the merge.
- Claude Code keeps some state per repository, not per folder, so both sessions share it: auto memory, and `.claude/settings.local.json`, which is stored in the main worktree. A permission rule saved from either session applies to both.

## The read-only guard

The worktree session starts with `--settings <worktree git dir>/claude-settings.json`, which denies `Edit` on the main worktree's path.
Deny rules hold in every permission mode, including bypass, and an `Edit` rule covers the built-in file tools, the file commands Claude Code recognises in Bash (`sed`, `tee`, ...) and redirection targets.
It does not cover a process that writes on its own: `cd <main>; make ...`, `git -C <main> commit`, a script opening a file there.
Closing that gap would take a PreToolUse hook on the Bash command's working directory and `git -C` target, or the sandbox's filesystem write list; neither is built.
The rule is not in `.claude/settings.local.json` because that file reaches the main worktree's session too.

## The launch

What the script relies on, so a change to it does not undo one:

- The zellij server hands its own environment to every pane, so the `CLAUDE*` variables of the session running the script are dropped when the server starts. Kept, the new Claude takes that session's ID, Remote Control link and messaging socket, and stops saving its transcript.
- `--remote-control <name>` is the title in the web UI; `--name` is the name in the local peer list, which is otherwise taken from the folder.
- zellij refuses a session name whose socket path passes the Unix limit, so the name is cut to 64 characters.
- Claude records folder trust on the main worktree's path, so a worktree of a trusted repo starts without the question. A repo never opened in Claude asks it in the pane; the user answers it from the web UI or with `zellij attach`.

## Adopting the script in a repo

1. Copy `scripts/spin_worktree` from this skill's folder into the repo's `scripts/`.
2. Set `REPO_SHORT`, and fill `setup_repo` with the repo's setup: the environment install, the links to gitignored secrets, the copies of ignored output.
3. Write the repo's own worktree rules in its docs (`docs/worktrees.md` or wherever the repo keeps such pages): the shared resources, the conflict files, the steps after a merge. The general rules stay here.
4. Test it by spinning a real worktree. That writes a folder, a branch and a zellij session and runs the setup: ask first.

The part below `# ---- core` is this skill's and may be refreshed from it; the part above is the repo's.
To see whether a repo's core has drifted:

```sh
diff <(sed -n '/^# ---- core/,$p' ~/.claude/skills/sibling-worktree/scripts/spin_worktree) \
     <(sed -n '/^# ---- core/,$p' scripts/spin_worktree)
```

## Closing one

A runbook, in order:

1. In the worktree: merge the default branch into the feature branch, then the repo's checks.
2. In the main worktree, on the default branch: `git merge --no-ff feat/NN_name`, then the checks.
3. Push the default branch from the box that holds the GitHub key.
4. The repo's own after-merge steps, from its worktree doc.
5. Bring the prose deferred in the branch up to date on the default branch.
6. End the Claude session in the worktree, and its zellij session: `zellij kill-session wt-...`, then `zellij delete-session wt-...`. Claude exits a few seconds after the kill.
7. In the main worktree: `git worktree remove ../<repo>-NN`, then `git branch -d feat/NN_name`.

`git worktree remove` refuses modified or untracked files, and `git branch -d` refuses an unmerged branch, so the order cannot lose a commit.

The worktree session's transcripts under `~/.claude/projects/` are kept: old sessions are mined for information, and closing never deletes them.
