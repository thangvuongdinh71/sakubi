# Sakubi — Yesterday's Grammar Guide

A complete, static edition of [Sakubi](https://sakubi.neocities.org/) with a book-style reading interface modeled on [Yokubi](https://yoku.bi/Introduction.html).

## Open it

Open `index.html` directly in your browser. No installation, build, account, API key, or backend is needed. All images, fonts, search data, CSS, and JavaScript are included locally. External learning resources and the embedded YouTube video still require an internet connection.

For a local HTTP preview:

```bash
python -m http.server 8000
```

Visit `http://localhost:8000`.

## Publish on GitHub Pages

1. Copy **the contents of this folder** into your GitHub repository, with `index.html` at its root. Keep `assets/`, all chapter `.html` files, and `.nojekyll`.
2. Commit and push to your repository.
3. Open the repository's **Settings → Pages**.
4. Under **Build and deployment**, choose **Deploy from a branch**.
5. Select your branch (usually `main`) and **/(root)**, then save.

All links are relative, so the same files work in a GitHub project site, a user site, or a custom domain. No base URL changes are needed.

## What is included

- All 54 original main lessons, optional lessons, intermissions, introductory material, license, dedication, resources, and changelog, split into 101 chapters.
- Sakubi branding and original lesson titles, numbering, order, Japanese examples, tables, and ruby markup.
- Yokubi-style navy palette, Open Sans typography, fixed contents sidebar, expandable parts, centered reading column, title bar, and chapter arrows.
- Light, Rust, Coal, Navy, and Ayu themes, remembered when browser storage is available.
- Full-text search across the guide, with Japanese text support; press `S` or `/` to open it.
- Previous/next chapter navigation; use the left/right arrow keys while outside form fields.
- Responsive mobile drawer, keyboard-accessible controls, skip link, and chapter print styles.
- Local assets and search index: core reading works without network requests.
- `Introduction.html` as an alias for the home page. Original `index.html#lesson-id` URLs redirect to corresponding chapters.

This is a restyled **Sakubi** edition, not Yokubi's rewritten curriculum. It does not replace Sakubi's text with Yokubi's text or claim affiliation with either project. The duplicated license block from the start of the original is presented once on the License page. The preface’s zoom links adjust reading text to 100%, 150%, or 250% and remember the size. Print prints the current chapter.

## Edit and rebuild

Edit chapter HTML files directly to make one-off changes. Shared appearance and behavior live in `assets/style.css` and `assets/app.js`.

For source-driven changes, edit `source/sakubi-original.html` and rebuild:

```bash
python -m pip install -r requirements.txt
python build.py
```

The generator replaces chapter HTML files and `assets/search-index.js`. It preserves original grammar text and internal cross-references. Direct edits to generated chapter HTML are overwritten by a rebuild. The build uses a local snapshot; it does not download source or assets. `source/pages.json` lists generated chapters and their hierarchy.

## Credits and licenses

- Original grammar content and Sakubi logos: Sakubi contributors, from https://sakubi.neocities.org/, retrieved October 29, 2026. The original declares its text and logos public domain / CC0. The full original notice is retained in `license.html` and the source snapshot. Its notice about quoted media examples is retained as well.
- Visual reference: Yokubi, https://yoku.bi/Introduction.html, a community rewrite of Sakubi, using an mdBook-style interface. This project implements its own reader CSS and JavaScript; it does not copy Yokubi's lesson text or logo.
- Open Sans fonts: Google / Steve Matteson; bundled WOFF2 files sourced from Yokubi's public font assets, under Apache License 2.0. See `assets/OPEN-SANS-LICENSE.txt`.
- New reader code and build script: MIT; see `LICENSE`.
