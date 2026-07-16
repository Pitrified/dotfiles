# Sudo handoff: skill + CLAUDE.md pointer + PreToolUse hook

## Goal

Make the sudo-handoff pattern (privileged commands run by the user in their own terminal,
teed to log files Claude then reads and verifies) available to every Claude session on every
machine that installs these dotfiles, with progressive disclosure and deterministic enforcement.

Origin: the 2026-07-15 cloudflare migration on `pmn-14g4`
(`linux-box-cloudflare/scratch_space/vibes/18-cloudflare-setup/`).
`! sudo <cmd>` fails in remote-controlled sessions - no TTY password prompt -
and Claude's own Bash tool has the same limitation everywhere unless NOPASSWD/cached creds exist.

## Decisions

- **Placement: hybrid + hook** (user-chosen over skill-only / always-on rule / CLAUDE.md paragraph):
  - `sudo-handoff` **skill** in dotfiles carries the full procedure; only its description (~80 tokens) is always in context.
  - One **pointer line** in the global `claude__CLAUDE.md.symlink` (Working conventions) so the model knows the skill exists before its first sudo attempt.
  - A **PreToolUse hook** hard-blocks Bash commands containing `sudo` when `sudo -n true` fails, with a deny message pointing at the skill. Advisory + deterministic.
- Hook script lives at `claude/claude__hooks__sudo-guard.sh.symlink` -> `~/.claude/hooks/sudo-guard.sh`; registered in `claude__settings.json.symlink` as a second PreToolUse/Bash entry alongside the existing `rtk hook claude`.
- Command parsing via `jq` with a `python3` fallback (both ubiquitous on these boxes); sudo matched as a command word. Known false positive: a quoted mention like `echo "use sudo x"` gets blocked - acceptable, the deny message tells the model to rephrase.
- If passwordless sudo works (`sudo -n true` exits 0), the hook allows the call - the skill is only for the no-TTY case.
- Log folder convention generalized to `~/handoff-logs/` (was `~/cf-setup-logs` in the origin session).

## Steps

1. This note.
2. Create `claude/claude__skills__sudo-handoff.symlink/SKILL.md` (procedure, verification loop, caveats: interactive prompts not captured, double-pasted batches, lockout guards, never ask for the password).
3. Create `claude/claude__hooks__sudo-guard.sh.symlink` (exit 2 + stderr message to block).
4. Register the hook in `claude__settings.json.symlink`.
5. Add the pointer line to `claude__CLAUDE.md.symlink`.
6. Symlink the two new files manually (same result as `uv run install/install.py`, without regenerating bash_aliases).
7. Test: hook script with synthetic stdin (sudo and non-sudo commands), then a live blocked `sudo true` through the Bash tool.
8. Cleanups elsewhere: delete the now-redundant project memory `sudo-handoff-tee-logs.md` (linux-box-cloudflare project); the `local-box.md` `! <command>` guidance needed no edit (it never prescribed `! sudo`; the stale advice was only in the cloudflare plan folder, which is history).

## Rollback

- Remove the two symlinks (`~/.claude/skills/sudo-handoff`, `~/.claude/hooks/sudo-guard.sh`).
- Revert the dotfiles commit (settings.json hook entry, CLAUDE.md line, new files).
- Sessions fall back to advisory-only behavior immediately; no system state outside `~/.claude` and `~/dotfiles` is touched.
