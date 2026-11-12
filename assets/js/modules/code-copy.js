// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// The copy button on highlighted code blocks. Extracted from main.js.

// Code block copy to clipboard
export function initCodeCopy() {
  // Localised strings, from <body>'s data-* attributes (see baseof.html).
  const { copyLabel, copiedLabel, copyFailedLabel } = document.body.dataset;

  const LABELS = { copy: copyLabel, copied: copiedLabel, failed: copyFailedLabel };

  // state is one of 'copy', 'copied', 'failed'. The icon is drawn by CSS
  // (.code-copy-btn::before) from the state class, so only the words change.
  function setButtonState(btn, state) {
    const label = LABELS[state];
    btn.classList.toggle('copied', state === 'copied');
    btn.classList.toggle('failed', state === 'failed');
    btn.setAttribute('aria-label', label);
    btn.textContent = label;
  }

  document.querySelectorAll('.highlight').forEach(block => {
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
