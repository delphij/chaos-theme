# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this Hugo theme.

## Project Overview

This is a minimalist Hugo theme designed for clarity, performance, and excellent Chinese typography support. Design philosophy:
- Fast-loading with minimal dependencies (only KaTeX vendored)
- Accessible and semantic HTML with full i18n support (WCAG 2.1 AA)
- Dark/light mode with system preference detection
- Responsive mobile navigation with glass-morphism effects
- Minimal JavaScript (~3KB for theme toggle + mobile menu)
- Production-ready code quality

## Commands

### Development
```bash
hugo server -D              # Local dev server with drafts and live reload
hugo server                 # Production preview without drafts
hugo --verbose              # Build with verbose output
hugo --gc --minify          # Production build with cleanup and minification
```

## Architecture

### Technology Stack
- **Hugo**: Static site generator (minimum version 0.146.0, standard edition)
- **Languages**: Go Templates, HTML5, CSS3, vanilla JavaScript
- **Asset Processing**: Hugo Pipes (bundling, minification, fingerprinting, SRI)
- **Dependencies**: KaTeX 0.16.22 (vendored at `static/_3p/katex/0.16.22/`)
- **i18n**: English, Simplified Chinese, Traditional Chinese, Japanese, Korean

### Directory Structure
```
/layouts/
  baseof.html              # Root template
  _default/                # Page templates (single, list, etc.)
  _markup/                 # Markdown renderers (images, code, math)
  _partials/               # Reusable components
    _funcs/                # Function partials
    head/                  # Head section components
    foot/                  # Footer section components
  archives/                # Archive page template
  shortcodes/              # Hugo shortcodes
/assets/
  css/                     # Source CSS (processed by Hugo Pipes)
  js/                      # Source JavaScript
/static/
  _3p/                     # Third-party vendored dependencies
    katex/0.16.22/         # KaTeX with fonts
/i18n/                     # Translation files
  en-us.toml
  zh-cn.toml
  zh-tw.toml
  ja-jp.toml
  ko-kr.toml
/config/_default/          # Configuration overrides
```

### Custom Output Formats
Defined in `config/_default/config.toml`:
- ATOM feed with XSLT stylesheet
- RSS feed
- Sitemap with XSLT stylesheet
- Redirect mapping format

## Coding Conventions

### Formatting Standards
- **Indentation**: 2 spaces (NO tabs)
- **Files**: kebab-case naming
- **Classes**: BEM-style or semantic naming
- **Line endings**: LF (Unix-style)
- **EOF**: All files end with single newline
- **Whitespace**: No trailing whitespace

### Template Best Practices
1. **Consistent spacing**: Use `{{-` and `-}}` intentionally for whitespace control
2. **Escaping**: Use `safeHTML`, `safeHTMLAttr`, `safeURL` appropriately
3. **i18n**: All user-facing text must use `{{ T "key" }}` - NO hardcoded strings
4. **Comments**: Use `{{- /* comment */ }}` for template documentation
5. **Partials**: Cache when possible with `partialCached`

### CSS Organization
CSS is organized in sections:
1. CSS Variables (colors, spacing, typography)
2. CSS Reset (normalize.css)
3. Base styles
4. Layout
5. Components
6. Utilities
7. Dark mode overrides

### JavaScript Guidelines
- Vanilla JavaScript only (no frameworks)
- IIFE to avoid global scope pollution
- Modern ES6+ features (const/let, arrow functions, template literals)
- Error handling with try/catch for localStorage
- Copyright header required (Apache 2.0)

### Internationalization (i18n)
All text strings must be externalized:
```toml
# i18n/en-US.toml
readMore = 'Read more…'

# i18n/zh-cn.toml
readMore = '阅读全文…'
```

In templates:
```html
{{ T "readMore" }}
```

**NEVER hardcode text** - always use i18n keys for:
- UI labels
- Button text
- ARIA labels
- Navigation items
- Error messages

### Accessibility Requirements (WCAG 2.1 AA)
- All images must have `alt` attributes
- ARIA labels and states must be localized via i18n (`aria-label`, `aria-expanded`, `aria-current`)
- Semantic HTML5 elements (`<header>`, `<main>`, `<article>`, `<nav>`, `<button>`)
- Full keyboard navigation support (Tab, Shift+Tab, Escape)
- Focus management (return focus to trigger on modal/menu close)
- Focus indicators visible on all interactive elements
- Color contrast exceeds WCAG AA standards
- Screen reader compatible with proper ARIA attributes

### Security
- Always escape template variables
- Use `safeHTML` only for pre-processed markdown
- No inline scripts (except essential config)
- SRI enabled for CSS/JS
- No external CDN dependencies

### Dependencies
Third-party libraries:
1. Place in `static/_3p/<libname>/<version>/`
2. Include LICENSE file
3. Document in NOTICE file
4. Prefer vendoring over CDNs

### Commit Messages
Follow Conventional Commits:
```
feat: add new feature
fix: resolve bug
docs: update documentation
style: formatting changes
refactor: code restructuring
perf: performance improvement
chore: maintenance tasks
```

## Best Practices Established

### Code Quality
- ✅ Consistent 2-space indentation (no tabs)
- ✅ All templates end with single newline
- ✅ Multi-line attributes use 2-space continuation
- ✅ No trailing whitespace
- ✅ Copyright headers on JavaScript files

### Internationalization
- ✅ Complete i18n coverage (no hardcoded text)
- ✅ ARIA labels localized
- ✅ Five languages supported (en-US, zh-CN, zh-TW, ja-JP, ko-KR)
- ✅ Proper Chinese typography (full-width punctuation, 「」 quotes)

### Performance
- ✅ Minimal JavaScript (~3KB for theme toggle + mobile menu)
- ✅ CSS bundled and minified in production
- ✅ Partial caching for header/footer
- ✅ Responsive images with WebP
- ✅ Lazy loading and async decoding
- ✅ KaTeX loaded conditionally
- ✅ Hardware-accelerated backdrop-filter for glass effects

### Mobile Navigation
- ✅ Hamburger menu for screens ≤600px
- ✅ Glass-morphism effect with 12px backdrop blur
- ✅ Absolute positioning (overlays content, doesn't push)
- ✅ Browser fallback for unsupported backdrop-filter
- ✅ Click outside, link click, and Escape key to close
- ✅ Full keyboard accessibility with focus management
- ✅ Consolidated navigation (main menu + RSS feed)

### Licensing
- ✅ Apache 2.0 license (LICENSE file)
- ✅ Proper attribution (NOTICE file)
- ✅ Third-party licenses included (KaTeX, Remark42)
- ✅ Copyright headers where appropriate

### Theme Distribution
- ✅ theme.toml with metadata
- ✅ Comprehensive README.md
- ✅ Clean .gitignore
- ✅ Example configuration in hugo.toml

## Important Notes

- The theme is production-ready and follows Hugo best practices
- All features are documented in README.md
- Custom markdown rendering in `layouts/_markup/` handles code blocks, images, and math
- Remark42 comment system is optional and configurable
- Theme uses partialCached for performance optimization
- Responsive image rendering is comprehensive (124 lines) but necessary for optimal performance
