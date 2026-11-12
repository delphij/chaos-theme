// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Renders the Mermaid diagrams on a page, re-renders them when the theme
// changes so the diagram's palette follows the page's, and swaps in the
// light-palette SVG while printing.
//
// Its own entry point rather than part of main.js: foot/mermaid.html loads it
// only on pages that actually contain a diagram, alongside the 2.5 MB Mermaid
// library it needs. Loading either unconditionally would put them on all of
// the site's pages to serve the few that have a figure.

import { THEME_CHANGE_EVENT } from './modules/events.js';

const diagrams = [...document.querySelectorAll('pre.mermaid')].map((el, i) => ({
  el,
  code: el.textContent.trim(),
  id: `mermaid-diagram-${i}`
}));
const rendered = {};

// theme.js sets the class before it announces a change, so the element is
// right both on the first render and on THEME_CHANGE_EVENT.
function isDarkTheme() {
  return document.documentElement.classList.contains('dark');
}

function show(isDark) {
  const key = isDark ? 'dark' : 'light';
  for (const d of diagrams) {
    if (d[key]) d.el.innerHTML = d[key];
  }
}

function render(isDark) {
  const key = isDark ? 'dark' : 'light';
  return (rendered[key] ||= (async () => {
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'loose',
      theme: isDark ? 'dark' : 'neutral',
      themeVariables: {
        fontFamily: 'inherit',
        edgeLabelBackground: isDark ? '#222222' : '#FFFFFF',
        primaryTextColor: isDark ? '#E6EDF3' : '#222222',
        textColor: isDark ? '#E6EDF3' : '#222222'
      }
    });

    for (const d of diagrams) {
      try {
        const { svg } = await mermaid.render(`${d.id}-${key}`, d.code);
        d[key] = svg;
      } catch (err) {
        console.error('Mermaid render error:', err);
      }
    }
  })());
}

async function renderMermaid() {
  if (typeof mermaid === 'undefined' || diagrams.length === 0) return;
  const isDark = isDarkTheme();
  await render(isDark);
  show(isDark);
  // Pre-render the light SVG in dark mode so beforeprint can swap it in
  // synchronously before the browser snapshots the page.
  if (isDark) await render(false);
}

// No DOMContentLoaded wrapper: this script and the Mermaid library are both
// deferred, and deferred scripts run in document order after parsing, so the
// library is loaded and the diagrams are in the DOM by the time this runs.
renderMermaid();
document.addEventListener(THEME_CHANGE_EVENT, renderMermaid);
window.addEventListener('beforeprint', () => show(false));
window.addEventListener('afterprint', () => show(isDarkTheme()));
