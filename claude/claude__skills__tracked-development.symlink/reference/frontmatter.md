# Plan file frontmatter and the rules a checker enforces

## Contents

- Frontmatter schema
- depends_on
- The status enum
- File naming
- What `check` reports
- What is deliberately not checked

## Frontmatter schema

`00_start.md`, one per feature folder, carries all three:

```yaml
---
status: in progress
priority: 0
depends_on: [20_repo_split]
description: |
  Two or three lines saying what this feature is and why, readable by someone who
  has not opened the folder. It is what a listing shows, one line per feature.
comment: anything worth keeping that the schema has no field for
---
```

`depends_on` and `comment` are both optional and both folder level. `comment` is freeform: nothing parses
it, nothing checks it, and it never appears in `list` output. It exists so that "this does not fit the
schema and I do not want to lose it" has somewhere to go other than a new key with rules attached.

`NN_name.md`, one per phase, carries `status` only. `description` is allowed and usually redundant,
since the file's own `## Overview` says it. `tracking.md` carries no frontmatter: the phase table holds
the statuses.

`priority` lives on `00_start.md` only. Phases inside a feature are already ordered, so a per-phase
priority would be a second ordering to keep in sync. Born at 0, bumped by one when a feature matters
more, back to 0 when the folder is `done`. The point is the diff: raising a priority is one reviewable
line, not a reshuffle of an index.

Other keys are ignored rather than rejected. Some older folders carry `depends_on` and `produces`.

## depends_on

Prerequisites, as an inline list of folder names, on a `00_start.md` only:

```yaml
depends_on: [20_repo_split]
```

**Folders, not phases.** The working unit is a whole feature, so a prerequisite is a folder being finished
rather than a phase inside one being reached. A phase file never carries this key; inside a feature, the
ordering is the numbering, and where that is worth recording it goes in `comment`.

**A prerequisite may be numbered higher.** A number is creation order; `depends_on` is execution order,
and they disagree whenever a prerequisite is discovered mid-effort: `20_logging` gets picked up and spins
off `21_backend_setup`, so the order is 21 then 20. Renumbering to keep the numbers sorted would rewrite
every inbound link and the branch name for an aesthetic. This is why cycles are checked: the numbers no
longer rule them out.

`list` shows prerequisites in a `needs` column with two markers, because they call for different actions:

| Shown | Means | What to do |
| ----- | ----- | ---------- |
| `20` | prerequisite is `done` | nothing, the row is startable |
| `20*` | prerequisite exists and is not `done` | that work comes first |
| `20?` | prerequisite is not in this tree | it is on another branch, so a merge comes first |

## The status enum

| Status | Meaning |
| ------ | ------- |
| `draft` | sketched, not yet agreed as the plan of record |
| `planned` | agreed and sequenced, not started |
| `in progress` | actively being worked |
| `done` | goals met and the "Done when" criteria verified |
| `superseded` | replaced by a different plan; name which one in the body |
| `discarded` | abandoned; keep the file and note why |

Nothing else. `complete`, `not-started` and `planned (deferred)` are what this enum exists to stop: a
status column with two facts in one cell is a status nobody can filter on.

## File naming

| Name | Role |
| ---- | ---- |
| `00_start.md` | the origin document: idea, analysis, decisions, questions. A folder without one is not a feature and is skipped entirely |
| `tracking.md` | the index: phase table plus an append-only log |
| `NN_name.md` | one phase. The `feat` in `NN_feat_name.md` is part of the placeholder, not a required word |
| `NN.M_name.md` | a side-document of phase NN: research, an analysis, a capture. Carries no status |

Numbers are unique within a folder and need not be contiguous.

## What `check` reports

Each finding names the file, and the line where a line applies.

- frontmatter missing, or opening with `---` and never closing
- `status`, `priority` or `description` missing from a `00_start.md`; `status` missing from a phase file
- a status, in a file or in a table row, that is not in the enum
- a priority that is not a non-negative integer, or a `done` folder not back at 0
- a phase file missing from its `tracking.md` table, or a table row naming a file that does not exist
- a table status that disagrees with the file's own frontmatter
- a duplicate phase number, or a file name that is not one of the four above
- `NEW_ANS:` left in a folder whose phases are all `done`
- with `--citations`: a reference to a specific plan folder from outside `plans/`

Over `depends_on`, as findings:

- a name that is not a folder anywhere, with the closest existing folder suggested
- a cycle, reported as the path found
- a dependent that is `in progress` or `done` while a prerequisite is not `done`
- a priority above a prerequisite's, so the listing offers work that cannot be started
- a `discarded` or `superseded` folder that something still depends on, reported from the discarded
  folder's side and naming every dependent. It cascades: repointing a dependent may mean discarding it
  too, which fails again for whatever depended on that, until the tree is consistent

And as a **warning**, which prints and does not fail: a prerequisite that is not in this tree but exists on
another ref. Someone else may be implementing it, and merging their plans in so that a name resolves is
overkill. The warning names the refs; when the dependent is itself `in progress` it says the merge is what
that work is waiting for, and an assistant reading it should raise that rather than note it.

## What is deliberately not checked

- **Relative links**, which have their own gate. Two gates checking links is one too many.
- **Anything requiring judgement**: whether a description is good, whether a phase is really done,
  whether the phases are the right ones. A checker that guessed at those would be ignored.
- **What a `superseded` folder was replaced by.** The status says it was; the body says what by. There is
  no `superseded_by` key, because this happens about once a year and the cascade message already names what
  is broken, so working out what to repoint at is a judgement made with the folder open.
- **Nothing is edited.** `check` and `list` are read-only, and there is no `--fix`: a gate that can edit
  the files it judges cannot be trusted about them. `rename` is the only writer, and it writes only when
  a person has given it a number.
