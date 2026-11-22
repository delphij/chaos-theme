// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Interactive GFM task lists (`- [ ]` / `- [x]`).
// Goldmark renders task list checkboxes with `disabled`, leaving online
// checklists unclickable. This module enables them in-session (no storage:
// reloading restores the Markdown defaults) and derives an accessible name
// from each item's own text without wrapping inline links in a <label>.

export function initTaskLists() {
  const checkboxes = document.querySelectorAll(
    'main li > input[type="checkbox"][disabled], main li > p:first-child > input[type="checkbox"][disabled]',
  );
  if (!checkboxes.length) return;

  for (const cb of checkboxes) {
    cb.disabled = false;
    if (!cb.hasAttribute('aria-label') && !cb.hasAttribute('aria-labelledby')) {
      const li = cb.closest('li');
      if (li) {
        const clone = li.cloneNode(true);
        for (const sub of clone.querySelectorAll('ul, ol, input')) sub.remove();
        const label = (clone.textContent || '').replace(/\s+/g, ' ').trim();
        if (label) cb.setAttribute('aria-label', label.slice(0, 120));
      }
    }
  }
}
