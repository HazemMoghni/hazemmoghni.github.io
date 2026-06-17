# hazemh.com

Personal site for Hazem Hassan — a single self-contained `index.html`.

## What it is

- One file: inline CSS and JS, no dependencies, no build step.
- Minimal left-aligned single column. System sans for prose, system mono for meta
  lines, one indigo accent, light/dark aware via `prefers-color-scheme`, quiet
  page-load fade (respects `prefers-reduced-motion`).

## Auto-updating bits

- **Penn standing** (e.g. "rising sophomore" → "sophomore" → "rising junior" …) is
  computed on load from a stored academic calendar in the `<script>` at the bottom.
  To maintain, update the `FALL_START` and `SPRING_END` maps with official dates from
  [almanac.upenn.edu/penn-academic-calendar](https://almanac.upenn.edu/penn-academic-calendar).
  Values marked `EST` are estimates and should be replaced once Penn publishes them.
- **Footer year** updates via JS.
- The "Robotics researcher · DAIR Lab, Penn" line is a manual field; edit it by hand
  when the role changes.

Note: writing entries are intentionally maintained by hand. Do **not** pull Substack
posts via client-side RSS — CORS fails on GitHub Pages. Auto-updating writing would
need a proxy or a build step.

## Deploy (GitHub Pages)

This serves as-is — `.nojekyll` tells Pages to skip Jekyll processing.

Either:
- name the repo `<username>.github.io` with this `index.html` at the root of `main`, or
- use any repo and set **Settings → Pages → Deploy from a branch → `main` / root**.

For the custom domain `hazemh.com`, add it under **Settings → Pages → Custom domain**
(GitHub will create a `CNAME` file) and point DNS at GitHub Pages.
