// Copyright 2026 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Section-link copy anchors on article headings.

import { copyWithFeedback } from './clipboard.js';

const setTitle = (el, label) => { el.title = label; };

export function initHeadingCopy() {
  const article = document.querySelector('article.post');
  const { headingLinkLabel } = document.body.dataset;
  if (!article || !headingLinkLabel) return;

  let decorated = false;
  article.querySelectorAll(':is(h2, h3, h4, h5, h6)[id]').forEach((heading, idx) => {
    if (heading.closest('#remark42, .footnotes')) return;
    decorated = true;

    // Wrap the heading's own content and point aria-labelledby at it so
    // heading navigation (the H key in screen readers) reads the title alone,
    // without appending the trailing anchor's label to every heading.
    const labelId = `heading-label-${idx}`;
    const span = document.createElement('span');
    span.id = labelId;
    span.append(...heading.childNodes);

    const anchor = document.createElement('a');
    anchor.className = 'heading-anchor';
    anchor.href = `#${heading.id}`;
    anchor.title = headingLinkLabel;
    anchor.setAttribute('aria-label', headingLinkLabel);
    anchor.setAttribute('aria-describedby', labelId);

    heading.setAttribute('aria-labelledby', labelId);
    heading.append(span, anchor);
  });

  if (!decorated) return;

  article.addEventListener('click', async e => {
    const anchor = e.target.closest('.heading-anchor');
    if (!anchor || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    const hash = anchor.getAttribute('href');
    const url = new URL(hash, window.location.href);
    try {
      window.history.replaceState(null, '', url);
    } catch {
      // Ignore if rate-limited by the UA.
    }
    if (!await copyWithFeedback(url.href, anchor, headingLinkLabel, setTitle)) {
      window.location.hash = hash;
    }
  });
}
