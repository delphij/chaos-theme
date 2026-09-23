# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this Hugo theme.

## Project Overview

Minimalist Hugo theme for personal blogs with excellent Chinese typography support. Design philosophy: fast-loading, accessible (WCAG 2.1 AA), mobile-first, minimal dependencies (brotli: ~2KB main.js, ~2KB search.js when search is enabled).

**Key Features**: Dark/light mode, responsive mobile menu with glass effects, automatic table of contents, instant page navigation, full i18n (5 languages).

## Commands

```bash
hugo server -D              # Dev server with drafts
hugo server                 # Production preview
hugo --gc --minify          # Production build
```

## Architecture

### Technology Stack
- **Hugo** 0.146.0+ (standard edition)
- **Languages**: Go Templates, HTML5, CSS3, vanilla JavaScript
- **Asset Processing**: Hugo Pipes (bundling, minification, SRI)
- **Dependencies**: KaTeX 0.17.0, instant.page 5.2.0, Mermaid 11.4.1, Noto Sans Mono 2.014 (Latin subset) — all vendored in `static/_3p/`

### Directory Structure
```
/layouts/          Templates (baseof, _default, _markup, _partials, shortcodes)
/assets/           Source CSS/JS (processed by Hugo Pipes)
/static/_3p/       Vendored dependencies (versioned)
/i18n/             Translation files (en-us, zh-cn, zh-tw, ja-jp, ko-kr)
/config/           Configuration overrides
```

## Coding Standards

### Formatting (Strictly Enforced)
- **Indentation**: 2 spaces in templates, CSS and JS; 4 in Python; the shell
  scripts in `tools/` are tab-indented. `.editorconfig` states all of this.
- **Line endings**: LF
- **EOF**: Single newline
- **Naming**: kebab-case files, BEM-style CSS classes

### Templates
1. **i18n**: ALL user-facing text must use `{{ T "key" }}` (including ARIA labels)
2. **Escaping**: Use `safeHTML`, `safeHTMLAttr`, `safeURL` appropriately
3. **Performance**: Use `partialCached` for static content
4. **Comments**: Document complex logic with `{{- /* comment */ }}`

### CSS
**Organization**: Variables → Reset → Base → Layout → Components → Utilities → Dark mode → Print

**Performance Rules**:
- Specific transitions (NOT `transition: all`)
- CSS containment on isolated components (`.toc`, `.alert`) - disable in print
- Modern viewport units (`dvh` for mobile)
- CSS variables for all repeated values
- No hardcoded colors

### JavaScript
- ES modules: each feature is one file under `assets/js/modules/` exporting a
  single `init*()`, and `main.js` is only the wiring. No IIFE wrapper -- a
  module is already its own scope
- `search.js` and `mermaid.js` are separate entry points, not modules of
  `main.js`: each is loaded only where it is wanted (a search-enabled site, a
  page with a diagram), so bundling them into `main.js` would put them on
  every page
- Bundled by `js.Build` (esbuild, built into Hugo), so no Node toolchain is
  involved: `hugo` alone builds the theme
- Syntax floor is declared as `es2020` in `_partials/foot/js.html`; write newer
  syntax freely and esbuild lowers it
- Apache 2.0 copyright header required
- Cache DOM references at initialization
- Modern DOM methods (`replaceChildren`, `append`)
- Helper functions for DRY patterns
- Intersection Observer for scroll tracking

### Internationalization
All text must be externalized to i18n files:
```toml
# i18n/en-us.toml
readMore = 'Read more…'

# i18n/zh-cn.toml
readMore = '阅读全文…'
```

**NEVER hardcode** UI labels, button text, ARIA labels, navigation items, or error messages.

### Accessibility (WCAG 2.1 AA)
- Semantic HTML5 elements (`<header>`, `<main>`, `<article>`, `<nav>`, `<button>`)
- Localized ARIA labels and states
- Full keyboard navigation (Tab, Escape)
- Focus management and visible indicators
- Alt text on all images

### Security
- Escape template variables by default
- SRI enabled for CSS/JS
- No inline scripts (except essential config)
- No external CDN dependencies

### Dependencies
Third-party libraries:
1. Place in `static/_3p/<libname>/<version>/`
2. Include LICENSE file
3. Document in NOTICE file
4. Prefer vendoring over CDNs

### Commit Messages
Conventional Commits format:
```
feat: add feature
fix: resolve bug
docs: update documentation
style: formatting
refactor: restructure code
perf: performance improvement
chore: maintenance
```

### Maintainer Tools (`tools/`)

Neither is part of a build: `hugo` builds the theme alone and a site never
runs them. See README.md for what each checks.

- `tools/check.py --public public` -- i18n key parity, unread translations,
  CJK literals, authored script left inline in a template, template
  indentation leaking into the feeds. Python 3 only. Exit 1 on failure
- `tools/search_harness.mjs` -- runs `assets/js/search.js` against a real
  index in a stubbed DOM; `--compare <file>` checks a change against the
  version it replaces. Derives its queries from the index, so it carries no
  site's content. Pass `--body`, or most queries return a single result and
  a ranking change cannot show. The only thing here that needs Node

Add a check to `check.py` when a mistake gets through that a build would not
have caught -- that is what it is for, and every check in it was put there by
one.

### Python Tools (auxmark and utilities)
- **Git integration**: Use `git mv` instead of `shutil.move()` for file operations when appropriate
  - Better history tracking (git recognizes renames vs delete+add)
  - Example: When converting `post.md` → `post/index.md` (Hugo page bundle expansion)
- **Testing**: All tools should include comprehensive test suites
  - Use temporary directories for testing
  - Test both dry-run and actual execution modes
  - Verify git-aware file scanning
- **Error handling**: Graceful degradation with informative error messages
- **Module architecture**: Follow plugin pattern for extensibility (see `tools/auxmark/`)

## Performance Optimizations

### CSS
- Shared utility classes (`.overlay-blur`)
- CSS containment on isolated components
- Specific transition properties
- Dynamic viewport units (`dvh`)
- CSS variables for theming

### JavaScript
- Cached DOM references (~80% fewer queries)
- Optimized IntersectionObserver (tracks current active element)
- Consolidated event listeners
- Modern DOM methods for batch operations
- Syncs with CSS variables

### Content
- Partial caching (header/footer)
- Lazy loading images with WebP
- Conditional KaTeX loading
- instant.page prefetching

## Important Notes

- Theme is production-ready following Hugo best practices
- All features documented in README.md
- Custom markdown rendering in `layouts/_markup/`
- Remark42 comment system optional
- Responsive image rendering comprehensive but necessary
- For detailed rationale and quality standards, see AGENTS.md
