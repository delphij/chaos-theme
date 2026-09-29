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

- `search.fingerprint = false` publishes the search indexes from `assets/` at
  fixed URLs. Every page embeds their URLs, so with a fingerprint any post edit
  changes every page; without one, the server must have browsers revalidate the
  two files. README.md has an nginx example. The default is unchanged.

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
