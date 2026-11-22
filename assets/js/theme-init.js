// Copyright 2024 The Chaos theme authors.
// Licensed under the Apache License, Version 2.0.
//
// Applies the reader's stored theme preference before first paint by syncing
// <meta name="color-scheme"> ("light dark", "light", or "dark"), on an
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
  var meta = document.querySelector('meta[name="color-scheme"]');
  if (meta) {
    meta.content = (mode === 'dark' || mode === 'light') ? mode : 'light dark';
  }
})();
