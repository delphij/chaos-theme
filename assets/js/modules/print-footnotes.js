// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Turns an article's external links into numbered footnotes while printing,
// and puts the page back afterwards. Extracted from main.js.

// Cached DOM references for performance
const printReferences = document.getElementById('print-references');
const articlePost = document.querySelector('article.post');

export function initPrintFootnotes() {
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
    heading.textContent = printReferences.dataset.heading || 'References';

    const list = document.createElement('ol');
    const items = footnotes.map(({ url, refId, noteId }) => {
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
}
