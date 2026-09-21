# Chaos

A minimalist Hugo theme designed for clarity, performance, and excellent Chinese typography support.

## Features

- **Performance-focused**: Lightweight with minimal dependencies, no JavaScript frameworks
- **Dark/Light/Auto Mode**: Three-state toggle (🌓 Auto / ☀️ Light / 🌙 Dark) with live real-time OS preference synchronization
- **Japanese Traditional Color Palette**: Crafted with classical 和色 (*Wairo*) aesthetics — 白練 (*Shiro-neri*), 墨 (*Sumi*), 红緋 (*Hi-iro*), 瑠璃色 (*Ruri-iro*), and 生成色 (*Kinari-iro*) — balancing paper-like tranquility with WCAG AAA accessibility
- **Responsive Design**: Mobile-first layout with hamburger menu and glass-morphism effects
- **Table of Contents**: Automatic TOC for article pages with sticky sidebar and active section highlighting
- **Instant Page Transitions & Prerendering**: Native 0ms navigation via W3C Speculation Rules API with fallback to [instant.page](https://instant.page/)
- **View Transitions**: Native cross-document transitions between pages via CSS `@view-transition`
- **Print-Ready Articles**: Automatic conversion of external links to footnotes for clean, readable printouts
- **Chinese Typography**: Modern CSS features for CJK text (text-autospace, hanging-punctuation, auto-phrase)
- **Mathematics Support**: Built-in KaTeX integration for scientific content
- **SEO & Licensing**: Comprehensive OpenGraph (with territory-cased locale, primary image alt, and alternates), Twitter Cards, Schema.org (JSON-LD BlogPosting/WebSite/BreadcrumbList with complete publisher metadata), multilingual hreflang and default-language x-default clusters, W3C-compliant XML sitemap, and machine-readable CC licensing support
- **Accessible**: WCAG 2.1 AA compliant with skip-to-content links, ARIA labels, screen reader announcements, and reduced-motion support
- **Multilingual**: Native i18n support for 5 languages (EN, zh-CN, zh-TW, JA, KO) with automatic hreflang links, localized SEO metadata, and x-default navigation paths

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

  # Taxonomy display controls (optional)
  excludedCategories = ["CategoryToHide"] # Hide from homepage "Core Categories"
  excludedTags = ["TagToHide"]           # Hide from homepage & /tags/ "Popular Tags"
  # featuredCategories = ["Category1", "Category2"] # Optional pinned list for "Core Categories"

  # Client-side full-text search (optional, disabled by default)
  [params.search]
    enable = true                      # Enable search button and '/' hotkey
    indexURL = "/search-index.json"    # Default: "/search-index.json"

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

# Indexing & Deprecation controls (optional)
deprecated = false                     # Set true to demote in on-site search and display [Deprecated] badge
searchHidden = false                   # Set true to exclude from on-site search (search engines unaffected)
noindex = false                        # Set true to exclude from search engines, on-site search, and sitemap
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

All markdown images are handled automatically by the custom render hook:

```markdown
![Alt text](image.jpg)
```

- **Page bundle images**: Automatically processed into responsive `<picture>` elements with WebP conversion, multiple viewport resolutions (360px, 640px, 960px, 1232px), 1x/2x DPR variants, and explicit `width`/`height` to eliminate Cumulative Layout Shift (CLS).
- **Static & relative paths**: Fall back to lazy-loaded `<picture><img>` elements with subpath-aware `relURL` resolution, preventing broken links and ignoring empty destinations.
- **Remote images**: Rendered with native `loading="lazy"` and `decoding="async"`.

### Social Media Embeds

Embed X/Twitter posts:

```markdown
{{< x user="username" id="1234567890" >}}
```

**Privacy-Enhanced Caching** (Recommended):

To avoid live API calls and remove tracking scripts, pre-cache tweets using the included tool:

```bash
# Fetch and cache a single tweet (removes scripts, no tracking)
python3 themes/chaos/tools/fetch_x_embed.py https://x.com/username/status/1234567890

# Or use just the tweet ID
python3 themes/chaos/tools/fetch_x_embed.py 1234567890

# Batch process from a file (one URL or ID per line)
python3 themes/chaos/tools/fetch_x_embed.py --batch tweets.txt

# Refresh an existing cached tweet
python3 themes/chaos/tools/fetch_x_embed.py --refresh 1234567890
```

Cached files are stored in `data/x_embeds/` and automatically used by the shortcode when available. The tool sanitizes HTML by removing:
- All `<script>` tags (no tracking, no external dependencies)
- Event handlers (`onclick`, `onload`, etc.)
- Iframes and embeds (marked as comments for review)

Benefits:
- **Privacy**: No client-side requests to X, no tracking
- **Performance**: Faster page loads, works offline
- **Reliability**: Content survives if tweets are deleted
- **Version control**: Cached content can be committed to git

### Client-Side Full-Text Search

Chaos provides a zero-dependency, privacy-preserving client-side full-text search feature.

1. **Enable in Site Configuration**:
   ```toml
   [params.search]
     enable = true
     indexURL = "/search-index.json"
   ```

2. **Generate Search Index During Build**:
   Run the offline indexing tool against your Hugo content directory:
   ```bash
   python3 themes/chaos/tools/build_search_index.py --content content --output public/search-index.json
   ```

3. **Key Features**:
   - **Chinese Segmentation**: Uses vendored `jieba` for accurate CJK phrase and technical vocabulary tokenization.
   - **Zero npm / Bundlers**: 100% native HTML5 `<dialog>` and Vanilla JavaScript (~1.5 KB minified).
   - **Keyboard Friendly**: Press `/` anywhere on the page to open search, `ArrowUp`/`ArrowDown` to navigate results, `Enter` to open, and `Esc` to close.
   - **Lazy Loading**: Index data is loaded asynchronously only on the first user interaction.

4. **Search & Indexing Controls (Front Matter)**:
   - `deprecated = true`: Marks the post as outdated. It remains indexed, but its relevance score is demoted (0.25x multiplier) so fresh content ranks first, and a localized `[Deprecated]` badge is displayed beside the title in search results. (Alias: `outdated = true`).
   - `searchHidden = true`: Excludes the post from the local search index (`search-index.json`), while leaving external search engine indexing and `sitemap.xml` intact. (Aliases: `search_hidden = true`, `search = false`).
   - `noindex = true`: Fully hides the post from on-site search and search engines; omits the post from `sitemap.xml` and outputs `<meta name="robots" content="noindex, nofollow">`. (Alias: `private = true`).

## Design System & Aesthetics

Chaos draws inspiration from Japanese editorial minimalism and traditional papercraft (*Washi* / 和紙), blending Eastern understatement with the crisp typography demanded by in-depth systems engineering essays.

### Color Palette (和色 *Wairo*)

The light mode palette is mapped to classical Japanese colors, pairing organic tones with high-contrast text to exceed WCAG 2.1 AAA accessibility standards:

| CSS Variable | Value | Japanese Name | Role & Intent |
| :--- | :--- | :--- | :--- |
| `--bg` | `#FAFAFA` | 白練 (*Shiro-neri*) | Soft, unbleached off-white base that eliminates harsh screen glare |
| `--surface` | `#FFFFFF` | 純白 (*Junpaku*) | Crisp panel surfaces providing subtle elevation |
| `--text` | `#222222` | 墨 (*Sumi*) | Deep soot-black ink for long-form reading (15.3:1 contrast) |
| `--heading` | `#111111` | 漆黑 (*Shikkoku*) | Pitch-black lacquer tone for section headings (18.2:1 contrast) |
| `--muted` | `#545454` | 墨灰 (*Sumi-hai*) | Muted graphite for metadata, timestamps, and captions (5.8:1 contrast) |
| `--primary` | `#A23E48` | 红緋 (*Hi-iro*) | Deep scarlet accent inspired by cinnabar seal paste and lacquerware |
| `--accent` | `#2E5A88` | 瑠璃色 (*Ruri-iro*) | Lapis lazuli blue for blockquote borders and secondary markers |
| `--paper` | `#F0E6D2` | 生成色 (*Kinari-iro*) | Unbleached washi tone for table headers, active sidebar jumps, and collapsible TOC |
| `--link` | `#0050A5` | 藍濃 (*Ai-nō*) | Distinct high-contrast blue meeting WCAG AAA (7.2:1 contrast) |

In Dark Mode, the palette transitions into a restful midnight theme anchored on `#1C1C1C` with warm coral orange (`#FF6F61` 珊瑚橙) highlights and soft charcoal paper surfaces (`#2A2A2A`).

## Customization

### Syntax Highlighting

The theme includes built-in syntax highlighting themes:
- Light mode: GitHub
- Dark mode: GitHub Dark

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
- **Security.txt**: RFC 9116 security vulnerability disclosure metadata (`/.well-known/security.txt`)

Configure in `config.toml`:

```toml
[outputs]
  home = ["HTML", "ATOM", "RSS", "SECURITY"]

[params.security]
  enable = true
  contact = "mailto:security@example.com"
  languages = "zh, en"
```

## Printing

The theme provides optimized print output for articles, ensuring a clean and readable experience:

- **Print-Friendly Layout**: Automatically hides navigation, interactive elements, and other non-essential components for a clutter-free printout.
- **Automatic Footnotes with Bidirectional Links**: External links within the article are automatically converted into a numbered "References" section at the end of the printed document. Each link in the text shows a clickable `[1]` reference, and each footnote includes a clickable `^` symbol that links back to the original reference (Wikipedia-style navigation).
- **Smart Code Block Pagination**: Code blocks shorter than 14 lines stay together on one page. Longer blocks break naturally across pages with minimum 7 lines on each side, preventing awkward fragments while avoiding wasted blank space.
- **GitHub Syntax Highlighting**: Code blocks use GitHub's color scheme for print, optimized for both color and monochrome printers. All colors meet WCAG AA contrast standards for excellent readability.
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
- **Instant Prerendering**: Integrates W3C Speculation Rules API for native 0ms background prerendering, with seamless fallback to [instant.page](https://instant.page/) 5.2.0 on older browsers
- **View Transitions**: Native cross-document view transitions (`@view-transition { navigation: auto; }`) for smooth app-like page transitions without JavaScript router overhead
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
- **Speculation Rules Scoping**: Prerendering rules are cleanly scoped via `relURL` (supporting subpath baseURL deployments), with an `instant.page` fallback for older browsers

### Content Delivery
- **Lazy Loading**: Images load on-demand with `async` decoding
- **WebP Conversion**: Automatic modern format support with fallbacks
- **Responsive Images**: Multiple resolutions and DPR variants; bundle images include explicit dimensions to prevent CLS
- **Universal Image Fallback**: Seamless fallback for static and non-bundle images with native lazy loading
- **Layout Stability**: Proper content width constraints prevent layout shifts from long code blocks

### SEO & Metadata Architecture
- **Mobile Viewport Compliance**: Strict `<meta name="viewport" content="width=device-width, initial-scale=1">` standards
- **Clean 404 Pages**: Automatic suppression of canonical links on 404 status pages to avoid search crawler confusion
- **Multilingual hreflang & x-default**: Seamless cross-language discovery cluster for translated articles, pointing `x-default` consistently to the default content language
- **W3C-Compliant XML Sitemap**: Namespaced with `xmlns:xhtml` and multilingual alternate links
- **Rich Structured Data**: Complete Schema.org JSON-LD (WebSite, BlogPosting, BreadcrumbList) with full publisher and author metadata
- **Standardized Social Cards**: OpenGraph `og:locale` normalized to `language_TERRITORY`, with primary card `og:image:alt` and `twitter:image:alt`

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

**Known Limitations:**
- Chrome/Edge: CJK line-breaking rules not applied to inline math formulas. Chinese punctuation may appear at line start after KaTeX formulas. Works correctly in Safari and Firefox.

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

All dependencies are vendored in `static/_3p/` and `tools/vendor/` to ensure reliability and privacy:

- **KaTeX 0.16.22**: Mathematical typesetting for scientific content
- **instant.page 5.2.0**: Link prefetching for near-instant page transitions
- **jieba 0.42.1**: Chinese text segmentation for offline search index generator (in `tools/vendor/jieba/`)

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
