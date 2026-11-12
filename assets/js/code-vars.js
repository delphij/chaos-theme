// Copyright 2026 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Interactive code parameters (layouts/_partials/code-vars.html).
//
// Its own entry point rather than part of main.js: code-vars.html loads it
// only on pages that declare `code_vars` in front matter, so articles without
// interactive parameters pay zero bytes for it.
//
// Variables are rendered inside a hidden `<aside class="code-vars-panel">`.
// When at least one `.highlight` code block matches, this script moves the
// panel above the first matching code block, un-hides it, wraps matched
// literals into `<var class="code-var">`, synchronizes edits across the page,
// and persists committed changes to the URL query string.

const IDENT_CHAR = /[A-Za-z0-9_]/;
const BOUNDARY_CHAR = /[A-Za-z0-9_-]/;
const DIGIT_CHAR = /[0-9]/;

const EDIT_ICON = '<svg class="code-var-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"></path></svg>';

const PLAINTEXT_EDITABLE = (() => {
  const probe = document.createElement('var');
  probe.setAttribute('contenteditable', 'plaintext-only');
  return probe.contentEditable === 'plaintext-only' ? 'plaintext-only' : 'true';
})();

/**
 * Expand variable definitions into concrete search patterns, including
 * regex-escaped dot (`\.`) and pipe-delimited alternation (`a|b|c`) variants.
 */
function buildPatterns(defs) {
  const patterns = [];
  const seen = new Set();
  const add = (match, def, transform) => {
    if (match && !seen.has(match)) {
      seen.add(match);
      patterns.push({ match, def, transform });
    }
  };

  for (const def of defs) {
    const val = def.defaultValue;
    add(val, def, 'none');
    if (val.includes('.') && !val.includes('\\.')) {
      add(val.replace(/\./g, '\\.'), def, 'escape-dot');
    }
    if (/^\S+(?:\s+\S+)+$/.test(val)) {
      add(val.trim().split(/\s+/).join('|'), def, 'space-to-pipe');
    }
  }

  return patterns.sort((a, b) => b.match.length - a.match.length);
}

/**
 * Check token boundaries so `dhcpd-key` does not match inside `my-dhcpd-key`
 * and `192.0.2.1` does not match inside `192.0.2.10`.
 */
function hasValidBoundaries(text, start, end, matchStr) {
  const firstChar = matchStr[0];
  const lastChar = matchStr[matchStr.length - 1];
  const prevChar = start > 0 ? text[start - 1] : '';
  const nextChar = end < text.length ? text[end] : '';

  if (IDENT_CHAR.test(firstChar) && prevChar && BOUNDARY_CHAR.test(prevChar)) {
    return false;
  }
  if (IDENT_CHAR.test(lastChar) && nextChar && BOUNDARY_CHAR.test(nextChar)) {
    return false;
  }
  if (DIGIT_CHAR.test(firstChar) && prevChar === '.' && start >= 2 && DIGIT_CHAR.test(text[start - 2])) {
    return false;
  }
  if (DIGIT_CHAR.test(lastChar) && nextChar === '.' && end + 1 < text.length && DIGIT_CHAR.test(text[end + 1])) {
    return false;
  }
  return true;
}

/**
 * Find all non-overlapping matches of `patterns` in `text`.
 */
function findMatches(text, patterns) {
  if (!text || !patterns.length) return [];
  const candidates = [];

  for (let pIdx = 0; pIdx < patterns.length; pIdx++) {
    const p = patterns[pIdx];
    const needle = p.match;
    let pos = 0;
    while (pos <= text.length - needle.length) {
      const idx = text.indexOf(needle, pos);
      if (idx === -1) break;
      const end = idx + needle.length;
      if (hasValidBoundaries(text, idx, end, needle)) {
        candidates.push({
          start: idx,
          end,
          length: needle.length,
          priority: pIdx,
          pattern: p
        });
      }
      pos = idx + 1;
    }
  }

  if (!candidates.length) return [];

  candidates.sort((a, b) => b.length - a.length || a.start - b.start || a.priority - b.priority);

  const accepted = [];
  for (const c of candidates) {
    if (!accepted.some((a) => c.start < a.end && c.end > a.start)) {
      accepted.push(c);
    }
  }

  return accepted.sort((a, b) => a.start - b.start);
}

/**
 * Wrap matched variable occurrences inside `root` in `<var class="code-var">`.
 */
function decorateContainer(root, patterns, editableInPlace) {
  const walker = document.createTreeWalker(
    root,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode(node) {
        const parent = node.parentElement;
        return (!parent || parent.closest('var.code-var, a'))
          ? NodeFilter.FILTER_REJECT
          : NodeFilter.FILTER_ACCEPT;
      }
    }
  );

  const segments = [];
  let fullText = '';
  let current;
  while ((current = walker.nextNode())) {
    const val = current.nodeValue || '';
    if (!val) continue;
    const start = fullText.length;
    fullText += val;
    segments.push({ node: current, start, end: fullText.length });
  }

  const matches = findMatches(fullText, patterns);
  if (!matches.length) return 0;

  const findPosition = (offset, isEnd) => {
    for (const seg of segments) {
      if (isEnd ? (offset >= seg.start && offset <= seg.end) : (offset >= seg.start && offset < seg.end)) {
        return { node: seg.node, offset: offset - seg.start };
      }
    }
    const last = segments[segments.length - 1];
    return { node: last.node, offset: last.end - last.start };
  };

  for (let i = matches.length - 1; i >= 0; i--) {
    const m = matches[i];
    const { match, def, transform } = m.pattern;
    const startPos = findPosition(m.start, false);
    const endPos = findPosition(m.end, true);

    const range = document.createRange();
    range.setStart(startPos.node, startPos.offset);
    range.setEnd(endPos.node, endPos.offset);

    const varEl = document.createElement('var');
    varEl.className = 'code-var';
    varEl.setAttribute('translate', 'no');
    varEl.dataset.var = def.name;
    if (transform !== 'none') {
      varEl.dataset.transform = transform;
    }

    if (editableInPlace) {
      varEl.setAttribute('contenteditable', PLAINTEXT_EDITABLE);
      varEl.setAttribute('spellcheck', 'false');
      varEl.setAttribute('autocorrect', 'off');
      varEl.setAttribute('autocapitalize', 'off');
      varEl.setAttribute('role', 'textbox');
      varEl.setAttribute('aria-label', def.desc);
      varEl.setAttribute('tabindex', '-1');
    }

    varEl.textContent = match;

    range.deleteContents();
    range.insertNode(varEl);
  }

  return matches.length;
}

function toCanonical(rawText, transform) {
  const clean = (rawText || '').replace(/[\r\n]+/g, '');
  if (transform === 'escape-dot') return clean.replace(/\\\./g, '.');
  if (transform === 'space-to-pipe') return clean.replace(/\|+/g, ' ');
  return clean;
}

function fromCanonical(canonical, transform) {
  if (transform === 'escape-dot') return canonical.replace(/\\?\./g, '\\.');
  if (transform === 'space-to-pipe') return canonical.trim().split(/[\s|]+/).filter(Boolean).join('|');
  return canonical;
}

function initCodeVars() {
  const article = document.querySelector('article.post');
  const panel = article?.querySelector('.code-vars-panel');
  if (!panel) return;

  const inputEls = Array.from(panel.querySelectorAll('.code-vars-input'));
  if (!inputEls.length) return;

  const detailsEl = panel.querySelector('.code-vars-details');
  const urlNoticeEl = panel.querySelector('.code-vars-url-notice');
  const resetBtn = panel.querySelector('.code-vars-reset');
  const { modifiedBadge: modifiedBadgeText, linkBadge: linkBadgeText } = panel.dataset;

  const defs = [];
  const defsByName = new Map();

  for (const input of inputEls) {
    const name = input.name;
    const defaultValue = input.defaultValue;
    const desc = input.closest('.code-vars-field').querySelector('.code-vars-label').textContent;
    const def = {
      name,
      defaultValue,
      desc,
      modifiedTip: input.dataset.modifiedTip,
      currentValue: defaultValue,
      fromUrl: false,
      inputEl: input
    };
    defs.push(def);
    defsByName.set(name, def);
  }

  const patterns = buildPatterns(defs);
  if (!patterns.length) return;

  const editableInPlace = !window.matchMedia('(pointer: coarse)').matches;
  let totalCreated = 0;
  let firstDecoratedBlock = null;
  const decoratedBlocks = [];

  article.querySelectorAll('.highlight:not([code_vars="false"])').forEach((block) => {
    const code = block.querySelector('.lntable .lntd:last-child code') || block.querySelector('code');
    if (!code) return;
    const blockMatches = decorateContainer(code, patterns, editableInPlace);
    if (blockMatches > 0) {
      if (!firstDecoratedBlock) firstDecoratedBlock = block;
      totalCreated += blockMatches;

      const badge = document.createElement('button');
      badge.type = 'button';
      badge.className = 'code-vars-badge';
      badge.hidden = true;
      badge.addEventListener('click', () => {
        detailsEl.open = true;
        panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      });
      block.appendChild(badge);

      decoratedBlocks.push({
        vars: Array.from(block.querySelectorAll('var.code-var')),
        badge
      });
    }
  });

  if (!totalCreated) return;

  // Place the parameter panel right before the top-level block containing the
  // first matching code block (walking out of any <li> or <blockquote>) so the
  // article's opening prose reads uninterrupted, then reveal it.
  let anchor = firstDecoratedBlock;
  while (anchor.parentElement && anchor.parentElement !== article) {
    anchor = anchor.parentElement;
  }
  if (anchor.parentElement === article) {
    article.insertBefore(panel, anchor);
  }
  panel.hidden = false;

  // Inline code in the prose follows the values too, and is edited in place
  // like the code blocks (the handlers below are delegated on the article).
  // Headings keep their text, as the table of contents repeats it. An
  // article that discusses the literal values sets code_vars_inline: false.
  if (panel.dataset.inline !== 'false') {
    for (const code of article.querySelectorAll(':not(pre) > code')) {
      if (!code.closest('h1, h2, h3, h4, h5, h6')) decorateContainer(code, patterns, editableInPlace);
    }
  }

  const varElements = Array.from(article.querySelectorAll('var.code-var'));

  const tooltip = document.createElement('div');
  tooltip.className = 'code-var-tooltip';
  tooltip.setAttribute('role', 'tooltip');
  tooltip.hidden = true;
  tooltip.innerHTML = `${editableInPlace ? EDIT_ICON : ''}<span class="code-var-tooltip-text"></span>`;
  const tooltipText = tooltip.querySelector('.code-var-tooltip-text');
  document.body.appendChild(tooltip);

  let activeTooltipTarget = null;
  let valueBeforeFocus = null;

  function updateTooltipContent(el) {
    const def = defsByName.get(el.dataset.var);
    if (!def) return;
    tooltipText.textContent = def.currentValue !== def.defaultValue ? def.modifiedTip : def.desc;
  }

  function positionTooltip(el) {
    if (tooltip.hidden) return;
    const rect = el.getBoundingClientRect();
    const tipRect = tooltip.getBoundingClientRect();
    const pad = 8;

    let top = rect.top - tipRect.height - 6;
    if (top < pad) top = rect.bottom + 6;

    const left = Math.max(pad, Math.min(
      rect.left + (rect.width - tipRect.width) / 2,
      window.innerWidth - tipRect.width - pad
    ));

    tooltip.style.top = `${Math.round(top)}px`;
    tooltip.style.left = `${Math.round(left)}px`;
  }

  function showTooltip(el) {
    activeTooltipTarget = el;
    updateTooltipContent(el);
    tooltip.hidden = false;
    positionTooltip(el);
  }

  function hideTooltip(el) {
    if (el && activeTooltipTarget !== el) return;
    tooltip.hidden = true;
    activeTooltipTarget = null;
  }

  function setHoverGroup(varName, hovered) {
    for (const el of varElements) {
      if (el.dataset.var === varName) {
        el.classList.toggle('is-hovered', hovered);
      }
    }
  }

  function updateChromeState() {
    let anyModified = false;
    let anyFromUrl = false;

    for (const def of defs) {
      if (def.currentValue !== def.defaultValue) {
        anyModified = true;
        if (def.fromUrl) anyFromUrl = true;
      } else {
        def.fromUrl = false;
      }
    }

    resetBtn.hidden = !anyModified;
    urlNoticeEl.hidden = !anyFromUrl;

    for (const item of decoratedBlocks) {
      let blockModified = false;
      let blockFromUrl = false;
      for (const el of item.vars) {
        const def = defsByName.get(el.dataset.var);
        if (def && def.currentValue !== def.defaultValue) {
          blockModified = true;
          if (def.fromUrl) blockFromUrl = true;
        }
      }
      item.badge.hidden = !blockModified;
      item.badge.classList.toggle('is-from-url', blockModified && blockFromUrl);
      if (blockModified) {
        item.badge.textContent = blockFromUrl ? linkBadgeText : modifiedBadgeText;
      }
    }
  }

  // Only called when an edit is committed (focusout, Enter, Escape, Reset)
  // rather than on every keystroke, avoiding browser history.replaceState
  // rate limits (Safari caps replaceState at 100 calls per 30 seconds).
  function commitUrlState() {
    updateChromeState();
    const url = new URL(window.location.href);

    for (const def of defs) {
      if (def.currentValue !== def.defaultValue && def.currentValue !== '') {
        url.searchParams.set(def.name, def.currentValue);
      } else {
        url.searchParams.delete(def.name);
      }
    }

    if (url.search !== window.location.search) {
      try {
        window.history.replaceState(null, '', url);
      } catch {
        // Ignore if rate-limited by the UA.
      }
    }
  }

  function applyValue(varName, rawValue, sourceEl) {
    const def = defsByName.get(varName);
    if (!def) return;

    const effective = rawValue.trim() || def.defaultValue;
    def.currentValue = effective;
    const isModified = effective !== def.defaultValue;
    const isFromUrl = isModified && def.fromUrl;

    def.inputEl.classList.toggle('is-modified', isModified);
    def.inputEl.classList.toggle('is-from-url', isFromUrl);
    if (sourceEl !== def.inputEl && def.inputEl.value !== rawValue) {
      def.inputEl.value = effective;
    }

    for (const el of varElements) {
      if (el.dataset.var !== varName) continue;
      el.classList.toggle('is-modified', isModified);
      el.classList.toggle('is-from-url', isFromUrl);
      if (el !== sourceEl) {
        el.textContent = fromCanonical(effective, el.dataset.transform);
      }
    }

    if (activeTooltipTarget?.dataset.var === varName) {
      updateTooltipContent(activeTooltipTarget);
      positionTooltip(activeTooltipTarget);
    }

    updateChromeState();
  }

  // Hydrate initial values from the URL query string (?zone=...&primary=...).
  // When any parameter comes from the URL, open the panel and show the notice
  // so readers see that the commands below were customized by the link.
  const initialParams = new URLSearchParams(window.location.search);
  let loadedFromUrl = false;
  for (const def of defs) {
    const trimmed = initialParams.get(def.name)?.trim();
    if (trimmed && trimmed !== def.defaultValue) {
      def.fromUrl = true;
      loadedFromUrl = true;
      applyValue(def.name, trimmed, null);
    }
  }
  if (loadedFromUrl) {
    detailsEl.open = true;
  }

  function getEditable(node) {
    const el = node.closest('.code-vars-input, var.code-var');
    if (!el) return null;
    const isInput = el.tagName === 'INPUT';
    const def = defsByName.get(isInput ? el.name : el.dataset.var);
    return def ? { el, isInput, def } : null;
  }

  function readEditable(el, isInput) {
    return isInput ? el.value : toCanonical(el.textContent, el.dataset.transform);
  }

  function writeEditable(el, isInput, val) {
    if (isInput) {
      el.value = val;
    } else {
      el.textContent = fromCanonical(val, el.dataset.transform);
    }
  }

  resetBtn.addEventListener('click', () => {
    for (const def of defs) {
      def.fromUrl = false;
      def.inputEl.value = def.defaultValue;
      applyValue(def.name, def.defaultValue, null);
    }
    commitUrlState();
  });

  // Hover tooltips on in-place <var class="code-var"> elements
  article.addEventListener('mouseover', (e) => {
    const target = e.target.closest('var.code-var');
    if (!target) return;
    setHoverGroup(target.dataset.var, true);
    showTooltip(target);
  });

  article.addEventListener('mouseout', (e) => {
    const target = e.target.closest('var.code-var');
    if (!target) return;
    setHoverGroup(target.dataset.var, false);
    if (document.activeElement !== target) {
      hideTooltip(target);
    }
  });

  // Unified focus, input, and keyboard handling for both panel <input> fields
  // and in-place <var class="code-var"> elements
  article.addEventListener('focusin', (e) => {
    const target = getEditable(e.target);
    if (!target) return;
    valueBeforeFocus = target.def.currentValue;
    setHoverGroup(target.def.name, true);
    if (!target.isInput) showTooltip(target.el);
  });

  article.addEventListener('focusout', (e) => {
    const target = getEditable(e.target);
    if (!target) return;
    const { el, isInput, def } = target;
    setHoverGroup(def.name, false);

    const committed = readEditable(el, isInput).trim() || def.defaultValue;
    writeEditable(el, isInput, committed);
    if (!isInput) hideTooltip(el);
    applyValue(def.name, committed, el);
    commitUrlState();
    valueBeforeFocus = null;
  });

  article.addEventListener('beforeinput', (e) => {
    const target = e.target.closest('var.code-var');
    if (target && (e.inputType === 'insertParagraph' || e.inputType === 'insertLineBreak')) {
      e.preventDefault();
      target.blur();
    }
  });

  article.addEventListener('input', (e) => {
    const target = getEditable(e.target);
    if (!target) return;
    const { el, isInput, def } = target;
    def.fromUrl = false;
    applyValue(def.name, readEditable(el, isInput), el);
  });

  article.addEventListener('keydown', (e) => {
    const target = getEditable(e.target);
    if (!target) return;
    const { el, isInput, def } = target;
    if (e.key === 'Escape') {
      e.preventDefault();
      if (valueBeforeFocus !== null) {
        writeEditable(el, isInput, valueBeforeFocus);
        applyValue(def.name, valueBeforeFocus, el);
      }
      el.blur();
    } else if (e.key === 'Enter') {
      e.preventDefault();
      el.blur();
    }
  });

  article.addEventListener('paste', (e) => {
    const target = e.target.closest('var.code-var');
    if (target && PLAINTEXT_EDITABLE !== 'plaintext-only') {
      e.preventDefault();
      const text = (e.clipboardData?.getData('text/plain') || '').replace(/[\r\n]+/g, ' ');
      document.execCommand('insertText', false, text);
    }
  });

  window.addEventListener('scroll', () => {
    if (activeTooltipTarget) {
      positionTooltip(activeTooltipTarget);
    }
  }, { passive: true });
}

initCodeVars();
