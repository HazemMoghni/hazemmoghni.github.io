#!/usr/bin/env python3
"""Regenerate the Writing list in index.html from the Substack RSS feed.

Replaces everything between the WRITING:START and WRITING:END markers with the
N most recent posts. Stdlib only — no pip installs needed on the runner.
"""
import html
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED = "https://hazemhasan.substack.com/feed"
COUNT = 3
INDEX = pathlib.Path(__file__).resolve().parent.parent / "index.html"

START = "        <!-- WRITING:START (auto-generated from Substack; do not edit by hand) -->"
END = "        <!-- WRITING:END -->"


def fetch_items():
    req = urllib.request.Request(FEED, headers={"User-Agent": "Mozilla/5.0 (hazemh.com writing-updater)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    root = ET.fromstring(data)
    return root.findall("./channel/item")[:COUNT]


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
    if not items:
        raise SystemExit("No items found in feed; aborting without changes.")
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
