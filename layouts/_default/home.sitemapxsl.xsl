<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:html="http://www.w3.org/TR/REC-html40"
  xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
  xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="html" encoding="UTF-8" indent="yes" />

  <xsl:template match="/">
    <html{{ with site.Language.Locale }} lang="{{ . }}"{{ end }}>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{{ T "sitemapPageTitle" }} — {{ site.Title }}</title>
        <style>
          {{ partial "xml-xsl-styles.html" . }}

          /* Sitemap specific content type tokens */
          :root {
            --content-width: 960px;
            --type-post-bg: #EBF3FB;
            --type-post-fg: #1D5B90;
            --type-post-border: #B8D5F2;
            --type-cat-bg: #FDF0ED;
            --type-cat-fg: var(--primary);
            --type-cat-border: #F5C6BE;
            --type-tag-bg: #F0F4F0;
            --type-tag-fg: #2D6A2E;
            --type-tag-border: #C4DFC4;
            --type-page-bg: #F2F2F2;
            --type-page-fg: #444444;
            --type-page-border: #D0D0D0;
          }

          /* Filter bar without dividing line */
          .stats-bar {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 14px;
            align-items: center;
          }

          .filter-label {
            font-size: 13px;
            font-weight: 600;
            color: var(--muted);
            margin-right: 2px;
          }

          .stat-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            font-weight: 500;
            padding: 5px 12px;
            border-radius: var(--radius-sm);
            cursor: pointer;
            user-select: none;
            border: 1px solid transparent;
            transition: opacity var(--transition-fast), background-color var(--transition-fast);
          }

          .stat-pill:hover {
            opacity: 0.85;
          }

          /* Active category states */
          .stat-pill[data-filter="post"].active {
            background: var(--type-post-bg);
            color: var(--type-post-fg);
            border-color: var(--type-post-border);
          }

          .stat-pill[data-filter="category"].active {
            background: var(--type-cat-bg);
            color: var(--type-cat-fg);
            border-color: var(--type-cat-border);
          }

          .stat-pill[data-filter="tag"].active {
            background: var(--type-tag-bg);
            color: var(--type-tag-fg);
            border-color: var(--type-tag-border);
          }

          .stat-pill[data-filter="page"].active {
            background: var(--type-page-bg);
            color: var(--type-page-fg);
            border-color: var(--type-page-border);
          }

          /* Inactive category state */
          .stat-pill.inactive {
            background: transparent;
            color: var(--muted);
            border-color: transparent;
            opacity: 0.45;
            text-decoration: line-through;
          }

          .stat-pill.inactive .stat-num {
            color: var(--muted);
          }

          .stat-num {
            font-weight: 700;
          }

          .filter-status {
            font-size: 13px;
            color: var(--muted);
            margin: 0 0 12px 2px;
            display: flex;
            justify-content: space-between;
            align-items: center;
          }

          .filter-status span strong {
            color: var(--heading);
          }

          /* Table without dense horizontal lines */
          .table-wrapper {
            background: var(--surface);
            border: var(--border);
            border-radius: var(--radius-md);
            overflow: hidden;
          }

          table {
            border-collapse: collapse;
            width: 100%;
            font-size: 13.5px;
            font-variant-numeric: tabular-nums;
          }

          th {
            background: var(--paper);
            color: var(--heading);
            text-align: left;
            padding: 12px 16px;
            font-weight: 600;
            border-bottom: 2px solid var(--border-color);
            user-select: none;
          }

          th.sortable {
            cursor: pointer;
            transition: background-color var(--transition-fast), color var(--transition-fast);
          }

          th.sortable:hover {
            background: var(--paper-strong);
            color: var(--primary);
          }

          th.sortable:focus-visible {
            outline: 2px solid var(--primary);
            outline-offset: -2px;
          }

          .sort-icon {
            display: inline-block;
            margin-left: 6px;
            font-size: 12px;
            color: var(--muted);
            transition: color var(--transition-fast);
          }

          th.sorted-asc .sort-icon,
          th.sorted-desc .sort-icon {
            color: var(--primary);
            font-weight: 700;
          }

          td {
            padding: 9px 16px;
            border-bottom: none;
            vertical-align: middle;
          }

          /* Zebra striping instead of lines on every row */
          tbody tr:nth-of-type(even) td {
            background-color: var(--table-stripe);
          }

          tr:hover td {
            background-color: var(--paper) !important;
          }

          tr.is-hidden {
            display: none !important;
          }

          a {
            color: var(--link);
            text-decoration: none;
            word-break: break-all;
          }

          a:hover {
            color: var(--link-hover);
            text-decoration: underline;
          }

          .type-badge {
            display: inline-block;
            font-size: 11px;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: var(--radius-sm);
            margin-right: 8px;
            vertical-align: middle;
            cursor: pointer;
            transition: opacity var(--transition-fast);
          }

          .type-badge:hover {
            opacity: 0.8;
          }

          .badge-post {
            background: var(--type-post-bg);
            color: var(--type-post-fg);
          }

          .badge-cat {
            background: var(--type-cat-bg);
            color: var(--type-cat-fg);
          }

          .badge-tag {
            background: var(--type-tag-bg);
            color: var(--type-tag-fg);
          }

          .badge-page {
            background: var(--type-page-bg);
            color: var(--type-page-fg);
          }

          .path-text {
            vertical-align: middle;
            font-family: "Noto Sans Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 13px;
          }

          .time-col {
            white-space: nowrap;
            color: var(--muted);
            font-size: 13px;
          }

          .empty-state {
            text-align: center;
            padding: 40px 16px;
            color: var(--muted);
            font-size: 14.5px;
          }
        </style>
      </head>
      <body>
        <header class="site-header">
          <div class="site-header-inner">
            <a class="site-brand" href="{{ "/" | relLangURL }}">{{ site.Title }}</a>
            <a class="back-link" href="{{ "/" | relLangURL }}">{{ T "visitBlogHome" }}</a>
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
            <span style="font-size: 12px; color: var(--muted);">{{ T "sitemapHint" }}</span>
          </div>

          <div class="table-wrapper">
            <table id="sitemapTable">
              <thead>
                <tr>
                  <th style="width: 70%;" class="sortable" id="thPath" data-col="path" tabindex="0" role="button" aria-label="{{ T `sortByPath` }}">
                    {{ T "sitemapColumnPath" }} <span class="sort-icon" id="iconPath">↕</span>
                  </th>
                  <th style="width: 30%;" class="sortable sorted-desc" id="thTime" data-col="time" tabindex="0" role="button" aria-label="{{ T `sortByTimeDescending` }}">
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
                          <span class="type-badge badge-post" data-filter-type="post" title="{{ T `sitemapOnlyType` (dict `Type` (T `contentTypePost`)) }}">{{ T "contentTypePost" }}</span>
                        </xsl:when>
                        <xsl:when test="$itemType = 'category'">
                          <span class="type-badge badge-cat" data-filter-type="category" title="{{ T `sitemapOnlyType` (dict `Type` (T `categories`)) }}">{{ T "categories" }}</span>
                        </xsl:when>
                        <xsl:when test="$itemType = 'tag'">
                          <span class="type-badge badge-tag" data-filter-type="tag" title="{{ T `sitemapOnlyType` (dict `Type` (T `tags`)) }}">{{ T "tags" }}</span>
                        </xsl:when>
                        <xsl:otherwise>
                          <span class="type-badge badge-page" data-filter-type="page" title="{{ T `sitemapOnlyType` (dict `Type` (T `contentTypePage`)) }}">{{ T "contentTypePage" }}</span>
                        </xsl:otherwise>
                      </xsl:choose>

                      <a>
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
        </main>

        <script>
        <![CDATA[
          (function() {
            // Localised strings the script sets at runtime. Fully resolved at build
            // time so no sentence is assembled from fragments in JavaScript.
            var I18N = {
              sortByPath: ]]>{{ T "sortByPath" | jsonify }}<![CDATA[,
              sortByPathAsc: ]]>{{ T "sortByPathAscending" | jsonify }}<![CDATA[,
              sortByPathDesc: ]]>{{ T "sortByPathDescending" | jsonify }}<![CDATA[,
              sortByTime: ]]>{{ T "sortByTime" | jsonify }}<![CDATA[,
              sortByTimeAsc: ]]>{{ T "sortByTimeAscending" | jsonify }}<![CDATA[,
              sortByTimeDesc: ]]>{{ T "sortByTimeDescending" | jsonify }}<![CDATA[
            };

            var activeTypes = {
              post: true,
              category: true,
              tag: true,
              page: true
            };
            var currentSort = { col: 'time', dir: 'desc' };

            var tbody = document.getElementById('sitemapTbody');
            var rows = Array.from(tbody.querySelectorAll('tr[data-type]'));
            var emptyRow = document.getElementById('emptyRow');
            var visibleCountEl = document.getElementById('visibleCount');
            var pills = Array.from(document.querySelectorAll('.stat-pill'));
            var thPath = document.getElementById('thPath');
            var thTime = document.getElementById('thTime');
            var iconPath = document.getElementById('iconPath');
            var iconTime = document.getElementById('iconTime');

            // 1. Toggle & filter logic
            function updateVisibility() {
              var visible = 0;

              rows.forEach(function(row) {
                var rowType = row.getAttribute('data-type');
                if (activeTypes[rowType]) {
                  row.classList.remove('is-hidden');
                  visible++;
                } else {
                  row.classList.add('is-hidden');
                }
              });

              pills.forEach(function(pill) {
                var filter = pill.getAttribute('data-filter');
                if (activeTypes[filter]) {
                  pill.classList.add('active');
                  pill.classList.remove('inactive');
                } else {
                  pill.classList.remove('active');
                  pill.classList.add('inactive');
                }
              });

              if (emptyRow) {
                emptyRow.classList.toggle('is-hidden', visible > 0);
              }

              if (visibleCountEl) {
                visibleCountEl.textContent = visible;
              }
            }

            function toggleType(type) {
              if (activeTypes.hasOwnProperty(type)) {
                activeTypes[type] = !activeTypes[type];
                updateVisibility();
              }
            }

            function isolateType(type) {
              // Check if only this type is active
              var onlyThisActive = activeTypes[type] && Object.keys(activeTypes).every(function(k) {
                return k === type ? activeTypes[k] : !activeTypes[k];
              });

              if (onlyThisActive) {
                // Restore all
                Object.keys(activeTypes).forEach(function(k) {
                  activeTypes[k] = true;
                });
              } else {
                // Isolate to this type only
                Object.keys(activeTypes).forEach(function(k) {
                  activeTypes[k] = (k === type);
                });
              }
              updateVisibility();
            }

            // Bind filter pills click (toggles this category)
            pills.forEach(function(pill) {
              pill.addEventListener('click', function() {
                var filter = this.getAttribute('data-filter');
                toggleType(filter);
              });
            });

            // Bind in-table type badges click (isolates to this category)
            tbody.addEventListener('click', function(e) {
              var badge = e.target.closest('.type-badge');
              if (badge) {
                var filterType = badge.getAttribute('data-filter-type');
                if (filterType) {
                  isolateType(filterType);
                }
              }
            });

            // 2. Sorting logic
            function sortTable(col) {
              var newDir = 'asc';
              if (currentSort.col === col) {
                newDir = currentSort.dir === 'asc' ? 'desc' : 'asc';
              } else {
                newDir = col === 'time' ? 'desc' : 'asc';
              }
              currentSort = { col: col, dir: newDir };

              rows.sort(function(a, b) {
                var valA = a.getAttribute('data-' + col) || '';
                var valB = b.getAttribute('data-' + col) || '';
                var res = valA.localeCompare(valB, undefined, { numeric: true, sensitivity: 'base' });
                return newDir === 'asc' ? res : -res;
              });

              // Re-attach sorted rows (keep emptyRow at bottom)
              rows.forEach(function(row) {
                tbody.appendChild(row);
              });
              if (emptyRow) {
                tbody.appendChild(emptyRow);
              }

              // Update Header indicators
              if (col === 'path') {
                thPath.className = 'sortable sorted-' + newDir;
                thTime.className = 'sortable';
                iconPath.textContent = newDir === 'asc' ? '↑' : '↓';
                iconTime.textContent = '↕';
                thPath.setAttribute('aria-label', newDir === 'asc' ? I18N.sortByPathAsc : I18N.sortByPathDesc);
                thTime.setAttribute('aria-label', I18N.sortByTime);
              } else {
                thTime.className = 'sortable sorted-' + newDir;
                thPath.className = 'sortable';
                iconTime.textContent = newDir === 'asc' ? '↑' : '↓';
                iconPath.textContent = '↕';
                thTime.setAttribute('aria-label', newDir === 'asc' ? I18N.sortByTimeAsc : I18N.sortByTimeDesc);
                thPath.setAttribute('aria-label', I18N.sortByPath);
              }
            }

            // Bind table headers click & keyboard (Enter/Space)
            [thPath, thTime].forEach(function(th) {
              th.addEventListener('click', function() {
                sortTable(this.getAttribute('data-col'));
              });
              th.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  sortTable(this.getAttribute('data-col'));
                }
              });
            });
          })();
        ]]>
        </script>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
