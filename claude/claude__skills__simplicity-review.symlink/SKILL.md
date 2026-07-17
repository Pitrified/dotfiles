---
# https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail-review/SKILL.md
name: simplicity-review
description: >
  Review code or diffs for unnecessary complexity, reinvented standard library, unneeded dependencies, speculative abstractions, or dead flexibility.
  Use when the user asks to review for over-engineering, asks what can be simplified or cut, or wants a complexity-focused pass on a diff or feature.
  Complements a normal correctness review; this one only looks at complexity, not bugs, security, or performance.
---

# Simplicity review

A review pass that looks only at complexity, not correctness.
Run it on a diff, a file, or a feature, whenever the user asks to check for over-engineering,
find what to simplify, or wants a second look before finishing a non-trivial change.

## Scope

In scope: reinvented standard library, reinvented existing project helpers,
a dependency that duplicates something already available, an abstraction built
for a case that doesn't exist yet, configuration or flexibility with no current caller.

Out of scope: correctness bugs, security issues, missing error handling, performance.
If one of these turns up while reviewing, mention it separately and label it clearly
as outside this review, don't fold it into the complexity findings.

Do not flag: a single test or self-check left behind for non-trivial logic,
validation at a trust boundary, error handling that prevents data loss,
anything the user explicitly asked for. These aren't complexity to trim.

## How to review

Read the actual diff or file before commenting, don't guess from a description of it.

For each finding, give:

- where it is, file and line or range
- what's there and why it looks unnecessary
- what would replace it, concretely: a stdlib call, the name of the existing helper, or deletion

Keep each finding short, a line or two is usually enough.
If the reasoning needs more than a couple of sentences, that's a sign the finding is
borderline, state the uncertainty plainly rather than padding the case for cutting it.

## Tone

The goal is a second pair of eyes, not a verdict.
Some complexity is there for a reason the reviewer doesn't have context on,
say "this looks like it might not be needed, unless X" rather than asserting it's wrong.
When genuinely unsure whether something is overbuilt or handling a real case, say so
instead of picking a side.

Present findings as a list. Don't rewrite the code and don't apply the changes,
leave that decision to the user.