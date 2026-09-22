// Copyright 2024 The Chaos theme authors.
// Licensed under the Apache License, Version 2.0.
//
// Applies the reader's stored theme preference on an XSLT-rendered page.
// Loaded inline by xml-xsl-theme.html, which minifies it; it lives here as a
// plain asset because it needs no template data.

(function() {
  var mode;
  try {
    mode = localStorage.getItem('theme-mode');
  } catch (e) {
    // Storage unavailable (private mode, blocked cookies): fall back to the system.
  }
  if (mode !== 'dark' && mode !== 'light') {
    mode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  document.documentElement.classList.add(mode);
})();
