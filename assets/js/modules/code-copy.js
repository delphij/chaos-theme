// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// The copy button on highlighted code blocks. Extracted from main.js.

const ICONS = {
  copy: '<svg class="code-copy-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>',
  copied: '<svg class="code-copy-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>',
  failed: '<svg class="code-copy-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>'
};

// Code block copy to clipboard
export function initCodeCopy() {
  // Localised strings, from <body>'s data-* attributes (see baseof.html).
  const {
    copyLabel = 'Copy',
    copiedLabel = 'Copied!',
    copyFailedLabel = 'Copy failed'
  } = document.body.dataset;

  const LABELS = { copy: copyLabel, copied: copiedLabel, failed: copyFailedLabel };

  // state is one of 'copy', 'copied', 'failed'.
  function setButtonState(btn, state) {
    const label = LABELS[state];
    btn.classList.toggle('copied', state === 'copied');
    btn.classList.toggle('failed', state === 'failed');
    btn.setAttribute('aria-label', label);
    btn.innerHTML = `${ICONS[state]}<span class="code-copy-text">${label}</span>`;
  }

  document.querySelectorAll('.highlight').forEach(block => {
    if (block.querySelector('.code-copy-btn')) return;

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'code-copy-btn';
    setButtonState(btn, 'copy');

    btn.addEventListener('click', async () => {
      const codeTd = block.querySelector('.lntable .lntd:last-child pre, .lntable .lntd:last-child code');
      const codeElement = codeTd || block.querySelector('code') || block.querySelector('pre');
      const text = (codeElement ? codeElement.textContent : block.textContent) || '';

      // navigator.clipboard alone: document.execCommand is deprecated, and
      // the fallback that used it was the theme's only reason to keep a
      // second copy implementation. Outside a secure context clipboard is
      // undefined and the property access throws, which this catches along
      // with a rejected write -- so a copy that cannot happen now says so
      // instead of doing nothing.
      try {
        await navigator.clipboard.writeText(text);
        setButtonState(btn, 'copied');
      } catch {
        setButtonState(btn, 'failed');
      }
      setTimeout(() => setButtonState(btn, 'copy'), 2000);
    });

    block.appendChild(btn);
  });
}
