<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:html="http://www.w3.org/TR/REC-html40"
  xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
  xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  {{- /* Without this the processor copies these declarations onto the
         result's <html> element, where they mean nothing. */}}
  exclude-result-prefixes="html image sitemap">

  <xsl:output method="html" encoding="UTF-8" indent="yes" />

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
        <style>
          {{ partial "xml-xsl-styles.html" . }}

          /* ----- Sitemap-specific layout ----- */

          /* A dense two-column table, so it uses the site's chrome measure
             rather than the narrower reading measure. */
          .container {
            max-width: var(--max-width);
          }

          /* One colour per content type, assigned from the existing palette so
             the pills and the in-table badges cannot drift apart. */
          .stat-pill[data-filter="post"],
          .type-badge[data-filter-type="post"] {
            --type-color: var(--accent);
          }

          .stat-pill[data-filter="category"],
          .type-badge[data-filter-type="category"] {
            --type-color: var(--primary);
          }

          .stat-pill[data-filter="tag"],
          .type-badge[data-filter-type="tag"] {
            --type-color: var(--muted);
          }

          .stat-pill[data-filter="page"],
          .type-badge[data-filter-type="page"] {
            --type-color: var(--heading);
          }

          /* Filter toolbar */
          .stats-bar {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 14px;
          }

          .filter-label {
            font-size: var(--text-sm);
            font-weight: 600;
            color: var(--muted);
          }

          /* Pills follow .tag-flat-item: flat by default, tinted when engaged. */
          .stat-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 8px;
            font: inherit;
            font-size: var(--text-sm);
            border: 0;
            border-radius: var(--radius-sm);
            background: transparent;
            color: var(--muted);
            cursor: pointer;
            user-select: none;
            transition: color var(--transition-fast), background-color var(--transition-fast);
          }

          .stat-pill.active {
            color: var(--type-color);
            background: var(--paper);
          }

          .stat-pill.inactive {
            text-decoration: line-through;
          }

          .stat-num {
            font-family: var(--font-mono);
            font-weight: 700;
          }

          .filter-status {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            flex-wrap: wrap;
            gap: 4px 16px;
            margin: 0 0 12px;
            font-size: var(--text-sm);
            color: var(--muted);
          }

          .filter-status strong {
            color: var(--heading);
          }

          .filter-hint {
            font-size: var(--text-xs);
          }

          /* The table itself is bare and striped (see the shared partial); only
             the sort affordances and the path column are added here. */
          .table-wrapper {
            overflow-x: auto;
          }

          table {
            font-size: var(--text-sm);
          }

          th.sortable {
            cursor: pointer;
            user-select: none;
            transition: background-color var(--transition-fast), color var(--transition-fast);
          }

          th.sortable:hover {
            background-color: var(--primary);
            color: var(--primary-fg);
          }

          .sort-icon {
            display: inline-block;
            margin-left: 6px;
            font-size: var(--text-xs);
            opacity: 0.55;
          }

          th.sorted-asc .sort-icon,
          th.sorted-desc .sort-icon {
            opacity: 1;
          }

          td {
            vertical-align: middle;
          }

          /* Rows highlight on hover like .archive-post-row on the site,
             and the row's link takes the primary colour with it. */
          tr:hover td {
            background-color: var(--paper);
          }

          tr:hover a.link-plain {
            color: var(--primary);
          }

          tr.is-hidden {
            display: none;
          }

          /* Type labels are flat coloured text, not chips - the site treats
             taxonomy the same way. */
          .type-badge {
            font-size: var(--text-2xs);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--type-color);
            margin-right: 8px;
            cursor: pointer;
            user-select: none;
          }

          .path-text {
            font-family: var(--font-mono);
            word-break: break-all;
          }

          .time-col {
            white-space: nowrap;
            color: var(--muted);
          }

          .empty-state {
            text-align: center;
            padding: 40px 16px;
            color: var(--muted);
            font-size: var(--small-size);
          }
        </style>
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
