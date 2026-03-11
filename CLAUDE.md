# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Static personal link-tree site for Victor Fragoso. No build system, no dependencies, no package manager — open `index.html` directly in a browser to preview.

## Structure

- `index.html` — main link-tree page (root)
- `victor/index.html` — "About" page with professional bio; references assets via `../` relative paths
- `styles/main.css` — single shared stylesheet for both pages
- `images/` — profile photo (`fragoso.jpg`), favicon, and SVG ornament under `images/ornaments/`

## Key Design Details

**Avatar ornament:** `images/ornaments/photo-ornament.svg` is loaded as an `<img>` with inline `onload`/`onerror` handlers that toggle the `.ornament-loaded` class on `.avatar-shell`. When the SVG loads, CSS `::before`/`::after` pseudo-elements (CSS-only fallback rings) are hidden. Do not remove these handlers.

**CSS variables** (defined in `:root`): `--bg`, `--text`, `--button`, `--button-hover`, `--button-text`, `--muted`. Use these for any color additions.

**Font:** Google Fonts `Patrick Hand` loaded via CDN. Both pages include the same `<link>` tags.

**Adding a link button:** copy an `<a class="link-button">` element inside `<section class="links">`. The `::before` pseudo-element automatically prepends a `✱` glyph — no extra markup needed.
