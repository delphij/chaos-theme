// Copyright 2026 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Appends post counts to article-footer tag links (`.post-tags[data-tag-counts-src]`)
// from the versioned tag-counts JSON (`/_data/v1/tag-counts.json`). Keeping counts
// out of static article HTML prevents publishing one post from changing every
// older post sharing its tags. Tags with count === 1 are omitted from the JSON
// and default to 1 here.

export function initTagCounts() {
  const container = document.querySelector('.post-tags[data-tag-counts-src]');
  const src = container?.dataset.tagCountsSrc;
  if (!container || !src) return;

  const links = container.querySelectorAll('a.tag-link');
  if (links.length === 0) return;

  const load = () => {
    fetch(src, { priority: 'low' })
      .then(res => (res.ok ? res.json() : null))
      .then(data => {
        const counts = data?.counts;
        if (!counts || typeof counts !== 'object') return;
        for (const a of links) {
          const name = a.textContent.trim().replace(/^#/, '');
          if (!name) continue;
          a.dataset.count = Object.hasOwn(counts, name) ? counts[name] : 1;
        }
      })
      .catch(() => {
        // Leave tag links without counts on network or parse failure.
      });
  };

  if (typeof requestIdleCallback === 'function') {
    requestIdleCallback(load, { timeout: 2000 });
  } else {
    setTimeout(load, 200);
  }
}
