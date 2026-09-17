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
        <style>
          {{ partial "xml-xsl-styles.html" . }}

          /* RSS-specific styles */
          .feed-notice-title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 19px;
            font-weight: 700;
            color: var(--heading);
            margin: 0 0 10px;
          }

          .feed-notice-title svg {
            color: var(--primary);
            flex-shrink: 0;
          }

          /* Clickable button: copies the feed address to the clipboard */
          .feed-url-box {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            width: 100%;
            margin-top: 14px;
            padding: 8px 12px;
            background: var(--paper);
            border: var(--border);
            border-radius: var(--radius-sm);
            font-family: "Noto Sans Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 13px;
            line-height: var(--line-height);
            color: var(--text);
            text-align: left;
            cursor: pointer;
            transition: border-color var(--transition-fast), background-color var(--transition-fast);
          }

          .feed-url-box:hover {
            border-color: var(--primary);
            background: var(--surface);
          }

          .feed-url-box:focus-visible {
            outline: 2px solid var(--primary);
            outline-offset: 2px;
          }

          .feed-url-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 700;
            color: var(--primary);
            background: var(--surface);
            padding: 2px 6px;
            border-radius: var(--radius-sm);
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
            font-size: 12px;
            font-weight: 500;
            color: var(--muted);
            background: var(--surface);
            padding: 2px 8px;
            border-radius: var(--radius-sm);
            border: var(--border);
            transition: color var(--transition-fast), border-color var(--transition-fast);
          }

          .feed-url-box:hover .feed-url-hint {
            color: var(--primary);
            border-color: var(--primary);
          }

          .feed-url-box.copied .feed-url-hint {
            color: var(--primary);
            border-color: var(--primary);
            font-weight: 700;
          }

          /* Feed section heading */
          .feed-section-heading {
            font-size: 19px;
            font-weight: 700;
            color: var(--heading);
            margin: 0 0 24px;
          }

          .feed-entries {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            flex-direction: column;
            gap: 48px;
          }

          .feed-entry {
            background: transparent;
            padding: 0;
            border: none;
          }

          .feed-entry-title {
            font-size: 21px;
            font-weight: 700;
            margin: 0 0 8px;
            line-height: 1.4;
          }

          .feed-entry-title a {
            color: var(--heading);
            text-decoration: none;
            transition: color var(--transition-fast);
          }

          .feed-entry-title a:hover {
            color: var(--primary);
          }

          .feed-entry-meta {
            font-size: 13px;
            color: var(--muted);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
          }

          .feed-entry-tag {
            background: var(--paper);
            padding: 2px 6px;
            border-radius: var(--radius-sm);
            font-size: 12px;
            color: var(--muted);
          }

          .feed-entry-content {
            font-size: var(--font-size-base);
            color: var(--text);
            line-height: var(--line-height);
            overflow-wrap: break-word;
          }

          .feed-entry-content p {
            margin: 14px 0;
          }

          .feed-entry-content img {
            max-width: 100%;
            height: auto;
            border-radius: var(--radius-sm);
            margin: 16px 0;
            display: block;
          }

          .feed-entry-content a {
            color: var(--link);
            text-decoration: underline;
            text-underline-offset: 3px;
          }

          .feed-entry-content a:hover {
            color: var(--link-hover);
          }

          /* Inline code: clean monospace without background tint */
          .feed-entry-content code {
            font-family: "Noto Sans Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.9em;
            overflow-wrap: break-word;
            background: transparent;
            padding: 0;
          }

          /* Code block container */
          .feed-entry-content pre,
          .feed-entry-content .highlight {
            background: var(--code-bg);
            border: var(--border);
            border-radius: var(--radius-md);
            margin: 16px 0;
            overflow-x: auto;
          }

          .feed-entry-content pre {
            padding: 12px;
            font-family: "Noto Sans Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 13.5px;
            line-height: 1.5;
          }

          .feed-entry-content .highlight pre {
            margin: 0;
            border: 0;
            background: transparent;
          }

          .feed-entry-content pre code,
          .feed-entry-content .highlight code,
          .feed-entry-content .chroma code {
            font-size: inherit;
            background: transparent;
            padding: 0;
          }

          /* Chroma line number table: reset borders and padding */
          .feed-entry-content .chroma {
            background: transparent !important;
          }

          .feed-entry-content .chroma .lntable {
            border: 0 !important;
            border-spacing: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            width: auto !important;
            background: transparent !important;
          }

          .feed-entry-content .chroma .lntd {
            border: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            vertical-align: top !important;
            background: transparent !important;
          }

          .feed-entry-content .chroma .lnt,
          .feed-entry-content .chroma .ln {
            white-space: pre;
            user-select: none;
            padding: 0 0.8em 0 0.4em;
            color: var(--muted);
          }

          .feed-entry-content .chroma .line {
            display: flex;
          }

          .feed-entry-content blockquote {
            margin: 16px 0;
            padding: 12px 18px;
            background: var(--paper);
            border-left: 4px solid var(--accent);
            border-radius: 0 var(--radius-md) var(--radius-md) 0;
          }

          /* Content data tables */
          .feed-entry-content table:not(.lntable) {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 14px;
          }

          .feed-entry-content table:not(.lntable) th,
          .feed-entry-content table:not(.lntable) td {
            padding: 8px 12px;
            border-bottom: var(--border);
            text-align: left;
          }

          .feed-entry-content table:not(.lntable) th {
            background: var(--paper);
            font-weight: 600;
          }

          .feed-entry-more {
            margin-top: 16px;
          }

          .feed-read-more {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 14px;
            font-weight: 600;
            color: var(--primary);
            text-decoration: none;
            transition: opacity var(--transition-fast);
          }

          .feed-read-more:hover {
            opacity: 0.8;
          }

          /* Footer */
          .feed-footer {
            text-align: center;
            font-size: 13px;
            color: var(--muted);
            margin-top: 64px;
            padding-top: 24px;
          }
        </style>
      </head>
      <body>
        <header class="site-header">
          <div class="site-header-inner">
            <a class="site-brand" href="{{ "/" | relLangURL }}">
              <xsl:value-of select="$feed-title" />
            </a>
            <a class="back-link" href="{{ "/" | relLangURL }}">
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

          <footer class="feed-footer">
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
          <a>
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
              <xsl:for-each select="atom:category/@term | category">
                <span class="feed-entry-tag"><xsl:value-of select="." /></span>
                <xsl:if test="position() != last()"> </xsl:if>
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
