# <project slug>

Study material for the <artist> concert(s), <venue>, <dates>.

## Layout

- `refs/` - the setlist overview (one table row per song with Genius links).
- `raw/` - the Genius lyrics pages as downloaded, one file per song per language:
  `NN_slug.<lang>.html` (original) and `NN_slug.en.html` (Genius English Translations page).
  Kept as the offline reference; the site is built from these.
- `scripts/` - a small uv project that downloads `raw/` and builds `site/`.
  Code files (`build_site.py`, `download_raw.py`) come from the concert-study-sheet skill;
  data files are per-project: `songs.py` (concert config + setlist),
  `overrides.json` (manual translation pass: exact original line -> English line),
  `energy.json` (manual high-energy pass: section headers, optional `@n` for the nth occurrence).
- `site/` - the generated local site: one page per song plus `index.html`,
  and `<project slug>.html`, the whole site as a single self-contained file for a phone.
  `style.css` and `app.js` are hand-written (from the skill), the rest is overwritten on every build.

## Build

Needs [uv](https://docs.astral.sh/uv/); dependencies are in `scripts/pyproject.toml`.

```sh
cd scripts
uv run download_raw.py   # fetch Genius pages into raw/ (skips existing; --force to refetch)
uv run build_site.py     # regenerate site/ from raw/
```

## Read

Fully local, no server needed: open `site/index.html` in a browser.
On a phone, copy the single file `site/<project slug>.html` over and open it in the browser.

Sections are color-coded (legend at the top of each page):
chorus/refrain sections get the chorus accent (detected from the header plus fuzzy similarity for unlabeled reprises);
high-energy sections get the energy accent, hand-picked in `scripts/energy.json`, which wins when a section is both.

Vibe tagging from the page itself: press "tag vibes" in the top bar, then click any section
to toggle its energy accent; clicks are saved in that browser (localStorage).
To make them permanent, press "copy vibes json", paste over `scripts/energy.json` and rebuild.

The "show translation" button toggles the English line under each original line;
the choice is remembered across pages (localStorage).
