// Copyright 2026 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.

/**
 * Lock text selection to a single language column (`dt` or `dd`) when a
 * pointer drag starts inside a `dl.bilingual` cell, preventing browsers from
 * interleaving left and right columns in DOM order. Starting a selection
 * outside `dl.bilingual`, holding Alt/Option, or pressing Ctrl/Cmd+A clears
 * the lock so both languages can be selected together.
 */
export function initBilingualSelect() {
  const lists = document.querySelectorAll('dl.bilingual');
  if (!lists.length) return;

  const setCol = (col) => {
    for (const dl of lists) {
      if (col) {
        dl.dataset.selectCol = col;
      } else {
        delete dl.dataset.selectCol;
      }
    }
  };

  document.addEventListener('pointerdown', (e) => {
    if (e.button !== 0) return;
    if (e.altKey) {
      setCol('');
      return;
    }
    const target = e.target instanceof Element ? e.target : null;
    const cell = target?.closest('dl.bilingual > dt, dl.bilingual > dd');
    // Stacked (narrow viewport) lists read in DOM order, so a selection
    // there cannot interleave the columns; locking would only get in the way.
    const sideBySide =
      cell && getComputedStyle(cell.parentElement).display === 'grid';
    setCol(sideBySide ? cell.tagName.toLowerCase() : '');
  });

  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'a') {
      setCol('');
    }
  });
}
