// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.

(function() {
  const root = document.documentElement;
  const btn = document.getElementById('themeToggle');
  const storageKey = 'scheme';

  // Get current theme from DOM
  function getCurrentTheme() {
    return root.classList.contains('dark') ? 'dark' : 'light';
  }

  // Toggle theme value
  function toggleTheme(theme) {
    return theme === 'dark' ? 'light' : 'dark';
  }

  // Apply theme to DOM and button
  function applyTheme(theme) {
    const isDark = theme === 'dark';
    root.classList.toggle('dark', isDark);
    btn.textContent = isDark ? '☀️' : '🌙';
    btn.setAttribute('aria-label', `Switch to ${toggleTheme(theme)} mode`);
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
    const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
    applyTheme(prefersDark ? 'dark' : 'light');
  }

  // Handle theme toggle clicks
  btn.addEventListener('click', () => {
    const nextTheme = toggleTheme(getCurrentTheme());
    applyTheme(nextTheme);
    setStoredTheme(nextTheme);
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
      overlays.forEach(({ overlay, button, closeOverlay }) => {
        if (overlay.classList.contains(overlay.dataset.openClass || 'menu-open') ||
            overlay.classList.contains('toc-open')) {
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
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          const id = entry.target.getAttribute('id');
          const tocLink = toc.querySelector(`a[href="#${id}"]`);

          if (tocLink) {
            if (entry.isIntersecting) {
              // Remove active class from all links
              tocLinks.forEach(link => link.classList.remove('active'));
              // Add active class to current link
              tocLink.classList.add('active');
            }
          }
        });
      }, {
        rootMargin: '-80px 0px -80% 0px',  // Trigger when heading is near top
        threshold: 0
      });

      headings.forEach(heading => observer.observe(heading));
    }
  }
})();
