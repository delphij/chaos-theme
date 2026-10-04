// Copyright 2024 The Chaos theme authors.
// Licensed under the Apache License, Version 2.0.
//
// Applies the reader's stored theme preference before first paint, on an
// XSLT-rendered page and, ahead of the deferred main.js, on every other one.
// Loaded inline by xml-xsl-theme.html and head.html, which minify it; it lives
// here as a plain asset because it needs no template data.

(function() {
  var mode;
  try {
    mode = localStorage.getItem('theme-mode');
  } catch (e) {
    // Storage unavailable (private mode, blocked cookies): fall back to the system.
  }
  // A stored choice wins; anything else follows the system. Light is the
  // absence of `dark`: nothing keys off a `light` class.
  if (mode === 'dark' || (mode !== 'light' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
  }
})();
