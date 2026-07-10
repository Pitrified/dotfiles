---
name: concert-study-sheet
description: >
  Build a lyrics study site for an upcoming concert (bilingual when the artist does not sing in English): research the setlist,
  resolve Genius original + English-translation pages, scrape and merge them line by line,
  and emit a local HTML site plus a single self-contained file for the phone.
  Trigger on: "study sheet for <artist> concert", "setlist with lyrics",
  "merge Genius translations", "lyrics site", "prep for the <artist> show".
allowed-tools: Bash, Read, Write, Edit, WebSearch, WebFetch
---

## Concert study sheet

Turn an upcoming concert into a study site: per-song pages showing the original lyrics
with a toggleable English translation under each line, section accents for chorus and
high-energy moments, and a one-file version to carry on a phone.
The key insight: Genius hosts both the original and a "Genius English Translations" page
for popular songs, both server-rendered and scrapeable with plain curl;
the two transcriptions almost align, and the residue is small enough for a manual pass.

The pipeline ships in this skill's `assets/` folder, already generalized:
copy it into the new project and fill in the data.
It is a head start, not a turnkey run: every new artist/language needs the manual passes
below (URL verification, translation overrides, header vocabulary, per-page quirks).
A complete built example may still exist at `~/ephem/concerti/`.

English-language artist (verified on brunomars2026): the pipeline degrades cleanly
to a monolingual site. Set `lang: "en"` and `en_slug = None` for every song;
the translation search (step 2), the merge (step 5) and the overrides pass (step 6)
all become no-ops and `overrides.json` stays empty.
The code handles the two edge cases this mode hits: `song_body()` guards the
orig/translation path collision (both resolve to `NN_slug.en.html` when lang is en)
and `genius_links()` drops the "no English translation" note when `LANG == "en"`.

Non-Latin-script artist (verified on btsmonaco2026, Korean): for readability use the
"Genius Romanizations" page as the original (`orig_slug`) and the
"Genius English Translations" page as the translation; set `lang` to the
BCP-47 romanized code (e.g. `ko-Latn`). Both community pages label sections in
English, so header matching is exact-key and needs no `HEADER_WORDS` entry.
Songs the artist sings in English get their normal page and `en_slug = None`.
Expect more manual-pass work than a same-script pair: the two community
transcriptions diverge more in section structure and line granularity.

Runtime: the scripts are a [uv](https://docs.astral.sh/uv/) project;
`uv run <script>.py` resolves the `pyproject.toml` deps (beautifulsoup4, rapidfuzz)
with no venv management. `site/app.js` is plain browser JS; to syntax-check it without
node, `gjs` works on GNOME boxes (see gotchas).

### Process

0. [deterministic] Set up the project from `assets/`.
   Create `<project>/`, copy `assets/scripts/` and `assets/site/` into it,
   adapt `assets/README.template.md` into the project README.
   Fill `scripts/songs.py`: the `PROJECT` dict (slug, title, heading, meta, note,
   source `lang`, placeholder slots) and the `SONGS` list; `NOTES` for per-song remarks.
   Everything project-specific lives in `songs.py` + the two json files;
   `build_site.py`, `download_raw.py`, `style.css`, `app.js` should need no edits.

1. [judgment] Research the setlist.
   Use the most recent setlist.fm show of the same tour leg, cross-checked against the
   setlist.fm "average setlist" for the tour and the Wikipedia tour page.
   Note structural quirks as `PROJECT["placeholders"]`, e.g. a rotating one-night-only slot.
   Write an overview markdown (refs/) with one table row per song: number, title, album,
   original lyrics link, translation link.

2. [deterministic] Resolve canonical Genius URLs.
   Never trust a guessed slug: verify with
   `curl -s -o /dev/null -w "%{http_code} %{url_effective}" -A "<browser UA>" -L <url>`.
   A 301 reveals the canonical slug (feature credits are part of it,
   e.g. `Bad-bunny-and-chencho-corleone-me-porto-bonito-lyrics`).
   For anything not found by guessing, especially translation pages, query the
   unauthenticated JSON search endpoint with a browser User-Agent:
   `https://genius.com/api/search/multi?q=<artist>%20<title>%20English%20Translation`
   and take `response.sections[].hits[] | select(.index=="song") | .result.url`.
   Not every song has a translation page; `en_slug = None` records the gap,
   never invent a URL.

3. [deterministic] Download raw pages: `uv run download_raw.py`
   (assets/scripts/download_raw.py) fetches into `raw/` as
   `NN_slug.<lang>.html` / `NN_slug.en.html`: sequential curl with a browser UA and
   0.5 s sleep, `.part` temp file renamed on HTTP 200, skips existing unless `--force`.

4. [deterministic] Parse lyrics from a page: `extract_lines()` in
   assets/scripts/build_site.py. BeautifulSoup over `[data-lyrics-container="true"]`
   (a page has several, split around ad slots); `decompose()` every
   `[data-exclude-from-selection="true"]` child, `<br>` -> newline, split lines.
   Section headers are lines matching `^\[[^\]]{1,80}\]$`.

5. [deterministic] Merge original and translation: `merge()` + `section_key()` in
   assets/scripts/build_site.py. Split into sections on header lines, drop all-blank
   sections, normalize headers to a language-neutral key via `HEADER_WORDS[lang]`
   (es verified; pt/it best effort, verify on first use; unmapped languages fall back
   to exact-key matching), align the key sequences with `difflib.SequenceMatcher`,
   pair lines by position inside matched sections, and consume translation lines in
   order across divergent stretches, appending leftovers rather than dropping them.
   Two repairs cover sections that exist on only one page (verified on btsmonaco2026):
   leftover translation lines first fill untranslated originals at the tail of the
   previous section, and a matched section's surplus translation lines are carried
   into a following unmatched stretch (the translation page merged two sections).
   New language? Add its header vocabulary to `HEADER_WORDS` in the assets copy too,
   so the next project inherits it.

6. [judgment] Manual translation pass.
   After building, list every original line without a translation
   (grep the generated pages for `class="orig"` spans without a following `class="en"`).
   Translate them yourself into `overrides.json` (`slug -> {exact original line: translation}`),
   applied at render time; an override also beats a bad automatic pairing.
   Rebuild and assert 0 uncovered lines programmatically.

7. [deterministic] Emit the site: `uv run build_site.py`.
   Per-song pages plus index sharing `site/style.css` / `site/app.js`
   (toggle button flips a class on `<html>`, choice kept in localStorage under keys
   derived from the `data-project` attribute the build stamps), and
   `site/<project slug>.html`, the one-file version with CSS/JS inlined,
   a TOC of anchors and `#top` links, generated by the same build so content never diverges.

8. [mixed] Section accents: `section_classes()` in assets/scripts/build_site.py.
   Auto chorus: header key starts with chorus/post-chorus/refrain, plus
   `rapidfuzz.fuzz.token_set_ratio >= 90` against a labeled chorus of the same song for
   unlabeled reprises (min ~40 chars to avoid short-text false positives).
   Manual "energy" pass: `energy.json` with `slug -> ["[Header]", "[Header]@n"]`
   selectors (`@n` = nth occurrence, absent = all). Sections carry
   `data-sel="[Header]@n"` and songs `data-slug`, so the page's "tag vibes" mode can
   toggle classes by click, persist to localStorage, and export build-ready `energy.json`.

Project shape: `refs/` overview, `raw/` cache, `scripts/` uv project
(code: `build_site.py`, `download_raw.py`, `pyproject.toml`;
data: `songs.py`, `overrides.json`, `energy.json`),
`site/` output, top-level README with rebuild and "open in browser" instructions.
`assets/genius_collapse_repeats.user.js` is an optional extra: a Tampermonkey script
that collapses repeated sections when reading on genius.com itself.

### Rules

- Verify every Genius URL with curl before putting it anywhere.
  Why: guessed slugs 301 to canonical multi-artist slugs or 404 outright;
  several first guesses were wrong in the reference build.
- Drop all-blank sections before aligning (already in `split_sections`; keep it).
  Why: original pages open with an empty credit section (`[Letra de "..."]` on Spanish
  pages) that has no counterpart on the translation page; it silently shifted every
  section pairing by one, mispairing all lyrics while looking plausible.
- Treat `lyricsPlaceholderReason` as "no lyrics" only when its value is a string.
  Why: the key exists on every page with value null; substring-checking the key marked
  every song as untranscribed. A string value (e.g. "unreleased") means Genius has no
  transcription; render an explicit note instead of an empty page.
- When original and translation line counts differ wildly, suspect different song
  versions, not merge bugs.
  Why: the "Diles" original page was the solo version while the translation covered the
  5-artist version actually performed live; the fix was swapping the source link,
  after which alignment was clean.
- Fill any templating placeholders in one pass.
  Why: a second `str.format` over a template already holding lyrics breaks on literal
  `{}` in the content.
- Download sequentially with a delay.
  Why: a parallel curl burst against genius.com returned exit-code-000 failures;
  sequential with 0.5-1 s sleep was fully reliable.
- After every merge change, re-check coverage and spot-check pairings programmatically
  (count rows missing a translation per page, print a sample side by side).
  Why: alignment bugs look fine in the build log and only show up in the rendered rows.
- Keep the code files project-agnostic; project facts go in `songs.py`/the jsons only.
  Why: the next concert copies the code from `assets/`; anything hardcoded there is a
  bug waiting for project two. Improvements to the code belong back in `assets/`.

### Gotchas

- Translation pages relabel sections with performers (`[Chorus: X & Y]` vs `[Coro]`)
  and translate the words -> exact-header matching never works across languages;
  match on the normalized key (`HEADER_WORDS`).
- The two transcriptions differ in line granularity (ad-libs merged or split), so a few
  lines per song stay untranslated even when sections match; that is what the manual
  overrides pass is for; do not chase perfect automatic alignment.
- A static page cannot rewrite its own file; "edit in the browser" means
  DOM + localStorage + an export button producing config the build accepts.
  Keep the selector language identical between the page (`data-sel`) and the build
  config so the export is paste-ready.
- No JS runtime for checking generated app.js? `gjs` is often present on GNOME boxes:
  a run that only fails with "document is not defined" proves the syntax is fine.
- Genius is fine with plain curl but only with a browser User-Agent; the search API too.
- Some Genius pages prefix every lyrics line with invisible format characters
  (U+200E left-to-right marks on BTS romanizations), silently breaking header and
  blank-line detection; `extract_lines()` strips them (the `INVISIBLE` table).
- An override mapping a line to `""` clears a wrong automatic pairing on a line
  that needs no translation (e.g. an English ad-lib inside a Korean verse).
