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
