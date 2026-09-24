# Chaos

A minimalist Hugo theme designed for clarity, performance, and excellent Chinese typography support.

| Light | Dark |
| --- | --- |
| ![Chaos theme homepage in light mode](https://raw.githubusercontent.com/delphij/chaos-theme/main/images/screenshot.png) | ![Chaos theme article page in dark mode, with KaTeX math and table of contents](https://raw.githubusercontent.com/delphij/chaos-theme/main/images/screenshot-dark.png) |

Screenshots are taken from the bundled [example site](#example-site).

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

- Hugo 0.158.0 or later (standard version, extended not required)

## Installation

### As a Hugo Module

```bash
cd your-hugo-site
hugo mod init github.com/you/your-site   # once, if the site is not a module yet
```

```toml
# hugo.toml
[module]
  [[module.imports]]
    path = 'github.com/delphij/chaos-theme'
```

`hugo mod get -u github.com/delphij/chaos-theme` updates to the latest release.
A Go toolchain must be installed for Hugo Modules to work.

### As a Git Submodule

```bash
cd your-hugo-site
git submodule add https://github.com/delphij/chaos-theme.git themes/chaos
```

```toml
# hugo.toml
theme = 'chaos'
```

### Manual Installation

1. Download `chaos-theme-<version>.tar.xz` from the
   [latest release](https://github.com/delphij/chaos-theme/releases)
2. Extract it in your site's `themes/` directory; it unpacks to `chaos/`:
   `tar -xJf chaos-theme-<version>.tar.xz -C themes`
3. Set `theme = 'chaos'` in your site's `hugo.toml`

The tool paths in this README (`themes/chaos/tools/...`) assume one of the last
two. With Hugo Modules, run the tools from a checkout of this repository.

## Example Site

The `exampleSite/` directory holds a small demo blog that exercises the theme's features: Chinese typography, ruby annotations, KaTeX math, alerts, syntax highlighting, Mermaid diagrams, taxonomies, and archives. Run it from the theme's root directory:

```bash
hugo server --source exampleSite
```

## Quick Start

`exampleSite/hugo.toml` is a complete configuration to start from. The settings
a site must make itself, because Hugo does not take them from a theme:

```toml
baseURL = 'https://example.org/'
locale = 'zh-cn'
defaultContentLanguage = 'zh-cn'
title = 'My Blog'

# Required for CJK content: without it Hugo counts a whole Chinese sentence as
# one word, so the reading stats are an order of magnitude too low and
# .Summary never truncates -- list pages print whole articles. The theme
# cannot set this for you; Hugo does not inherit it from theme config.
hasCJKLanguage = true

# Hugo does not inherit [outputs] from a theme, so name the formats here or
# /feed.xsl, /sitemap.xsl and /atom.xml are never built.
[outputs]
  home = ['HTML', 'ATOM', 'sitemapxsl', 'RSS', 'feedxsl', 'REDIR']
  section = ['HTML']
  taxonomy = ['HTML']
  term = ['HTML']

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
  # unpaginatedSections = ["archives"] # Sections whose layout renders its own
                                       # complete listing, so the theme must not
                                       # paginate them (default: ["archives"])

  # Routing (optional)
  # Emitted as host redirect rules in /redirects.txt; the "from" URLs are also
  # kept out of the sitemap. Useful when a section URL has moved, e.g. a site
  # that lists its posts at /archives/ instead of /posts/:
  # redirects = [{ from = "/posts/", to = "/archives/" }]
  # archiveBreadcrumbSections = ["posts"] # Sections whose Schema.org breadcrumb
                                          # points at /archives/ instead of the
                                          # section page (pairs with the above)

  # Taxonomy display controls (optional)
  excludedCategories = ["CategoryToHide"] # Hide from homepage "Core Categories"
  excludedTags = ["TagToHide"]           # Hide from homepage & /tags/ "Popular Tags"
  # featuredCategories = ["Category1", "Category2"] # Optional pinned list for "Core Categories" (sorted dynamically by recent activity)
  # featuredCategoriesRecentYears = 5    # Time window in years to prioritize active categories (default: 5, set 0 for all-time count)

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

Chaos includes a zero-dependency, privacy-preserving, high-performance client-side full-text search engine powered by an offline inverted index.

#### Architecture: Progressive Two-Tier Indexing

To balance instant interaction speed with full technical recall, Chaos uses a **two-tier zero-redundancy indexing model**:

1. **Tier 1 — Core Index (`search-index.json`)**:
   - Contains compact document metadata (`id`, `title`, `url`, `date`, `tags`, `categories`, and explicit front matter `description`) plus an inverted index for Title and Tags.
   - Designed for instant interaction (typically ~10–15% of the total index size, achieving an ~85% reduction in initial payload). The modal opens and becomes immediately searchable without user-perceptible delay.
2. **Tier 2 — Body Index (`search-index-body.json`)**:
   - Contains incremental inverted index postings extracted from post bodies and code blocks.
   - **Zero Redundancy**: Posting lists for terms already matched in a post's Title or Tag are strictly omitted (`P_T1(w) ∩ P_T2(w) = ∅`), and document metadata is never duplicated.
   - Streamed asynchronously in the background via `requestIdleCallback` after the modal opens; merges into the memory index in <15ms without blocking user keystrokes.

```
┌─────────────────────────────────────────────────────────────┐
│  Tier 1 (Core Index)               ~10–15% of total index   │
│  ├─ docs: [ {id, title, date, url, tags, description} ]     │
│  └─ index: { term -> [doc_ids from Title/Tags/Categories] } │
└──────────────────────────────┬──────────────────────────────┘
                               │ Immediate modal open (TTI < 50ms)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  Tier 2 (Body Index)               Remaining body postings  │
│  └─ index: { term -> [doc_ids ONLY in Body/Code] }          │
└─────────────────────────────────────────────────────────────┘
                               ▲ Background idle stream & merge
```

#### 1. Enable in Site Configuration

Add to `config.toml` (or `hugo.toml`):

```toml
[params.search]
  enable = true
  indexURL = "/search-index.json"
  # Optional: Hugo automatically fingerprints search-index-body.json
  # if placed in assets/. Explicit path override is also supported:
  # bodyIndexURL = "/search-index-body.json"
```

#### 2. Generate Search Index During Build

Run the offline indexing tool against your Hugo content directory:

```bash
# Recommended: Output to assets/ so Hugo can fingerprint both index files
python3 themes/chaos/tools/build_search_index.py --content content --output assets/search-index.json
```

**Tool Options:**
| Option | Default | Description |
| :--- | :--- | :--- |
| `--content` | `content` | Path to Hugo content directory |
| `--output` | `assets/search-index.json` | Path to Tier 1 core search index |
| `--output-body` | `<stem>-body.json` | Path to Tier 2 body search index (defaults to `assets/search-index-body.json`) |
| `--single-file` | `false` | Generate a legacy single monolithic index file instead of two-tier |
| `--max-body-chars` | `6000` | Maximum body characters to index per post (covers 95%+ of full posts) |
| `--base-url` | `/` | Base URL prefix for post links |

#### 3. Technical Code & Keyword Preservation

Unlike generic blog themes that strip code, Chaos **fully indexes technical code content**:
- **Inline Code (`` `identifier` ``)**: Variable names, struct members, error constants, and CLI flags are preserved.
- **Code Blocks (```` ```lang ... ``` ````)**: Kernel function names, panic backtraces, data structures (e.g. `fatEntry`, `kmem_alloc`), and configuration blocks are fully searchable.
- **CJK Segmentation**: Vendored `jieba` segments mixed Chinese and English prose with domain-specific technical symbol preservation (e.g. `C++`, `C#`, `.NET`, `Google+`, `TCP/IP`).

#### 4. Ranking Algorithm & Scoring Weights

Client-side ranking in `search.js` combines BM25-style IDF with multi-field coordinate boosting:

1. **Smoothed BM25-IDF**: Rare, discriminative keywords (e.g. error codes, specific APIs) receive significantly higher base scores than pervasive words:
   $$\text{IDF} = \max\left(0.6, \ln\left(1 + \frac{N - \text{df} + 0.5}{\text{df} + 0.5}\right)\right)$$
2. **Multi-Field Boosting**:
   - **Exact Title Match**: `+120` pts
   - **Title Consecutive Phrase**: `+60` pts
   - **Tag Consecutive Phrase**: `+45` pts
   - **Summary Phrase Match**: `+25` pts
   - **Token in Title**: `+18` pts (extra `+6` pts if at title start)
   - **Token in Tag**: `+12` pts
   - **Token in Body**: Base IDF score (`~0.6` to `8` pts)
3. **Coordinate Coverage Bonus**: When querying multiple terms, documents matching all terms receive `+35` pts and are multiplied by `(0.5 + 0.5 * coverage)`.
4. **Outdated Demotion**: Documents marked `deprecated` receive a `0.25x` score multiplier.
5. **Tie-Breaking**: Matches with equal scores rank newer posts first.

#### 5. Search & Indexing Controls (Front Matter)

Control per-post visibility and ranking via TOML/YAML front matter:

```toml
+++
title = "FreeBSD Kernel Debugging"
date = 2026-09-21T00:00:00-07:00
description = "Practical guide to analyzing kernel crash dumps with kgdb"
tags = ["FreeBSD", "Kernel", "Debugging"]

# Search Controls
deprecated = false   # Set true to demote (0.25x score) and show [Deprecated] badge
searchHidden = false # Set true to exclude from on-site search (search engines unaffected)
noindex = false      # Set true to hide from search engines, on-site search, and sitemap.xml
+++
```

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

### Custom CSS

The theme's stylesheets are in cascade layers (`chaos.reset`, `chaos.tokens`,
`chaos.base`, `chaos.syntax`, `chaos.components`), and unlayered CSS beats any
layer. A stylesheet your site adds after the theme's (for example from an
overridden `layouts/_partials/head.html`) therefore wins with a plain selector
-- no `!important`, no matching the theme's specificity. To change a colour,
redefine its custom property from `tokens.css` on `:root` (or `html.dark`).

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

### Readable XML in a Post-XSLT Browser

The feeds and the sitemap carry an `<?xml-stylesheet?>` instruction, which is
what makes `feed.xsl` and `sitemap.xsl` render them as readable pages rather
than raw XML. Browsers are removing the XSLT engine behind that: Chrome stops
running XSLT on stable in 158 (November 2026) and removes it in 176, and
Firefox and WebKit have signalled the same.

`tools/render_xsl_companions.sh` keeps those pages working without shipping an
XSLT engine to the browser. Run it after `hugo`, on the built site:

```bash
hugo --minify
sh themes/chaos/tools/post_build.sh public
```

`post_build.sh` is the only entry point a site's build script needs: it runs
the theme's post-build steps in the order they require, so a step added later
reaches every site without each one editing its own build script. Today that
is `strip_xsl_space.sh` followed by `render_xsl_companions.sh`; both are
idempotent and either can still be run on its own.

`strip_xsl_space.sh` removes the whitespace Hugo's minifier cannot: it has no
minifier for `application/xslt+xml`, and routing the stylesheet through the XML
one instead silently trims text nodes that have content, which in XSLT destroys
`<xsl:text> </xsl:text>` -- the only way to emit a literal space. The script
strips whitespace-only text nodes and nothing else, through `xsl:strip-space`,
which is what an XSLT processor already does with a stylesheet when it loads
one, so the rendered output is unchanged. About 11% off each stylesheet.

For every XML output carrying an `<?xml-stylesheet?>` instruction it runs that
stylesheet with `xsltproc` and writes the result beside the XML —
`public/atom.xml.html`, `public/sitemap.xml.html`. Nothing needs to list which
outputs exist: the documents name their own stylesheets. Requires `xsltproc`
(macOS ships it; FreeBSD `textproc/libxslt`, Debian `xsltproc`).

The server then serves the companion to browser navigations and the untouched
XML to everything else, so `/atom.xml` stays one URL that is readable to people
and unchanged for feed readers and crawlers. In nginx:

```nginx
map $http_sec_fetch_dest $xslc_nav { default ""; document ".html"; }

location ~ \.xml$ {
    add_header Vary "Sec-Fetch-Dest";
    try_files $uri$xslc_nav $uri =404;
}
```

`Sec-Fetch-Dest` is added by the browser's own network stack, cannot be forged
by page script, and is absent from every non-browser HTTP client, so robots
never reach the HTML branch. (A second `map` on `$http_user_agent` can force
anything self-identifying as a robot back to the XML, for the case of a crawler
that renders through a headless browser.) The second `try_files` candidate is
the XML itself: if the render step never ran, browsers simply get the XML,
which is what they get today.

Note that an `add_header` in this block suppresses any `add_header` inherited
from `server{}`, so repeat the site's other headers there if it has any.

Because the companion is rendered *from the stylesheet*, there is no second
copy of the design to drift out of step — the `.xsl` file stays the single
source of truth for both paths.

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

The theme targets [Baseline Widely Available](https://web.dev/baseline): web
platform features that have worked in every major engine for at least 30
months. As of 2026 that is roughly **Chrome/Edge 122+, Firefox 124+ and
Safari/iOS 17.4+**. The floor moves with the calendar, not with a pinned
browser list.

- **Widely available features are used without fallbacks** when doing so buys
  something real (less code, simpler CSS, better behaviour). Browsers below the
  floor are not broken on purpose, but they are not preserved at a cost either.
- **Newer features are progressive enhancements only**: the page must work
  without them (e.g. view transitions, Speculation Rules with the instant.page
  fallback, `text-wrap`, CJK `text-autospace`).
- **JavaScript syntax** is lowered by esbuild to `es2024`, set in
  `layouts/_partials/foot/script.html`. Runtime APIs are not polyfilled and are
  held to the same Baseline rule.

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

# Preview the theme itself using the bundled example site
hugo server --source exampleSite
```

### Project Structure

```
themes/chaos/
├── archetypes/              # Content templates
├── assets/
│   ├── css/                 # Source CSS files
│   └── js/                  # Source JavaScript
├── exampleSite/             # Demo site (hugo server --source exampleSite)
├── i18n/                    # Translation files
├── images/                  # Theme screenshots
├── layouts/
│   ├── _default/            # Default templates
│   ├── _markup/             # Markdown render hooks
│   ├── _partials/           # Reusable components
│   └── _shortcodes/         # Content shortcodes
├── static/
│   └── _3p/                 # Third-party dependencies
│       └── katex/           # KaTeX for math rendering
├── tools/                   # Build steps, content tooling, checks (below)
├── go.mod                   # Hugo Module definition
└── hugo.toml                # Theme defaults and minimum Hugo version
```

`assets/js/` holds one entry point per thing the browser loads: `main.js`,
which imports the feature modules in `assets/js/modules/`, plus `search.js`
and `mermaid.js`, each loaded only on pages that need it.

### `tools/`

Three kinds of script live here, and the difference matters when wiring up a
site's build.

**Build steps.** A site's build script runs these, and parts of the theme do
not work without them:

- `build_search_index.py` — the offline search index, without which the search
  dialog has nothing to read (see *Client-Side Full-Text Search* above)
- `post_build.sh` — the single post-build entry point, which runs
  `strip_xsl_space.sh` and `render_xsl_companions.sh` (see *Readable XML in a
  Post-XSLT Browser* above)
- `check.py` — the checks below. Cheap enough to belong in the same build,
  right after `hugo`

**Content tooling**, run by hand while writing rather than by a build:
`fetch_x_embed.py` caches an X embed into `data/x_embeds/`, `auxmark.py`
preprocesses and expands Markdown under git control, and
`generate_default_card.py` renders the default social sharing card.

**Diagnostics**, never part of a build: `search_harness.mjs`, below.

`hugo` alone still builds the theme. None of this is a dependency of the
theme's templates — the build steps produce content and post-process output,
and a site that skips them gets a working site with less in it.

#### `check.py`

Covers the classes of mistake Hugo has no opinion about, and
every one of them shipped here at some point without failing a build:

```bash
python3 themes/chaos/tools/check.py --public public
```

- the five i18n files define the same keys
- no translated string that nothing renders
- `theme.toml` and `hugo.toml` declare the same minimum Hugo version
- no CJK outside comments, so a five-language theme never falls back to
  Chinese
- no authored script over eight lines left inline in a template, where
  `js.Build` cannot reach it
- no space-indented tag in a built feed, the signature of a template shipping
  its indentation through CDATA (needs `--public`)
- every page's menu marks that page's own entry as current, and only that one
  — a header rendered once and reused marks the wrong entry everywhere, and
  menu entries configured with `url` instead of `pageRef` mark none at all
  (needs `--public`)

Exit status is 1 on failure, so a build script can stop on it.

#### `search_harness.mjs`

Runs `assets/js/search.js` against a real index in
a stubbed DOM, to see what a query returns or to check a change against the
version it replaces:

```bash
# What does this query match?
node themes/chaos/tools/search_harness.mjs \
  --index assets/search-index.json --query "some term"

# Did a change to search.js alter any ranking?
git -C themes/chaos show HEAD:assets/js/search.js > /tmp/search-old.js
node themes/chaos/tools/search_harness.mjs \
  --index assets/search-index.json --body assets/search-index-body.json \
  --compare /tmp/search-old.js
```

With no `--query`, queries are derived from the index itself, sampled across
the frequency range plus a multi-token query, a single character and one
string that matches nothing — so nothing about any particular site is baked
in. Pass `--body` when comparing: the core index alone matches so little that
most queries return a single result, and a single result cannot show a change
in ranking. The tool says so when that happens rather than reporting a
reassuring "identical".

This is the one thing in the theme that needs Node, and the one script in
`tools/` that no build should run.

## Dependencies

### Included (Vendored)

All dependencies are vendored in `static/_3p/` and `tools/vendor/` to ensure reliability and privacy:

- **KaTeX 0.18.9**: Mathematical typesetting for scientific content
- **instant.page 5.2.0**: Link prefetching for near-instant page transitions
- **Mermaid 11.17.2**: Diagram and flowchart generation from text
- **Noto Sans Mono 2.014**: Monospace font subset for code blocks and dates
- **jieba 0.42.1**: Chinese text segmentation for offline search index generator (in `tools/vendor/jieba/`)

### No External Dependencies

- No npm packages required
- No JavaScript frameworks
- No external CDNs (except optional comment system)
- No build tools beyond Hugo for the site itself; two optional helpers run on the built output (`python3` for the search index, `xsltproc` for the XSLT companions)
- All assets self-hosted for performance and privacy

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Follow the existing code style (2-space indentation for HTML/TOML)
2. Test changes with `hugo server`
3. Ensure the example site builds cleanly, and the self-checks pass:
   ```bash
   hugo --source exampleSite --destination /tmp/chaos-public \
     --gc --minify --panicOnWarning --printI18nWarnings
   python3 tools/check.py --public /tmp/chaos-public
   ```
   CI runs the same with the minimum and the latest Hugo release.
4. Update documentation for new features, and add an entry to `CHANGELOG.md`
5. Use conventional commit messages (`feat:`, `fix:`, `docs:`, etc.)

## License

Apache 2.0 License - see LICENSE file for details.

## Credits

- Built with [Hugo](https://gohugo.io/)
- Syntax highlighting by [Chroma](https://github.com/alecthomas/chroma)
- Math rendering by [KaTeX](https://katex.org/)
- Instant navigation by [instant.page](https://instant.page/)
- Comment system support for [Remark42](https://remark42.com/)
