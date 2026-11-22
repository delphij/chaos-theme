// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Active-section highlighting, shared by the article TOC, the /tags/ A-Z
// navigation and the /archives/ timeline. Extracted from main.js.

const root = document.documentElement;

// ScrollSpy - Active section highlighting with IntersectionObserver
// Reused across Article TOC, /tags/ A-Z navigation, and /archives/ timeline
function setupScrollSpy(navContainer, targetSelector) {
  if (!navContainer) return;
  const targets = document.querySelectorAll(targetSelector);
  if (targets.length === 0) return;

  let currentActive = null;
  const navHeight = getComputedStyle(root).getPropertyValue('--nav-height').trim() || '80px';

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      const id = entry.target.id;
      const navLink = navContainer.querySelector(`a[href="#${CSS.escape(id)}"]`) ||
        navContainer.querySelector(`a[href="#${CSS.escape(encodeURIComponent(id))}"]`);

      if (navLink && entry.isIntersecting) {
        if (currentActive && currentActive !== navLink) {
          currentActive.classList.remove('active');
          currentActive.removeAttribute('aria-current');
        }
        navLink.classList.add('active');
        navLink.setAttribute('aria-current', 'true');
        currentActive = navLink;
      }
    });
  }, {
    rootMargin: `-${navHeight} 0px -70% 0px`,
    threshold: 0
  });

  targets.forEach(target => observer.observe(target));
}

export function initScrollSpy() {
  // 1. Table of Contents in Articles
  setupScrollSpy(document.getElementById('tableOfContents'), 'article h2[id], article h3[id], article h4[id]');

  // 2. A-Z Tag Navigation on Tags page
  setupScrollSpy(document.querySelector('.sidebar-tag-nav'), '#hot-tags, .tag-letter-group[id]');

  // 3. Year / Group Timeline Navigation on Archives page
  setupScrollSpy(document.querySelector('.sidebar-year-list'), '.archive-year-section[id], .archive-section[id]');

  // 4. Category Jump Navigation on Categories and Index Homepage
  setupScrollSpy(document.querySelector('.sidebar-cat-nav'), '.archive-section[id]');
}
