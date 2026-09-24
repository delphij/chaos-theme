// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Renders the Mermaid diagrams on a page, and re-renders them when the theme
// changes so the diagram's palette follows the page's.
//
// Its own entry point rather than part of main.js: foot/mermaid.html loads it
// only on pages that actually contain a diagram, alongside the 2.5 MB Mermaid
// library it needs. Loading either unconditionally would put them on all of
// the site's pages to serve the few that have a figure.

import { THEME_CHANGE_EVENT } from './modules/events.js';

function isDarkTheme(event) {
  // The event carries the theme that was just applied; without one (the
  // first render) read what is on the element.
  if (event?.detail?.theme) return event.detail.theme === 'dark';
  return document.documentElement.classList.contains('dark');
}

function renderMermaid(event) {
  if (typeof mermaid === 'undefined') return;

  const isDark = isDarkTheme(event);
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

  document.querySelectorAll('pre.mermaid').forEach((el, i) => {
    // The first render replaces the element's text with an <svg>, so the
    // source is kept in an attribute for every render after it.
    let code = el.getAttribute('data-original-code');
    if (!code) {
      code = el.textContent.trim();
      el.setAttribute('data-original-code', code);
    }

    const id = `mermaid-diagram-${i}`;
    try {
      mermaid.render(id, code)
        .then(res => { el.innerHTML = res.svg; })
        .catch(err => console.error('Mermaid render error:', err));
    } catch (e) {
      console.error('Mermaid render exception:', e);
    }
  });
}

// No DOMContentLoaded wrapper: this script and the Mermaid library are both
// deferred, and deferred scripts run in document order after parsing, so the
// library is loaded and the diagrams are in the DOM by the time this runs.
renderMermaid();
document.addEventListener(THEME_CHANGE_EVENT, renderMermaid);
