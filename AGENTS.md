# AGENTS.md: AI Collaboration Guide

This document provides essential context for AI models and human contributors collaborating on this Hugo theme. Following these guidelines ensures **consistency, maintainability, and production quality**.

## 1. Project Overview & Purpose

* **Primary Goal:** A minimalist, production-ready Hugo theme for personal blogs with excellent Chinese typography support
* **Target Users:** Technical bloggers, developers, writers who value performance and accessibility
* **Design Philosophy:**
  * Fast-loading with minimal dependencies (~2KB JavaScript)
  * Accessible and semantic HTML with WCAG AA compliance
  * Dark/light mode with system preference detection
  * Full internationalization (en-US, zh-CN, zh-TW)
  * Mobile-first responsive design

## 2. Core Technologies & Stack

* **Languages:** Go Templates (Hugo), HTML5, CSS3, JavaScript (vanilla ES6+)
* **Framework:** Hugo 0.146.0+ (standard edition, extended not required)
* **Asset Processing:** Hugo Pipes (bundling, minification, fingerprinting, SRI)
* **Dependencies:**
  * **KaTeX 0.16.22**: Mathematical typesetting (vendored at `static/_3p/katex/0.16.22/`)
  * **Remark42**: Optional comment system (embed script, MIT license)
* **Package Management:** Manual vendoring (NO npm/node_modules)
* **i18n:** Hugo's built-in i18n system with TOML translation files

## 3. Architecture & Structure

### Static Site Generation Model
Hugo compiles Markdown content into static HTML. The theme provides:
- Template hierarchy (`baseof.html` → specific templates)
- Partial components for reusability
- Custom markdown renderers for images, code, and math
- Asset pipeline for CSS/JS optimization

### Directory Organization
```
/layouts/          Template files following Hugo conventions
  baseof.html      Root template with base HTML structure
  _default/        Page templates (single, list, taxonomy)
  _markup/         Custom markdown renderers
  _partials/       Reusable components
    _funcs/        Function partials (pure logic)
    head/          Head section components
    foot/          Footer components
  archives/        Archive page template
  shortcodes/      Content shortcodes (X/Twitter embed)
/assets/           Source files processed by Hugo Pipes
  css/             Unminified CSS (main, normalize, syntax)
  js/              Source JavaScript (theme switching)
/static/           Static assets (copied verbatim)
  _3p/             Vendored third-party dependencies
    katex/         Versioned KaTeX releases
/i18n/             Translation files (en-US, zh-CN, zh-TW)
/config/           Configuration overrides (output formats, media types)
```

## 4. Coding Standards & Best Practices

### Formatting (STRICTLY ENFORCED)
* **Indentation:** 2 spaces (NEVER tabs)
* **Line endings:** LF (Unix-style)
* **EOF:** All files MUST end with single newline
* **Whitespace:** No trailing whitespace
* **Naming:** kebab-case for files, BEM-style for CSS classes

### Template Guidelines
1. **i18n REQUIRED:** All user-facing text MUST use `{{ T "key" }}`
   ```html
   ❌ BAD:  <button>Toggle theme</button>
   ✅ GOOD: <button>{{ T "themeToggle" }}</button>
   ```

2. **Escaping:** Use appropriate escaping functions
   - `safeHTML`: For pre-processed markdown content
   - `safeHTMLAttr`: For HTML attributes
   - `safeURL`: For URL attributes
   - Default escaping otherwise

3. **Performance:** Use `partialCached` for static content
   ```html
   {{ partialCached "header.html" . site.Language.Lang }}
   ```

4. **Comments:** Document complex logic
   ```html
   {{- /*
   Renders responsive image with WebP support
   @context {page} page The current page
   */ }}
   ```

### CSS Organization
CSS is divided into logical sections:
1. **CSS Variables** - Design tokens (colors, spacing, typography)
2. **CSS Reset** - normalize.css for cross-browser consistency
3. **Base Styles** - Typography, links, defaults
4. **Layout** - Grid, flex, containers
5. **Components** - Header, footer, navigation, cards
6. **Utilities** - Helper classes
7. **Dark Mode** - `html.dark` overrides

### JavaScript Standards
* **Style:** Modern ES6+ (const/let, arrow functions, template literals)
* **Scope:** IIFE to avoid global pollution
* **Error Handling:** try/catch for localStorage access
* **Copyright:** Apache 2.0 header required (year 2025)
* **Size:** Keep minimal (~2KB unminified)

Example:
```javascript
// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.

(function() {
  // Implementation
})();
```

### Internationalization Requirements

**CRITICAL:** All text must be externalized to i18n files.

i18n file structure:
```toml
# Navigation
mainNavigation = 'Main navigation'
feedsNavigation = 'Feeds'

# Pagination
paginationLabel = 'Pagination'
previousPage = '← Previous'
nextPage = 'Next →'
```

**NEVER hardcode text** in templates, including:
- UI labels and button text
- ARIA labels (accessibility)
- Navigation items
- Error messages
- Title attributes

Chinese typography conventions:
- Use full-width punctuation (，。！？)
- Use 「」 for quotes (not "" or '')
- Add half-width space before untranslatable English (URLs, names)

## 5. Quality Assurance Standards

### Pre-Commit Checklist
- [ ] No tabs (only 2-space indentation)
- [ ] All files end with single newline
- [ ] No trailing whitespace
- [ ] No hardcoded text (all i18n)
- [ ] ARIA labels localized
- [ ] Alt text on images
- [ ] Conventional commit message

### Accessibility (WCAG AA)
- Semantic HTML5 elements (`<header>`, `<main>`, `<article>`, `<nav>`)
- ARIA labels on navigation and interactive elements
- `aria-current` for active states
- Focus indicators visible (outline on :focus)
- Color contrast ≥4.5:1 for text
- Alt attributes on all images

### Security
- Escape all template variables by default
- Use `safeHTML` sparingly and only for trusted content
- No inline scripts (except essential config)
- SRI (Subresource Integrity) enabled for assets
- No external CDN dependencies (except optional Remark42)

### Performance
- Minimal JavaScript (~2KB)
- CSS bundled and minified in production
- Responsive images with srcset and WebP
- Lazy loading on images
- KaTeX loaded conditionally (only when math detected)
- Partial caching for static components

## 6. Development Workflow

### Local Development
```bash
# Start development server with drafts
hugo server -D

# Production-like preview
hugo server

# Build with verbose output
hugo --verbose

# Production build
hugo --gc --minify
```

### Testing Strategy
- **Visual Testing:** Test with sample content in multiple languages
- **Accessibility:** Use browser DevTools accessibility checker
- **Performance:** Lighthouse audit (target: 95+ score)
- **Cross-browser:** Test in Chrome, Firefox, Safari
- **Responsive:** Test on mobile, tablet, desktop viewports

### Version Control
```bash
# Conventional commit format
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
git commit -m "docs: update documentation"
git commit -m "style: formatting changes"
git commit -m "refactor: restructure code"
git commit -m "perf: improve performance"
git commit -m "chore: maintenance tasks"
```

## 7. Dependencies & Licensing

### Adding New Dependencies
1. **Evaluate:** Is vendoring necessary? Can we avoid it?
2. **Version:** Place in `static/_3p/<libname>/<version>/`
3. **License:** Include LICENSE file in vendored directory
4. **Attribution:** Add to NOTICE file with:
   - Library name
   - Copyright holder
   - License type
   - Location in repo
   - Website URL

Example NOTICE entry:
```
Library Name
Copyright (c) YEAR Copyright Holder
Licensed under the MIT License
Location: static/_3p/libname/version/
Website: https://example.com/
```

### Current Dependencies
- **KaTeX 0.16.22** (MIT) - Mathematical typesetting
- **Remark42 embed** (MIT) - Comment system integration

### Licensing
- **Theme License:** Apache 2.0
- **Copyright:** 2024-2025 The Hugo Authors
- **Attribution:** Required in NOTICE file
- **Third-party:** Properly attributed in NOTICE and LICENSE files

## 8. AI Collaboration Guidelines

### Contribution Philosophy
* **Minimalism:** Add features only when necessary
* **Incremental Changes:** Small, auditable commits over large rewrites
* **Documentation:** Update docs for all user-facing changes
* **Testing:** Verify changes don't break existing functionality

### AI Editing Rules
1. **Preserve Conventions:** Follow existing patterns in codebase
2. **i18n First:** Never hardcode text - always use i18n keys
3. **Format Consistently:** Use 2-space indentation, no tabs
4. **Document Changes:** Update README/docs for new features
5. **Security:** Escape variables, no unreviewed third-party scripts

### Code Review Priorities
1. Does it follow i18n requirements?
2. Is formatting consistent (2-space, no tabs)?
3. Are ARIA labels localized?
4. Does it maintain performance?
5. Is accessibility preserved?
6. Are dependencies properly attributed?

### Translation Guidelines
When adding i18n strings:
1. Add to all three language files (en-US, zh-CN, zh-TW)
2. Use semantic key names (`themeToggle` not `button1`)
3. Group related keys with comments
4. Use proper Chinese typography (「」quotes, full-width punctuation)

Example:
```toml
# Navigation
mainNavigation = 'Main navigation'      # en-US
mainNavigation = '主导航'                # zh-CN
mainNavigation = '主導航'                # zh-TW
```

## 9. Production Readiness Checklist

Before public release or major version:
- [ ] All text internationalized (no hardcoded strings)
- [ ] ARIA labels localized
- [ ] Formatting consistent (2-space, no tabs, EOF newlines)
- [ ] All templates documented
- [ ] README.md comprehensive and accurate
- [ ] LICENSE and NOTICE files complete
- [ ] theme.toml metadata correct
- [ ] .gitignore excludes build artifacts
- [ ] No console errors or warnings
- [ ] Accessibility audit passed (WCAG AA)
- [ ] Lighthouse score 95+
- [ ] Cross-browser tested
- [ ] Mobile responsive verified

## 10. Common Pitfalls to Avoid

❌ **Don't:**
- Use tabs for indentation
- Hardcode text in templates
- Skip i18n for ARIA labels
- Add dependencies without documentation
- Use external CDNs (except optional features)
- Commit files without EOF newlines
- Write inline styles or scripts
- Use unsafe HTML without escaping

✅ **Do:**
- Use 2-space indentation consistently
- Externalize all text to i18n files
- Localize ARIA labels
- Vendor dependencies with version numbers
- Document third-party code in NOTICE
- End files with single newline
- Use Hugo's asset pipeline
- Escape template variables properly

## Summary

This theme prioritizes **performance**, **accessibility**, and **internationalization** while maintaining **minimal complexity**. Every change should align with these principles. When in doubt, refer to existing patterns in the codebase and prioritize user experience over developer convenience.
