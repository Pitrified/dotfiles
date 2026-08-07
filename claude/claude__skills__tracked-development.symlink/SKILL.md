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
  add/remove passes.
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

```
<plan-folder>/
  00_start.md            # bootstrap: the idea, analysis, decisions, open questions
  tracking.md            # the index: phases table + append-only log (read this first)
  01_feat_name.md        # sub-plan for phase 1
  02_feat_name.md        # sub-plan for phase 2
  NN_feat_name.md        # ...one per phase
```

Naming:

- All files use `snake_case`.
- `00_start.md` sorts first, ahead of any phase (it is prose, not a phase).
- Phase sub-plans use `NN_feat_name.md` with a zero-padded number and
  `snake_case` name, so they sort in execution order.
- A folder holds roughly five sub-plans. Past that, the work might be two features, assess.

## The three file roles

### `00_start.md` - bootstrap / brainstorm

The origin document. Free-form prose, not a checklist. It captures:

- the original note / idea in the user's own framing,
- the analysis (current state, inventory, the proposed approach),
- decisions made and **why** (record rejected alternatives - they explain the
  shape of everything downstream),
- open questions, following the convention below.

This file is append-and-refine, not status-tracked. It is the reasoning record
the phases were derived from.

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

### `NN_feat_name.md` - sub-plans

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
3. **Write a sub-plan per phase** (`NN_feat_name.md`) with `status:` frontmatter.
   It is fine to detail near-term phases fully and leave later ones as `draft`.
4. **Execute a phase.** Set its status to `in progress` in both the frontmatter
   and the table. **Review the plan before writing any code** (see "Reviewing a
   plan"), correcting it where it turns out to be wrong. Then do the work.
5. **Close a phase.** When "Done when" is verified, review the phase once more,
   set status to `done` in both places, and **append a dated line to the Log**
   describing what was actually done (including experiments tried, even ones
   that failed - they are findings).
6. **Recover a session.** On a new session or after `/clear`, read `tracking.md`
   first, then `00_start.md`, then the sub-plan of the first non-`done` phase.
   The files, not the prior context, are the source of truth.

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
