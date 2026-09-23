// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// The mobile menu and table-of-contents overlays: open/close, click-outside
// and Escape. Extracted from main.js.

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

export function initOverlays() {
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
