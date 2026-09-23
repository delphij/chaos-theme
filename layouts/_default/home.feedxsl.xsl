<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:atom="http://www.w3.org/2005/Atom"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  {{- /* Without this the processor copies these three declarations onto the
         result's <html> element, where they mean nothing. */}}
  exclude-result-prefixes="atom content dc">

{{- /* doctype-system is how an XSLT 1.0 serializer is asked for a doctype at
       all; libxslt special-cases this value and emits the modern
       "<!DOCTYPE html>" rather than the legacy SYSTEM form the name
       suggests. Without it the serializer emits no doctype, which leaves
       the static companion pages -- real .html files served as text/html --
       in quirks mode. */}}
  <xsl:output method="html" encoding="utf-8" indent="yes" doctype-system="about:legacy-compat" />

  <xsl:template match="/">
    <xsl:variable name="is-atom" select="boolean(/atom:feed)" />
    <xsl:variable name="feed-title" select="atom:feed/atom:title | rss/channel/title" />

    <html{{ with site.Language.Locale }} lang="{{ . }}"{{ end }}>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        {{- /* This page is a rendering of the feed, not a page of the site:
               keep it, and the static companion the build renders from this
               same stylesheet, out of the index. */}}
        <meta name="robots" content="noindex, follow" />
        <title>
          <xsl:value-of select="$feed-title" />
          <xsl:text> — </xsl:text>
          <xsl:choose>
            <xsl:when test="$is-atom">{{ T "feedPageTitle" }}</xsl:when>
            <xsl:otherwise>{{ T "rssFeedPageTitle" }}</xsl:otherwise>
          </xsl:choose>
        </title>
        {{ partial "xml-xsl-theme.html" . }}
        {{- /* Minified: the source of these styles is documented, the copy that
               reaches every reader of the feed does not need to be. */ -}}
        <style>{{ (resources.FromString "css/xml-xsl-feed.css" (partial "xml-xsl-feed-styles.html" .) | resources.Minify).Content }}</style>
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

        {{- /* Minified, and wrapped in CDATA because the stylesheet is XML. */ -}}
        <script><![CDATA[{{ (resources.FromString "js/xml-xsl-feed.js" (partial "xml-xsl-feed-script.html" .) | resources.Minify).Content }}]]></script>
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
