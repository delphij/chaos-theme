<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:atom="http://www.w3.org/2005/Atom"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:dc="http://purl.org/dc/elements/1.1/">

  <xsl:output method="html" encoding="utf-8" indent="yes" />

  <xsl:template match="/">
    <xsl:variable name="is-atom" select="boolean(/atom:feed)" />
    <xsl:variable name="feed-title" select="atom:feed/atom:title | rss/channel/title" />

    <html{{ with site.Language.Locale }} lang="{{ . }}"{{ end }}>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>
          <xsl:value-of select="$feed-title" />
          <xsl:text> — </xsl:text>
          <xsl:choose>
            <xsl:when test="$is-atom">{{ T "feedPageTitle" }}</xsl:when>
            <xsl:otherwise>{{ T "rssFeedPageTitle" }}</xsl:otherwise>
          </xsl:choose>
        </title>
        {{ partial "xml-xsl-theme.html" . }}
        <style>
          {{ partial "xml-xsl-styles.html" . }}

          /* Syntax highlighting reused verbatim from the site's own stylesheets,
             so code inside a feed entry reads exactly as it does in the article.
             The dark sheet is scoped to html.dark, which xml-xsl-theme.html sets. */
          {{ (resources.Get "css/syntax.css").Content }}
          {{ (resources.Get "css/syntax-dark.css").Content }}

          /* Code blocks: a tinted, unframed, horizontally scrollable slab, as in
             the article. The main site hangs the line-number column into the
             margin on wide screens; that flourish is skipped here. */
          .highlight pre {
            margin: 0;
            padding: 12px;
            overflow-x: auto;
            max-width: 100%;
          }

          .chroma .lntable {
            border-spacing: 0;
            padding: 0;
            margin: 0;
            border: 0;
            display: block;
            overflow-x: auto;
            max-width: 100%;
          }

          .chroma .lntd {
            vertical-align: top;
            padding: 0;
            margin: 0;
            border: 0;
          }

          .chroma .lntd:first-child {
            padding-right: 1em;
          }

          .chroma .lnt,
          .chroma .ln {
            white-space: pre;
            -webkit-user-select: none;
            user-select: none;
            padding: 0 0 0 0.4em;
          }

          .chroma .line {
            display: flex;
          }

          /* The feed pipeline hands us formulas and diagrams as plain preformatted
             blocks rather than as Chroma output, so they need the code ground
             that .chroma would otherwise supply. (No angle brackets in this
             file's CSS: it is XML, and a literal tag name would be parsed.) */
          .feed-entry-content pre:not(.chroma) {
            margin: 1.5rem 0;
            padding: 12px;
            background: var(--code-bg);
            overflow-x: auto;
          }

          .feed-entry-content figure {
            margin: 1.5rem 0;
          }

          .feed-entry-content figcaption {
            margin-top: 6px;
            font-size: var(--text-sm);
            color: var(--muted);
          }

          /* ----- Feed-specific layout ----- */

          /* Icon sits on the baseline of the banner heading; size, colour and
             spacing come from .info-card h1 in the shared partial. */
          .feed-notice-title {
            display: flex;
            align-items: center;
            gap: 10px;
          }

          .feed-notice-title svg {
            color: var(--primary);
            flex-shrink: 0;
          }

          /* The feed address, built like the article code-copy button: a quiet
             inset field that copies itself when clicked. */
          .feed-url-box {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            width: 100%;
            margin-top: 14px;
            padding: 8px 12px;
            background: var(--surface);
            border: var(--border);
            border-radius: var(--radius-sm);
            font-family: var(--font-mono);
            font-size: var(--text-sm);
            line-height: var(--line-height);
            color: var(--text);
            text-align: left;
            cursor: pointer;
            transition: border-color var(--transition-fast);
          }

          .feed-url-box:hover {
            border-color: var(--primary);
          }

          .feed-url-label {
            font-size: var(--text-2xs);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--primary);
            flex-shrink: 0;
          }

          .feed-url-value {
            flex: 1 1 auto;
            min-width: 0;
            word-break: break-all;
            user-select: text;
          }

          .feed-url-hint {
            flex-shrink: 0;
            margin-left: auto;
            padding: 3px 8px;
            font-size: var(--text-xs);
            line-height: 1.4;
            color: var(--muted);
            background: var(--surface);
            border: var(--border);
            border-radius: var(--radius-sm);
            user-select: none;
            transition: color var(--transition-fast), background var(--transition-fast), border-color var(--transition-fast);
          }

          .feed-url-box:hover .feed-url-hint {
            color: var(--heading);
            background: var(--paper);
            border-color: var(--primary);
          }

          .feed-url-box.copied .feed-url-hint {
            color: var(--alert-tip-border);
            border-color: var(--alert-tip-border);
          }

          /* Section label above the list: deliberately quieter than the entry
             titles it introduces, like .tags-section-heading on the site. */
          .feed-section-heading {
            font-size: var(--text-md);
            margin: 0 0 24px;
          }

          /* Entries are spaced like .post-entry on the homepage: whitespace
             only, no rules or cards between them. */
          .feed-entries {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            flex-direction: column;
            gap: 48px;
          }

          .feed-entry-title {
            font-size: var(--h1-size);
            letter-spacing: -0.01em;
            margin: 0 0 10px;
          }

          .feed-entry-meta {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            font-size: var(--small-size);
            color: var(--muted);
            line-height: 1.6;
          }

          .feed-entry-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 6px 10px;
          }

          .feed-entry-content {
            margin: 14px 0;
          }

          .feed-entry-content p {
            margin: 0 0 1.15em;
          }

          .feed-entry-content img {
            margin: 1em 0;
          }

          .feed-entry-more {
            margin-top: 14px;
          }

          .feed-read-more {
            font-weight: 600;
          }
        </style>
      </head>
      <body>
        <header class="site-header">
          <div class="site-header-inner">
            <a class="site-brand link-plain" href="{{ "/" | relLangURL }}">
              <xsl:value-of select="$feed-title" />
            </a>
            <a class="back-link link-plain" href="{{ "/" | relLangURL }}">
              {{ T "visitBlogHome" }}
            </a>
          </div>
        </header>

        <main class="container">
          <section class="info-card accent-primary">
            <h1 class="feed-notice-title">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M4 11a9 9 0 0 1 9 9"></path>
                <path d="M4 4a16 16 0 0 1 16 16"></path>
                <circle cx="5" cy="19" r="1"></circle>
              </svg>
              <span>
                <xsl:choose>
                  <xsl:when test="$is-atom">{{ T "feedPageTitle" }}</xsl:when>
                  <xsl:otherwise>{{ T "rssFeedPageTitle" }}</xsl:otherwise>
                </xsl:choose>
              </span>
            </h1>
            <p>
              <xsl:choose>
                <xsl:when test="$is-atom">{{ T "feedIntro" }}</xsl:when>
                <xsl:otherwise>{{ T "rssFeedIntro" }}</xsl:otherwise>
              </xsl:choose>
            </p>
            {{- $readers := slice
                  `<a href="https://netnewswire.com/" target="_blank" rel="noopener noreferrer">NetNewsWire</a>`
                  `<a href="https://reeder.app/" target="_blank" rel="noopener noreferrer">Reeder</a>`
                  `<a href="https://feedly.com/" target="_blank" rel="noopener noreferrer">Feedly</a>`
                  `<a href="https://inoreader.com/" target="_blank" rel="noopener noreferrer">Inoreader</a>` }}
            <p>
              {{ T "feedSubscribeHelp" (dict
                   "Title" `<xsl:value-of select="atom:feed/atom:title | rss/channel/title" />`
                   "Readers" (delimit $readers (T "listSeparator"))) }}
            </p>
            <button type="button" class="feed-url-box" id="feedUrlCopy" title="{{ T `copyFeedUrl` }}" aria-label="{{ T `copyFeedUrl` }}">
              <span class="feed-url-label">{{ T "feedUrlLabel" }}</span>
              <span class="feed-url-value" id="feedUrlValue">
                <xsl:choose>
                  <xsl:when test="atom:feed/atom:link[@rel='self']/@href">
                    <xsl:value-of select="atom:feed/atom:link[@rel='self']/@href" />
                  </xsl:when>
                  <xsl:when test="rss/channel/atom:link[@rel='self']/@href">
                    <xsl:value-of select="rss/channel/atom:link[@rel='self']/@href" />
                  </xsl:when>
                  <xsl:when test="rss/channel/link">
                    <xsl:value-of select="rss/channel/link" />
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:value-of select="atom:feed/atom:id" />
                  </xsl:otherwise>
                </xsl:choose>
              </span>
              <span class="feed-url-hint" id="feedUrlHint">{{ T "copyFeedUrl" }}</span>
            </button>
          </section>

          <h2 class="feed-section-heading">{{ T "feedLatestPosts" }}</h2>

          <ul class="feed-entries">
            <xsl:apply-templates select="atom:feed/atom:entry | rss/channel/item" />
          </ul>

          <footer class="page-footer">
            <p>
              © <xsl:choose>
                <xsl:when test="$is-atom and string-length(atom:feed/atom:updated) &gt;= 4">
                  <xsl:value-of select="substring(atom:feed/atom:updated, 1, 4)" />
                </xsl:when>
                <xsl:when test="string-length(rss/channel/lastBuildDate) &gt;= 16">
                  <xsl:value-of select="substring(rss/channel/lastBuildDate, 13, 4)" />
                </xsl:when>
                <xsl:otherwise>{{ now.Format "2006" }}</xsl:otherwise>
              </xsl:choose><xsl:text> </xsl:text><xsl:value-of select="$feed-title" />.
            </p>
          </footer>
        </main>

        <script>
        <![CDATA[
          (function() {
            var box = document.getElementById('feedUrlCopy');
            var value = document.getElementById('feedUrlValue');
            var hint = document.getElementById('feedUrlHint');
            if (!box || !value || !hint) return;

            var copyLabel = ]]>{{ T "copyFeedUrl" | jsonify }}<![CDATA[;
            var copiedLabel = ]]>{{ T "copiedCode" | jsonify }}<![CDATA[;
            var resetTimer;

            function report(ok) {
              if (ok) {
                hint.textContent = copiedLabel;
                box.classList.add('copied');
                clearTimeout(resetTimer);
                resetTimer = setTimeout(function() {
                  hint.textContent = copyLabel;
                  box.classList.remove('copied');
                }, 2000);
              }
            }

            function legacyCopy(text) {
              var area = document.createElement('textarea');
              area.value = text;
              area.setAttribute('readonly', '');
              area.style.position = 'fixed';
              area.style.top = '-1000px';
              document.body.appendChild(area);
              area.select();
              var ok = false;
              try {
                ok = document.execCommand('copy');
              } catch (e) {
                ok = false;
              }
              document.body.removeChild(area);
              return ok;
            }

            box.addEventListener('click', function() {
              var text = value.textContent.trim();
              if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(text).then(function() {
                  report(true);
                }).catch(function() {
                  report(legacyCopy(text));
                });
              } else {
                report(legacyCopy(text));
              }
            });
          })();
        ]]>
        </script>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="atom:entry | item">
    <li class="feed-entry">
      <article>
        <h3 class="feed-entry-title">
          <a class="link-plain">
            <xsl:attribute name="href">
              <xsl:value-of select="atom:link[not(@rel) or @rel='alternate']/@href | link" />
            </xsl:attribute>
            <xsl:value-of select="atom:title | title" disable-output-escaping="yes" />
          </a>
        </h3>

        <div class="feed-entry-meta">
          <time>
            <xsl:choose>
              <xsl:when test="atom:published">
                <xsl:value-of select="substring(atom:published, 1, 10)" />
                <xsl:if test="string-length(atom:published) &gt;= 16">
                  <xsl:text> </xsl:text>
                  <xsl:value-of select="substring(atom:published, 12, 5)" />
                </xsl:if>
              </xsl:when>
              <xsl:when test="atom:updated">
                <xsl:value-of select="substring(atom:updated, 1, 10)" />
                <xsl:if test="string-length(atom:updated) &gt;= 16">
                  <xsl:text> </xsl:text>
                  <xsl:value-of select="substring(atom:updated, 12, 5)" />
                </xsl:if>
              </xsl:when>
              <xsl:when test="pubDate">
                <xsl:choose>
                  <xsl:when test="string-length(pubDate) &gt;= 16">
                    <xsl:value-of select="substring(pubDate, 1, 16)" />
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:value-of select="pubDate" />
                  </xsl:otherwise>
                </xsl:choose>
              </xsl:when>
            </xsl:choose>
          </time>

          <xsl:variable name="author-name">
            <xsl:choose>
              <xsl:when test="atom:author/atom:name">
                <xsl:value-of select="atom:author/atom:name" />
              </xsl:when>
              <xsl:when test="dc:creator">
                <xsl:value-of select="dc:creator" />
              </xsl:when>
              <xsl:when test="author">
                <xsl:value-of select="author" />
              </xsl:when>
            </xsl:choose>
          </xsl:variable>
          <xsl:if test="normalize-space($author-name) != ''">
            <span>•</span>
            <span><xsl:value-of select="$author-name" /></span>
          </xsl:if>

          <xsl:if test="atom:category | category">
            <span>•</span>
            <span class="feed-entry-tags">
              {{- /* Tags are flat muted text, like .tag-link on the site; the
                     flex gap on .feed-entry-tags does the separating. */}}
              <xsl:for-each select="atom:category/@term | category">
                <span><xsl:value-of select="." /></span>
              </xsl:for-each>
            </span>
          </xsl:if>
        </div>

        <div class="feed-entry-content">
          <xsl:choose>
            <xsl:when test="atom:content">
              <xsl:value-of select="atom:content" disable-output-escaping="yes" />
            </xsl:when>
            <xsl:when test="content:encoded">
              <xsl:value-of select="content:encoded" disable-output-escaping="yes" />
            </xsl:when>
            <xsl:when test="atom:summary">
              <p><xsl:value-of select="atom:summary" disable-output-escaping="yes" /></p>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="description" disable-output-escaping="yes" />
            </xsl:otherwise>
          </xsl:choose>
        </div>

        <div class="feed-entry-more">
          <a class="feed-read-more">
            <xsl:attribute name="href">
              <xsl:value-of select="atom:link[not(@rel) or @rel='alternate']/@href | link" />
            </xsl:attribute>
            {{ T "feedReadMore" }}
          </a>
        </div>
      </article>
    </li>
  </xsl:template>

</xsl:stylesheet>
