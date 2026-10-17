// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Three-state theme toggle (auto / dark / light) and its Remark42 sync.
// Extracted from main.js.

import { THEME_CHANGE_EVENT } from './events.js';

// Constants
const THEME_AUTO = 'auto';
const THEME_DARK = 'dark';
const THEME_LIGHT = 'light';

const root = document.documentElement;
const btn = document.getElementById('themeToggle');
const storageKey = 'theme-mode';
const legacyStorageKey = 'scheme';
const systemDark = window.matchMedia('(prefers-color-scheme: dark)');

// Cached DOM references for performance
const themeAnnouncement = document.getElementById('theme-announcement');

// Localised strings, from the toggle button's data-* attributes (see
// _partials/header.html). Read once: the button does not change.
const labels = btn?.dataset ?? {};
const NEXT_LABEL = { [THEME_DARK]: labels.labelToDark, [THEME_LIGHT]: labels.labelToLight, [THEME_AUTO]: labels.labelToAuto };
const ANNOUNCEMENT = { [THEME_DARK]: labels.announceDark, [THEME_LIGHT]: labels.announceLight, [THEME_AUTO]: labels.announceAuto || 'Auto' };

function systemTheme() {
  return systemDark.matches ? THEME_DARK : THEME_LIGHT;
}

// Resolve visual theme ('dark' | 'light') from mode
function getEffectiveTheme(mode) {
  return mode === THEME_AUTO ? systemTheme() : mode;
}

// Get current active mode ('auto' | 'dark' | 'light')
function getCurrentMode() {
  const stored = getStoredTheme();
  return stored === THEME_DARK || stored === THEME_LIGHT ? stored : THEME_AUTO;
}

// Three-state cycle:
// Auto -> opposite of current system -> same as system -> Auto
function getNextMode(currentMode) {
  const system = systemTheme();
  const opposite = system === THEME_DARK ? THEME_LIGHT : THEME_DARK;
  if (currentMode === THEME_AUTO) return opposite;
  return currentMode === opposite ? system : THEME_AUTO;
}

// Apply theme to DOM and button
function applyTheme(mode) {
  const effectiveTheme = getEffectiveTheme(mode);
  const isDark = effectiveTheme === THEME_DARK;
  root.classList.toggle(THEME_DARK, isDark);

  // Anything that has to redraw itself for the new theme listens for this
  // rather than watching the toggle button, so it also fires when the OS
  // scheme flips while the site is in auto mode -- which a click listener
  // on the button never sees.
  document.dispatchEvent(new CustomEvent(THEME_CHANGE_EVENT, {
    detail: { mode, theme: effectiveTheme }
  }));

  if (btn) {
    // 🌓 for Auto (following system), 🌙 for forced dark, ☀️ for forced light
    btn.textContent = mode === THEME_AUTO ? '🌓' : (isDark ? '🌙' : '☀️');
    const nextLabel = NEXT_LABEL[getNextMode(mode)];
    if (nextLabel) btn.setAttribute('aria-label', nextLabel);
  }
}

// Announce theme change to screen readers via aria-live region
function announceTheme(mode) {
  if (themeAnnouncement) themeAnnouncement.textContent = ANNOUNCEMENT[mode];
}

// Pass a theme change on to Remark42. Its first theme comes from remark_config
// (_partials/remark.html), which is kept current too: until the embed script
// has run there is no changeTheme, and the frame is built from the config.
function syncRemark42Theme() {
  const theme = getEffectiveTheme(getCurrentMode());
  if (window.remark_config) window.remark_config.theme = theme;
  window.REMARK42?.changeTheme?.(theme);
}

// A theme posted while the frame is still loading is not heard, so send it
// again when the frame reports `inited`, the message the embed script itself
// waits for before it shows the frame.
function watchRemark42Inited() {
  let origin;
  try {
    origin = new URL(window.remark_config?.host).origin;
  } catch {
    return; // No comments on this page
  }
  window.addEventListener('message', event => {
    if (event.origin === origin && event.data?.inited === true) syncRemark42Theme();
  });
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

export function initTheme() {
  // Migrate existing users to Auto mode by clearing legacy two-state preference
  try {
    if (localStorage.getItem(legacyStorageKey)) {
      localStorage.removeItem(legacyStorageKey);
    }
  } catch {
    // Ignore localStorage access errors (e.g. cookies/storage disabled)
  }

  // Initialize theme on page load
  const initialMode = getCurrentMode();
  applyTheme(initialMode);
  watchRemark42Inited();

  // Real-time listener for OS/browser color scheme changes
  systemDark.addEventListener('change', () => {
    if (getCurrentMode() === THEME_AUTO) {
      applyTheme(THEME_AUTO);
      syncRemark42Theme();
    }
  });

  // Handle theme toggle clicks
  btn?.addEventListener('click', () => {
    const nextMode = getNextMode(getCurrentMode());
    applyTheme(nextMode);
    setStoredTheme(nextMode);
    announceTheme(nextMode);
    syncRemark42Theme();
  });
}
