// Shows the times on the pages sitemap.xsl and feed.xsl render in the
// reader's own time zone.
//
// The XML carries UTC, and XSLT 1.0 has no time zones, so the stylesheets
// print the UTC time, marked as such, in a <time data-utc="..."> element.
// This replaces it with local time and keeps the UTC text as the tooltip;
// without JavaScript the UTC text stays.
//
// Concatenated ahead of each page's own script, and inlined inside a CDATA
// section -- so nothing here may contain the string that would close one.

(function() {
  function pad(n) {
    return (n < 10 ? '0' : '') + n;
  }

  var times = document.querySelectorAll('time[data-utc]');
  for (var i = 0; i < times.length; i++) {
    var el = times[i];
    // Accepts both ISO 8601 (Atom, sitemap) and RFC 822 (RSS).
    var ms = Date.parse(el.getAttribute('data-utc'));
    if (isNaN(ms)) continue;
    var d = new Date(ms);
    el.title = el.textContent.trim();
    el.textContent = d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) +
      ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes());
  }
})();
