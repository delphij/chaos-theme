// Copy-to-clipboard for the feed address on the page feed.xsl renders.
//
// 
//
// Executed as a template (resources.ExecuteAsTemplate) for the localised
// strings, then minified and inlined into an XML document inside a CDATA
// section -- so nothing here may contain the string that would close one.

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
