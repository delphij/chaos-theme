# AGENTS.md: AI Collaboration Guide

This document provides essential context for AI models and human contributors collaborating on this Hugo theme. Following these guidelines ensures **consistency, maintainability, and production quality**.

## 1. Project Philosophy

### Design Principles
* **Minimalism**: Add features only when necessary; prefer simplicity over complexity
* **Performance First**: Every byte counts - target <10KB total JavaScript, efficient CSS
* **Visual language**: Use `--radius-card` for content cards and panels, small
  radii for controls, and square neutral backgrounds for code blocks. Keep
  prose lists open and unboxed. Use the shared light/dark palette in
  `assets/css/tokens.css`; verify text against tinted and selected backgrounds
  as well as the page background.
* **Accessibility Always**: WCAG 2.1 AA compliance is non-negotiable
* **Internationalization by Default**: No hardcoded text; proper CJK typography support
* **Baseline Widely Available**: Use what every major engine has shipped for 30+ months; anything newer is progressive enhancement
* **Self-Hosted**: Vendor dependencies for reliability and privacy (no CDNs)

### Target Audience
Technical bloggers, developers, and writers who value:
- Fast page loads and minimal JavaScript
- Excellent Chinese typography
- Dark/light mode support
- Mobile-first responsive design
- Clean, semantic HTML

## 2. Architecture Philosophy

### Static Site Generation Model
Hugo compiles Markdown → static HTML at build time. No client-side frameworks, no build complexity beyond Hugo itself.

**Key architectural decisions:**
- **Template hierarchy**: `baseof.html` provides base structure, specific templates extend it
- **Partial components**: Reusable, cacheable components for performance
- **Custom renderers**: Override markdown rendering for images, code, math (`layouts/_markup/`)
- **Asset pipeline**: Hugo Pipes handles bundling, minification, fingerprinting, SRI

### Why Vendored Dependencies?
- **Reliability**: No external service outages
- **Privacy**: No tracking via CDN requests
- **Performance**: Served from same domain (no DNS lookup, connection overhead)
- **Versioning**: Explicit control over versions

### Client-Side Search Engine Architecture
Chaos implements a zero-dependency, privacy-preserving client-side full-text search engine powered by an offline pre-computed inverted index:
- **Offline Indexing (`tools/build_search_index.py`)**:
  - Reads the Markdown pages `hugo list published` reports, with Hugo's URL, title and date for each; preserves technical identifiers inside code blocks and inline backticks, tokenizes with vendored `jieba`.
  - Splits output into two mathematically disjoint tiers: Tier 1 (Core metadata + Title/Tags) and Tier 2 (Body only, strictly `P_T1(w) ∩ P_T2(w) = ∅`).
  - Writes each inverted index as two space-joined strings, `terms` and `postings` (gap-encoded doc ids, base-32 digits). `encode_postings` there and `decodePostings` in `search.js` must change together, and `tools/search_harness.mjs --compare … --old-index …` checks such a change.
- **Progressive Delivery**:
  - Tier 1 (a small fraction of the total index) is loaded upon opening the search modal for sub-50ms Time-to-Interactive.
  - Tier 2 (the remaining body index) is fetched in the background via `requestIdleCallback` and merged into the memory index without UI stalls.
- **Scoring & Safety**:
  - BM25-IDF + multi-field boosting (Title exact +120, Title phrase +60, Tag phrase +45, Token in Title +18, Token in Tag +12).
  - The in-memory index is a `Map` from term to its still-encoded posting list, decoded per query, so a term such as `constructor` or `toString` cannot collide with an Object prototype property.

## 3. Working Conventions

The concrete rules for changing the theme; the sections around this one give
the reasons.

### Overview

Minimalist Hugo theme for personal blogs with excellent Chinese typography support. Design philosophy: fast-loading, accessible (WCAG 2.1 AA), mobile-first, minimal dependencies (brotli: ~2KB main.js, ~3KB search.js when search is enabled).

**Key Features**: Dark/light mode, responsive mobile menu with glass effects, automatic table of contents, instant page navigation, full i18n (5 languages).

### Commands

```bash
hugo server -D              # Dev server with drafts
hugo server                 # Production preview
hugo --gc --minify          # Production build
```

### Technology Stack
- **Hugo** 0.158.0+ (standard edition)
- **Languages**: Go Templates, HTML5, CSS3, vanilla JavaScript
- **Asset Processing**: Hugo Pipes (bundling, minification, SRI)
- **Dependencies**: vendored, the browser's in `static/_3p/` and the build tools' in `tools/vendor/`; versions and reasons under [Dependency Management](#9-dependency-management)

### Directory Structure
```
/layouts/          Templates (baseof, _default, _markup, _partials, shortcodes)
/assets/           Source CSS/JS (processed by Hugo Pipes)
/static/_3p/       Vendored dependencies (versioned)
/i18n/             Translation files (en-us, zh-cn, zh-tw, ja-jp, ko-kr)
/config/           Configuration overrides
```

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
**Organization**: cascade layers, declared once at the top of `tokens.css`:
`chaos.reset` (normalize.css) → `chaos.tokens` → `chaos.base` (element
defaults in prose.css) → `chaos.syntax` (Chroma classes onto the `--syntax-*`
roles) → `chaos.components` (everything with a class or id, then print). A
later layer wins regardless of specificity, and unlayered CSS beats them all.

**Nesting**: nest a component's states, children and breakpoints inside it.
Only nest under a single selector or a list of equal specificity -- `&` takes
the list's highest specificity, like `:is()` -- and put declarations before
nested rules. Element defaults go in `chaos.base` -- element selectors and
their states (`a:hover`, `:focus-visible`), the focus ring, the `[id]` anchor
offset -- and anything naming a class or id in `chaos.components`, so a
component never has to restate a default's `:hover` to override it.
Before adding a rule, look for the concept it belongs to: shared shapes
(side panels, panel labels, navigation items, term chips, result pills) are
one grouped rule, with only the differences left per component.
Breakpoints are listed at the top of main.css.

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
- Syntax floor is declared as `es2024` in `_partials/foot/script.html`; write
  newer syntax freely and esbuild lowers it. Runtime APIs and CSS are held to
  Baseline Widely Available (see Browser Support in README.md)
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

### `tools/`

Not all one kind, and the difference decides whether a build calls it. See
README.md for the full list.

- **Build steps**, run by a site's build script: `build_search_index.py`,
  `post_build.sh` (which runs `strip_xsl_space.sh` and
  `render_xsl_companions.sh`), and `check.py`
- **Content tooling**, run by hand while writing: `fetch_x_embed.py`,
  `auxmark.py`, `generate_default_card.py`
- **Diagnostics**, never in a build: `search_harness.mjs`, and
  `check_chroma.py` after a Hugo upgrade (see `assets/css/syntax-upgrade.md`)

`hugo` alone still builds the theme; none of these is a dependency of the
templates.

The two added for this theme's own correctness:

- `tools/check.py --public public` -- i18n key parity, unread translations,
  version parity (theme.toml vs hugo.toml), CJK literals, authored script left
  inline in a template, template indentation leaking into the feeds, an XSL
  stylesheet that no longer parses as XML, a menu whose active entry is not
  the page's own, a search result linking a page that was not published.
  Python 3 only, exit 1 on failure, and it belongs in the build right after
  `hugo`
- `tools/search_harness.mjs` -- runs `assets/js/search.js` against a real
  index in a stubbed DOM; `--compare <file>` checks a change against the
  version it replaces. Derives its queries from the index, so it carries no
  site's content. Pass `--body`, or most queries return a single result and
  a ranking change cannot show. The only thing here that needs Node

Add a check to `check.py` when a mistake gets through that a build would not
have caught -- that is what it is for, and every check in it was put there by
one.

## 4. Code Quality Standards

### Formatting Rationale
**2-space indentation** (4 in Python, tabs only in the shell scripts in `tools/`, as `.editorconfig` states):
- Consistent across editors
- Balances readability with horizontal space
- Standard for HTML/CSS/JS ecosystems

**Single newline EOF**:
- POSIX standard for text files
- Prevents git diff noise

**No trailing whitespace**:
- Cleaner git diffs
- No semantic meaning

### Why i18n is Non-Negotiable
Hardcoded text creates:
- Maintenance burden (changes require code edits)
- Poor user experience for non-English speakers
- ARIA labels that can't be localized
- Barrier to contributions from international community

**Solution**: Hugo's built-in i18n system with TOML files. Key naming should be semantic (`themeToggle` not `button1`).

### Accessibility Standards (WCAG 2.1 AA)
**Why it matters:**
- Legal requirements in many jurisdictions
- Ethical responsibility (universal access)
- Better UX for everyone (keyboard navigation, contrast, etc.)

**Non-negotiable requirements:**
- Semantic HTML5 elements
- Localized ARIA labels
- Keyboard navigation (Tab, Escape)
- Focus management
- Color contrast ≥4.5:1
- Alt text on images

## 5. Performance Philosophy

### CSS Performance
**Problem**: Poor CSS practices cause layout thrashing and repaints.

**Solutions applied:**
1. **Specific transitions** (not `all`): Browser only watches properties that change
2. **CSS containment**: Isolates component layout calculations from rest of page
3. **Modern viewport units** (`dvh`): Adjusts for mobile browser UI
4. **CSS variables**: Single source of truth, reduces duplication
5. **Shared prose rules**: `prose.css` holds the element defaults and the
   components Markdown renders, and the XSLT pages inline it rather than
   keeping their own copy
6. **Cascade layers and nesting**: Theme CSS lives in `chaos.*` layers (order
   declared in `tokens.css`), so a component never has to outbid an element
   rule and a site overrides the theme with plain unlayered CSS. Nest states,
   children and breakpoints inside the component they belong to, but never
   under a selector list of mixed specificity (`&` takes the highest)

**When to use CSS containment:**
- ✅ Isolated components (TOC, alerts, cards)
- ✅ Frequently updating elements (active TOC links)
- ❌ Complex nested tables (syntax highlighting)
- ❌ Components affecting parent layout
- **Always disable in print** (prevents margin collapse issues)

### JavaScript Performance
**Problem**: Repeated DOM queries, inefficient observer patterns.

**Solutions applied:**
1. **Cache DOM references**: Query once at init, reuse throughout
2. **Modern DOM methods**: `replaceChildren()`, `append()` for batch operations
3. **Optimized observers**: Track current active element (80% fewer DOM operations)
4. **Consolidated listeners**: Single handlers for common patterns
5. **Helper functions**: DRY code with reusable utilities
6. **Sync with CSS**: Read CSS variables instead of magic numbers

**Example impact**: TOC scroll tracking reduced from ~500 operations to ~100 per scroll.

### Content Delivery
- **Lazy loading**: Images load on-demand
- **WebP conversion**: Modern format with fallbacks
- **Responsive srcsets**: Multiple resolutions for different viewports
- **Partial caching**: for what does not vary per page (the header is not in it:
  its menu marks the current entry)
- **Conditional loading**: KaTeX and Mermaid only on pages that use them
- **instant.page**: Prefetches links on hover for near-instant navigation

## 6. Internationalization Strategy

### Why Five Languages?
- **English**: International standard
- **Simplified Chinese**: Mainland China market
- **Traditional Chinese**: Taiwan, Hong Kong, Macau
- **Japanese**: Major Asian market
- **Korean**: Another major Asian market

### Chinese Typography Conventions
- Full-width punctuation: `，。！？` (not `,. !?`)
- Chinese quotes: `「」『』` (not `""''`)
- Spacing: Add space around untranslatable English terms
- **Why**: Proper CJK typography is essential for readability

## 7. Security Principles

### Defense in Depth
1. **Escape by default**: All template variables
2. **SRI (Subresource Integrity)**: Verify asset integrity
3. **No inline scripts**: Except essential config (theme preference)
4. **Vendor dependencies**: No external CDNs to compromise
5. **CSP-friendly**: Compatible with Content Security Policy

### When to use `safeHTML`
Only for:
- Pre-processed markdown content (already sanitized by Hugo)
- Trusted configuration (site subtitle)

**Never** for user input or external content.

## 8. Development Workflow Philosophy

### Incremental Changes
- Small, focused commits over large rewrites
- Each commit should be independently auditable
- Conventional commit format for clarity

### Testing Strategy
- **Visual**: Test with multilingual sample content
- **Accessibility**: Browser DevTools accessibility panel
- **Performance**: Lighthouse audit (target 95+)
- **Cross-browser**: Chrome, Firefox, Safari
- **Responsive**: Mobile, tablet, desktop breakpoints

### Documentation Discipline
- Update README.md for user-facing changes
- Update AGENTS.md: [Working Conventions](#3-working-conventions) for coding
  conventions, the other sections for design philosophy. CLAUDE.md and
  GEMINI.md only import it
- Document all i18n keys with comments

## 9. Dependency Management

### Adding Dependencies - Decision Tree
1. **Can we avoid it?** (Most important question)
2. **Is it well-maintained?** (Recent releases, active community)
3. **What's the license?** (Compatible with Apache 2.0)
4. **What's the size?** (Every KB matters)
5. **Can we vendor it?** (Self-hosting requirement)

### Current Dependencies Rationale
- **KaTeX 0.19.0**: Best-in-class math rendering, self-contained
- **instant.page 5.2.0**: Tiny (1KB), dramatic perceived performance improvement
- **Mermaid 11.17.2**: Generation of diagram and flowchart from text, loaded conditionally
- **Noto Sans Mono 2.014**: Clean Latin monospace subset with consistent character metrics
- **polyxslt 1.1.0**: Keeps the styled feeds working after browsers drop XSLT; never requested by a browser that still has it
- **jieba 0.42.1**: Chinese text segmentation for offline search index generator (in `tools/vendor/jieba/`)
- **OpenCC 1.4.2** (character table only): lets a search in Simplified or Traditional Chinese find posts in either, at about 5 KB of index (in `tools/vendor/opencc/`)
- **Remark42**: Optional, user's choice, not vendored (embedded script)

### Attribution Standards
- Include LICENSE file in vendored directory
- Document in NOTICE file with copyright, license, location, URL
- Apache 2.0 copyright header on our code

### Python Tools (auxmark and utilities)

**Design Philosophy:**
- **Modularity**: Plugin architecture for extensibility (see `tools/auxmark/modules/`)
- **Git-aware**: Tools should respect git state and integrate with version control
- **Testing first**: Comprehensive test suites using temporary directories
- **Dry-run mode**: All tools must support `--dry-run` to preview changes
- **Verbose logging**: `--verbose` flag for debugging and transparency

**Key Best Practices:**
1. **Use `git mv` for file operations** instead of `shutil.move()` when moving tracked files
   - Git recognizes it as a rename operation (better history)
   - Example: Converting `post.md` → `post/index.md` for Hugo page bundles
   - Fallback gracefully if git command fails

2. **Track state carefully in multi-pass operations**
   - When expanding files (e.g., EXPAND action in auxmark), mark **old paths** as processed
   - Queue **new paths** for processing
   - Example: Mark `post.md` as processed, queue `post/index.md` for next iteration

3. **Test coverage requirements**
   - Dry-run mode validation
   - Git-aware file scanning (only tracked files)
   - Module selection and filtering
   - Actual execution with real downloads/operations
   - Error handling and edge cases

4. **Error handling patterns**
   - Log warnings to stderr, continue processing other files
   - Return non-zero exit codes on critical failures
   - Provide clear, actionable error messages
   - Use subprocess error handling for git operations

## 10. AI Collaboration Philosophy

### Contribution Guidelines
**Priorities:**
1. Preserve existing conventions (consistency > personal preference)
2. i18n first (internationalization is non-negotiable)
3. Performance matters (measure impact of changes)
4. Accessibility always (WCAG compliance)
5. Document decisions (help future contributors understand "why")

### Code Review Focus
When reviewing changes, prioritize:
1. **i18n compliance**: No hardcoded text?
2. **Formatting**: as `.editorconfig` states (2 spaces; 4 in Python; tabs in `tools/*.sh`), EOF newline?
3. **ARIA localization**: All labels internationalized?
4. **Performance impact**: Adds bloat? Layout thrashing?
5. **Accessibility**: Keyboard navigation? Focus management?
6. **Dependencies**: Properly attributed? Necessary?

### When to Push Back
Reject changes that:
- Hardcode text (violates i18n requirement)
- Add unnecessary dependencies
- Harm performance without justification
- Break accessibility
- Break the formatting `.editorconfig` states
- Lack documentation

## 11. Common Pitfalls & Solutions

### Anti-Patterns to Avoid
❌ **Hardcoded text**: Use `{{ T "key" }}` instead
❌ **`transition: all`**: Specify exact properties
❌ **Repeated DOM queries**: Cache references
❌ **Magic numbers**: Use CSS variables
❌ **External CDNs**: Vendor dependencies
❌ **Formatting against `.editorconfig`**: 2 spaces, 4 in Python, tabs only in `tools/*.sh`
❌ **Inline styles/scripts**: Use external files
❌ **CSS containment on tables**: Only simple components

### Best Practices
✅ **Externalize all text** to i18n files
✅ **Specific transitions** for performance
✅ **Cache DOM references** at initialization
✅ **CSS variables** for repeated values
✅ **Vendor dependencies** with versions
✅ **Formatting** as `.editorconfig` states
✅ **Hugo asset pipeline** for processing
✅ **Semantic HTML5** elements
✅ **Git mv for file operations** (Python tools: prefer `git mv` over `shutil.move()` for better history tracking)

## 12. Browser Support Philosophy

### Baseline Widely Available
Target: [Baseline Widely Available](https://web.dev/baseline), a rolling floor.
As of 2026: Chrome/Edge 122+, Firefox 124+, Safari/iOS 17.4+.

**Rules:**
- A widely available feature may be used without a fallback when that buys a
  real gain (less code, simpler CSS). Don't break older browsers gratuitously,
  but don't keep workarounds for browsers below the floor either
- A feature newer than the floor is a progressive enhancement: the page must
  still work without it
- JS syntax is lowered by esbuild to `es2024` (`_partials/foot/script.html`);
  runtime APIs are not polyfilled, so check them against Baseline in review
- Check a feature's status on [web-features](https://web-platform-dx.github.io/web-features-explorer/)
  or MDN's Baseline badge before relying on it

### Progressive Enhancement
- **Backdrop-filter**: Glass effect with solid background fallback
- **LocalStorage**: Graceful degradation if unavailable
- **CSS `@supports`**: Feature detection for critical features

### Modern Features Used
- CSS: Variables, Grid, Flexbox, `dvh`, containment, `color-scheme`, backdrop-filter
- CJK Typography: `text-autospace: normal`, `text-spacing-trim: normal`, `font-feature-settings: "chws" 1` for OpenType CJK punctuation kerning
- Build-time CJK Filtering: line-wrap newlines are collapsed at parse time by
  `markup.goldmark.extensions.cjk` (site config); spaces typed between CJK and
  Latin runs are stripped in `layouts/_partials/_funcs/typeset-content.html` so
  `text-autospace` can insert the proportional space instead. That partial also
  expands ruby annotations, and is shared by the HTML and feed pipelines.
- JS: ES2024 syntax floor, ES modules, `<dialog>`, modern array/DOM methods, Intersection Observer

## 13. Quality Assurance Checklist

Before committing:
- [ ] No hardcoded text (all i18n)
- [ ] ARIA labels localized
- [ ] Indentation as `.editorconfig` states
- [ ] Files end with single newline
- [ ] No trailing whitespace
- [ ] Conventional commit message
- [ ] Documentation updated
- [ ] Accessibility preserved
- [ ] Performance not regressed

Before release:
- [ ] All i18n files complete (5 languages)
- [ ] README.md comprehensive
- [ ] LICENSE and NOTICE accurate
- [ ] No console errors/warnings
- [ ] Lighthouse score 95+
- [ ] Cross-browser tested
- [ ] Mobile responsive verified
- [ ] WCAG AA audit passed

## Summary

This theme prioritizes **performance**, **accessibility**, and **internationalization** while maintaining **minimal complexity**. Every decision should align with these principles.

**When in doubt:**
1. Check existing patterns in codebase
2. Consult [Working Conventions](#3-working-conventions) for specific conventions
3. Prioritize user experience over developer convenience
4. Ask before adding complexity

The goal is a theme that's fast, accessible, and maintainable for years to come.
