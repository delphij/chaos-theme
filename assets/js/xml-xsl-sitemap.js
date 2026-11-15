// Type filters, column sorting and the visible-count readout of the page
//
// sitemap.xsl renders.
//
// Executed as a template (resources.ExecuteAsTemplate) for the localised
// strings, then minified and inlined into an XML document inside a CDATA
// section -- so nothing here may contain the string that would close one.

(function() {
  // Localised strings the script sets at runtime. Fully resolved at build
  // time so no sentence is assembled from fragments in JavaScript.
  var I18N = {
    sortByPath: {{ T "sortByPath" | jsonify }},
    sortByPathAsc: {{ T "sortByPathAscending" | jsonify }},
    sortByPathDesc: {{ T "sortByPathDescending" | jsonify }},
    sortByTime: {{ T "sortByTime" | jsonify }},
    sortByTimeAsc: {{ T "sortByTimeAscending" | jsonify }},
    sortByTimeDesc: {{ T "sortByTimeDescending" | jsonify }}
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
  var headers = [
    { col: 'path', th: thPath, btn: thPath && thPath.querySelector('.sort-btn'), icon: document.getElementById('iconPath'), label: I18N.sortByPath, asc: I18N.sortByPathAsc, desc: I18N.sortByPathDesc },
    { col: 'time', th: thTime, btn: thTime && thTime.querySelector('.sort-btn'), icon: document.getElementById('iconTime'), label: I18N.sortByTime, asc: I18N.sortByTimeAsc, desc: I18N.sortByTimeDesc }
  ];

  // 1. Toggle & filter logic
  function updateVisibility() {
    var visible = 0;

    rows.forEach(function(row) {
      var shown = !!activeTypes[row.getAttribute('data-type')];
      row.classList.toggle('is-hidden', !shown);
      if (shown) visible++;
    });

    pills.forEach(function(pill) {
      var active = !!activeTypes[pill.getAttribute('data-filter')];
      pill.setAttribute('aria-pressed', active ? 'true' : 'false');
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
      var res;
      if (col === 'time') {
        // UTC timestamps, so string order is time order. Ties keep the
        // order the stylesheet gave them in both directions: posts first.
        var timeA = a.getAttribute('data-time') || '';
        var timeB = b.getAttribute('data-time') || '';
        res = timeA < timeB ? -1 : (timeA > timeB ? 1 : 0);
        if (res !== 0) {
          return newDir === 'asc' ? res : -res;
        }
        return a.getAttribute('data-order') - b.getAttribute('data-order');
      }
      var valA = a.getAttribute('data-' + col) || '';
      var valB = b.getAttribute('data-' + col) || '';
      res = valA.localeCompare(valB, undefined, { numeric: true, sensitivity: 'base' });
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
    headers.forEach(function(h) {
      var on = h.col === col;
      h.th.setAttribute('aria-sort', on ? (newDir === 'asc' ? 'ascending' : 'descending') : 'none');
      h.icon.textContent = on ? (newDir === 'asc' ? '↑' : '↓') : '↕';
      if (h.btn) {
        h.btn.setAttribute('aria-label', on ? (newDir === 'asc' ? h.asc : h.desc) : h.label);
      }
    });
  }

  // Bind table header buttons
  headers.forEach(function(h) {
    if (h.btn) {
      h.btn.addEventListener('click', function() {
        sortTable(h.col);
      });
    }
  });
})();
