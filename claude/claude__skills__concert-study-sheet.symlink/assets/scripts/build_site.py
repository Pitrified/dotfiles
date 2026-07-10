"""Build the local lyrics site from the raw Genius pages.

Usage: uv run build_site.py
Reads raw/NN_slug.{<lang>,en}.html, writes site/NN_slug.html plus
site/index.html, and the one-file version site/<project slug>.html;
site/style.css and site/app.js are hand-written and only read.

Merging: both pages are split into sections on [Header] lines. Sections are
matched by header type and order (Coro <-> Chorus, Verso n <-> Verse n, ...)
with difflib, since a few translations split verses differently than the
original; lines inside matched sections are paired by position. Where the
section structures diverge, translation lines are consumed in order against
the original sections of that stretch, so nothing is dropped.

Lines the merge leaves untranslated get a manual translation from
overrides.json (per song slug, exact original line -> English line); an
override also wins over the automatic pairing when both exist.

Section accents: chorus/refrain sections are detected from the header
(plus rapidfuzz similarity for unlabeled reprises of a labeled chorus) and
get the chorus accent; energy.json is a manual list of high-energy sections
per song, which get the energy accent instead.
"""

import html
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

from bs4 import BeautifulSoup
from rapidfuzz import fuzz

from songs import GENIUS, NOTES, PROJECT, SONGS

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
SITE = ROOT / "site"
LANG = PROJECT["lang"]
OVERRIDES = json.loads((Path(__file__).parent / "overrides.json").read_text())
ENERGY = json.loads((Path(__file__).parent / "energy.json").read_text())

HEADER_RE = re.compile(r"^\s*\[[^\]]{1,80}\]\s*$")

# invisible format characters some Genius pages prefix on every line
# (e.g. U+200E left-to-right marks); they break header/blank detection
INVISIBLE = dict.fromkeys(
    map(ord, "\u200b\u200c\u200d\u200e\u200f\u2060\ufeff")
)


class LyricsNotFound(RuntimeError):
    pass


def extract_lines(path: Path) -> list[str]:
    """All lyrics lines of a Genius page, headers included, '' for stanza gaps."""
    text = path.read_text(encoding="utf-8")
    if re.search(r'lyricsPlaceholderReason\\?":\\?"', text):
        # Genius has the song but no transcription (e.g. marked "unreleased");
        # the placeholder key is null on normal pages
        return []
    soup = BeautifulSoup(text, "html.parser")
    containers = soup.select('[data-lyrics-container="true"]')
    if not containers:
        raise LyricsNotFound(f"no lyrics containers in {path.name}")
    lines: list[str] = []
    for c in containers:
        # inline interstitials ("You might also like", ads) and the header
        # widget live inside the container; drop them before reading text
        for junk in c.select('[data-exclude-from-selection="true"]'):
            junk.decompose()
        for br in c.find_all("br"):
            br.replace_with("\n")
        for raw in c.get_text().split("\n"):
            lines.append(raw.translate(INVISIBLE).strip())
    # collapse runs of blank lines and trim the edges
    out: list[str] = []
    for line in lines:
        if line == "" and (not out or out[-1] == ""):
            continue
        out.append(line)
    while out and out[-1] == "":
        out.pop()
    return out


Section = tuple[str | None, list[str]]


def split_sections(lines: list[str]) -> list[Section]:
    sections: list[Section] = []
    current: list[str] = []
    sections.append((None, current))
    for line in lines:
        if HEADER_RE.match(line):
            current = []
            sections.append((line, current))
        else:
            current.append(line)
    # drop empty sections, notably the credit header ("[Letra de ...]") that
    # opens every original page and has no counterpart on the translation
    return [(h, ls) for h, ls in sections if any(ls)]


# section-header vocabulary per source language, mapped to the English words
# Genius translation pages use; unknown words pass through unchanged, so an
# unmapped language degrades to exact-key matching instead of breaking.
# es is verified (badbunny2026); pt and it are best effort, check on first use.
HEADER_WORDS = {
    "es": {
        "coro": "chorus",
        "pre-coro": "pre-chorus",
        "post-coro": "post-chorus",
        "verso": "verse",
        "puente": "bridge",
        "interludio": "interlude",
        "estribillo": "chorus",
        "refrán": "refrain",
    },
    "pt": {
        "refrão": "chorus",
        "pré-refrão": "pre-chorus",
        "pós-refrão": "post-chorus",
        "verso": "verse",
        "ponte": "bridge",
        "interlúdio": "interlude",
        "coro": "chorus",
    },
    "it": {
        "ritornello": "chorus",
        "pre-ritornello": "pre-chorus",
        "post-ritornello": "post-chorus",
        "strofa": "verse",
        "ponte": "bridge",
        "interludio": "interlude",
    },
}
WORDS = HEADER_WORDS.get(LANG, {})


def section_key(header: str | None) -> str:
    """Language-neutral header key: '[Verso 1: X]' and '[Verse 1: Y]' match."""
    if not header:
        return ""
    s = header.strip().strip("[]").split(":")[0].strip().lower()
    return " ".join(WORDS.get(w, w) for w in s.split())


def pair(orig_lines: list[str], en_lines: list[str]) -> list[tuple[str, str]]:
    return [
        (orig_lines[k] if k < len(orig_lines) else "",
         en_lines[k] if k < len(en_lines) else "")
        for k in range(max(len(orig_lines), len(en_lines)))
    ]


def merge(orig: list[str], en: list[str] | None) -> list[Section]:
    """Sections whose lines are (original, en) pairs, rendered-ready."""
    orig_secs = split_sections(orig)
    en_secs = split_sections(en) if en else []
    if not en_secs:
        return [(h, [(l, "") for l in ls]) for h, ls in orig_secs]
    ka = [section_key(h) for h, _ in orig_secs]
    kb = [section_key(h) for h, _ in en_secs]
    merged: list[Section] = []
    matcher = SequenceMatcher(None, ka, kb, autojunk=False)
    opcodes = matcher.get_opcodes()
    carry: list[str] = []  # en surplus handed to the following stretch
    for n, (tag, i1, i2, j1, j2) in enumerate(opcodes):
        if tag == "equal":
            nxt = opcodes[n + 1][0] if n + 1 < len(opcodes) else None
            for off in range(i2 - i1):
                header, orig_lines = orig_secs[i1 + off]
                en_lines = en_secs[j1 + off][1]
                # surplus en lines at the tail of the last matched section
                # usually belong to the following unmatched original section
                # (the translation merged two sections into one)
                if (nxt in ("delete", "replace") and off == i2 - i1 - 1
                        and len(en_lines) > len(orig_lines)):
                    carry = [t for t in en_lines[len(orig_lines):] if t]
                    en_lines = en_lines[:len(orig_lines)]
                merged.append((header, pair(orig_lines, en_lines)))
            continue
        # structures diverge here: feed the translation lines of this
        # stretch to its original sections in order
        en_pool = carry + [l for _, ls in en_secs[j1:j2] for l in ls]
        carry = []
        pos = 0
        for header, orig_lines in orig_secs[i1:i2]:
            merged.append((header, pair(orig_lines, en_pool[pos:pos + len(orig_lines)])))
            pos += len(orig_lines)
        leftover = [t for t in en_pool[pos:] if t]
        if leftover and merged:
            # an en-only section often continues the previous one (the original
            # merged two sections): fill its untranslated lines in order before
            # appending what remains as translation-only rows
            header, rows = merged[-1]
            rows = list(rows)
            for k, (o, t) in enumerate(rows):
                if not leftover:
                    break
                if o and not t:
                    rows[k] = (o, leftover.pop(0))
            merged[-1] = (header, rows + [("", t) for t in leftover])
    return merged


PAGE = """<!doctype html>
<html lang="{lang}" data-project="{project}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{num} - {title}</title>
<link rel="stylesheet" href="style.css">
<script src="app.js" defer></script>
</head>
<body>
<nav>
  <span class="crumbs">{prev}<a href="index.html">setlist</a>{next}</span>
  <span class="btns"><button id="vibe-export" hidden>copy vibes json</button><button id="vibe-toggle" hidden>tag vibes</button><button id="toggle-en" hidden>show translation</button></span>
</nav>
<header>
  <h1>{num}. {title}</h1>
  <p class="meta">{album} &middot; {links}</p>
  <p class="meta legend"><span class="sw-chorus">&#9632;</span> chorus &middot; <span class="sw-energy">&#9632;</span> high energy</p>
</header>
<main data-slug="{slug}">
{body}
</main>
</body>
</html>
"""


def esc(s: str) -> str:
    return html.escape(s, quote=False)


CHORUS_WORDS = {"chorus", "post-chorus", "refrain"}


def is_chorus_header(header: str | None) -> bool:
    words = section_key(header).split()
    return bool(words) and words[0] in CHORUS_WORDS


def section_classes(merged: list[Section], slug: str) -> list[str]:
    """CSS classes per section: 'chorus' detected, 'energy' from energy.json."""
    classes: list[set[str]] = [set() for _ in merged]
    texts = [" ".join(e for e, _ in rows if e) for _, rows in merged]
    chorus_idx = [i for i, (h, _) in enumerate(merged) if is_chorus_header(h)]
    for i in chorus_idx:
        classes[i].add("chorus")
    for i, txt in enumerate(texts):
        if classes[i] or len(txt) < 40:
            continue
        # unlabeled reprise of a labeled chorus (e.g. an outro echoing it)
        if any(fuzz.token_set_ratio(txt, texts[j]) >= 90 for j in chorus_idx):
            classes[i].add("chorus")
    seen: dict[str, int] = {}
    for i, (header, _) in enumerate(merged):
        if not header:
            continue
        seen[header] = seen.get(header, 0) + 1
        for sel in ENERGY.get(slug, []):
            base, _, n = sel.partition("@")
            if base == header and (not n or int(n) == seen[header]):
                classes[i].add("energy")
    return [" ".join(sorted(c)) for c in classes]


def song_body(num, slug) -> str:
    """The lyrics of one song as HTML sections, translations merged in."""
    orig_path = RAW / f"{num}_{slug}.{LANG}.html"
    en_path = RAW / f"{num}_{slug}.en.html"
    orig_lines = extract_lines(orig_path)
    en_lines = None
    # en_path == orig_path when the source language is English: no translation
    if en_path != orig_path and en_path.exists():
        en_lines = extract_lines(en_path)
    over = OVERRIDES.get(slug, {})
    parts = []
    if not orig_lines:
        parts.append('<p class="meta">Genius has no transcription for this song.</p>')
    if slug in NOTES:
        parts.append(f'<p class="meta">{esc(NOTES[slug])}</p>')
    merged = merge(orig_lines, en_lines)
    seen: dict[str, int] = {}
    for (header, rows), cls in zip(merged, section_classes(merged, slug)):
        attrs = f' class="{cls}"' if cls else ""
        if header:
            # stable section id, same "[Header]@n" language as energy.json;
            # lets the page's vibe-tagging mode export build-ready selectors
            seen[header] = seen.get(header, 0) + 1
            attrs += f' data-sel="{html.escape(header)}@{seen[header]}"'
        parts.append(f"<section{attrs}>")
        if header:
            parts.append(f"<h3>{esc(header)}</h3>")
        for e, t in rows:
            if not e and not t:
                parts.append('<div class="gap"></div>')
                continue
            t = over.get(e, t)
            en_span = f'<span class="en">{esc(t)}</span>' if t else ""
            parts.append(
                f'<div class="line"><span class="orig">{esc(e)}</span>{en_span}</div>'
            )
        parts.append("</section>")
    return "\n".join(parts)


def genius_links(orig_slug, en_slug) -> str:
    if en_slug:
        en_link = f' &middot; <a href="{GENIUS}{en_slug}">English translation</a>'
    elif LANG == "en":
        en_link = ""  # English-language concert: no translation page expected
    else:
        en_link = " &middot; no English translation on Genius"
    return f'<a href="{GENIUS}{orig_slug}">Genius</a>{en_link}'


def render_song(num, slug, title, album, orig_slug, en_slug,
                prev_link, next_link) -> str:
    return PAGE.format(
        lang=LANG, project=PROJECT["slug"],
        num=num, title=esc(title), album=esc(album), slug=slug,
        links=genius_links(orig_slug, en_slug),
        body=song_body(num, slug), prev=prev_link, next=next_link,
    )


INDEX_HEADER = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} study sheet</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header>
  <h1>{heading}</h1>
  <p class="meta">{meta}</p>
  <p class="meta">{note}</p>
  <p class="meta legend"><span class="sw-chorus">&#9632;</span> chorus &middot; <span class="sw-energy">&#9632;</span> high energy</p>
</header>
<main>
<ol class="setlist">
"""

INDEX_FOOTER = """</ol>
</main>
</body>
</html>
"""

ONEFILE = """<!doctype html>
<html lang="{lang}" data-project="{project}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{css}
article {{ border-top: 1px solid var(--rule); margin-top: 2rem; padding-top: 0.5rem; }}
article h2 {{ margin: 0.5rem 0 0.2rem; font-size: 1.25rem; }}
.top {{ font-size: 0.85rem; }}
</style>
</head>
<body>
<nav>
  <span class="crumbs"><a href="#top">setlist</a></span>
  <span class="btns"><button id="vibe-export" hidden>copy vibes json</button><button id="vibe-toggle" hidden>tag vibes</button><button id="toggle-en" hidden>show translation</button></span>
</nav>
<header id="top">
  <h1>{heading}</h1>
  <p class="meta">{meta}</p>
  <p class="meta">{note}</p>
  <p class="meta legend"><span class="sw-chorus">&#9632;</span> chorus &middot; <span class="sw-energy">&#9632;</span> high energy</p>
</header>
<main>
<ol class="setlist">
{toc}
</ol>
{articles}
</main>
<script>
{js}
</script>
</body>
</html>
"""


def placeholders_after() -> dict[str, list[str]]:
    """Placeholder <li>s (unknown setlist slots) keyed by the song num they follow."""
    out: dict[str, list[str]] = {}
    nums = [num for num, *_ in SONGS]
    for pnum, label, note in PROJECT.get("placeholders", []):
        prevs = [n for n in nums if int(n) < int(pnum)]
        if not prevs:
            continue
        li = (f'<li value="{int(pnum)}" class="placeholder">{esc(label)}'
              f' <span class="album">{esc(note)}</span></li>')
        out.setdefault(prevs[-1], []).append(li)
    return out


def build_onefile() -> None:
    css = (SITE / "style.css").read_text(encoding="utf-8")
    js = (SITE / "app.js").read_text(encoding="utf-8")
    fillers = placeholders_after()
    toc, articles = [], []
    for num, slug, title, album, orig_slug, en_slug in SONGS:
        toc.append(
            f'<li value="{int(num)}"><a href="#{slug}">{esc(title)}</a>'
            f' <span class="album">{esc(album)}</span></li>'
        )
        toc.extend(fillers.get(num, []))
        articles.append(
            f'<article id="{slug}" data-slug="{slug}">\n'
            f"<h2>{num}. {esc(title)}</h2>\n"
            f'<p class="meta">{esc(album)} &middot; {genius_links(orig_slug, en_slug)}'
            f' &middot; <a class="top" href="#top">&uarr; top</a></p>\n'
            f"{song_body(num, slug)}\n</article>"
        )
    out = ONEFILE.format(
        lang=LANG, project=PROJECT["slug"], title=esc(PROJECT["title"]),
        heading=esc(PROJECT["heading"]), meta=PROJECT["meta"], note=PROJECT["note"],
        css=css, js=js, toc="\n".join(toc), articles="\n".join(articles),
    )
    name = f"{PROJECT['slug']}.html"
    (SITE / name).write_text(out, encoding="utf-8")
    print(f"wrote {name}")


def main() -> None:
    SITE.mkdir(exist_ok=True)
    fillers = placeholders_after()
    index_items = []
    names = [f"{num}_{slug}.html" for num, slug, *_ in SONGS]
    for i, (num, slug, title, album, orig_slug, en_slug) in enumerate(SONGS):
        prev_link = f'<a href="{names[i - 1]}">&larr; prev</a> ' if i else ""
        next_link = (
            f' <a href="{names[i + 1]}">next &rarr;</a>'
            if i + 1 < len(names) else ""
        )
        page = render_song(num, slug, title, album, orig_slug, en_slug,
                           prev_link, next_link)
        (SITE / names[i]).write_text(page, encoding="utf-8")
        print(f"wrote {names[i]}")
        index_items.append(
            f'<li value="{int(num)}"><a href="{num}_{slug}.html">{esc(title)}</a>'
            f' <span class="album">{esc(album)}</span></li>'
        )
        index_items.extend(fillers.get(num, []))
    index_header = INDEX_HEADER.format(
        title=esc(PROJECT["title"]), heading=esc(PROJECT["heading"]),
        meta=PROJECT["meta"], note=PROJECT["note"],
    )
    (SITE / "index.html").write_text(
        index_header + "\n".join(index_items) + INDEX_FOOTER, encoding="utf-8"
    )
    print("wrote index.html")
    build_onefile()


if __name__ == "__main__":
    main()
