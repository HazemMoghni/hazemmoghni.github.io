#!/usr/bin/env python3
"""Regenerate the Writing list in index.html from the Substack RSS feed.

Replaces everything between the WRITING:START and WRITING:END markers with the
N most recent posts. Stdlib only — no pip installs needed on the runner.

Substack sits behind Cloudflare, which 403s requests it fingerprints as bots —
including Python's urllib, especially from datacenter IPs (GitHub Actions). So in
CI the feed is fetched with `curl` (browser-like TLS fingerprint) and the saved
file is passed to this script. Run with no argument and it fetches directly,
which still works from a normal machine for local testing.
"""
import html
import pathlib
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED = "https://hazemhasan.substack.com/feed"
COUNT = 3
INDEX = pathlib.Path(__file__).resolve().parent.parent / "index.html"

START = "        <!-- WRITING:START (auto-generated from Substack; do not edit by hand) -->"
END = "        <!-- WRITING:END -->"

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def items_from_bytes(data):
    items = ET.fromstring(data).findall("./channel/item")
    if not items:
        raise SystemExit("Feed parsed but contained no <item> entries.")
    return items[:COUNT]


def fetch_directly():
    headers = {"User-Agent": UA, "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.5"}
    last = None
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(FEED, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return items_from_bytes(resp.read())
        except Exception as exc:  # noqa: BLE001
            last = repr(exc)
            print(f"attempt {attempt}/3 failed: {last}")
            time.sleep(3)
    raise SystemExit(f"Could not fetch the Substack feed: {last}")


def load_items():
    # CI passes a feed file fetched by curl; otherwise fetch directly.
    if len(sys.argv) > 1:
        return items_from_bytes(pathlib.Path(sys.argv[1]).read_bytes())
    return fetch_directly()


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
    block = render(load_items())
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
