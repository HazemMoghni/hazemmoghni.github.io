#!/usr/bin/env python3
"""Regenerate the Writing list in index.html from the Substack RSS feed.

Replaces everything between the WRITING:START and WRITING:END markers with the
N most recent posts. Stdlib only — no pip installs needed on the runner.

Substack sits behind Cloudflare, which 403s plain `Python-urllib` requests
(especially from datacenter IPs like GitHub Actions runners). So we request with
a full browser User-Agent + headers and retry a few times.
"""
import html
import pathlib
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED = "https://hazemhasan.substack.com/feed"
COUNT = 3
INDEX = pathlib.Path(__file__).resolve().parent.parent / "index.html"

START = "        <!-- WRITING:START (auto-generated from Substack; do not edit by hand) -->"
END = "        <!-- WRITING:END -->"

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": ("application/rss+xml, application/atom+xml, application/xml;q=0.9, "
               "text/xml;q=0.8, */*;q=0.5"),
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
}


def fetch_items():
    last = None
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(FEED, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            items = ET.fromstring(data).findall("./channel/item")
            if items:
                return items[:COUNT]
            last = "feed parsed but had no <item> entries"
        except Exception as exc:  # noqa: BLE001 - report and retry
            last = repr(exc)
        print(f"attempt {attempt}/3 failed: {last}")
        time.sleep(3)
    raise SystemExit(f"Could not fetch the Substack feed: {last}")


def render(items):
    rows = []
    for it in items:
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        dt = parsedate_to_datetime(it.findtext("pubDate"))
        date = f"{dt:%B} {dt.day}, {dt.year}"  # e.g. "May 1, 2026"
        rows.append(
            "        <li>\n"
            f'          <a href="{html.escape(link)}">{html.escape(title, quote=False)}</a>\n'
            f'          <span class="meta mono">{date}</span>\n'
            "        </li>"
        )
    return START + "\n" + "\n".join(rows) + "\n" + END


def main():
    items = fetch_items()
    block = render(items)
    text = INDEX.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        raise SystemExit("WRITING markers not found in index.html; aborting.")
    new_text = pattern.sub(lambda _m: block, text)
    if new_text != text:
        INDEX.write_text(new_text, encoding="utf-8")
        print("index.html updated.")
    else:
        print("No change.")


if __name__ == "__main__":
    main()
