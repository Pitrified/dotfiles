# 00 - feat: anti-superficiality rules in main CLAUDE.md

## Goal

Add a small, high-signal set of rules to the main CLAUDE.md dotfile
(`claude/claude__CLAUDE.md.symlink` -> `~/.claude/CLAUDE.md`) that push Claude
toward depth over speed: read before acting, fix root causes not symptoms,
verify before claiming done, and surface uncertainty instead of guessing.
These are the behaviors that, when skipped, produce superficial changes and bugs.

## What the web research says (condensed)

Recurring, well-supported findings across Anthropic docs and 2026 practitioner writeups:

- **Size is the first constraint.** Instruction-following degrades non-linearly:
  rules start dropping past ~80 lines, large blocks get ignored past ~200 lines.
  Ideal is short and dense. So: add a *few* rules, not a manifesto. Prune as much as we add.
- **Specific, not aspirational.** "Write clean code" is ignored; a testable rule
  ("read the file before editing it") is followed. Avoid vibes.
- **Every rule needs a why.** A rule with a reason generalizes to new edge cases;
  a rule without one is dropped the moment context shifts.
- **Read / ground before acting.** Never speculate about code not yet opened;
  read the referenced file before answering or editing. Top hallucination-reducer.
- **Root cause, not symptom.** AI agents default to the quickest surface fix.
  Explicitly distinguish symptom from cause; "five whys"; name the cause; flag workarounds as workarounds.
- **Verify before "done".** Give Claude a check it can run (tests/build/lint) and
  require it before claiming completion; "looks done" is the failure mode when no check is run.
- **Allow "I don't know" + state assumptions.** Permission to admit uncertainty and
  a short assumptions/unknowns note cuts fabrication sharply (Anthropic guidance).
- **Search before adding.** AI anti-patterns: duplication (didn't search the codebase),
  ghost files (new file instead of editing the real one). Look for the existing pattern first.
- **Fresh-context review catches what the author misses.** A reviewer that sees only
  the diff has no sunk-cost bias. (We already have `/code-review`; reference the habit, don't duplicate the tool.)

Sources are listed at the bottom of this file.

## Decisions

- **Where:** new section in the main CLAUDE.md, after `## Working conventions`,
  named `## Rigor` (plain label, no parenthetical, per existing style).
- **How much:** target 6-9 bullets, each one line with an inline "because ..." why.
  Keep the whole file comfortably under the ~80-line danger zone (currently 33 lines).
- **Tone/format:** match the existing file - hyphens not em dashes, logical-break
  newlines, specific and testable phrasing, no hype words.
- **Don't duplicate tooling:** mention verification and fresh-context review as habits,
  but do not re-document `/code-review` or hooks; CLAUDE.md is for style/judgment, not deterministic actions.
- **No per-language content:** these are language-agnostic, so they belong in the
  root file, not `rules/<lang>.md`.

## Proposed new section (draft to refine on approval)

```
## Rigor

Depth over speed - the skipped steps below are what turn a quick change into a bug.

- Read before you act: open the actual file before answering about it or editing it; never speculate about code you have not read.
- Fix the cause, not the symptom: trace a bug to its root before patching; if you must apply a workaround, say so and name what the real fix would be.
- Search before adding: look for the existing pattern, helper, or file first; edit the real one rather than creating a parallel/ghost version (duplication is the common AI failure).
- Verify before you call it done: run the relevant test/build/lint and report the result; "looks done" is not done.
- Surface uncertainty: when unsure, say so and state the assumption you are proceeding on instead of guessing; "I don't know" is a valid answer.
- State assumptions and unknowns briefly when a task is ambiguous, rather than inventing an interpretation.
- Prefer a fresh-context review of your own diff before declaring completion on non-trivial changes.
```

(Exact wording to be trimmed during implementation - some bullets may merge to stay tight.)

## Steps

1. Edit `claude/claude__CLAUDE.md.symlink`: insert the `## Rigor` section after `## Working conventions`.
2. Re-read the whole file for style consistency (em dashes, line length, hype words) and total length.
3. Sanity check: the symlink resolves to `~/.claude/CLAUDE.md` so the change is live for all projects (no rebuild needed for symlinked dotfiles).
4. Optionally: ask Claude in a fresh session to summarize the rules to confirm they survive (research-recommended test). Manual, not part of this edit.

## Rollback

Single-file, version-controlled change. `git checkout -- claude/claude__CLAUDE.md.symlink`
or revert the commit removes the section entirely.

## Sources

- https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations
- https://code.claude.com/docs/en/best-practices
- https://techsy.io/en/blog/claude-md-best-practices
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- https://buildwithclaude.com/stories/code-review-subagent
- https://www.unpromptedmind.com/system-prompts-claude-agents-best-practices/
- https://nyosegawa.com/en/posts/harness-engineering-best-practices-2026/
