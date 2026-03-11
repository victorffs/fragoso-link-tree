# Napkin Runbook

## Curation Rules
- Re-prioritize on every read.
- Keep recurring, high-value notes only.
- Max 10 items per category.
- Each item includes date + "Do instead".

## Execution & Validation (Highest Priority)
1. **[2026-03-10] No build system — static HTML/CSS only**
   Do instead: edit `index.html` and `styles/main.css` directly; no npm, no bundler, no server needed.

2. **[2026-03-10] Two HTML entry points exist**
   Do instead: check both `index.html` (root) and `victor/index.html` when making layout/style changes — both may need updating.

## Shell & Command Reliability
1. **[2026-03-10] No package.json or lock files**
   Do instead: skip any `npm install` or dependency steps; all assets are local or CDN (Google Fonts).

## Domain Behavior Guardrails
1. **[2026-03-10] SVG ornament uses JS-triggered class `ornament-loaded`**
   Do instead: keep `onload`/`onerror` inline handlers on the ornament `<img>` — removing them breaks the avatar reveal animation.

2. **[2026-03-10] CSS lives in `styles/main.css` (not inline)**
   Do instead: put all style changes in `styles/main.css`; avoid adding inline styles to HTML.

3. **[2026-03-10] Images are in `images/` with ornament refs under `images/ornaments/`**
   Do instead: place new assets in the correct subfolder and reference with relative paths from `index.html`.

## User Directives
1. **[2026-03-10] Personal link-tree site for Victor Fragoso — Software Engineer**
   Do instead: keep content and tone professional; links are Portfolio, LinkedIn, GitHub, Hackster.
