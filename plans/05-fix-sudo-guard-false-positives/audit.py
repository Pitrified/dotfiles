"""Audit real Bash traffic in the local Claude transcripts.

Answers: which commands did the guard actually block, when, and how many of those
were sudo that would have really run vs sudo that was only being written.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sudo_guard import invokes_sudo  # the proposed matcher

OLD = re.compile(r"(^|[^A-Za-z0-9_./-])sudo([ \t\n]|$)")
DENY_MARK = "PreToolUse:Bash hook error"  # harness prefix, not the script's own text

cmds = []          # (ts, session, command)
denials = []       # (ts, session, command)

PATHS = sorted(
    list(Path.home().glob(".claude/projects/*/*.jsonl"))
    + list(Path.home().glob(".claude/projects/*/*/*/*.jsonl"))  # subagent transcripts
)

for path in PATHS:
    pending = {}   # tool_use_id -> (ts, command)
    for line in path.read_text(errors="replace").splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        ts = rec.get("timestamp", "")
        msg = rec.get("message") or {}
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("name") == "Bash":
                cmd = (block.get("input") or {}).get("command", "")
                if cmd:
                    cmds.append((ts, path.stem, cmd))
                    pending[block.get("id")] = (ts, cmd)
            elif block.get("type") == "tool_result":
                text = block.get("content")
                if isinstance(text, list):
                    text = " ".join(
                        p.get("text", "") for p in text if isinstance(p, dict)
                    )
                guard_deny = (
                    isinstance(text, str)
                    and DENY_MARK in text
                    and "guard" in text
                )
                if guard_deny:
                    ts0, cmd = pending.get(block.get("tool_use_id"), (ts, "<unmatched>"))
                    denials.append((ts0, path.stem, cmd))

print(f"transcripts: {len(PATHS)}")
print(f"Bash calls:  {len(cmds)}")
print(f"guard denials found in transcripts: {len(denials)}\n")

print("=== actual denials ===")
for ts, sess, cmd in denials:
    verdict = "REAL" if invokes_sudo(cmd) else "FALSE POSITIVE"
    one = " ".join(cmd.split())
    print(f"{ts[:19]}  {verdict:<14} {one[:110]}")

print("\n=== disagreement over ALL Bash calls ===")
old_only = [c for c in cmds if OLD.search(c[2] + "\n") and not invokes_sudo(c[2])]
new_only = [c for c in cmds if invokes_sudo(c[2]) and not OLD.search(c[2] + "\n")]
both = [c for c in cmds if invokes_sudo(c[2]) and OLD.search(c[2] + "\n")]
print(f"old blocks, new allows (false positives avoided): {len(old_only)}")
print(f"new blocks, old allows (caught by new only):       {len(new_only)}")
print(f"both block:                                        {len(both)}")

for label, rows in (("old-only", old_only), ("new-only", new_only)):
    if rows:
        print(f"\n--- {label} ---")
        for ts, sess, cmd in rows:
            print(f"{ts[:19]}  {' '.join(cmd.split())[:120]}")

print("\n=== dates of all sudo-ish traffic ===")
print(Counter(ts[:10] for ts, _, c in cmds if OLD.search(c + "\n") or invokes_sudo(c)))
