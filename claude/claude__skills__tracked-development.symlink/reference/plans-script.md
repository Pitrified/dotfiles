# plans.py: listing and checking the plan folders

## Contents

- Two copies, and which one to run
- Commands
- Workflows: what to work on next, spinning off, a number used twice, before committing, finishing
- Adopting the script in a repo
- Keeping a repo's copy in step

The frontmatter schema, the status enum and every rule `check` enforces are in
[frontmatter.md](frontmatter.md). Read that file when writing or fixing a plan file; this one is the
workflows.

## Two copies, and which one to run

The canonical copy is `scripts/plans.py` in this skill's folder, installed at
`~/.claude/skills/tracked-development/scripts/plans.py`. It is one file, standard library only.

A repo that uses it as a gate carries its own copy at `scripts/plans.py`, because CI has no dotfiles
checkout. When the repo has one, run the repo's copy: it is what the gate runs, so its answers match the
gate's. Without one, run the skill's copy against the repo with `--root`.

`plans.py --version` prints which version a copy is.

## Commands

```bash
cd "$(git rev-parse --show-toplevel)"
python3 scripts/plans.py list                      # every folder, by priority
python3 scripts/plans.py list --status "in progress"
python3 scripts/plans.py list --index 15           # or 09-12: what those folders contain
python3 scripts/plans.py list --out /tmp/roadmap.md   # or .html, to attach in chat
python3 scripts/plans.py check                     # mechanical faults, file and line
python3 scripts/plans.py check --citations         # also: nothing outside plans/ cites a plan
python3 scripts/plans.py branches                  # folder numbers across every branch
python3 scripts/plans.py rename 21_old_name 22     # renumber, and fix sibling links
python3 scripts/plans.py --version
```

`--root <dir>` points it at a plans directory anywhere; without it the root is
`$(git rev-parse --show-toplevel)/plans`.

## Workflows

### What should I work on next

`list` sorts by priority descending, then by number. Priority is the only ordering: every folder is
born at `priority: 0`, a more important one is bumped by one, and a folder going to `done` goes back to
0 so a finished feature never sits at the top. Read the `status` and `phases` columns before
recommending anything: a folder at `in progress` with `3/5` is a better answer than a `draft` at the
same priority.

Read the `needs` column too, and do not recommend a row marked `*` or `?`: the first is waiting on another
feature, the second on a merge. A `?` on a folder that is already `in progress` is the one to raise
unprompted, because that merge is what the current work is waiting for.

There is no roadmap document. This output is it.

### Spinning off a new folder

1. `python3 scripts/plans.py branches`. It reads refs, not the working tree, because a number is
   claimed the moment someone creates the folder and an unmerged branch is invisible otherwise.
2. **Ask the person which number to use**, telling them which are taken and on which refs. Do not take
   `max + 1` silently: two people picking the same free slot on their own branches reproduce the
   collision one number along.
3. Create `plans/NN_name/00_start.md` with full frontmatter (`status: draft`, `priority: 0`, a
   `description` block) and the note of where the idea came from. A draft needs no `tracking.md` until
   it is picked up.
4. Work on it in a branch named after it, `feat/<NN_name>`, cut from the default branch; its first
   commit is the new `00_start.md`. Name, do not link, a folder that is on another branch.

### A number is used twice

`branches` prints `COLLISION` and the refs. Ask the person for the new number, then
`rename <folder> <NN>`. It refuses while anything outside `plans/` cites a plan folder, since renaming
would otherwise mean editing code to keep a diary reference alive. Afterwards run the repo's gates and
commit: `branches` reads refs, so it keeps reporting the collision until the rename is committed.

### Before committing a plan change

Where `check` is one of the repo's gates, it runs in the pre-commit hook and there is normally nothing
to do. Run it directly after editing several plan files at once, and read its output as a list of files
to fix rather than as advice: every rule is mechanical.

### Finishing a folder

Set the phase to `done` in both its frontmatter and the `tracking.md` row, append a dated line to the
log saying what was actually done, and when the last phase closes set the folder's `00_start.md` to
`done` and its `priority` back to `0`. `check` catches all four if one is forgotten.

Then stop. Do not merge the branch as the closing act: merging is a person's decision.

## Adopting the script in a repo

A repo without `scripts/plans.py` has not adopted it. Offer to adopt rather than writing a one-off
script; do it only when the person agrees, since it adds a gate.

1. Copy the skill's `scripts/plans.py` into the repo's `scripts/`.
2. Run `python3 scripts/plans.py check --citations` and show the findings. A repo whose `plans/` predates
   the convention usually needs its folders normalised first: frontmatter on every `00_start.md`, the
   status enum, a `tracking.md` table that agrees with the files. That is a feature folder of its own,
   not a side effect of adoption.
3. Once `check` passes, add it to the repo's gate command, and to its CI where it has one.
4. Add the skew line below to the repo's local gate script.

## Keeping a repo's copy in step

Each repo's copy is vendored and drifts. No one change reaches every repo that uses the skill, so each
repo checks itself, and reconciliation flows one way: **from the skill's copy into the repo**. A repo
never pushes its copy back.

When running the script in a repo, compare the two copies first:

```bash
cmp -s ~/.claude/skills/tracked-development/scripts/plans.py scripts/plans.py \
  || { python3 scripts/plans.py --version; python3 ~/.claude/skills/tracked-development/scripts/plans.py --version; }
```

A difference is reported to the person with both versions. Reconciling is copying the skill's file over
the repo's, running the repo's gates, and committing that as its own change.

The repo's local gate script carries the same comparison, as a line that prints and never fails, and is
silent where no skill copy is installed, which includes CI:

```bash
canon="$HOME/.claude/skills/tracked-development/scripts/plans.py"
if [[ -f "$canon" ]] && ! cmp -s "$canon" scripts/plans.py; then
  echo "note: scripts/plans.py ($(python3 scripts/plans.py --version)) differs from" \
    "the tracked-development copy ($(python3 "$canon" --version)); copy it from $canon"
fi
```

A change to what the script does is made in the skill's copy, in dotfiles, with `VERSION` bumped. Each
repo then picks it up the next time its gate reports the difference.
