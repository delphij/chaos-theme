# Changelog

All notable changes to this theme are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases follow
[Semantic Versioning](https://semver.org/).

## Compatibility

From 1.0.0 on, a change that makes an existing site build differently without
the site asking for it -- or stop building -- needs a new major version. What a
site can rely on:

- **Configuration**: the `[params]` keys documented in README.md, and the
  output format names a site lists under `[outputs]` (`ATOM`, `feedxsl`,
  `sitemapxsl`, `REDIR`, `SECURITY`).
- **Front matter**: the page variables documented in README.md.
- **Shortcodes**: `x` and `x_simple`, with their arguments.
- **Overrides**: the i18n keys, and the CSS custom properties in
  `assets/css/tokens.css`, which a site may redefine.
- **Tools**: the command-line options of the scripts in `tools/`.

Partial names, CSS class names and markup structure are not in that list: a
site that overrides a partial or styles a theme class is tied to the version it
was written against.

Raising the minimum Hugo version is a minor release, and is always called out
here.

## [Unreleased]

### Added

- A specimen page in the example site, `posts/specimen/`, with every component
  the theme renders on one page. Every push to `main`, and a manual run of the
  CI workflow, publishes the example site to GitHub Pages.
- `search.fingerprint = false` publishes the search indexes from `assets/` at
  fixed URLs. Every page embeds their URLs, so with a fingerprint any post edit
  changes every page; without one, the server must have browsers revalidate the
  two files. README.md has an nginx example. The default is unchanged.
- A search in Simplified or Traditional Chinese finds posts in either script.
  `build_search_index.py` indexes Traditional characters as their Simplified
  forms, from the character table of OpenCC 1.4.2, now vendored in
  `tools/vendor/opencc/`, and puts the pairs a query can need in the index,
  where `search.js` folds the query with them. `--keep-traditional` turns this
  off. An index built earlier still works, without the folding.
- A misspelt Latin word in a search is matched to the terms one edit away: a
  character missing, extra or wrong, or two swapped, so `freebds` finds
  FreeBSD. Only for a word of four characters or more that is neither a term
  nor the start of one, so no search that found something before changes.
- `tools/search_harness.mjs --old-index` and `--old-body` give the `--compare`
  script its own index, for a change to the index format.

### Changed

- The search indexes hold their terms and posting lists as two strings, with
  each posting list gap-encoded, instead of an object of arrays. On a blog of
  1,950 posts the body index went from 1.8 MB to 0.9 MB (527 KB to 432 KB with
  Brotli) and loads in about a third of the time; results are unchanged. An
  index must be rebuilt with this version's `build_search_index.py`: `search.js`
  reports one from an earlier version as an unsupported format.
- `build_search_index.py` indexes the whole body of a post. It stopped at 6,000
  characters, so a word further into a long post could not be found.
  `--max-body-chars` still sets a limit, and `0`, now the default, means none.
- Sidebar panels, the table of contents, X embeds, the pagination and
  code-copy buttons and the feed address box are blocks of ground with no
  hairline border, as quotes and callouts already were: panels and embeds on
  `--ground` instead of a bordered `--surface`. In forced-colours mode they
  take a system-colour border.
- The labels of the table of contents and the sidebar panels, and the X
  embed's source row, are bands of a new `--ground-head` across the block's
  full width: the same warm tint as `--ground`, a step deeper. A panel's
  first label caps it and the rest divide it.
- The sticky header, on the site and on the feed and sitemap pages, is frosted
  glass again: `--bg` at 82% over a 16px backdrop blur, in place of the opaque
  ground of 1.1.0.
- The dark palette is deeper, so the page does not glow at night: `--bg` is
  `#151514`, and the surfaces, grounds, callout grounds and code ground step
  down with it, keeping their tiers. Headings are 白鼠 `#DCDDDD`, body text
  `#CFCFCE` and secondary text `#989896`; the table header is `#2D2C28`.
  Strings in code are 白群 `#83CCD2` and variables 飴色 `#DEB068`, so that no
  syntax colour is brighter than body text on the deeper ground. A site
  that redefines only some of the dark colour properties should check them
  against the new ones.

### Fixed

- A site deployed under a subpath (`baseURL = "https://example.org/blog/"`)
  had links that left it: a category link whose term page was not found by
  its urlized name, which is every non-Latin category; the "all categories"
  and "all tags" links in the sidebars; the home links on the 404, feed and
  sitemap pages; the Atom feed's `id` and author `uri`; the Mermaid script;
  the default social image; and the fallback search index URL. All of them
  were built from a path with a leading slash, which `relURL` and `absURL`
  resolve against the host rather than the `baseURL`.
- `build_search_index.py --base-url` did not prefix a page whose front matter
  sets `url`, so under a subpath its search result linked outside the site.

- A search for a word with a hyphen, an underscore or a full stop in it found
  nothing: `utf-8`, `x86_64`, `node.js`. The index holds the words between
  them, and the query was looked up whole.
- A search for part of a CJK word the index holds whole found unrelated posts:
  two characters of a three-character name were looked up one character at a
  time. A piece of the query that is no term but is inside one now matches the
  terms that hold it, weighted like a prefix.
- `build_search_index.py` indexed each `_index.md` as a post, with a URL that
  does not exist.
- `build_search_index.py` took every list in a post's front matter for its
  tags when they were written as a YAML block list, and read no categories
  written that way.
- A search term could be highlighted inside an HTML entity of a result's title
  or summary, breaking the entity.

## [1.1.0] - 2026-09-27

A new palette and code colours, feeds that render without browser XSLT, and
fixes to code fences and callouts. Requires Hugo 0.158.0 or later, as before.

### Added

- The Atom and RSS feeds load [polyxslt](https://github.com/delphij/polyxslt)
  1.0.0, so a browser without XSLT still renders them through `feed.xsl`. A
  browser that has XSLT never requests it, and feed readers ignore the element.
- auxmark and `fetch_x_embed.py` replace the t.co short links in a cached X
  embed with their destinations, so readers are not sent through X first.
  `--no-expand-links`, or `expand_links = false` in `.auxmark.toml`, keeps the
  short links. The cached JSON is still X's response as received.
- CSS custom properties a site may redefine: `--ground` (quotes, table stripes
  and quiet chrome), `--blockquote-bg`, `--radius-card`, `--table-head-bg` and
  `--table-head-fg`, and the syntax roles `--syntax-text`, `-keyword`,
  `-string`, `-constant`, `-function`, `-variable`, `-tag`, `-comment`,
  `-line-hl`, `-inserted-bg` and `-deleted-bg`.
- `tools/check_chroma.py` compares `syntax.css` with the classes the installed
  Chroma emits and checks the code inks' contrast in both modes. Run it after a
  Hugo upgrade; `assets/css/syntax-upgrade.md` describes the procedure.
- `tools/check.py` checks that the XSL stylesheets still parse as XML.

### Changed

- A new palette in traditional colours at their published values, light and
  dark. The dark mode is a warm charcoal with off-white ink. Every text colour
  clears 4.5:1 on each ground it is used on. README.md documents the roles.
- Quotes, callouts, embeds and the feed and sitemap banners share one card
  style: a tinted ground with no accent rail and an 8px radius. `--radius`
  remains, as an alias of `--radius-card`.
- Table headers take `--table-head-bg` and `--table-head-fg` instead of
  `--paper`. A site that redefined `--paper` to style its tables should
  redefine these instead.
- Code is coloured by role through the `--syntax-*` properties, the same in
  both modes apart from the colours. `syntax-dark.css` is gone.
- Keyboard focus is the link blue in both modes, and every transition and
  animation honours `prefers-reduced-motion`.
- The sticky header has an opaque ground instead of a blur. The search dialog
  is restyled, keeps its input's focus ring, and its close button is a 44px
  target.
- The element defaults and Markdown components are in `prose.css`, shared by
  the site and the feed and sitemap pages, which used to carry their own
  copies.
- `render_xsl_companions.sh` skips a document that loads polyxslt, and removes
  a companion an earlier build left beside it. Out of the box only the sitemap
  gets a companion now. A server set up as README.md describes needs no change:
  a feed without a companion is served as XML.
- The tweet downloader spaces its requests at least `request_interval` seconds
  (default 1) apart per host, `fetch_x_embed.py --batch` included, and its
  retries honour `Retry-After`.

### Fixed

- A code fence's `hl_lines` highlighted the line below the one asked for, and
  nothing with `linenostart`. Its own `linenos` lost to the default.
- With `eastAsianLineBreaks`, a callout's body became its title, and a custom
  title swallowed the text below it.
- Firefox showed feed entries as literal markup and drew no feed icon.
- A feed entry title containing `<` was parsed as markup.
- Lists inside a feed entry took nested-list markers.
- Consecutive highlighted code blocks touched, and a line-numbered block hung
  into the margin in print.

## [1.0.0] - 2026-09-23

First stable release. Requires Hugo 0.158.0 or later, standard edition.

### Added

- Hugo Module support: import `github.com/delphij/chaos-theme` instead of
  adding a submodule.
- A table render hook, so Markdown tables are the same on every supported Hugo
  version and in the feeds.
- A `series` translation in all five languages.
- Continuous integration: the example site is built under `--panicOnWarning`
  with the minimum and the latest Hugo, then checked with `tools/check.py`.
- Release tarballs: pushing a `v*` tag publishes a GitHub release with a
  `chaos-theme-<tag>.tar.xz` that extracts to `chaos/`, and this file's
  section for the version as its notes.

### Changed

- The theme's `hugo.toml` keeps only settings Hugo merges from a theme. The
  site-level keys it used to carry (`baseURL`, `title`, `locale`,
  `hasCJKLanguage`, `[outputs]`) were never read; `exampleSite/hugo.toml` is
  the configuration to start from.
- README screenshots use absolute URLs, so they show on themes.gohugo.io.

### Fixed

- Tables in the Atom and RSS feeds no longer carry Hugo's pretty-printing
  indentation.
- A section or taxonomy the theme has no translation for (`pages`, `notes`)
  no longer logs a missing-translation warning on every build.
- `tools/check.py` no longer reports the feeds' own indentation as leaked
  template whitespace when the site is built without `--minify`.

[Unreleased]: https://github.com/delphij/chaos-theme/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/delphij/chaos-theme/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/delphij/chaos-theme/releases/tag/v1.0.0
