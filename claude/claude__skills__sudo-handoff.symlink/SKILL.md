---
name: sudo-handoff
description: >
  Run privileged commands by handing them to the user's own terminal with tee logging,
  then verifying from the logs - Claude's shell has no TTY for the sudo password prompt.
  Use BEFORE running or presenting any sudo/root command (installs, systemctl, /etc edits,
  ufw, reboot) unless `sudo -n true` succeeds. A PreToolUse hook blocks direct sudo anyway;
  on that error, follow this skill instead of retrying.
---

# Sudo handoff

Claude's Bash tool has no TTY, so `sudo` cannot prompt for a password.
Unless passwordless sudo is available, privileged commands are run by the user
in their own terminal, with output teed to files Claude reads to verify each step.

## When sudo works directly

Check once per session:

```bash
sudo -n true
```

Exit 0 (NOPASSWD or cached credentials): run sudo commands normally, skip this skill.
Anything else: follow the procedure below. Never ask the user to type their password
into the session, and never work around the block (`echo <pw> | sudo -S`, su, setuid tricks).

## Procedure

1. **Set up logging once.** Pick a task-scoped folder, default `~/handoff-logs`:

   ```bash
   mkdir -p ~/handoff-logs
   ```

   Claude can create this itself (no sudo needed).

2. **Hand over each step as a copy-paste block**, appending
   `2>&1 | tee ~/handoff-logs/<NN><letter>-<slug>.log` to every command.
   Number by plan step (`01a-apt-update`, `01b-apt-upgrade`, `03c-ufw-enable`)
   so logs sort and map back to the plan.

   ```bash
   sudo apt update 2>&1 | tee ~/handoff-logs/01a-apt-update.log
   sudo apt upgrade -y 2>&1 | tee ~/handoff-logs/01b-apt-upgrade.log
   ```

   Keep batches small (2-5 related commands); destructive or state-changing
   commands (reboot, rm, disk operations) go one at a time.

3. **Verify from the log before handing the next step.** After the user confirms,
   read the log file and any relevant system state (unprivileged checks are fine
   to run directly), report the result, then continue. Do not stack unverified steps.

4. **Clean up** when the effort is done: tell the user the log folder can be deleted.

## Caveats

- `2>&1` goes **before** the pipe so stderr lands in the log.
- Interactive prompts (debconf dialogs, `ufw enable` confirmations, password entries)
  do not appear in the log; the user answers them on screen. Truly interactive commands
  (`pro attach`, logins) are handed over without tee - ask the user for the outcome instead.
- A batch pasted twice makes move/create steps error on the second run
  (`mv: cannot stat`); check whether the first run already succeeded before diagnosing.
- **Lockout guard** for anything touching the remote-access path (firewall, sshd,
  network, tailscale): keep the current session open, have the user open a second
  session to confirm access still works, and state the revert command up front.
- If a long-running handed-over command loses its terminal (SSH drop), it may
  survive orphaned or stopped; verify completion from system state
  (`dpkg --audit`, service status, timestamps), not from the truncated log alone.
- Logs may capture secrets printed by commands; prefer commands that do not echo
  secrets, and never tee anything that prints tokens or key material.
