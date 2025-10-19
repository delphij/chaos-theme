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

  // Mobile menu toggle
  const menuBtn = document.getElementById('menuToggle');
  const mainNav = document.getElementById('mainNav');

  if (menuBtn && mainNav) {
    // Toggle menu open/closed
    menuBtn.addEventListener('click', (e) => {
      e.stopPropagation();  // Prevent immediate close from document listener
      const isOpen = mainNav.classList.toggle('menu-open');
      menuBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (mainNav.classList.contains('menu-open') &&
          !menuBtn.contains(e.target) &&
          !mainNav.contains(e.target)) {
        mainNav.classList.remove('menu-open');
        menuBtn.setAttribute('aria-expanded', 'false');
      }
    });

    // Close menu when a link is clicked
    mainNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mainNav.classList.remove('menu-open');
        menuBtn.setAttribute('aria-expanded', 'false');
      });
    });

    // Close menu on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && mainNav.classList.contains('menu-open')) {
        mainNav.classList.remove('menu-open');
        menuBtn.setAttribute('aria-expanded', 'false');
        menuBtn.focus();  // Return focus to button for keyboard users
      }
    });
  }
})();
