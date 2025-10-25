# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this Hugo theme.

## Project Overview

Minimalist Hugo theme for personal blogs with excellent Chinese typography support. Design philosophy: fast-loading, accessible (WCAG 2.1 AA), mobile-first, minimal dependencies (~3KB JavaScript total).

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
- **Dependencies**: KaTeX 0.16.22, instant.page 5.2.0 (vendored in `static/_3p/`)

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
- **Indentation**: 2 spaces (NO tabs)
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
- Vanilla ES6+ (const/let, arrow functions, IIFE scope)
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
