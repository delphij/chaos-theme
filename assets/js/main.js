// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.

(function() {
  // Constants
  const THEME_DARK = 'dark';
  const THEME_LIGHT = 'light';

  const root = document.documentElement;
  const btn = document.getElementById('themeToggle');
  const storageKey = 'scheme';

  // Helper function for media query checks
  function checkMediaQuery(query) {
    return window.matchMedia?.(query).matches ?? false;
  }

  // Cached DOM references for performance
  const themeAnnouncement = document.getElementById('theme-announcement');
  const printReferences = document.getElementById('print-references');
  const articlePost = document.querySelector('article.post');

  // Get current theme from DOM
  function getCurrentTheme() {
    return root.classList.contains(THEME_DARK) ? THEME_DARK : THEME_LIGHT;
  }

  // Toggle theme value
  function toggleTheme(theme) {
    return theme === THEME_DARK ? THEME_LIGHT : THEME_DARK;
  }

  // Apply theme to DOM and button
  function applyTheme(theme) {
    const isDark = theme === THEME_DARK;
    root.classList.toggle(THEME_DARK, isDark);
    btn.textContent = isDark ? '☀️' : '🌙';
    btn.setAttribute('aria-label', `Switch to ${toggleTheme(theme)} mode`);
  }

  // Announce theme change to screen readers (only for users who likely care about visual themes)
  function announceTheme(theme) {
    if (!themeAnnouncement || !window.i18n) return;

    // Only announce if user has accessibility preferences indicating they care about visual themes
    const prefersContrast = checkMediaQuery('(prefers-contrast: more)') ||
                            checkMediaQuery('(prefers-contrast: less)');
    const prefersReducedTransparency = checkMediaQuery('(prefers-reduced-transparency: reduce)');

    // Announce only if user has visual accessibility preferences enabled
    if (prefersContrast || prefersReducedTransparency) {
      themeAnnouncement.textContent = theme === THEME_DARK ? window.i18n.themeDarkMode : window.i18n.themeLightMode;
    }
  }

  // Sync theme with Remark42 comment system
  function syncRemark42Theme(withRetries = false) {
    const theme = getCurrentTheme();
    window.REMARK42?.changeTheme(theme);

    if (withRetries) {
      // Retry with exponential backoff for race conditions
      [100, 400, 800, 1600, 3200].forEach(delay => {
        setTimeout(() => window.REMARK42?.changeTheme(getCurrentTheme()), delay);
      });
    }
  }

  // LocalStorage helpers with error handling
  function getStoredTheme() {
    try {
      return localStorage.getItem(storageKey);
    } catch {
      return null;
    }
  }

  function setStoredTheme(theme) {
    try {
      localStorage.setItem(storageKey, theme);
    } catch {
      // Silently fail if localStorage is unavailable
    }
  }

  // Initialize theme on page load
  const savedTheme = getStoredTheme();
  if (savedTheme) {
    applyTheme(savedTheme);
  } else {
    const prefersDark = checkMediaQuery('(prefers-color-scheme: dark)');
    applyTheme(prefersDark ? THEME_DARK : THEME_LIGHT);
  }

  // Handle theme toggle clicks
  btn.addEventListener('click', () => {
    const nextTheme = toggleTheme(getCurrentTheme());
    applyTheme(nextTheme);
    setStoredTheme(nextTheme);
    announceTheme(nextTheme);
    syncRemark42Theme(false);
  });

  // Sync with Remark42 when it becomes ready
  window.addEventListener('REMARK42::ready', () => syncRemark42Theme(true), { once: true });

  // Reusable overlay toggle handler
  function setupOverlayToggle(button, overlay, openClass) {
    if (!button || !overlay) return;

    const closeOverlay = () => {
      overlay.classList.remove(openClass);
      button.setAttribute('aria-expanded', 'false');
    };

    // Toggle on button click
    button.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = overlay.classList.toggle(openClass);
      button.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    // Close when clicking links inside overlay
    overlay.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', closeOverlay);
    });

    return { overlay, button, openClass, closeOverlay };
  }

  // Setup mobile menu toggle
  const menuOverlay = setupOverlayToggle(
    document.getElementById('menuToggle'),
    document.getElementById('mainNav'),
    'menu-open'
  );

  // Setup TOC toggle
  const tocOverlay = setupOverlayToggle(
    document.getElementById('tocToggle'),
    document.getElementById('tableOfContents'),
    'toc-open'
  );

  // Consolidated click-outside and Escape key handlers
  const overlays = [menuOverlay, tocOverlay].filter(Boolean);

  if (overlays.length > 0) {
    // Close overlays when clicking outside
    document.addEventListener('click', (e) => {
      overlays.forEach(({ overlay, button, openClass, closeOverlay }) => {
        if (overlay.classList.contains(openClass)) {
          if (!button.contains(e.target) && !overlay.contains(e.target)) {
            closeOverlay();
          }
        }
      });
    });

    // Close overlays on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        overlays.forEach(({ overlay, button, openClass, closeOverlay }) => {
          if (overlay.classList.contains(openClass)) {
            closeOverlay();
            button.focus();
          }
        });
      }
    });
  }

  // Table of Contents - Active section highlighting
  const toc = document.getElementById('tableOfContents');
  if (toc) {

    // Active section highlighting with Intersection Observer
    const headings = document.querySelectorAll('article h2[id], article h3[id], article h4[id]');
    const tocLinks = toc.querySelectorAll('a');

    if (headings.length > 0 && tocLinks.length > 0) {
      // Track currently active link for efficient updates
      let currentActive = null;

      // Get nav height from CSS variable for consistent offset
      const navHeight = getComputedStyle(root).getPropertyValue('--nav-height').trim();

      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          const id = entry.target.getAttribute('id');
          const tocLink = toc.querySelector(`a[href="#${id}"]`);

          if (tocLink && entry.isIntersecting) {
            // Remove active class only from previously active link
            if (currentActive && currentActive !== tocLink) {
              currentActive.classList.remove('active');
            }
            // Add active class to current link
            tocLink.classList.add('active');
            currentActive = tocLink;
          }
        });
      }, {
        rootMargin: `-${navHeight} 0px -80% 0px`,  // Use CSS variable for offset
        threshold: 0
      });

      headings.forEach(heading => observer.observe(heading));
    }
  }

  // Print footnotes - Convert external links to footnotes
  let originalContent = '';

  window.addEventListener('beforeprint', () => {
    if (!printReferences || !articlePost) return;

    const links = Array.from(articlePost.querySelectorAll('a[href*="://"]'));

    if (links.length === 0) return;

    // Store original innerHTML for cleanup
    originalContent = printReferences.innerHTML;

    // Create footnote references and build list with IDs for bidirectional linking
    const footnotes = [];
    links.forEach((link, index) => {
      const num = index + 1;
      const refId = `print-fnref-${num}`;
      const noteId = `print-fn-${num}`;

      // Wrap the link in a span with ID for back-reference
      const wrapper = document.createElement('span');
      wrapper.id = refId;
      link.parentNode.insertBefore(wrapper, link);
      wrapper.appendChild(link);

      // Add superscript number to link (now links to footnote)
      const sup = document.createElement('a');
      sup.href = `#${noteId}`;
      sup.className = 'print-footnote-ref';
      sup.textContent = `[${num}]`;
      link.appendChild(sup);

      // Store URL and IDs for footnote list
      footnotes.push({ url: link.href, refId, noteId });
    });

    // Build references section with clickable numbers
    const heading = document.createElement('h2');
    heading.textContent = window.i18n?.printReferences || 'References';

    const list = document.createElement('ol');
    const items = footnotes.map(({ url, refId, noteId }, index) => {
      const li = document.createElement('li');
      li.id = noteId;

      // Create clickable caret that links back to reference (Wikipedia-style)
      const backLink = document.createElement('a');
      backLink.href = `#${refId}`;
      backLink.className = 'print-footnote-backref';
      backLink.textContent = '^';

      li.appendChild(backLink);
      li.appendChild(document.createTextNode(' ' + url));
      return li;
    });
    list.append(...items);

    printReferences.replaceChildren(heading, list);
  });

  window.addEventListener('afterprint', () => {
    if (!printReferences) return;

    // Remove footnote reference numbers from links
    document.querySelectorAll('.print-footnote-ref').forEach(el => el.remove());

    // Remove wrapper spans and restore original link structure
    document.querySelectorAll('span[id^="print-fnref-"]').forEach(wrapper => {
      const parent = wrapper.parentNode;
      while (wrapper.firstChild) {
        parent.insertBefore(wrapper.firstChild, wrapper);
      }
      wrapper.remove();
    });

    // Clear references section
    printReferences.innerHTML = originalContent;
  });
})();
