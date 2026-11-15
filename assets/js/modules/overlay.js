// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// The mobile menu and table-of-contents overlays (open/close, click-outside,
// focusout and Escape) plus the skip-link focus handoff to <main>.

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

  // Close when keyboard focus tabs out of an open overlay and its toggle, so
  // focus never lands underneath a full-screen mobile/tablet drawer.
  const onFocusOut = (e) => {
    if (!overlay.classList.contains(openClass)) return;
    const next = e.relatedTarget;
    if (next && !overlay.contains(next) && !button.contains(next)) {
      closeOverlay();
    }
  };
  overlay.addEventListener('focusout', onFocusOut);
  button.addEventListener('focusout', onFocusOut);

  return { overlay, button, openClass, closeOverlay };
}

export function initOverlays() {
  // Move focus to <main> when the skip link is activated without keeping a
  // permanent tabindex="-1" on <main> (which otherwise makes clicking anywhere
  // in the prose focus <main> and outline it when pressing Space to scroll).
  const skipLink = document.querySelector('.skip-link');
  const main = document.getElementById('main-content');
  if (skipLink && main) {
    skipLink.addEventListener('click', () => {
      main.setAttribute('tabindex', '-1');
      main.addEventListener('blur', () => main.removeAttribute('tabindex'), { once: true });
      main.focus({ preventScroll: true });
    });
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
}
