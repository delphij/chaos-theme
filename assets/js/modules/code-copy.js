// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// The copy button on highlighted code blocks. Extracted from main.js.

// Code block copy to clipboard
export function initCodeCopy() {
  const copyLabel = window.i18n?.copyCode || 'Copy';
  const copiedLabel = window.i18n?.copiedCode || 'Copied!';
  const copyIconSvg = '<svg class="code-copy-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
  const checkIconSvg = '<svg class="code-copy-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>';

  function setButtonState(btn, isCopied) {
    btn.classList.toggle('copied', isCopied);
    const label = isCopied ? copiedLabel : copyLabel;
    const icon = isCopied ? checkIconSvg : copyIconSvg;
    btn.setAttribute('aria-label', label);
    btn.innerHTML = `${icon}<span class="code-copy-text">${label}</span>`;
  }

  document.querySelectorAll('.highlight').forEach(block => {
    if (block.querySelector('.code-copy-btn')) return;

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'code-copy-btn';
    setButtonState(btn, false);

    btn.addEventListener('click', () => {
      const codeTd = block.querySelector('.lntable .lntd:last-child pre, .lntable .lntd:last-child code');
      const codeElement = codeTd || block.querySelector('code') || block.querySelector('pre');
      const text = (codeElement ? codeElement.textContent : block.textContent) || '';

      const onSuccess = () => {
        setButtonState(btn, true);
        setTimeout(() => setButtonState(btn, false), 2000);
      };

      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(onSuccess).catch(() => fallbackCopy(text, onSuccess));
      } else {
        fallbackCopy(text, onSuccess);
      }
    });

    block.appendChild(btn);
  });

  function fallbackCopy(text, onSuccess) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.top = '0';
    ta.style.left = '0';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try {
      if (document.execCommand('copy')) {
        onSuccess();
      }
    } catch {
      // Silently fail
    }
    document.body.removeChild(ta);
  }
}
