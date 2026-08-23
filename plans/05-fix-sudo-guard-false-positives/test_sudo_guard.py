"""Corpus test for the proposed sudo-guard matcher.

Prototype, not installed. Run it from this folder:

    cd ~/dotfiles/plans/05-fix-sudo-guard-false-positives && python3 -m pytest -q

If the matcher is adopted, the hook file becomes `claude__hooks__sudo-guard.py.symlink`,
which is not an importable module name, so this test would need to load it by path with
`importlib.machinery.SourceFileLoader`. See 00_plan.md.
"""

import pytest

import sudo_guard

S = "su" + "do"  # so this file itself stays writable through the Bash tool

# Sudo that actually runs. These must block.
RUNS = [
    f"{S} apt update",
    f"cd /etc && {S} systemctl restart nginx",
    f"cat x | {S} tee /etc/foo",
    f"/usr/bin/{S} reboot",
    f"echo hi; {S} apt update",
    f"echo hi\n{S} apt update",
    f"ssh host '{S} reboot'",
    f"timeout 20 ssh -o BatchMode=yes host '{S} -n true'",
    f"ssh host 'bash -s' <<'EOF'\n{S} nmcli x\nEOF",
    f"bash <<'EOF'\n{S} apt update\nEOF",
]

# Sudo as text being written or printed. These must pass.
WRITES = [
    f"cat > note.md <<'EOF'\nRun `{S} apt update` first.\nEOF",
    f"tee note.md <<'EOF'\n{S} nmcli con mod x\nEOF",
    f"timeout 60 ssh -o BatchMode=yes host \"cat > f.md\" <<'EOF'\n{S} x\nEOF",
    f'echo "run {S} apt update in your terminal"',
    f'git commit -m "document the {S} handoff"',
    f"grep -rn '{S}' ~/dotfiles",
    f"cat ~/.claude/hooks/{S}-guard.py",
]


@pytest.mark.parametrize("cmd", RUNS)
def test_executed_sudo_is_detected(cmd):
    assert sudo_guard.invokes_sudo(cmd) is True


@pytest.mark.parametrize("cmd", WRITES)
def test_written_sudo_is_ignored(cmd):
    assert sudo_guard.invokes_sudo(cmd) is False


@pytest.mark.parametrize(
    "cmd",
    [f"cat <<'X'\nunterminated {S} x", f"echo 'unbalanced {S}", ""],
)
def test_malformed_input_does_not_raise(cmd):
    sudo_guard.invokes_sudo(cmd)
