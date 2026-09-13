// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.

(function() {
  // Constants
  const THEME_AUTO = 'auto';
  const THEME_DARK = 'dark';
  const THEME_LIGHT = 'light';

  const root = document.documentElement;
  const btn = document.getElementById('themeToggle');
  const storageKey = 'theme-mode';
  const legacyStorageKey = 'scheme';

  // Migrate existing users to Auto mode by clearing legacy two-state preference
  try {
    if (localStorage.getItem(legacyStorageKey)) {
      localStorage.removeItem(legacyStorageKey);
    }
  } catch {
    // Ignore localStorage access errors (e.g. cookies/storage disabled)
  }

  // Helper function for media query checks
  function checkMediaQuery(query) {
    return window.matchMedia?.(query).matches ?? false;
  }

  function isSystemDark() {
    return checkMediaQuery('(prefers-color-scheme: dark)');
  }

  // Cached DOM references for performance
  const themeAnnouncement = document.getElementById('theme-announcement');
  const printReferences = document.getElementById('print-references');
  const articlePost = document.querySelector('article.post');

  // Resolve visual theme ('dark' | 'light') from mode
  function getEffectiveTheme(mode) {
    if (mode === THEME_DARK) return THEME_DARK;
    if (mode === THEME_LIGHT) return THEME_LIGHT;
    return isSystemDark() ? THEME_DARK : THEME_LIGHT;
  }

  // Get current active mode ('auto' | 'dark' | 'light')
  function getCurrentMode() {
    const stored = getStoredTheme();
    if (stored === THEME_DARK || stored === THEME_LIGHT) return stored;
    return THEME_AUTO;
  }

  // Three-state cycle:
  // Auto -> opposite of current system -> same as system -> Auto
  function getNextMode(currentMode) {
    if (currentMode === THEME_AUTO) {
      return isSystemDark() ? THEME_LIGHT : THEME_DARK;
    }
    const systemTheme = isSystemDark() ? THEME_DARK : THEME_LIGHT;
    const oppositeTheme = isSystemDark() ? THEME_LIGHT : THEME_DARK;
    if (currentMode === oppositeTheme) {
      return systemTheme;
    }
    return THEME_AUTO;
  }

  // Apply theme to DOM and button
  function applyTheme(mode) {
    const effectiveTheme = getEffectiveTheme(mode);
    const isDark = effectiveTheme === THEME_DARK;
    root.classList.toggle(THEME_DARK, isDark);

    if (btn) {
      // 🌓 for Auto (following system), 🌙 for forced dark, ☀️ for forced light
      btn.textContent = mode === THEME_AUTO ? '🌓' : (isDark ? '🌙' : '☀️');
      const nextMode = getNextMode(mode);
      let nextLabel = '';
      if (nextMode === THEME_DARK) nextLabel = window.i18n?.themeToggleToDark;
      else if (nextMode === THEME_LIGHT) nextLabel = window.i18n?.themeToggleToLight;
      else if (nextMode === THEME_AUTO) nextLabel = window.i18n?.themeToggleToAuto;
      if (nextLabel) btn.setAttribute('aria-label', nextLabel);
    }
  }

  // Announce theme change to screen readers via aria-live region
  function announceTheme(mode) {
    if (!themeAnnouncement || !window.i18n) return;
    if (mode === THEME_AUTO) {
      themeAnnouncement.textContent = window.i18n.themeAutoMode || 'Auto';
    } else {
      themeAnnouncement.textContent = mode === THEME_DARK ? window.i18n.themeDarkMode : window.i18n.themeLightMode;
    }
  }

  // Sync theme with Remark42 comment system
  function syncRemark42Theme(withRetries = false) {
    const theme = getEffectiveTheme(getCurrentMode());
    window.REMARK42?.changeTheme(theme);

    if (withRetries) {
      // Retry with exponential backoff for race conditions
      [100, 400, 800, 1600, 3200].forEach(delay => {
        setTimeout(() => window.REMARK42?.changeTheme(getEffectiveTheme(getCurrentMode())), delay);
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

  function setStoredTheme(mode) {
    try {
      if (mode === THEME_AUTO) {
        localStorage.removeItem(storageKey);
      } else {
        localStorage.setItem(storageKey, mode);
      }
    } catch {
      // Silently fail if localStorage is unavailable
    }
  }

  // Initialize theme on page load
  const initialMode = getCurrentMode();
  applyTheme(initialMode);

  // Real-time listener for OS/browser color scheme changes
  window.matchMedia?.('(prefers-color-scheme: dark)')?.addEventListener('change', () => {
    if (getCurrentMode() === THEME_AUTO) {
      applyTheme(THEME_AUTO);
      syncRemark42Theme(false);
    }
  });

  // Handle theme toggle clicks
  btn?.addEventListener('click', () => {
    const nextMode = getNextMode(getCurrentMode());
    applyTheme(nextMode);
    setStoredTheme(nextMode);
    announceTheme(nextMode);
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
        if (!id) return;
        const navLink = navContainer.querySelector(`a[href="#${CSS.escape(id)}"]`);

        if (navLink && entry.isIntersecting) {
          if (currentActive && currentActive !== navLink) {
            currentActive.classList.remove('active');
          }
          navLink.classList.add('active');
          currentActive = navLink;
        }
      });
    }, {
      rootMargin: `-${navHeight} 0px -70% 0px`,
      threshold: 0
    });

    targets.forEach(target => observer.observe(target));
  }

  // 1. Table of Contents in Articles
  setupScrollSpy(document.getElementById('tableOfContents'), 'article h2[id], article h3[id], article h4[id]');

  // 2. A-Z Tag Navigation on Tags page
  setupScrollSpy(document.querySelector('.sidebar-tag-nav'), '#hot-tags, .tag-letter-group[id]');

  // 3. Year Timeline Navigation on Archives page
  setupScrollSpy(document.querySelector('.sidebar-year-list'), '.archive-year-section[id]');

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

  // Code block copy to clipboard
  function setupCodeCopyButtons() {
    const copyLabel = window.i18n?.copyCode || 'Copy';
    const copiedLabel = window.i18n?.copiedCode || 'Copied!';
    const copyIconSvg = '<svg class="code-copy-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
    const checkIconSvg = '<svg class="code-copy-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>';

    function setButtonState(btn, isCopied) {
      btn.classList.toggle('copied', isCopied);
      const label = isCopied ? copiedLabel : copyLabel;
      const icon = isCopied ? checkIconSvg : copyIconSvg;
      btn.setAttribute('aria-label', label);
      btn.innerHTML = `${icon}<span class="code-copy-text">${label}</span>`;
    }

    document.querySelectorAll('.highlight').forEach(block => {
      if (block.querySelector('.code-copy-btn')) return;

      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'code-copy-btn';
      setButtonState(btn, false);

      btn.addEventListener('click', () => {
        const codeTd = block.querySelector('.lntable .lntd:last-child pre, .lntable .lntd:last-child code');
        const codeElement = codeTd || block.querySelector('code') || block.querySelector('pre');
        const text = (codeElement ? codeElement.textContent : block.textContent) || '';

        const onSuccess = () => {
          setButtonState(btn, true);
          setTimeout(() => setButtonState(btn, false), 2000);
        };

        if (navigator.clipboard && window.isSecureContext) {
          navigator.clipboard.writeText(text).then(onSuccess).catch(() => fallbackCopy(text, onSuccess));
        } else {
          fallbackCopy(text, onSuccess);
        }
      });

      block.appendChild(btn);
    });

    function fallbackCopy(text, onSuccess) {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.top = '0';
      ta.style.left = '0';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      try {
        if (document.execCommand('copy')) {
          onSuccess();
        }
      } catch {
        // Silently fail
      }
      document.body.removeChild(ta);
    }
  }

  setupCodeCopyButtons();
})();
