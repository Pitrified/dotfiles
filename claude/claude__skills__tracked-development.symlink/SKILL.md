---
name: tracked-development
description: >-
  Plan and execute multi-phase work using a persistent folder of markdown files
  that survives context loss: a bootstrap/brainstorm file, a tracking index with
  a phases table and append-only log, and numbered sub-plans with status
  frontmatter. Use whenever work spans several phases or sessions, or when the
  user asks for "tracked development", a "phased plan", a "tracking file", a
  "plan folder", or to keep a long effort organized across context windows.
  Also covers reviewing a plan before executing it: verifying its claims against
  the system, checking consistency, bloat, pitfalls and anti-patterns, and
  add/remove passes. Ships scripts/plans.py, which lists and checks the numbered
  plans/ folders of a repo: use it when asked what is in progress or what to work
  on next, when spinning off or finishing a folder, when a plan file fails a
  gate, or when two branches have claimed the same folder number.
---

# Tracked development

A file-based pattern for planning and running work that is too big for one
session. Instead of holding the plan in the context window (where it is lost on
`/clear` or compaction), the plan lives on disk as a small folder of markdown
files. They are the durable working memory: re-readable at the start of any
session, editable by the user, and a faithful record of what was decided and
done.

Use this when work spans **multiple phases or multiple sessions**, has decisions
worth recording, or the user explicitly asks for tracked development. For a
single small change that finishes in one session, do not set this up - it is
overhead.

## Folder layout

One folder per initiative. Each file is one concern.
In a repo, the initiatives are numbered folders under `plans/`, one per feature:
`plans/NN_name/`. The number is identity and creation order, not priority.

```
plans/NN_name/
  00_start.md            # bootstrap: the idea, analysis, decisions, open questions
  tracking.md            # the index: phases table + append-only log (read this first)
  01_feat_name.md        # sub-plan for phase 1
  02_feat_name.md        # sub-plan for phase 2
  02.1_feat_name.md      # side-document of phase 2: research or a capture, no status
  NN_feat_name.md        # ...one per phase
```

Naming:

- All files use `snake_case`.
- `00_start.md` sorts first, ahead of any phase (it is prose, not a phase).
- Phase sub-plans are `NN_<name>.md` with a zero-padded number, so they sort in
  execution order. `feat_name` is a placeholder: `03_checker_and_gate.md` is as
  valid as `03_feat_checker.md`, and no tool reads the word `feat`.
- `NN.M_<name>.md` is a side-document of phase NN: a research note, an analysis,
  a capture. It carries no status and gets no row in the phases table.
- Numbers are unique within a folder and need not be contiguous.
- A folder holds roughly five sub-plans. Past that, the work might be two features, assess.

## The three file roles

### `00_start.md` - bootstrap / brainstorm

The origin document. Free-form prose, not a checklist. It captures:

- the original note / idea in the user's own framing,
- the analysis (current state, inventory, the proposed approach),
- decisions made and **why** (record rejected alternatives - they explain the
  shape of everything downstream),
- open questions, following the convention below.

This file is append-and-refine: the reasoning record the phases were derived
from. It is also the folder's identity card, so it opens with frontmatter that
the script reads:

```yaml
---
status: draft
priority: 0
description: |
  Two or three lines saying what this feature is and why, readable by someone
  who has not opened the folder. It is what a listing shows.
depends_on: [20_repo_split]
comment: |
  anything worth keeping that has no field
---
```

`status` is the folder's status, `priority` orders the listing (born at 0,
bumped by one when it matters more, back to 0 when `done`). `depends_on` and
`comment` are optional: the folders that must be done first, and freeform text
nothing parses. The full schema and
every rule the checker enforces are in
[reference/frontmatter.md](reference/frontmatter.md).

#### Open questions convention

Questions are numbered `Q1`, `Q2`, ... and numbering never resets - a later
batch continues where the previous one stopped. Each question carries the
context needed to answer it cold, lettered options where there is a real choice,
a recommendation, and an empty `NEW_ANS:` slot for the user to type into:

```markdown
- Q1: <the question, with enough context to answer it cold>
  a. <option>
  b. <option>
  Recommended: a, because <the reason, in one line>.
  NEW_ANS:
- Q2: <question, where the answer is open rather than a choice>
  NEW_ANS:
```

The recommendation goes **above** the answer slot, so the cheapest possible
reply is a single letter and the reasoning is in front of the user at the moment
they decide. It stays in the file whether or not it was taken: a question where
the user overrode the recommendation then reads as a decision rather than as an
unexplained choice.

Two tags, and the difference is the point:

- `NEW_ANS:` is an answer the assistant has not processed yet.
- `ANS:` is an answer already folded into the plan.

The loop: the user fills in `NEW_ANS:` lines (in the file or in chat), then
`grep -n NEW_ANS` finds exactly the new batch - not the forty already settled -
and each one gets **folded in**, updating the decisions, phases, and sub-plans
it affects. As the last step of folding a batch in, demote its `NEW_ANS:` tags
to `ANS:`. That clears the grep for the next round. A start file mid-planning
holds a mix of both; a settled one holds only `ANS:`.

Do not delete the answered questions: the Q + ANS pairs stay in the file as the
decision record (ADR); they explain why the plan has its shape. Only fold in,
never rewrite an existing answer.

New questions that surface while folding in (or later in the work) are appended
as a new batch *after* the answered ones, continuing the numbering (`Q5`,
`Q6`, ...), each with a fresh `NEW_ANS:` slot. Whenever iterating on the plans,
reread the md files and incorporate any user edits found there.

Review findings use this same mechanism rather than one of their own - see
"Reviewing a plan" below.

**Question numbers are local to the file that raised them.** A bare `(Q4)` in
any other file is a broken reference; name the file, as
`13_key_distribution/00_start.md` Q4.

**Reopening a decision from a later folder.** Anything can be reopened on new
evidence, including an answer in a folder that is already `done`. The later
folder raises and answers the question in its own `00_start.md`. In the earlier
file, the old answer stays as written and gets a note under it naming the file
and question that reopened it and what changed; its `tracking.md` gets a log
line saying which key decision is superseded. The done folder stays `done`:
reopening a decision does not reopen its phases.

### `tracking.md` - the index

The first file to read in any session - the map of the whole effort. It holds:

1. A one-paragraph summary and a link to `00_start.md`.
2. Any cross-cutting decisions that span phases (short bullets, with phase notes
   as they accrue).
3. A **phases table**: number, phase, link to the sub-plan, status.
4. A **Log** section: append-only history of what was actually done.

Template:

```markdown
# implementation tracking

<one paragraph: what this effort is>. Analysis and decisions in
[`00_start.md`](00_start.md).

## Key decisions

- <decision that spans phases, with the why>

## Phases

| #  | Phase                          | Plan                                  | Status      |
| -- | ------------------------------ | ------------------------------------- | ----------- |
| 1  | <short phase name>             | [`01_feat_name.md`](01_feat_name.md)  | done        |
| 2  | <short phase name>             | [`02_feat_name.md`](02_feat_name.md)  | in progress |
| 3  | <short phase name>             | [`03_feat_name.md`](03_feat_name.md)  | planned     |

Status values: draft / planned / in progress / done / superseded / discarded.

## Log

Append-only. Newest at the bottom. One bullet point per meaningful step,
can be longer than a one-liner if relevant information is needed.

- 2026-06-15 : bootstrapped the plan folder; drafted phases 1-3 in tracking.md
- 2026-06-15 : phase 1 - froze the public API, defined the content layout; tests green
```

### `NN_<name>.md` - sub-plans

One per phase. Each starts with **frontmatter** carrying its status, then the
plan for that phase. The status in the frontmatter and in the `tracking.md`
table must agree.

Template:

```markdown
---
status: planned
---

# Phase N - <phase title>

## Overview

<what this phase does and why it is sequenced here. Link context.>
Context: [`00_start.md`](00_start.md)[, depends on [`0M_...md`](0M_....md)].

## Goals

1. <concrete goal>

## Plan

- <step>

## Out of scope

- <explicitly deferred to a later phase>

## Done when

- <verifiable exit criterion>
- <e.g. the project's verification suite passes>

## What the implementation found

<what only appeared once the code ran; absent until then>
```

The last section is written after the phase runs, and only if there is
something to say: what the code showed that the plan could not. Everything
above it stays as written. A finding that needs fixing becomes a new step.

## Reviewing a plan

Review a phase without waiting to be asked, at three points: when its sub-plans
are written, as the first act of executing it, and when it looks finished. The
third run is where defects in what was just built show up, so run it even when
the phase passed its own tests.

Five questions:

- **claims** - the plan asserts things about the system. Pick the assertions
  that look shaky and would change the plan if they were wrong, and check those.
  Judgement, not an audit.
- **consistency** - do the goals, tables and steps agree with each other?
  do the plans contradict each other?
- **bloat** - what is structure for its own sake, or generality with no case?
- **pitfalls** - what could go wrong during execution that the plan does not mention?
- **anti-patterns** - a proxy standing in for the real check, a second
  implementation of something that already exists, a tool that measures
  something it is part of. general good coding practices.

Correct a wrong claim in the plan itself: these are living documents, and each
should keep stating what *will* be done. Split or merge phases when reality has
diverged further than an edit can cover. Anything that is not a correction is a
finding.

Log the review, including when it found nothing.

### Add/remove - when the plan feels finished

Propose exactly five things to add and three to remove, with a pro, a con and a
recommendation for each, in chat only, nothing written. An open invitation to
improve a plan only ever grows it; the quota to cut three forces a defence of
what is already there.

### What a review produces

Findings. Write each as a numbered `Qn` in the open questions of `00_start.md`,
with its recommendation and a `NEW_ANS:` slot, and let the normal fold-in loop
apply them, so agreeing to a finding and applying it stay separate steps.

## Work that surfaces mid-effort

Reviews and implementations both turn up work that is not the step at hand.
Where it goes depends on whether it is in scope.

**In scope: the next numbered step.** A real defect gets its own sub-plan.
Fixed in passing inside another step, it leaves no record that it existed.

**Out of scope: a sibling feature folder.** A side-finding, a "while we are at
it", a deferred capability - not an extra phase in this one. Create the
next-numbered folder with a minimal `00_start.md` at
`status: draft` frontmatter: a short note on what it is and where it came from,
linking back to the originating feature's `00_start.md` for reference.

Keep the scopes independent: the spin-off must be executable on its own later,
and the originating feature must not depend on it. The originating feature
notes the spin-off in its decisions (and tracking key decisions) with a link,
then stops mentioning it. A draft spin-off needs no `tracking.md` or phases
until it is actually picked up.

**Its number.** "Next-numbered" means next free across every branch, not in
this checkout: a number is claimed the moment any branch creates the folder.
Run `plans.py branches`, tell the person which numbers are taken and on which
refs, and ask which to use. Two branches that each take `max + 1` on their own
produce the collision one number along.

**Links across branches.** Each feature is worked on its own branch (below), so
a spin-off usually lives on a branch the originating folder is not on, and a
relative link to it is broken there. Link within a branch; across branches,
name the folder (`25_skill_to_dotfiles`, on `feat/25_skill_to_dotfiles`) and
turn the name into a link once both are on the same branch.

## Status values (frontmatter `status:`)

| Status        | Meaning                                                         |
| ------------- | -------------------------------------------------------------- |
| `draft`       | sketched, not yet agreed as the plan of record                 |
| `planned`     | agreed and sequenced, not started                              |
| `in progress` | actively being worked                                          |
| `done`        | goals met and "Done when" criteria verified                    |
| `superseded`  | replaced by a different plan (note which one and why)          |
| `discarded`   | abandoned, will not be done (keep the file; note why)          |

Keep `superseded` and `discarded` files in place - the record of a dropped path
is part of the history. Note the reason at the top of the body.

## Plans are a diary, docs are the as-is

`plans/` records how a project got where it is; the project's docs record what
it is now. A reader who needs to know why something is the way it is reads the
docs, not a diary entry from four features ago.

So nothing outside `plans/` points at a specific plan: no path to a plan folder
or file, no `Qn`/`Dn` id, in code, comments, scripts or docs. When one of those
needs to lean on a decision, the decision goes into the doc whose topic it is,
and the citation points there. A decision with no obvious home means a missing
doc, not an exception. `plans.py check --citations` enforces this.

Meta files that describe the convention (a repo's agent instructions, a docs
index) may describe the *shape*, such as `plans/<folder>/tracking.md`, but not
point at an instance of it.

## Branches and merging

A feature folder is worked on a branch named after it, `feat/<NN_name>`, so the
branch list sorts the way the plans do and a branch name answers what it is for
with a folder to read.

The merge is not part of finishing the feature. An effort ends with its last
phase closed: sub-plan and table at `done`, a dated log line, the folder's
`priority` back at 0. The branch then waits, because work found along the way
often belongs on it. Merging is a separate decision, taken by a person who
knows whether anything else is coming.

## How a plan is written

Plans keep the reasoning from being re-derived, not from being reopened.
Reopening on new evidence is the plan working: record what changed and leave
the previous answer visible rather than editing it away.

- Write each point at the strength it has. "for now", "until the spike
  reports", "unless X changes" are accurate about most choices and cost
  nothing. Keep "never" and "hard requirement" for the few things that are
  fixed. A line written as an absolute is read a month later as a deal breaker,
  and then something obvious does not get tried.
- Weight remarks by how they were made. An offhand comment is a signal, not an
  instruction. When one would become a constraint, mark it provisional or ask
  before promoting it.

## The script

`scripts/plans.py` in this skill's folder lists and checks the `plans/` tree of
a repo, standard library only. The workflows it serves (what to work on next,
spinning off, a number used twice, finishing a folder), how a repo adopts it,
and how its copies are kept in step are in
[reference/plans-script.md](reference/plans-script.md). Read that file before
running it.

## Workflow

When asked to start tracked work, or partway through work that has grown into
this shape:

1. **Bootstrap.** Create the folder and `00_start.md`. Capture the idea, the
   analysis and the decisions, and raise the real open questions rather than
   guessing, per the open questions convention above.
2. **Derive phases.** Break the work into sequential, bounded phases - each with
   clear goals, an out-of-scope boundary, and a verifiable "Done when". Prefer
   the cheapest/lowest-risk phase first. Write `tracking.md` with the phases
   table (all `planned`/`draft`) and an empty Log.
3. **Write a sub-plan per phase** (`NN_<name>.md`) with `status:` frontmatter.
   Set the folder's `00_start.md` to `in progress` when the first phase starts.
   It is fine to detail near-term phases fully and leave later ones as `draft`.
4. **Execute a phase.** Set its status to `in progress` in both the frontmatter
   and the table. **Review the plan before writing any code** (see "Reviewing a
   plan"), correcting it where it turns out to be wrong. Then do the work.
5. **Close a phase.** When "Done when" is verified, review the phase once more,
   set status to `done` in both places, and **append a dated line to the Log**
   describing what was actually done (including experiments tried, even ones
   that failed - they are findings). When the last phase closes, set the
   folder's `00_start.md` to `done` and its `priority` back to 0.
6. **Recover a session.** On a new session or after `/clear`, run
   `plans.py list` first where the repo has the script: it is the roadmap across
   folders, and there is no roadmap document. Then, for the folder being worked,
   read `tracking.md`, then `00_start.md`, then the sub-plan of the first
   non-`done` phase. The files, not the prior context, are the source of truth.

## Log conventions

- Append-only. Never rewrite or delete past entries; correct via a new entry.
- Newest at the bottom.
- One line per meaningful step: `- YYYY-MM-DD : <what was done; experiments,
  decisions, surprises>`.
- Use the real current date.
- Record what was *done and learned*, not what is *planned* (plans live in the
  sub-plans). A failed experiment is worth a line - it stops the next session
  repeating it.
- A review gets a line whether or not it found anything; otherwise a checked
  plan and an unchecked one look the same.

## Keeping it honest

- The table status, the sub-plan frontmatter, and reality must agree. If they
  drift, fix the files before continuing.
- Update the files as part of the work, not as an afterthought - they are how
  the next session (or the user) understands where things stand.
- After editing a plan mid-effort, re-read the plans sequenced after it. An
  upstream change can invalidate what comes downstream of it.
