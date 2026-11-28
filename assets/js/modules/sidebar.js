// Copyright 2026 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Populates the browsing-guide sidebar (`aside[data-sidebar-src]`) from the
// versioned sidebar JSON (`/_data/v1/sidebar.json`) on desktop viewports
// (>= 1360px). The container starts `hidden` so pages without JS (or if the
// fetch fails) show no empty shell, and narrow viewports where `.home-sidebar`
// is hidden never issue a request.

const DESKTOP_QUERY = '(min-width: 1360px)';

function normalizePath(url) {
  if (!url) return '';
  try {
    const { pathname } = new URL(url, window.location.href);
    return pathname.replace(/\/page\/\d+\/?$/, '/').replace(/\/?$/, '/');
  } catch {
    return '';
  }
}

function buildWidget(section, currentPath) {
  if (!section || !Array.isArray(section.items)) return null;

  const widget = document.createElement('div');
  widget.className = 'sidebar-widget';

  const heading = document.createElement('h2');
  heading.className = 'sidebar-widget-title';
  heading.textContent = section.title || '';

  const cloud = document.createElement('div');
  cloud.className = 'sidebar-tags-cloud';
  const prefix = section.prefix || '';
  for (const item of section.items) {
    const a = document.createElement('a');
    a.className = 'sidebar-tag-item';
    a.href = item.url;
    a.textContent = `${prefix}${item.name}`;
    a.dataset.count = item.count;
    if (currentPath && normalizePath(item.url) === currentPath) {
      a.classList.add('active');
      a.setAttribute('aria-current', 'page');
    }
    cloud.append(a);
  }

  widget.append(heading, cloud);

  if (section.more?.url && section.more?.text) {
    const footer = document.createElement('div');
    footer.className = 'sidebar-widget-footer';
    const more = document.createElement('a');
    more.className = 'sidebar-more-link';
    more.href = section.more.url;
    more.textContent = section.more.text;
    footer.append(more);
    widget.append(footer);
  }

  return widget;
}

export function initSidebar() {
  const aside = document.querySelector('aside[data-sidebar-src]');
  const src = aside?.dataset.sidebarSrc;
  if (!aside || !src) return;

  let requested = false;
  const load = async () => {
    if (requested) return;
    requested = true;
    try {
      const res = await fetch(src);
      if (!res.ok) return;
      const data = await res.json();
      if (!Array.isArray(data?.widgets)) return;
      const card = document.createElement('div');
      card.className = 'sidebar-card';
      const currentPath = normalizePath(window.location.href);
      for (const section of data.widgets) {
        const widget = buildWidget(section, currentPath);
        if (widget) card.append(widget);
      }
      if (card.childElementCount > 0) {
        aside.replaceChildren(card);
        aside.hidden = false;
      }
    } catch {
      // Leave the sidebar hidden on network or parse failure.
    }
  };

  const desktop = window.matchMedia(DESKTOP_QUERY);
  if (desktop.matches) {
    load();
  } else {
    desktop.addEventListener('change', (e) => {
      if (e.matches) load();
    }, { once: true });
  }
}
