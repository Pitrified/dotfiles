#!/usr/bin/env python3
"""PreToolUse hook (Bash matcher): block sudo when it cannot work.

Claude's shell has no TTY, so sudo cannot prompt for a password. When
passwordless sudo is unavailable, running sudo only produces a confusing
failure; this hook denies the call and points the model at the sudo-handoff
skill (hand the command to the user's own terminal with tee logging).

The hook allows the call when the command has no sudo that would actually run,
or when `sudo -n true` succeeds (NOPASSWD or cached credentials).

"Actually run" is the whole point. `sudo` written into a document is not a sudo
invocation, and blocking it fights the sudo-handoff skill, whose job is to write
privileged commands into plan notes and handoff blocks. So:

  ssh host 'sudo reboot'          -> blocked, it runs on the remote
  bash <<EOF ... sudo x ... EOF   -> blocked, the body is code
  cat > f.md <<EOF ... sudo x ... -> allowed, the body is data
  echo "run sudo x yourself"      -> allowed, it is a string

On any internal error the hook allows the call: a broken guard should degrade to
advisory, never to a blocked shell.
"""

import json
import re
import shlex
import subprocess
import sys
from pathlib import PurePosixPath

# Command words that execute a string argument or a heredoc body as shell code.
EXECUTORS = {"bash", "sh", "zsh", "ssh", "su"}

# Command words that wrap another command: the real command word follows.
WRAPPERS = {"timeout", "env", "nohup", "time", "nice", "xargs", "command", "exec"}

PRIVILEGE = {"sudo", "doas"}

_PUNCT = "();<>|&\n"

# Wrapper options and operands to skip while looking for the real command word:
# `-v`, `60`, `2.5s`, `FOO=bar`.
_WRAPPER_NOISE = re.compile(r"^(-.*|\d+(\.\d+)?[smhd]?|[A-Za-z_]\w*=.*)$")

# `Key=value` operands belonging to a preceding flag, e.g. `ssh -o BatchMode=yes`.
_OPTION_OPERAND = re.compile(r"^[\w.]+=\S*$")

_HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_]\w*)\1")


def _basename(tok):
    return PurePosixPath(tok).name if "/" in tok else tok


def _tokenize(text):
    lex = shlex.shlex(text, posix=True, punctuation_chars=_PUNCT)
    lex.whitespace_split = True
    lex.whitespace = " \t\r"  # newline is a separator token, not whitespace
    try:
        return list(lex)
    except ValueError:
        # Unbalanced quotes: fall back to a whitespace split so we still scan.
        return text.split()


def _is_separator(tok):
    return bool(tok) and all(ch in _PUNCT for ch in tok)


def _consumer_is_shell(prefix):
    """Does `prefix` end in a command that runs a heredoc body as code?

    `bash <<EOF` and `ssh host 'bash -s' <<EOF` do. `cat > f <<EOF`,
    `tee f <<EOF` and `ssh host "cat > f" <<EOF` do not: there the body is data.
    """
    seg = []
    for tok in _tokenize(prefix):
        seg = [] if _is_separator(tok) else seg + [tok]
    while seg and _basename(seg[0]) in WRAPPERS:
        seg = seg[1:]
        while seg and _WRAPPER_NOISE.match(seg[0]):
            seg = seg[1:]
    if not seg:
        return False

    base = _basename(seg[0])
    if base == "ssh":
        operands = [
            t for t in seg[1:]
            if not t.startswith("-") and not _OPTION_OPERAND.match(t)
        ]
        # operands[0] is the host; anything after it is the remote command.
        if len(operands) > 1:
            return _consumer_is_shell(" ".join(operands[1:]))
        return True  # no remote command: the body feeds a login shell
    return base in EXECUTORS


def _split_heredocs(cmd):
    """Pull heredoc bodies out of `cmd`.

    Returns the remaining command text plus a list of (body, is_code) pairs.
    """
    lines = cmd.split("\n")
    kept, bodies, i = [], [], 0
    while i < len(lines):
        line = lines[i]
        match = _HEREDOC.search(line)
        if not match:
            kept.append(line)
            i += 1
            continue

        delim = match.group(2)
        kept.append(line[: match.start()])
        body = []
        i += 1
        while i < len(lines) and lines[i].strip() != delim:
            body.append(lines[i])
            i += 1
        i += 1  # skip the terminator
        bodies.append(("\n".join(body), _consumer_is_shell(line[: match.start()])))
    return "\n".join(kept), bodies


def invokes_sudo(cmd, depth=0):
    if depth > 4:
        return False

    text, bodies = _split_heredocs(cmd)
    for body, is_code in bodies:
        if is_code and invokes_sudo(body, depth + 1):
            return True

    at_command_word = True
    after_wrapper = False
    prev_was_executor = False

    for tok in _tokenize(text):
        if _is_separator(tok):
            at_command_word, after_wrapper, prev_was_executor = True, False, False
            continue

        if at_command_word:
            if after_wrapper and _WRAPPER_NOISE.match(tok):
                continue  # wrapper option or duration, real command word still ahead
            base = _basename(tok)
            if base in PRIVILEGE:
                return True
            if base in WRAPPERS:
                after_wrapper = True
                continue
            prev_was_executor = base in EXECUTORS
            at_command_word = False
            after_wrapper = False
            continue

        # An argument. Only worth descending into if something will execute it.
        if prev_was_executor and invokes_sudo(tok, depth + 1):
            return True

    return False


DENY_MESSAGE = """\
sudo blocked: this shell has no TTY for the password prompt and passwordless
sudo is unavailable, so the command cannot work. Do not retry it or attempt a
workaround (no sudo -S, no su). Follow the sudo-handoff skill instead: hand the
command to the user to run in their own terminal, appending
`2>&1 | tee ~/handoff-logs/<NN><letter>-<slug>.log`, then verify from the log.

This hook only fires on sudo that would actually run, including inside a heredoc
piped to a shell and inside `ssh host '...'`. Writing the word into a file or a
string is allowed. If you are somehow still blocked while only writing content,
use the Write tool - never reword or omit the privileged command in a document
to get past this hook.
"""


def main():
    try:
        cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except Exception:
        return 0
    if not cmd:
        return 0

    try:
        if not invokes_sudo(cmd):
            return 0
    except Exception:
        return 0  # a broken guard degrades to advisory, not to a blocked shell

    try:
        if subprocess.run(
            ["sudo", "-n", "true"], capture_output=True, timeout=5
        ).returncode == 0:
            return 0  # passwordless sudo works: the skill is not needed
    except Exception:
        pass

    print(DENY_MESSAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
