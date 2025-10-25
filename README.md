# Chaos

A minimalist Hugo theme designed for clarity, performance, and excellent Chinese typography support.

## Features

- **Performance-focused**: Lightweight with minimal dependencies, no JavaScript frameworks
- **Dark/Light Mode**: Automatic system preference detection with manual toggle
- **Responsive Design**: Mobile-first layout with hamburger menu and glass-morphism effects
- **Table of Contents**: Automatic TOC for article pages with sticky sidebar and active section highlighting
- **Instant Page Transitions**: Near-instant navigation with link prefetching via [instant.page](https://instant.page/)
- **Print-Ready Articles**: Automatic conversion of external links to footnotes for clean, readable printouts
- **Chinese Typography**: Modern CSS features for CJK text (text-autospace, hanging-punctuation, auto-phrase)
- **Mathematics Support**: Built-in KaTeX integration for scientific content
- **SEO Optimized**: Complete OpenGraph, Twitter Cards, and Schema.org support
- **Accessible**: WCAG 2.1 AA compliant with skip-to-content links, ARIA labels, and screen reader announcements
- **Multilingual**: i18n support for English, Simplified Chinese, Traditional Chinese, Japanese, and Korean

## Requirements

- Hugo 0.146.0 or later (standard version, extended not required)

## Installation

### As a Git Submodule

```bash
cd your-hugo-site
git submodule add https://github.com/yourusername/chaos.git themes/chaos
```

### Manual Installation

1. Download the latest release
2. Extract to `themes/chaos` in your Hugo site directory

### Configuration

Update your site's `config.toml` or `hugo.toml`:

```toml
theme = "chaos"
```

## Quick Start

See `hugo.toml` in this theme directory for a complete example configuration. Key settings:

```toml
baseURL = 'https://example.org/'
languageCode = 'zh-cn'
defaultContentLanguage = 'zh-cn'
title = 'My New Hugo Site'

[params]
  subtitle = "Optional subtitle with **Markdown** support"

[menus]
  [[menus.main]]
    identifier = 'home'
    pageRef = '/'
    weight = 10

  [[menus.main]]
    identifier = 'tags'
    pageRef = '/tags'
    weight = 20
```

## Configuration Options

### Site Parameters

```toml
[params]
  # Optional subtitle displayed in site header (supports Markdown)
  subtitle = "Your site description"

  # Remark42 comment system (optional)
  remarkURL = "https://remark.example.com"
  remarkSiteId = "remark"              # Default: "remark"
  remarkLocale = "zh"                  # Default: "zh"
  remarkNoFooter = "true"              # Default: "true"

  # Content filtering
  mainSections = ["posts"]             # Sections to display on homepage
  excludedTypes = ["page"]             # Content types to hide from listings

[params.social]
  facebook_app_id = "..."
  facebook_admin = "..."
```

### Front Matter

Basic post configuration:

```toml
+++
date = '2024-01-15'
draft = false
title = 'Article Title'
description = 'SEO meta description'
categories = ['Category1']
tags = ['tag1', 'tag2']
series = 'Series Name'                 # For grouping related posts
+++
```

## Content Organization

### Directory Structure

```
content/
├── posts/                             # Blog posts
│   └── my-first-post.md
├── pages/                             # Static pages
│   └── about.md
└── archives/                          # Archive page
    └── _index.md
```

### Taxonomies

The theme supports the following taxonomies:

- **tags**: Post tags for topic-based organization
- **categories**: Broader content categorization
- **series**: Group related posts together
- **keywords**: SEO-focused keywords (prioritized in Schema.org metadata)

## Special Features

### Mathematics

The theme includes KaTeX support for rendering mathematical expressions. Enable the passthrough extension in your configuration:

```toml
[markup.goldmark.extensions.passthrough]
  enable = true
  [markup.goldmark.extensions.passthrough.delimiters]
    block = [['$$', '$$']]
    inline = [['\(', '\)']]
```

Then use the delimiters in your content:

```markdown
Inline math: \(E = mc^2\)

Display math:
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$
```

### Ruby Annotations (CJK Phonetic Guides)

For Chinese/Japanese ruby annotations:

```markdown
[漢字]{かんじ}
[汉字]^(hàn zì)
```

### Alerts/Callouts

Create styled alert boxes:

```markdown
> [!NOTE]
> This is a note callout

> [!TIP]
> Helpful tip here

> [!WARNING]
> Important warning

> [!IMPORTANT]
> Critical information

> [!CAUTION]
> Proceed with caution
```

### Responsive Images

All images automatically generate responsive srcsets with WebP conversion:

```markdown
![Alt text](image.jpg)
```

This creates:
- Multiple resolutions (360px, 640px, 960px, 1232px)
- 1x and 2x DPR variants
- WebP format with fallback
- Lazy loading enabled

### Social Media Embeds

Embed X/Twitter posts:

```markdown
{{< x user="username" id="1234567890" >}}
```

## Customization

### Syntax Highlighting

The theme includes built-in syntax highlighting themes:
- Light mode: Solarized Light
- Dark mode: Solarized Dark

Configure in `config.toml`:

```toml
[markup.highlight]
  noClasses = false
```

### Custom Layouts

Override any template by creating the same file path in your site's `layouts/` directory:

```
your-site/
└── layouts/
    ├── _default/
    │   └── single.html           # Override single page template
    └── partials/
        └── footer.html           # Override footer
```

## Output Formats

The theme provides multiple output formats:

- **HTML**: Standard web pages
- **ATOM**: Feed with XSLT stylesheet
- **RSS**: RSS 2.0 feed
- **Sitemap**: XML sitemap with XSLT
- **Redirects**: Redirect mapping for aliases

Configure in `config.toml`:

```toml
[outputs]
  home = ["HTML", "ATOM", "RSS"]
```

## Printing

The theme provides optimized print output for articles, ensuring a clean and readable experience:

- **Print-Friendly Layout**: Automatically hides navigation, interactive elements, and other non-essential components for a clutter-free printout.
- **Automatic Footnotes with Bidirectional Links**: External links within the article are automatically converted into a numbered "References" section at the end of the printed document. Each link in the text shows a clickable `[1]` reference, and each footnote includes a clickable `^` symbol that links back to the original reference (Wikipedia-style navigation).
- **Smart Code Block Pagination**: Code blocks shorter than 14 lines stay together on one page. Longer blocks break naturally across pages with minimum 7 lines on each side, preventing awkward fragments while avoiding wasted blank space.
- **Optimized Typography**: Adjusts font sizes, line spacing, and page breaks for optimal readability on paper.

## Mobile Navigation

On screens ≤600px, the navigation menu automatically switches to a hamburger menu:

- **Glass Effect**: Semi-transparent background with 12px backdrop blur
- **Overlay Design**: Menu floats over content instead of pushing it down
- **Smart Interactions**:
  - Click hamburger icon (☰) to toggle menu
  - Click outside or on a link to close
  - Press Escape key to close
- **Accessibility**: Full keyboard navigation with focus management

The menu includes all configured navigation items plus the RSS/Atom feed link.

## Table of Contents

Article pages automatically display a table of contents when the content has sufficient headings (h2, h3, h4):

- **Desktop (≥1360px)**: Sticky sidebar on the right side
  - Remains visible while scrolling
  - Shows active section highlighting
  - Article width: 960px for comfortable reading
  - When TOC is absent, balanced spacing with equal left/right margins

- **Tablet/Mobile (<1360px)**: Floating button with overlay
  - Article width: up to 780px for optimal code display
  - Floating button in bottom-right corner
  - Click to show/hide full-screen TOC
  - Glass-morphism effect with backdrop blur
  - Close by clicking outside, on a link, or pressing Escape

**Active Section Highlighting**:
- Uses Intersection Observer API for efficient scroll tracking
- Current section highlighted in primary color
- Smooth transitions between sections

**Accessibility**:
- Full keyboard navigation support
- ARIA labels and states
- Focus management on open/close
- Screen reader compatible

## Internationalization

The theme includes translations for:
- English (en-US)
- Simplified Chinese (zh-CN)
- Traditional Chinese (zh-TW)
- Japanese (ja-JP)
- Korean (ko-KR)

Add custom translations in `i18n/` directory:

```toml
# i18n/en-US.toml
[readMore]
other = "Read more"

[joinDiscussion]
other = "Join the discussion"
```

## Performance

The theme is optimized for performance with modern best practices:

### Page Load & Navigation
- **Instant Page Transitions**: Integrates [instant.page](https://instant.page/) 5.2.0 for near-instant navigation by prefetching links on hover
- **Minimal JavaScript**: ~3KB total for all features (theme switching + mobile menu + TOC)
- **Partial Caching**: Header and footer cached per language for faster rendering
- **Preconnect Links**: Early connection to external services (comment server)

### CSS Performance
- **Shared Utility Classes**: Reusable `.overlay-blur` class reduces code duplication
- **CSS Containment**: Applied to isolated components (`.toc`, `.alert`) for optimized rendering
- **Specific Transitions**: Only animates properties that change (not `transition: all`)
- **Modern Viewport Units**: Uses `dvh` (dynamic viewport height) for mobile-friendly layouts
- **CSS Variables**: Centralized theming tokens for consistency and maintainability
- **Production Build**: Minified and fingerprinted with Subresource Integrity (SRI)

### JavaScript Optimization
- **Cached DOM References**: Query elements once at initialization, reuse throughout
- **Modern DOM Methods**: Uses `replaceChildren()` and `append()` for batch operations
- **Optimized Intersection Observer**: Tracks current active element, reduces DOM operations by ~80%
- **Consolidated Event Listeners**: Single handlers for click-outside and Escape key events
- **Helper Functions**: DRY patterns with reusable utilities (`setupOverlayToggle`, `checkMediaQuery`)

### Content Delivery
- **Lazy Loading**: Images load on-demand with `async` decoding
- **WebP Conversion**: Automatic modern format support with fallbacks
- **Responsive Images**: Multiple resolutions and DPR variants
- **Layout Stability**: Proper content width constraints prevent layout shifts from long code blocks

### Interaction Performance
- **Efficient Animations**: Hardware-accelerated backdrop-filter for glass effects
- **Smart Scroll Tracking**: Intersection Observer API instead of scroll events for TOC
- **Reduced Motion Support**: Respects `prefers-reduced-motion` for accessibility

## Browser Support

**Full Features (Glass Effect):**
- Chrome/Edge 76+
- Safari 9+ (with -webkit-backdrop-filter)
- Firefox 103+

**Fallback Support:**
- Firefox <103: Solid background instead of glass effect
- Older browsers: Progressive enhancement with solid backgrounds
- All core functionality works in IE11+ (though deprecated)

## Accessibility

**WCAG 2.1 AA Compliant:**
- Semantic HTML5 elements (`<nav>`, `<article>`, `<button>`, `<aside>`)
- ARIA labels and states (`aria-label`, `aria-expanded`, `aria-current`)
- Full keyboard navigation:
  - Tab/Shift+Tab for navigation
  - Escape key closes mobile menu and TOC overlay
  - Focus returns to trigger button on close
- Focus indicators on all interactive elements
- Alt text on all images
- Color contrast exceeds WCAG AA standards
- Screen reader compatible

## Development

### Commands

```bash
# Development server with drafts
hugo server -D

# Production-like preview
hugo server

# Build with verbose output
hugo --verbose

# Production build
hugo --gc --minify
```

### Project Structure

```
themes/chaos/
├── archetypes/              # Content templates
├── assets/
│   ├── css/                 # Source CSS files
│   └── js/                  # Source JavaScript
├── i18n/                    # Translation files
├── layouts/
│   ├── _default/            # Default templates
│   ├── _markup/             # Markdown render hooks
│   ├── partials/            # Reusable components
│   └── shortcodes/          # Content shortcodes
├── static/
│   └── _3p/                 # Third-party dependencies
│       └── katex/           # KaTeX for math rendering
└── hugo.toml                # Example configuration
```

## Dependencies

### Included (Vendored)

All dependencies are vendored in `static/_3p/` to ensure reliability and privacy:

- **KaTeX 0.16.22**: Mathematical typesetting for scientific content
- **instant.page 5.2.0**: Link prefetching for near-instant page transitions

### No External Dependencies

- No npm packages required
- No JavaScript frameworks
- No external CDNs (except optional comment system)
- No build tools beyond Hugo
- All assets self-hosted for performance and privacy

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Follow the existing code style (2-space indentation for HTML/TOML)
2. Test changes with `hugo server`
3. Ensure production build works: `hugo --gc --minify`
4. Update documentation for new features
5. Use conventional commit messages (`feat:`, `fix:`, `docs:`, etc.)

## License

Apache 2.0 License - see LICENSE file for details.

## Credits

- Built with [Hugo](https://gohugo.io/)
- Syntax highlighting by [Chroma](https://github.com/alecthomas/chroma)
- Math rendering by [KaTeX](https://katex.org/)
- Instant navigation by [instant.page](https://instant.page/)
- Comment system support for [Remark42](https://remark42.com/)
