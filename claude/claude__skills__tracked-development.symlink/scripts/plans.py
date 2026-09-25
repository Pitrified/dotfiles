#!/usr/bin/env python3
"""Query and check the plan folders under `plans/`.

Reads the frontmatter the `tracked-development` skill describes and answers the
questions nobody wants to answer by opening twenty folders: what is in progress,
what is next by priority, what a phase range contains.

    python3 scripts/plans.py list
    python3 scripts/plans.py list --status "in progress"
    python3 scripts/plans.py list --index 15
    python3 scripts/plans.py list --out /tmp/roadmap.md

Every path is an argument with a default, because this file is meant to be
callable from anywhere: `--root` is the plans directory, and without it the root
comes from `git rev-parse --show-toplevel`, never from this file's own location.
"""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from dataclasses import dataclass, field
from html import escape
from pathlib import Path

# The canonical copy of this file lives in the tracked-development skill in
# dotfiles; a repo carries a vendored copy so its gate runs without dotfiles.
# Bump this on any change to the canonical copy, so two copies can be told apart
# by `--version` as well as by comparing the files.
VERSION = "1.0.0"

STATUSES = ("draft", "planned", "in progress", "done", "superseded", "discarded")

# A phase file is NN_name.md; NN.M_name.md is a side-document of phase NN, which
# carries no status of its own. Three digits are allowed too: a big project can
# pass a hundred features, and the number is what orders everything here.
PHASE = re.compile(r"^(\d{2,3})_([a-z0-9_.]+)\.md$")
SIDE = re.compile(r"^(\d{2,3})\.(\d+)_([a-z0-9_.]+)\.md$")
FOLDER = re.compile(r"^(\d{2,3})_([a-z0-9_]+)$")


class PlansError(Exception):
    """Something about the plans tree stops the tool from doing its job."""


class FrontmatterError(PlansError):
    """A `---` block exists but does not parse."""


@dataclass
class Frontmatter:
    """A plan file's `---` block, typed, with its own problems collected.

    Built once per file so that a rule such as "priority is a non-negative
    integer" lives here rather than at each place a caller looks at the value.
    Problems are collected rather than raised: a file with two faults should
    report two.
    """

    status: str | None = None
    priority: int | None = None
    priority_raw: str | None = None
    description: str | None = None
    # Prerequisites, as folder names, on a 00_start.md. Folders rather than phases:
    # the working unit is a whole feature, so a prerequisite is a folder being
    # finished rather than a phase inside one being reached.
    depends_on: list[str] = field(default_factory=list)
    # Freeform, never parsed and never checked: the place for something worth
    # keeping that the schema has no field for.
    comment: str | None = None
    extra: dict[str, str] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)

    KNOWN = ("status", "priority", "description", "depends_on", "comment")

    def missing(self, key: str) -> bool:
        """Whether `key` is absent. `priority: 0` is present and falsy, which is
        why this is not a truth test on the value."""
        if key == "priority":
            return self.priority_raw is None
        return not getattr(self, key)

    @classmethod
    def read(cls, md: Path) -> "Frontmatter":
        """Parse `md`'s frontmatter. A block that does not parse is one problem."""
        try:
            raw = parse_frontmatter(md.read_text(encoding="utf-8"), md)
        except FrontmatterError as exc:
            return cls(problems=[str(exc).split(": ", 1)[-1]])
        front = cls(
            status=raw.get("status"),
            description=raw.get("description"),
            comment=raw.get("comment"),
            extra={k: v for k, v in raw.items() if k not in cls.KNOWN},
        )
        listed = raw.get("depends_on")
        if listed is not None:
            inner = listed.strip()
            if not (inner.startswith("[") and inner.endswith("]")):
                front.problems.append(
                    f"depends_on {listed!r} is not an inline list, as [20_repo_split]"
                )
            else:
                front.depends_on = [
                    name.strip() for name in inner[1:-1].split(",") if name.strip()
                ]
        front.priority_raw = raw.get("priority")
        if front.priority_raw is not None:
            if front.priority_raw.isdigit():
                front.priority = int(front.priority_raw)
            else:
                front.problems.append(
                    f"priority {front.priority_raw!r} is not a non-negative integer"
                )
        return front


@dataclass
class Phase:
    """One `NN_name.md` sub-plan."""

    path: Path
    number: str
    front: Frontmatter

    @property
    def status(self) -> str | None:
        return self.front.status


@dataclass
class Folder:
    """One `plans/NN_name/` feature folder."""

    path: Path
    number: str
    name: str
    start: Path | None
    front: Frontmatter = field(default_factory=lambda: Frontmatter())
    phases: list[Phase] = field(default_factory=list)
    sides: list[Path] = field(default_factory=list)
    tracking: Path | None = None

    @property
    def status(self) -> str | None:
        return self.front.status

    @property
    def priority(self) -> int | None:
        return self.front.priority

    @property
    def depends_on(self) -> list[str]:
        return self.front.depends_on

    @property
    def summary(self) -> str:
        """First line of `description`, which is what a listing has room for."""
        text = self.front.description or ""
        return text.strip().splitlines()[0] if text.strip() else ""


def parse_frontmatter(text: str, where: Path) -> dict[str, str]:
    """The `---` block as a dict, supporting `key: value` and `key: |` blocks.

    Hand-rolled rather than PyYAML: six keys do not justify a dependency, and
    this box runs the gates on the standard library only.
    """
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        raise FrontmatterError(f"{where}: frontmatter opens with --- and never closes")
    lines = text[4:end].splitlines()
    front: dict[str, str] = {}
    key: str | None = None
    block: list[str] = []
    for line in lines:
        if key is not None and (line.startswith("  ") or not line.strip()):
            block.append(line[2:] if line.startswith("  ") else "")
            continue
        if key is not None:
            front[key] = "\n".join(block).strip()
            key, block = None, []
        if not line.strip():
            continue
        if ":" not in line:
            raise FrontmatterError(f"{where}: cannot read frontmatter line {line!r}")
        name, _, value = line.partition(":")
        value = value.strip()
        if value in ("|", ">", "|-", ">-"):
            key = name.strip()
        else:
            front[name.strip()] = value
    if key is not None:
        front[key] = "\n".join(block).strip()
    return front


def load(root: Path, skipped: list[str] | None = None) -> list[Folder]:
    """Every numbered folder under `root`, in number order.

    A folder with no start file is not a feature (a reference dump such as
    `00_drafts` or `99_notes`) and is skipped; its name is appended to `skipped`
    so a caller can say so rather than leaving a folder silently absent.
    """
    if not root.is_dir():
        raise PlansError(f"{root}: not a directory")
    folders: list[Folder] = []
    for path in sorted(p for p in root.iterdir() if p.is_dir()):
        match = FOLDER.match(path.name)
        if not match:
            continue
        start = path / "00_start.md"
        if not start.exists():
            if skipped is not None:
                skipped.append(path.name)
            continue
        folder = Folder(
            path=path,
            number=match.group(1),
            name=match.group(2),
            start=start,
            front=Frontmatter.read(start),
            tracking=(path / "tracking.md") if (path / "tracking.md").exists() else None,
        )
        for md in sorted(path.glob("*.md")):
            if md.name in ("00_start.md", "tracking.md"):
                continue
            if SIDE.match(md.name):
                folder.sides.append(md)
            elif phase := PHASE.match(md.name):
                folder.phases.append(Phase(md, phase.group(1), Frontmatter.read(md)))
        folders.append(folder)
    return folders


def default_root() -> Path:
    """`<repo>/plans`, from git rather than from this file's location."""
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise PlansError(
            "not in a git repository, so --root is required to say where plans/ is"
        ) from exc
    return Path(top) / "plans"


def in_range(number: str, spec: str) -> bool:
    """`15` matches 15; `09-12` matches 9 through 12 inclusive; `100` matches 100."""
    low, _, high = spec.partition("-")
    try:
        first = int(low)
        last = int(high) if high else first
    except ValueError as exc:
        raise PlansError(f"--index wants NN or NN-MM, not {spec!r}") from exc
    return first <= int(number) <= last


def rows(folders: list[Folder]) -> list[tuple[str, ...]]:
    """One row per folder, sorted by priority descending then number."""

    def sort_key(folder: Folder) -> tuple[int, int]:
        return (-(folder.priority or 0), int(folder.number))

    by_name = {f"{f.number}_{f.name}": f for f in folders}
    out = []
    for folder in sorted(folders, key=sort_key):
        done = sum(1 for p in folder.phases if p.status == "done")
        phases = f"{done}/{len(folder.phases)}" if folder.phases else "-"
        needs = []
        for name in folder.depends_on:
            prerequisite = by_name.get(name)
            if prerequisite is None:
                # Not in this tree: it may be on a branch that has not merged, which
                # needs a merge rather than work. A different marker for that reason.
                needs.append(f"{name[:2]}?")
            elif prerequisite.status != "done":
                needs.append(f"{name[:2]}*")
            else:
                needs.append(name[:2])
        out.append(
            (
                folder.number,
                folder.name,
                folder.status or "-",
                "-" if folder.priority is None else str(folder.priority),
                phases,
                ",".join(needs) if needs else "-",
                folder.summary or "-",
            )
        )
    return out


HEADERS = ("NN", "folder", "status", "pri", "phases", "needs", "description")


def print_table(table: list[tuple[str, ...]], width: int = 66) -> None:
    body = [r[:-1] + (r[-1][:width],) for r in table]
    widths = [max(len(h), *(len(r[i]) for r in body)) if body else len(h)
              for i, h in enumerate(HEADERS)]
    line = "  ".join(h.ljust(w) for h, w in zip(HEADERS, widths))
    print(line)
    print("  ".join("-" * w for w in widths))
    for row in body:
        print("  ".join(cell.ljust(w) for cell, w in zip(row, widths)))


def write_out(table: list[tuple[str, ...]], out: Path) -> None:
    """Markdown or HTML by extension, untracked: a message, not a tracked file."""
    if out.suffix == ".html":
        cells = "\n".join(
            "<tr>" + "".join(f"<td>{escape(c)}</td>" for c in row) + "</tr>"
            for row in table
        )
        head = "".join(f"<th>{h}</th>" for h in HEADERS)
        out.write_text(
            "<!doctype html><meta charset=utf-8><title>plans</title>"
            "<style>body{font:14px system-ui;margin:2rem}"
            "td,th{padding:.2rem .6rem;text-align:left;border-bottom:1px solid #ddd}</style>"
            f"<table><tr>{head}</tr>\n{cells}</table>\n",
            encoding="utf-8",
        )
    else:
        md = ["| " + " | ".join(HEADERS) + " |", "| " + " | ".join("---" for _ in HEADERS) + " |"]
        md += ["| " + " | ".join(c.replace("|", r"\|") for c in row) + " |" for row in table]
        out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {out}")


# A row of a tracking table: `| 4.1 | Phase name | [`04.1_x.md`](04.1_x.md) | done |`
ROW = re.compile(
    r"^\|\s*([\d.]+)\s*\|[^|]*\|\s*\[`([^`]+)`\]\([^)]*\)\s*\|\s*([^|]+?)\s*\|\s*$"
)

# A reference to a specific plan folder from outside `plans/`. The `NN_` is what
# turns a description of the convention into a citation of an instance, so that is
# what this keys on; a bare `plans/` is a location and passes.
CITATION = re.compile(r"plans/\d{2,3}_[A-Za-z0-9_]+")
REQUIRED_START = ("status", "priority", "description")


def check_folder(folder: Folder) -> list[str]:
    """Every mechanical fault in one folder, each naming its file."""
    out = []
    start = folder.start.relative_to(folder.path.parent.parent)
    out += [f"{start}: {problem}" for problem in folder.front.problems]
    unreadable = any("never closes" in p for p in folder.front.problems)
    for key in REQUIRED_START:
        if not unreadable and folder.front.missing(key):
            out.append(f"{start}: no {key} in frontmatter")
    if folder.status and folder.status not in STATUSES:
        out.append(f"{start}: status {folder.status!r} is not one of {list(STATUSES)}")
    if folder.status == "done" and folder.priority not in (None, 0):
        out.append(
            f"{start}: status is done, so priority should be back at 0, not {folder.priority}"
        )

    numbers: dict[str, str] = {}
    for phase in folder.phases:
        name = phase.path.relative_to(folder.path.parent.parent)
        out += [f"{name}: {problem}" for problem in phase.front.problems]
        if phase.front.problems:
            pass
        elif phase.status is None:
            out.append(f"{name}: no status in frontmatter")
        elif phase.status not in STATUSES:
            out.append(f"{name}: status {phase.status!r} is not one of {list(STATUSES)}")
        if phase.number in numbers:
            out.append(f"{name}: number {phase.number} is already used by {numbers[phase.number]}")
        else:
            numbers[phase.number] = phase.path.name

    for md in sorted(folder.path.glob("*.md")):
        if md.name in ("00_start.md", "tracking.md") or PHASE.match(md.name) or SIDE.match(md.name):
            continue
        out.append(
            f"{md.relative_to(folder.path.parent.parent)}: not a plan file name "
            "(00_start.md, tracking.md, NN_name.md or NN.M_name.md)"
        )

    if folder.phases and folder.tracking is None:
        out.append(f"{folder.path.name}/: {len(folder.phases)} phase file(s) and no tracking.md")
    if folder.tracking is not None:
        out += check_tracking(folder)

    if folder.phases and all(p.status == "done" for p in folder.phases):
        for md in [folder.start, folder.tracking, *(p.path for p in folder.phases)]:
            if md and "NEW_ANS:" in md.read_text(encoding="utf-8").replace("`NEW_ANS:`", ""):
                out.append(
                    f"{md.relative_to(folder.path.parent.parent)}: NEW_ANS: left in a folder "
                    "whose phases are all done"
                )
    return out


def check_tracking(folder: Folder) -> list[str]:
    """The table and the phase files have to agree, both ways."""
    out = []
    tracking = folder.tracking
    where = tracking.relative_to(folder.path.parent.parent)
    by_name = {p.path.name: p for p in folder.phases}
    listed = set()
    for number, line in enumerate(tracking.read_text(encoding="utf-8").splitlines(), 1):
        row = ROW.match(line)
        if not row:
            continue
        _, name, table_status = row.groups()
        listed.add(name)
        if table_status not in STATUSES:
            out.append(
                f"{where}:{number}: status {table_status!r} is not one of {list(STATUSES)}"
            )
        phase = by_name.get(name)
        if phase is None:
            if not (folder.path / name).exists():
                out.append(f"{where}:{number}: table names {name}, which does not exist")
            continue  # a side-document may be listed; it carries no status of its own
        if table_status in STATUSES and phase.status != table_status:
            out.append(
                f"{where}:{number}: table says {table_status!r}, {name} says {phase.status!r}"
            )
    for name in sorted(by_name):
        if name not in listed:
            out.append(f"{where}: {name} is missing from the phases table")
    return out


def check_citations(repo: Path) -> list[str]:
    """Nothing outside `plans/` may cite a specific plan folder.

    Plans are a diary of development; docs are the as-is. A decision worth citing
    belongs in the docs file whose topic it is, so the reader finds the answer
    rather than a plan from four phases ago. A path containing `<` is a shape
    (`plans/<folder>/tracking.md`) rather than a reference, and passes.
    """
    try:
        files = subprocess.run(
            ["git", "-C", str(repo), "ls-files"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise PlansError(f"{repo}: cannot list tracked files, so citations cannot be checked") from exc
    out = []
    for name in files:
        if name.startswith("plans/") or not (repo / name).is_file():
            continue
        try:
            text = (repo / name).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for hit in CITATION.finditer(line):
                if "plans/<" in line[max(0, hit.start() - 8) : hit.end()]:
                    continue
                out.append(f"{name}:{number}: cites {hit.group(0)}; a decision belongs in docs/")
    return out


def check_dependencies(folders: list[Folder]) -> list[str]:
    """Every fault in the dependency graph, as findings.

    Prerequisites are folders, so an edge means "that whole feature has to be
    finished". Nothing here reads a git ref: a name that is not in this tree is
    handled by `check_across_refs`, which knows whether someone else has it.
    """
    out = []
    by_name = {f"{f.number}_{f.name}": f for f in folders}
    where = {name: f.start.relative_to(f.path.parent.parent) for name, f in by_name.items()}
    dependents: dict[str, list[str]] = {}
    for name, folder in by_name.items():
        for target in folder.depends_on:
            dependents.setdefault(target, []).append(name)

    for name, folder in sorted(by_name.items()):
        for target in folder.depends_on:
            prerequisite = by_name.get(target)
            if prerequisite is None:
                continue  # unresolved names are reported by the caller
            if folder.status in ("in progress", "done") and prerequisite.status != "done":
                out.append(
                    f"{where[name]}: status is {folder.status}, but it needs {target}, "
                    f"which is {prerequisite.status}"
                )
            if (folder.priority or 0) > (prerequisite.priority or 0):
                out.append(
                    f"{where[name]}: priority {folder.priority} is above {target}'s "
                    f"{prerequisite.priority or 0}, so the list offers work that cannot be started"
                )

    # Read the other way: discarding a feature is the moment to see what it breaks.
    for target, names in sorted(dependents.items()):
        prerequisite = by_name.get(target)
        if prerequisite is not None and prerequisite.status in ("discarded", "superseded"):
            out.append(
                f"{where[target]}: {prerequisite.status}, and {', '.join(sorted(names))} "
                "depends on it"
            )

    out += check_cycles(by_name, where)
    return out


def check_cycles(by_name: dict[str, Folder], where: dict[str, Path]) -> list[str]:
    """Cycles, reported as the path found.

    Needed because a number says nothing about order: `20` may depend on `21`, so
    only walking the edges rules a cycle out.
    """
    out, done = [], set()

    def walk(name: str, seen: list[str]) -> None:
        if name in seen:
            cycle = seen[seen.index(name):] + [name]
            key = frozenset(cycle)
            if key not in done:
                done.add(key)
                out.append(
                    f"{where[name]}: depends on itself through {' -> '.join(cycle)}"
                )
            return
        folder = by_name.get(name)
        if folder is None:
            return
        for target in folder.depends_on:
            walk(target, seen + [name])

    for name in sorted(by_name):
        walk(name, [])
    return out


def unresolved(folders: list[Folder]) -> list[tuple[Folder, str]]:
    """Every (folder, name) whose prerequisite is not a folder in this tree."""
    names = {f"{f.number}_{f.name}" for f in folders}
    return [
        (folder, target)
        for folder in folders
        for target in folder.depends_on
        if target not in names
    ]


def suggestion(name: str, folders: list[Folder]) -> str:
    close = difflib.get_close_matches(name, [f"{f.number}_{f.name}" for f in folders], n=1)
    return f"; did you mean {close[0]}" if close else ""


def resolve_elsewhere(
    repo: Path, folders: list[Folder], missing: list[tuple[Folder, str]]
) -> tuple[list[str], list[str]]:
    """Split unresolved prerequisites into warnings and findings.

    A prerequisite may be on a branch that has not merged: someone else may be
    implementing it, and merging their plans in so that a name resolves is
    overkill. That is a warning. A name that exists nowhere is a typo, and stays a
    finding.

    The refs are read only when something is missing, which is why this does not
    undo folder 21's decision to keep ref-reading out of every run.
    """
    if not missing:
        return [], []
    on_refs = folders_on_refs(repo)
    elsewhere = {
        name: refs
        for names in on_refs.values()
        for name, refs in names.items()
    }
    warnings, findings = [], []
    for folder, name in missing:
        where = folder.start.relative_to(repo)
        refs = elsewhere.get(name)
        if refs is None:
            findings.append(
                f"{where}: depends on {name}, which is not a plan folder"
                f"{suggestion(name, folders)}"
            )
        elif folder.status == "in progress":
            warnings.append(
                f"{where}: in progress, and needs {name}, which is only on "
                f"{', '.join(sorted(refs))}. That merge is what this work is waiting for."
            )
        else:
            warnings.append(
                f"{where}: needs {name}, which is not in this tree yet; it is on "
                f"{', '.join(sorted(refs))}"
            )
    return warnings, findings


def cmd_check(args: argparse.Namespace) -> int:
    folders = load(args.root)
    findings = []
    for folder in folders:
        findings += check_folder(folder)
    findings += check_dependencies(folders)
    warnings, unresolved_findings = resolve_elsewhere(
        args.root.parent, folders, unresolved(folders)
    )
    findings += unresolved_findings
    if args.citations:
        findings += check_citations(args.root.parent)
    for warning in warnings:
        print(f"plans: warning: {warning}")
    for finding in findings:
        print(f"plans: {finding}")
    if findings:
        print(f"\n{len(findings)} finding(s). The files have to agree with the convention.")
        return 1
    tail = f", {len(warnings)} warning(s)" if warnings else ""
    print(f"plans: {len(folders)} folder(s) agree with the convention{tail}")
    return 0


def folders_on_refs(repo: Path) -> dict[str, dict[str, list[str]]]:
    """Which plan folders exist on every branch, as {number: {name: [refs]}}.

    Read-only and with no checkout: a folder number is claimed by whoever spins the
    folder off, and a branch that has not merged is invisible to anyone counting
    folders in the working tree.
    """
    refs = subprocess.run(
        ["git", "-C", str(repo), "for-each-ref", "--format=%(refname:short)",
         "refs/heads", "refs/remotes"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    seen: dict[str, dict[str, list[str]]] = {}
    for ref in refs:
        listing = subprocess.run(
            ["git", "-C", str(repo), "ls-tree", "-d", "--name-only", ref, "plans/"],
            capture_output=True, text=True,
        )
        for line in listing.stdout.split():
            name = line.split("/", 1)[-1]
            match = FOLDER.match(name)
            if match:
                seen.setdefault(match.group(1), {}).setdefault(name, []).append(ref)
    return seen


def cmd_branches(args: argparse.Namespace) -> int:
    repo = args.root.parent
    seen = folders_on_refs(repo)
    collisions = {n: names for n, names in seen.items() if len(names) > 1}
    for number in sorted(seen):
        names = seen[number]
        collides = number in collisions
        for name, refs in sorted(names.items()):
            # The full ref list is what a collision needs and what everything else
            # does not: the same folder on nine refs is a branch that has not merged.
            where = ", ".join(sorted(refs)) if collides or len(refs) <= 3 else f"{len(refs)} refs"
            print(f"{'COLLISION' if collides else '         '} {number}  {name:<26} {where}")
    print()
    if collisions:
        print(f"{len(collisions)} number(s) used by more than one folder.")
        print("Pick a free number with a person, then: plans.py rename <folder> <NN>")
        return 1
    print(f"{len(seen)} number(s) across the refs, each used by one folder")
    return 0


def cmd_rename(args: argparse.Namespace) -> int:
    """Renumber a folder, and fix the sibling links that point at it.

    The new number is an argument rather than `max + 1`: two people renaming into
    the same free slot on their own branches reproduce the collision one number
    along, so a person picks it, knowing what `branches` reported.
    """
    repo = args.root.parent
    old = args.folder.rstrip("/").split("/")[-1]
    source = args.root / old
    match = FOLDER.match(old)
    if not match:
        raise PlansError(f"{old}: not a plan folder name (NN_name)")
    if not source.is_dir():
        raise PlansError(f"{source}: no such folder")
    if not re.fullmatch(r"\d{2,3}", args.number):
        raise PlansError(f"{args.number}: a folder number is two or three digits")
    new = f"{args.number}_{match.group(2)}"
    if (args.root / new).exists():
        raise PlansError(f"{new} already exists; run `branches` and pick a free number")

    stale = check_citations(repo)
    if stale:
        for finding in stale:
            print(f"plans: {finding}")
        raise PlansError(
            "something outside plans/ cites a plan folder. Fix that first: renaming "
            "would mean editing code to keep a diary reference alive"
        )

    subprocess.run(["git", "-C", str(repo), "mv", f"plans/{old}", f"plans/{new}"], check=True)
    touched = []
    for md in sorted(args.root.glob("*/*.md")):
        text = md.read_text(encoding="utf-8")
        if old not in text:
            continue
        md.write_text(text.replace(old, new), encoding="utf-8")
        touched.append(f"{md.relative_to(args.root)}: {text.count(old)} reference(s)")
    print(f"renamed {old} -> {new}")
    for line in touched:
        print(f"  {line}")
    if not touched:
        print("  no sibling folder pointed at it")
    print("\nRun scripts/check.sh: the links gate is what proves nothing dangles.")
    print("Then commit: `branches` reads refs, so it keeps reporting the collision until you do.")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    skipped: list[str] = []
    folders = load(args.root, skipped)
    if args.index:
        folders = [f for f in folders if in_range(f.number, args.index)]
    if args.status:
        folders = [
            f
            for f in folders
            if f.status == args.status or any(p.status == args.status for p in f.phases)
        ]
    if not folders:
        print("no folder matches")
        return 0
    table = rows(folders)
    if args.out:
        write_out(table, args.out)
    else:
        print_table(table)
    if args.index:
        skipped = [s for s in skipped if in_range(s[:2], args.index)]
    if any("*" in row[5] or "?" in row[5] for row in table):
        print("\nneeds: * a prerequisite that is not done, ? one not in this tree (needs a merge)")
    if skipped and not args.out:
        print(f"\nno 00_start.md, so not listed: {', '.join(skipped)}")
    if args.index or args.status:
        for folder in sorted(folders, key=lambda f: f.number):
            if not folder.phases and not folder.sides:
                continue
            print(f"\n{folder.number}_{folder.name}")
            for phase in folder.phases:
                print(f"  {phase.path.name:<46} {phase.status or '-'}")
            for side in folder.sides:
                print(f"  {side.name:<46} (side-document)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", action="version", version=f"plans.py {VERSION}")
    parser.add_argument(
        "--root",
        type=Path,
        help="the plans directory (default: <repo>/plans, via git rev-parse)",
    )
    sub = parser.add_subparsers(dest="command")
    listing = sub.add_parser("list", help="one line per folder, by priority")
    listing.add_argument("--status", choices=STATUSES, help="only this status")
    listing.add_argument("--index", help="NN or NN-MM")
    listing.add_argument("--out", type=Path, help="write .md or .html instead of printing")
    listing.set_defaults(func=cmd_list)

    checking = sub.add_parser("check", help="mechanical faults in the plan files")
    checking.add_argument(
        "--citations",
        action="store_true",
        help="also check that nothing outside plans/ cites a specific plan folder",
    )
    checking.set_defaults(func=cmd_check)

    branches = sub.add_parser(
        "branches", help="folder numbers across every branch, and any collision"
    )
    branches.set_defaults(func=cmd_branches)

    renaming = sub.add_parser("rename", help="renumber a folder and fix sibling links")
    renaming.add_argument("folder", help="the folder to renumber, e.g. 21_plans_query_skill")
    renaming.add_argument("number", help="its new number, two or three digits, chosen by a person")
    renaming.set_defaults(func=cmd_rename)

    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        args = parser.parse_args((argv or []) + ["list"])
    try:
        args.root = args.root or default_root()
        return args.func(args)
    except PlansError as exc:
        print(f"plans: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
