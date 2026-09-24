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

## [1.0.0]

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

[Unreleased]: https://github.com/delphij/chaos-theme/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/delphij/chaos-theme/releases/tag/v1.0.0
