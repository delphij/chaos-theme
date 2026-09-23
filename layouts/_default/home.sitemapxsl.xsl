<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:html="http://www.w3.org/TR/REC-html40"
  xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
  xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  {{- /* Without this the processor copies these declarations onto the
         result's <html> element, where they mean nothing. */}}
  exclude-result-prefixes="html image sitemap">

{{- /* doctype-system is how an XSLT 1.0 serializer is asked for a doctype at
       all; libxslt special-cases this value and emits the modern
       "<!DOCTYPE html>" rather than the legacy SYSTEM form the name
       suggests. Without it the serializer emits no doctype, which leaves
       the static companion pages -- real .html files served as text/html --
       in quirks mode. */}}
  <xsl:output method="html" encoding="UTF-8" indent="yes" doctype-system="about:legacy-compat" />

  <xsl:template match="/">
    <html{{ with site.Language.Locale }} lang="{{ . }}"{{ end }}>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        {{- /* This page is a rendering of the sitemap, not a page of the site:
               keep it, and the static companion the build renders from this
               same stylesheet, out of the index. */}}
        <meta name="robots" content="noindex, follow" />
        <title>{{ T "sitemapPageTitle" }} — {{ site.Title }}</title>
        {{ partial "xml-xsl-theme.html" . }}
        {{- /* Minified: the source of these styles is documented, the copy that
               reaches every reader of the sitemap does not need to be. */ -}}
        <style>{{ partial "_funcs/get-xsl-css.html" (dict "page" . "name" "sitemap" "sheets" (slice "css/xml-xsl-sitemap.css")) }}</style>
      </head>
      <body>
        <header class="site-header">
          <div class="site-header-inner">
            <a class="site-brand link-plain" href="{{ "/" | relLangURL }}">{{ site.Title }}</a>
            <a class="back-link link-plain" href="{{ "/" | relLangURL }}">{{ T "visitBlogHome" }}</a>
          </div>
        </header>

        <main class="container">
          <section class="info-card">
            <h1>{{ T "sitemapPageTitle" }}</h1>
            {{- /* Counts are evaluated by the browser's XSLT processor, so they are handed
                   to the translations as literal <xsl:value-of/> elements. */}}
            <p>
              {{ T "sitemapIntro" (dict "Count" `<xsl:value-of select="count(sitemap:urlset/sitemap:url)"/>`) }}
            </p>
            <div class="stats-bar" role="toolbar" aria-label="{{ T `sitemapFilterToolbar` }}">
              <span class="filter-label">{{ T "sitemapFilterLabel" }}</span>
              <button type="button" class="stat-pill active" data-filter="post" title="{{ T `sitemapToggleType` (dict `Type` (T `contentTypePost`)) }}">
                <span>📝 {{ T "contentTypePost" }}</span>
                <span class="stat-num"><xsl:value-of select="count(sitemap:urlset/sitemap:url[contains(sitemap:loc, '/posts/')])"/></span>
              </button>
              <button type="button" class="stat-pill active" data-filter="category" title="{{ T `sitemapToggleType` (dict `Type` (T `categories`)) }}">
                <span>📁 {{ T "categories" }}</span>
                <span class="stat-num"><xsl:value-of select="count(sitemap:urlset/sitemap:url[contains(sitemap:loc, '/categories/')])"/></span>
              </button>
              <button type="button" class="stat-pill active" data-filter="tag" title="{{ T `sitemapToggleType` (dict `Type` (T `tags`)) }}">
                <span>🏷️ {{ T "tags" }}</span>
                <span class="stat-num"><xsl:value-of select="count(sitemap:urlset/sitemap:url[contains(sitemap:loc, '/tags/')])"/></span>
              </button>
              <button type="button" class="stat-pill active" data-filter="page" title="{{ T `sitemapToggleType` (dict `Type` (T `contentTypePage`)) }}">
                <span>📄 {{ T "contentTypePage" }}</span>
                <span class="stat-num"><xsl:value-of select="count(sitemap:urlset/sitemap:url[not(contains(sitemap:loc, '/posts/')) and not(contains(sitemap:loc, '/categories/')) and not(contains(sitemap:loc, '/tags/'))])"/></span>
              </button>
            </div>
          </section>

          <div class="filter-status" aria-live="polite">
            <span>{{ T "sitemapVisibleCount" (dict
                  "Visible" `<strong id="visibleCount"><xsl:value-of select="count(sitemap:urlset/sitemap:url)"/></strong>`
                  "Total" `<xsl:value-of select="count(sitemap:urlset/sitemap:url)"/>`) }}</span>
            <span class="filter-hint">{{ T "sitemapHint" }}</span>
          </div>

          <div class="table-wrapper">
            <table id="sitemapTable">
              <thead>
                <tr>
                  <th class="sortable" id="thPath" data-col="path" tabindex="0" role="button" aria-label="{{ T `sortByPath` }}">
                    {{ T "sitemapColumnPath" }} <span class="sort-icon" id="iconPath">↕</span>
                  </th>
                  <th class="sortable sorted-desc" id="thTime" data-col="time" tabindex="0" role="button" aria-label="{{ T `sortByTimeDescending` }}">
                    {{ T "sitemapColumnLastModified" }} <span class="sort-icon" id="iconTime">↓</span>
                  </th>
                </tr>
              </thead>
              <tbody id="sitemapTbody">
                <xsl:for-each select="sitemap:urlset/sitemap:url">
                  <xsl:sort select="sitemap:lastmod" order="descending" />
                  <xsl:variable name="itemType">
                    <xsl:choose>
                      <xsl:when test="contains(sitemap:loc, '/posts/')">post</xsl:when>
                      <xsl:when test="contains(sitemap:loc, '/categories/')">category</xsl:when>
                      <xsl:when test="contains(sitemap:loc, '/tags/')">tag</xsl:when>
                      <xsl:otherwise>page</xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>

                  <xsl:variable name="itemPath">
                    <xsl:choose>
                      <xsl:when test="contains(substring-after(sitemap:loc, '://'), '/')">
                        /<xsl:value-of select="substring-after(substring-after(sitemap:loc, '://'), '/')" />
                      </xsl:when>
                      <xsl:otherwise>/</xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>

                  <tr data-type="{$itemType}" data-path="{$itemPath}" data-time="{sitemap:lastmod}">
                    <td>
                      <xsl:choose>
                        <xsl:when test="$itemType = 'post'">
                          <span class="type-badge" data-filter-type="post" title="{{ T `sitemapOnlyType` (dict `Type` (T `contentTypePost`)) }}">{{ T "contentTypePost" }}</span>
                        </xsl:when>
                        <xsl:when test="$itemType = 'category'">
                          <span class="type-badge" data-filter-type="category" title="{{ T `sitemapOnlyType` (dict `Type` (T `categories`)) }}">{{ T "categories" }}</span>
                        </xsl:when>
                        <xsl:when test="$itemType = 'tag'">
                          <span class="type-badge" data-filter-type="tag" title="{{ T `sitemapOnlyType` (dict `Type` (T `tags`)) }}">{{ T "tags" }}</span>
                        </xsl:when>
                        <xsl:otherwise>
                          <span class="type-badge" data-filter-type="page" title="{{ T `sitemapOnlyType` (dict `Type` (T `contentTypePage`)) }}">{{ T "contentTypePage" }}</span>
                        </xsl:otherwise>
                      </xsl:choose>

                      <a class="link-plain">
                        <xsl:attribute name="href">
                          <xsl:value-of select="sitemap:loc" />
                        </xsl:attribute>
                        <span class="path-text">
                          <xsl:value-of select="$itemPath" />
                        </span>
                      </a>
                    </td>
                    <td class="time-col">
                      <xsl:value-of select="substring(sitemap:lastmod, 1, 10)" />
                      <xsl:if test="string-length(sitemap:lastmod) &gt;= 16">
                        <xsl:text> </xsl:text>
                        <xsl:value-of select="substring(sitemap:lastmod, 12, 5)" />
                      </xsl:if>
                    </td>
                  </tr>
                </xsl:for-each>
                <tr id="emptyRow" class="is-hidden">
                  <td colspan="2" class="empty-state">
                    {{ T "sitemapAllHidden" }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <footer class="page-footer">
            <p>© {{ now.Format "2006" }} {{ site.Title }}.</p>
          </footer>
        </main>

        {{- /* Minified, and wrapped in CDATA because the stylesheet is XML. */ -}}
        <script><![CDATA[{{ (resources.Get "js/xml-xsl-sitemap.js" | resources.ExecuteAsTemplate "js/xml-xsl-sitemap.js" . | resources.Minify).Content }}]]></script>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
