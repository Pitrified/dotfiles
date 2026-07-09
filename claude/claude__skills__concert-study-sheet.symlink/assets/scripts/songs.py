"""Per-project data: the concert and its setlist. This file is yours;
the code files (build_site.py, download_raw.py) come from the
concert-study-sheet skill and should stay project-agnostic.

Fill PROJECT and SONGS for the new concert; keep numbers in sync with the
refs/ overview. Slots with unknown content (e.g. a rotating exclusive song)
get a PROJECT["placeholders"] entry instead of a SONGS entry.
en_slug is None where Genius has no English translation page.
"""

GENIUS = "https://genius.com/"

PROJECT = {
    # storage-key prefix and one-file output name (site/<slug>.html)
    "slug": "artist2026",
    "title": "Artist - City 2026",
    "heading": "Artist - City, 1-2 Month 2026",
    # meta and note are raw HTML (entities allowed), title/heading are text
    "meta": "Tour Name &middot; Venue",
    "note": "Setlist per the <city> show of <date>.",
    # source language code: raw/NN_slug.<lang>.html, header vocab, html lang=
    "lang": "es",
    # unknown setlist slots: (num, label, album-style note), placed by number
    "placeholders": [
        # ("22", "exclusive song", "announced on the night"),
    ],
}

# optional per-song note rendered above the lyrics
NOTES = {
    # "some_slug": "Sung over the tape with the opening band.",
}

SONGS = [
    # (num, file_slug, title, album, orig_slug, en_slug)
    # ("01", "la_mudanza", "LA MuDANZA", "Debí Tirar Más Fotos (2025)",
    #  "Bad-bunny-la-mudanza-lyrics",
    #  "Genius-english-translations-bad-bunny-la-mudanza-english-translation-lyrics"),
]
