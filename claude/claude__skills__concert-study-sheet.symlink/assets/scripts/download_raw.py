"""Download the raw Genius HTML pages into raw/ via curl.

Usage: uv run download_raw.py [--force]
Skips files that already exist unless --force is given.
"""

import subprocess
import sys
import time
from pathlib import Path

from songs import GENIUS, PROJECT, SONGS

RAW = Path(__file__).resolve().parent.parent / "raw"
LANG = PROJECT["lang"]
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


class DownloadError(RuntimeError):
    pass


def fetch(url: str, dest: Path) -> None:
    tmp = dest.with_suffix(dest.suffix + ".part")
    code = subprocess.run(
        ["curl", "-s", "-L", "-A", UA, "-o", str(tmp),
         "-w", "%{http_code}", url],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    if code != "200":
        tmp.unlink(missing_ok=True)
        raise DownloadError(f"HTTP {code} for {url}")
    tmp.rename(dest)


def main() -> None:
    force = "--force" in sys.argv
    RAW.mkdir(exist_ok=True)
    jobs = []
    for num, slug, _title, _album, orig_slug, en_slug in SONGS:
        jobs.append((RAW / f"{num}_{slug}.{LANG}.html", GENIUS + orig_slug))
        if en_slug:
            jobs.append((RAW / f"{num}_{slug}.en.html", GENIUS + en_slug))
    for dest, url in jobs:
        if dest.exists() and not force:
            print(f"skip  {dest.name}")
            continue
        fetch(url, dest)
        print(f"ok    {dest.name}")
        time.sleep(0.5)


if __name__ == "__main__":
    main()
