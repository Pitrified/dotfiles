---
name: tracked-development
description: >-
  Plan and execute multi-phase work using a persistent folder of markdown files
  that survives context loss: a bootstrap/brainstorm file, a tracking index with
  a phases table and append-only log, and numbered sub-plans with status
  frontmatter. Use whenever work spans several phases or sessions, or when the
  user asks for "tracked development", a "phased plan", a "tracking file", a
  "plan folder", or to keep a long effort organized across context windows.
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
batch continues where the previous one stopped. Each question ships with an
`ANS: ...` placeholder line so the user can answer by editing the file directly:

```markdown
- Q1: <the question, with enough context to answer it cold>
  ANS: ...
- Q2: <question>
  ANS: ...
```

The loop: the user fills in `ANS:` lines (in the file or in chat), then the
answers get **folded in** - update the decisions, phases, and sub-plans that the
answer affects. Do not delete the answered questions: the Q + ANS pairs stay in
the file as the decision record (ADR); they explain why the plan has its shape.
Only fold in, never rewrite an existing answer.

New questions that surface while folding in (or later in the work) are appended
as a new batch *after* the answered ones, continuing the numbering (`Q5`,
`Q6`, ...), each with a fresh `ANS: ...` placeholder. Whenever iterating on the
plans, reread the md files and incorporate any user edits found there.

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
```

## Spin-off features

Work that surfaces mid-effort but does not belong to the current feature's
scope (a side-finding, a "while we are at it", a deferred capability) becomes a
**new sibling feature folder**, not an extra phase. Create the next-numbered
folder with a minimal `00_start.md` at `status: draft` frontmatter: a short
note on what it is and where it came from, linking back to the originating
feature's `00_start.md` for reference.

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

1. **Bootstrap.** Create the folder and `00_start.md`. Capture the idea,
   analysis, decisions, and open questions. Surface real open questions to the
   user rather than guessing, as numbered `Qn` items with `ANS: ...`
   placeholders; fold answers in per the open questions convention.
2. **Derive phases.** Break the work into sequential, bounded phases - each with
   clear goals, an out-of-scope boundary, and a verifiable "Done when". Prefer
   the cheapest/lowest-risk phase first. Write `tracking.md` with the phases
   table (all `planned`/`draft`) and an empty Log.
3. **Write a sub-plan per phase** (`NN_feat_name.md`) with `status:` frontmatter.
   It is fine to detail near-term phases fully and leave later ones as `draft`.
4. **Execute a phase.** Set its status to `in progress` in both the frontmatter
   and the table. Do the work.
5. **Close a phase.** When "Done when" is verified, set status to `done` in both
   places, and **append a dated line to the Log** describing what was actually
   done (including experiments tried, even ones that failed - they are findings).
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

## Keeping it honest

- The table status, the sub-plan frontmatter, and reality must agree. If they
  drift, fix the files before continuing.
- Update the files as part of the work, not as an afterthought - they are how
  the next session (or the user) understands where things stand.
- These are living documents. Refine `00_start.md` and split or merge phases
  when reality diverges from the original plan; record the change in the Log.
