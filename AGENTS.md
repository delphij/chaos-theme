# AGENTS.md: AI Collaboration Guide

This document provides essential context for AI models and human contributors collaborating on this Hugo theme. Following these guidelines ensures **consistency, maintainability, and production quality**.

## 1. Project Philosophy

### Design Principles
* **Minimalism**: Add features only when necessary; prefer simplicity over complexity
* **Performance First**: Every byte counts - target <10KB total JavaScript, efficient CSS
* **Accessibility Always**: WCAG 2.1 AA compliance is non-negotiable
* **Internationalization by Default**: No hardcoded text; proper CJK typography support
* **Progressive Enhancement**: Modern browsers first, graceful degradation for older ones
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
- **Custom renderers**: Override markdown rendering for images, code, math
- **Asset pipeline**: Hugo Pipes handles bundling, minification, fingerprinting, SRI

### Why Vendored Dependencies?
- **Reliability**: No external service outages
- **Privacy**: No tracking via CDN requests
- **Performance**: Served from same domain (no DNS lookup, connection overhead)
- **Versioning**: Explicit control over versions

## 3. Code Quality Standards

### Formatting Rationale
**2-space indentation** (not tabs):
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

## 4. Performance Philosophy

### CSS Performance
**Problem**: Poor CSS practices cause layout thrashing and repaints.

**Solutions applied:**
1. **Specific transitions** (not `all`): Browser only watches properties that change
2. **CSS containment**: Isolates component layout calculations from rest of page
3. **Modern viewport units** (`dvh`): Adjusts for mobile browser UI
4. **CSS variables**: Single source of truth, reduces duplication
5. **Shared utilities**: `.overlay-blur` used by menu and TOC

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
- **Partial caching**: Static components cached per language
- **instant.page**: Prefetches links on hover for near-instant navigation

## 5. Internationalization Strategy

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

## 6. Security Principles

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

## 7. Development Workflow Philosophy

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
- Update CLAUDE.md for coding conventions
- Update AGENTS.md for design philosophy
- Document all i18n keys with comments

## 8. Dependency Management

### Adding Dependencies - Decision Tree
1. **Can we avoid it?** (Most important question)
2. **Is it well-maintained?** (Recent releases, active community)
3. **What's the license?** (Compatible with Apache 2.0)
4. **What's the size?** (Every KB matters)
5. **Can we vendor it?** (Self-hosting requirement)

### Current Dependencies Rationale
- **KaTeX 0.16.22**: Best-in-class math rendering, self-contained
- **instant.page 5.2.0**: Tiny (1KB), dramatic perceived performance improvement
- **Remark42**: Optional, user's choice, not vendored (embedded script)

### Attribution Standards
- Include LICENSE file in vendored directory
- Document in NOTICE file with copyright, license, location, URL
- Apache 2.0 copyright header on our code

## 9. AI Collaboration Philosophy

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
2. **Formatting**: 2-space, no tabs, EOF newline?
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
- Use tabs or inconsistent formatting
- Lack documentation

## 10. Common Pitfalls & Solutions

### Anti-Patterns to Avoid
❌ **Hardcoded text**: Use `{{ T "key" }}` instead
❌ **`transition: all`**: Specify exact properties
❌ **Repeated DOM queries**: Cache references
❌ **Magic numbers**: Use CSS variables
❌ **External CDNs**: Vendor dependencies
❌ **Tabs for indentation**: Use 2 spaces
❌ **Inline styles/scripts**: Use external files
❌ **CSS containment on tables**: Only simple components

### Best Practices
✅ **Externalize all text** to i18n files
✅ **Specific transitions** for performance
✅ **Cache DOM references** at initialization
✅ **CSS variables** for repeated values
✅ **Vendor dependencies** with versions
✅ **2-space indentation** consistently
✅ **Hugo asset pipeline** for processing
✅ **Semantic HTML5** elements

## 11. Browser Support Philosophy

### Modern Browsers First
Target: Chrome/Edge 112+, Firefox 117+, Safari 16.5+ (2023+)

**Rationale:**
- Enables modern CSS/JS features
- Reduces polyfill bloat
- Most users on modern browsers
- Legacy browser share <2% globally

### Progressive Enhancement
- **Backdrop-filter**: Glass effect with solid background fallback
- **LocalStorage**: Graceful degradation if unavailable
- **CSS `@supports`**: Feature detection for critical features

### Modern Features Used
- CSS: Variables, Grid, Flexbox, `dvh`, containment, `color-scheme`, backdrop-filter
- JS: ES6+, optional chaining, nullish coalescing, modern array/DOM methods, Intersection Observer

## 12. Quality Assurance Checklist

Before committing:
- [ ] No hardcoded text (all i18n)
- [ ] ARIA labels localized
- [ ] 2-space indentation, no tabs
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
2. Consult CLAUDE.md for specific conventions
3. Prioritize user experience over developer convenience
4. Ask before adding complexity

The goal is a theme that's fast, accessible, and maintainable for years to come.
