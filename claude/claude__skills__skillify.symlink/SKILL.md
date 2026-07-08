---
name: skillify
description: "Turn a working solution into a permanent, tested skill — extract pattern, interrogate for depth, create SKILL.md, publish to registry. Use when the user says 'skillify', 'make this a skill'."
allowed-tools: Read, Glob, Grep, Write, Edit, Agent
# source : https://github.com/belt-sh/skills/blob/main/skills/skillify/SKILL.md (registry steps adapted from belt to skills.sh / npx skills)
---

## Skillify

Turn what just worked into a skill that works forever. This follows a structured interrogation process — don't rush to write the SKILL.md.

### When to use

- A multi-step workflow was refined through trial and error
- The user recovered from a failure and wants to prevent recurrence
- The user says "skillify", "make this a skill", "remember this as a skill"
- A working solution emerged that could apply to other projects

### Process

#### 1. Triage — Is this actually worth a skill?

Before doing anything, evaluate:
- **Refinement arc?** Did something fail first, then get corrected into a working approach? That correction IS the skill.
- **Reusable?** Would this help in a different project, or is it specific to this exact codebase?
- **Multi-step?** Is it a workflow with ordered steps, not a one-liner?

If the answer to all three is "no", tell the user why and suggest saving it as a plain note or memory instead, not a skill.

#### 2. Interrogate — Dig deep before writing

Launch a subagent to analyze the conversation. The subagent should answer:

1. What specific steps make up this workflow? List them in order.
2. Where did the naive approach fail? What corrections or pivots happened?
3. What are the hard-won gotchas — things that look right but break?
4. Which steps are deterministic (same input → same output) vs judgment (requires LLM reasoning)?
5. What would someone need to know BEFORE attempting this?

Be concrete — actual commands, endpoints, file paths, error messages.

Present findings to the user for validation before proceeding.

#### 3. Check for existing skills

Search your own installed skills first, then the skills.sh registry:
```bash
grep -rli "<relevant keywords>" ~/.claude/skills/   # local skills (dotfiles symlinks)
npx skills find "<relevant keywords>"               # remote registry
```

If a similar skill exists, inspect it. Local: read its `SKILL.md`. Remote:
```bash
npx skills use <owner/repo>
```

Then decide:
- **Create new** — if genuinely novel
- **Update existing** — if the conversation revealed something the existing skill missed. Review line-by-line:
  - What specific instructions were wrong or missing?
  - What new gotchas should be added?
  - What existing content is still correct?

#### 4. Produce the SKILL.md

Write the skill with these quality criteria:

**Abstraction**: Remove instance-specific details (specific file paths, project names, API keys). Keep the reusable pattern.

**Conciseness**: Capture the pattern in minimum words. Dense > verbose. Every line must earn its place.

**Actionability**: Every step should be executable. No vague "consider doing X" — say exactly what to do and when.

**Deterministic work is deterministic**: If a step is "same input → same output" (API calls, file parsing, data lookup), it should be a script or exact command, not LLM reasoning.

**Rules have reasons**: Every constraint traces back to a specific failure. Not "always validate input" but "validate the response schema because the API returns 200 with an error body when the model name is wrong (discovered when deployment succeeded but inference returned empty)."

**Pushy description**: The `description` field in frontmatter determines whether this skill gets loaded. Be explicit about trigger conditions. Instead of "Helps with deployments" write "Deploy and test inference.sh apps — use when building new apps, adding providers, or debugging deployment failures. Trigger on: app creation, provider integration, deploy errors, pricing configuration."

#### SKILL.md structure

```markdown
---
name: <kebab-case-name>
description: "<what it does> — <when to use it, be specific and slightly pushy about trigger conditions>"
allowed-tools: <tools needed>
---

## <Name>

<One paragraph: what this skill does and the key insight that makes it valuable.>

### When to use

<Specific trigger conditions — not vague categories but concrete situations.>

### Process

<Numbered steps. Each step says what to do, not what to consider.
Mark deterministic steps with [deterministic] and judgment steps with [judgment].>

### Rules

<Hard constraints from real failures. Each rule format:
- Rule statement
- Why: the specific failure that taught this lesson>

### Gotchas

<Things that look right but break. Format:
- What seems correct → What actually happens → What to do instead>
```

#### 5. Publish

Scaffold the directory if starting fresh:
```bash
npx skills init <skill-name>
```

There is no upload command on skills.sh — a skill is "published" by living in a git repo. Write the SKILL.md, commit, and push:
```bash
git add <skill-directory> && git commit -m "add <skill-name> skill" && git push
```

Others install it with `npx skills add <owner/repo>`, and skills.sh indexes it from install telemetry. Same name in a new commit = new version.

### Quality checklist

Before publishing:
- [ ] Triage passed — this is genuinely reusable, not a one-off
- [ ] Interrogation done — the hard-won details are captured
- [ ] No duplicates — searched registry
- [ ] Description is pushy — lists explicit trigger conditions
- [ ] Steps are ordered — someone cold can follow the procedure
- [ ] Rules have reasons — every constraint traces to a failure
- [ ] Deterministic work uses scripts/commands, not LLM reasoning
