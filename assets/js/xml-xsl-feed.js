// Script for the page feed.xsl renders: parses entry HTML that the XSLT
// engine left as text, and copies the feed address to the clipboard.
//
// Executed as a template (resources.ExecuteAsTemplate) for the localised
// strings, then minified and inlined into an XML document inside a CDATA
// section -- so nothing here may contain the string that would close one.

// The feed carries entry bodies as escaped HTML, and the stylesheet emits them
// with disable-output-escaping. libxslt (Chrome, Safari) and polyxslt honour
// that; Firefox's XSLT engine builds the result tree directly and cannot, so
// the markup arrives as a text node (Mozilla bug 98168). An element holding
// only text is re-parsed as HTML -- the same trust the stylesheet already
// grants the feed -- and where the markup was honoured this finds nothing.
(function() {
  var targets = document.querySelectorAll('[data-feed-html]');
  for (var i = 0; i < targets.length; i++) {
    var el = targets[i];
    if (el.childElementCount === 0 && el.textContent.trim() !== '') {
      el.innerHTML = el.textContent;
    }
  }
})();

(function() {
  var box = document.getElementById('feedUrlCopy');
  var value = document.getElementById('feedUrlValue');
  var hint = document.getElementById('feedUrlHint');
  if (!box || !value || !hint) return;

  var copyLabel = {{ T "copyFeedUrl" | jsonify }};
  var copiedLabel = {{ T "copiedCode" | jsonify }};
  var failedLabel = {{ T "feedUrlCopyFailed" | jsonify }};
  var resetTimer;

  function report(ok) {
    hint.textContent = ok ? copiedLabel : failedLabel;
    box.classList.toggle('copied', ok);
    box.classList.toggle('failed', !ok);
    clearTimeout(resetTimer);
    resetTimer = setTimeout(function() {
      hint.textContent = copyLabel;
      box.classList.remove('copied');
      box.classList.remove('failed');
    }, 2000);
  }

  box.addEventListener('click', function() {
    // navigator.clipboard alone: document.execCommand is deprecated, and the
    // textarea fallback that used it was a second copy of what main.js also
    // carried. Outside a secure context clipboard is undefined and the
    // property access throws, so the try covers that as well as a rejected
    // write -- and the page now says so rather than appearing to do nothing.
    try {
      navigator.clipboard.writeText(value.textContent.trim()).then(function() {
        report(true);
      }).catch(function() {
        report(false);
      });
    } catch (e) {
      report(false);
    }
  });
})();
