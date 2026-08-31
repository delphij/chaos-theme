<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:atom="http://www.w3.org/2005/Atom">

  <xsl:output method="html" encoding="utf-8" indent="yes" />

  <xsl:template match="/">
    <html{{ with site.Language.Locale }} lang="{{ . }}"{{ end }}>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title><xsl:value-of select="atom:feed/atom:title" /> — {{ T "feedPageTitle" }}</title>
        <style>
          :root {
            color-scheme: light;
            --bg: #FAFAFA;
            --surface: #FFFFFF;
            --text: #222222;
            --heading: #111111;
            --muted: #545454;
            --primary: #A23E48;
            --primary-fg: #FFFFFF;
            --accent: #2E5A88;
            --paper: #F0E6D2;
            --link: #0050A5;
            --link-hover: #003875;
            --danger: #CC3333;
            --code-bg: #F5F5F5;
            --border: 1px solid rgba(0, 0, 0, 0.1);
            --transition-fast: 0.2s ease;
            --content-width: 780px;
            --radius-sm: 4px;
            --radius-md: 6px;
            --radius-lg: 8px;
            --font-size-base: 16px;
            --line-height: 1.8;
          }

          * {
            box-sizing: border-box;
          }

          body {
            margin: 0;
            padding: 0;
            background: var(--bg);
            color: var(--text);
            font-family: "Noto Sans SC", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            font-size: var(--font-size-base);
            line-height: var(--line-height);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
          }

          /* Header */
          .feed-header {
            background: var(--surface);
            border-bottom: var(--border);
            padding: 16px 24px;
            position: sticky;
            top: 0;
            z-index: 10;
          }

          .feed-header-inner {
            max-width: var(--content-width);
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
          }

          .feed-brand {
            font-size: 18px;
            font-weight: 700;
            color: var(--heading);
            text-decoration: none;
          }

          .feed-brand:hover {
            color: var(--primary);
          }

          .feed-back-link {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 14px;
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
            padding: 6px 12px;
            border-radius: var(--radius-sm);
            background: var(--paper);
            transition: opacity var(--transition-fast);
          }

          .feed-back-link:hover {
            opacity: 0.85;
          }

          /* Main container */
          .feed-container {
            max-width: var(--content-width);
            margin: 32px auto;
            padding: 0 20px 60px;
          }

          /* Hero notice banner */
          .feed-notice {
            background: var(--surface);
            border: var(--border);
            border-left: 4px solid var(--primary);
            border-radius: var(--radius-lg);
            padding: 20px 24px;
            margin-bottom: 36px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
          }

          .feed-notice-title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 18px;
            font-weight: 700;
            color: var(--heading);
            margin: 0 0 10px;
          }

          .feed-notice-title svg {
            color: var(--primary);
            flex-shrink: 0;
          }

          .feed-notice p {
            margin: 8px 0;
            font-size: 14.5px;
            color: var(--text);
            line-height: 1.6;
          }

          .feed-notice a {
            color: var(--link);
            text-decoration: underline;
            text-underline-offset: 3px;
          }

          .feed-notice a:hover {
            color: var(--link-hover);
          }

          /* Clickable button: copies the feed address to the clipboard. */
          .feed-url-box {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            width: 100%;
            margin-top: 14px;
            padding: 10px 14px;
            background: var(--paper);
            border: var(--border);
            border-radius: var(--radius-sm);
            font-family: ui-monospace, SFMono-Regular, Consolas, Monaco, monospace;
            font-size: 13.5px;
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

          .feed-url-value {
            flex: 1 1 auto;
            min-width: 0;
            word-break: break-all;
            user-select: text;              /* keep the address selectable by hand */
          }

          .feed-url-hint {
            flex-shrink: 0;
            margin-left: auto;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
            color: var(--muted);
            background: var(--surface);
            padding: 2px 6px;
            border-radius: var(--radius-sm);
            transition: color var(--transition-fast);
          }

          .feed-url-box:hover .feed-url-hint {
            color: var(--primary);
          }

          /* Reserve a line so the feedback message does not shift the layout. */
          .feed-url-status {
            margin: 8px 0 0;
            min-height: 1.5em;
            font-size: 13px;
            color: var(--muted);
          }

          .feed-url-status[data-state="ok"] {
            color: var(--primary);
          }

          .feed-url-status[data-state="error"] {
            color: var(--danger);
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

          /* Section header */
          .feed-section-heading {
            font-size: 20px;
            font-weight: 700;
            color: var(--heading);
            margin: 0 0 20px;
            padding-bottom: 8px;
            border-bottom: var(--border);
          }

          .feed-entries {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            flex-direction: column;
            gap: 36px;
          }

          .feed-entry {
            background: var(--surface);
            border: var(--border);
            border-radius: var(--radius-lg);
            padding: 28px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
            transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
          }

          .feed-entry:hover {
            border-color: var(--primary);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
          }

          .feed-entry-title {
            font-size: 22px;
            font-weight: 700;
            margin: 0 0 10px;
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
            font-size: 13.5px;
            color: var(--muted);
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
          }

          .feed-entry-content {
            font-size: 15.5px;
            color: var(--text);
            line-height: 1.8;
            overflow-wrap: break-word;
          }

          .feed-entry-content p {
            margin: 14px 0;
          }

          .feed-entry-content img {
            max-width: 100%;
            height: auto;
            border-radius: var(--radius-md);
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

          .feed-entry-content pre {
            background: var(--code-bg);
            border: var(--border);
            border-radius: var(--radius-md);
            padding: 14px;
            overflow-x: auto;
            font-family: ui-monospace, SFMono-Regular, Consolas, Monaco, monospace;
            font-size: 13.5px;
            line-height: 1.5;
          }

          .feed-entry-content code {
            font-family: ui-monospace, SFMono-Regular, Consolas, Monaco, monospace;
            font-size: 0.9em;
            background: var(--paper);
            padding: 2px 6px;
            border-radius: var(--radius-sm);
          }

          .feed-entry-content pre code {
            background: transparent;
            padding: 0;
          }

          .feed-entry-content blockquote {
            margin: 16px 0;
            padding: 12px 18px;
            background: var(--paper);
            border-left: 4px solid var(--accent);
            border-radius: 0 var(--radius-md) var(--radius-md) 0;
          }

          .feed-entry-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 14px;
          }

          .feed-entry-content th,
          .feed-entry-content td {
            padding: 8px 12px;
            border: var(--border);
          }

          .feed-entry-content th {
            background: var(--paper);
            font-weight: 600;
          }

          .feed-entry-more {
            margin-top: 20px;
            padding-top: 14px;
            border-top: var(--border);
          }

          .feed-read-more {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 14px;
            font-weight: 600;
            color: var(--primary);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color var(--transition-fast);
          }

          .feed-read-more:hover {
            border-bottom-color: var(--primary);
          }

          /* Footer */
          .feed-footer {
            text-align: center;
            font-size: 13px;
            color: var(--muted);
            margin-top: 48px;
            padding-top: 24px;
            border-top: var(--border);
          }
        </style>
      </head>
      <body>
        <header class="feed-header">
          <div class="feed-header-inner">
            <a class="feed-brand" href="{{ "/" | relLangURL }}">
              <xsl:value-of select="atom:feed/atom:title" />
            </a>
            <a class="feed-back-link" href="{{ "/" | relLangURL }}">
              {{ T "visitBlogHome" }}
            </a>
          </div>
        </header>

        <main class="feed-container">
          <section class="feed-notice">
            <h1 class="feed-notice-title">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M4 11a9 9 0 0 1 9 9"></path>
                <path d="M4 4a16 16 0 0 1 16 16"></path>
                <circle cx="5" cy="19" r="1"></circle>
              </svg>
              <span>{{ T "feedPageTitle" }}</span>
            </h1>
            <p>
              {{ T "feedIntro" }}
            </p>
            {{- /* The feed title is resolved by the browser's XSLT processor, so it is
                   handed to the translation as a literal <xsl:value-of/> element. The
                   reader names are joined here so translators only own the sentence. */}}
            {{- $readers := slice
                  `<a href="https://netnewswire.com/" target="_blank" rel="noopener noreferrer">NetNewsWire</a>`
                  `<a href="https://reeder.app/" target="_blank" rel="noopener noreferrer">Reeder</a>`
                  `<a href="https://feedly.com/" target="_blank" rel="noopener noreferrer">Feedly</a>`
                  `<a href="https://inoreader.com/" target="_blank" rel="noopener noreferrer">Inoreader</a>` }}
            <p>
              {{ T "feedSubscribeHelp" (dict
                   "Title" `<xsl:value-of select="atom:feed/atom:title" />`
                   "Readers" (delimit $readers (T "listSeparator"))) }}
            </p>
            <button type="button" class="feed-url-box" id="feedUrlCopy" title="{{ T `copyFeedUrl` }}">
              <span class="feed-url-label">{{ T "feedUrlLabel" }}</span>
              <span class="feed-url-value" id="feedUrlValue"><xsl:value-of select="atom:feed/atom:link[@rel='self']/@href" /></span>
              <span class="feed-url-hint">{{ T "copyFeedUrl" }}</span>
            </button>
            <p class="feed-url-status" id="feedUrlStatus" role="status"></p>
          </section>

          <h2 class="feed-section-heading">{{ T "feedLatestPosts" }}</h2>

          <ul class="feed-entries">
            <xsl:apply-templates select="atom:feed/atom:entry" />
          </ul>

          <footer class="feed-footer">
            <p>
              © <xsl:value-of select="substring(atom:feed/atom:updated, 1, 4)" /><xsl:text> </xsl:text><xsl:value-of select="atom:feed/atom:title" />.
            </p>
          </footer>
        </main>

        <script>
        <![CDATA[
          (function() {
            var box = document.getElementById('feedUrlCopy');
            var value = document.getElementById('feedUrlValue');
            var status = document.getElementById('feedUrlStatus');
            if (!box || !value || !status) return;

            var I18N = {
              copied: ]]>{{ T "feedUrlCopied" | jsonify }}<![CDATA[,
              failed: ]]>{{ T "feedUrlCopyFailed" | jsonify }}<![CDATA[
            };

            var resetTimer;

            function report(ok) {
              status.textContent = ok ? I18N.copied : I18N.failed;
              status.setAttribute('data-state', ok ? 'ok' : 'error');
              clearTimeout(resetTimer);
              resetTimer = setTimeout(function() {
                status.textContent = '';
                status.removeAttribute('data-state');
              }, 4000);
            }

            // Fallback for browsers without the async clipboard API, and for pages
            // served over plain HTTP where that API is unavailable.
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

  <xsl:template match="atom:entry">
    <li class="feed-entry">
      <article>
        <h3 class="feed-entry-title">
          <a>
            <xsl:attribute name="href">
              <xsl:value-of select="atom:link[@type='text/html']/@href" />
            </xsl:attribute>
            <xsl:value-of select="atom:title" disable-output-escaping="yes" />
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
            </xsl:choose>
          </time>
          <xsl:if test="atom:author/atom:name">
            <span>•</span>
            <span><xsl:value-of select="atom:author/atom:name" /></span>
          </xsl:if>
        </div>

        <div class="feed-entry-content">
          <xsl:choose>
            <xsl:when test="atom:content">
              <xsl:value-of select="atom:content" disable-output-escaping="yes" />
            </xsl:when>
            <xsl:otherwise>
              <p><xsl:value-of select="atom:summary" disable-output-escaping="yes" /></p>
            </xsl:otherwise>
          </xsl:choose>
        </div>

        <div class="feed-entry-more">
          <a class="feed-read-more">
            <xsl:attribute name="href">
              <xsl:value-of select="atom:link[@type='text/html']/@href" />
            </xsl:attribute>
            {{ T "feedReadMore" }}
          </a>
        </div>
      </article>
    </li>
  </xsl:template>

</xsl:stylesheet>
