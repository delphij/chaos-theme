// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Keyboard scrollability and the copy button on highlighted code blocks.

import { copyWithFeedback } from './clipboard.js';
import { CODE_VARS_CHANGE_EVENT } from './events.js';

const setText = (el, label) => { el.textContent = label; };

export function initCodeCopy() {
  const blocks = document.querySelectorAll('.highlight');
  if (!blocks.length) return;

  const { copyLabel } = document.body.dataset;

  // A code <pre> is a horizontal scroller, and one that actually overflows
  // must be reachable from the keyboard so its hidden columns can be
  // scrolled into view (WCAG 2.1.1). Chrome 130+ and Firefox make such a
  // scroller focusable by themselves, Safari does not, so the tabindex="0"
  // Chroma writes is what lets a Safari keyboard user read a long line.
  //
  // A block whose lines all fit has nothing to scroll, and there the
  // tabindex is only an empty Tab stop in front of the copy button, so it is
  // set or removed by whether the <pre> overflows right now. That changes
  // with the viewport (a phone overflows where a desktop does not, and the
  // line-number column is hidden below 769px), when the block first becomes
  // visible (a <pre> inside a closed <details> measures 0 by 0), when the web
  // fonts arrive, and when interactive code_vars parameters change line width;
  // the ResizeObserver covers the first two, document.fonts.ready and
  // CODE_VARS_CHANGE_EVENT the rest. render-codeblock.html leaves the
  // attribute in the HTML, so without JavaScript every code block keeps it: an
  // extra Tab stop is the cheaper failure.
  //
  // A <pre> that holds focus when it stops overflowing (the window was
  // widened) keeps its tabindex until focus leaves it: removing it at once
  // would drop focus to <body>, and moving focus elsewhere would have a
  // screen reader announce a control the reader never chose. syncOnBlur is
  // one shared function, so however often this runs while the <pre> is
  // focused the listener is registered once (addEventListener ignores a
  // listener it already has). xml-xsl-feed.js applies the same rule to the
  // feed preview.
  const scrollers = [];
  const syncOnBlur = e => syncTabStop(e.currentTarget);
  const syncTabStop = pre => {
    if (pre.scrollWidth > pre.clientWidth) {
      pre.tabIndex = 0;
    } else if (document.activeElement === pre) {
      pre.addEventListener('blur', syncOnBlur, { once: true });
    } else {
      pre.removeAttribute('tabindex');
    }
  };
  const resizeObserver = new ResizeObserver(entries => {
    entries.forEach(entry => syncTabStop(entry.target));
  });

  blocks.forEach(block => {
    // With line numbers, Chroma writes two <pre>s into a layout table and
    // only the code column's scrolls; the line-number <pre> beside it never
    // does. render-codeblock.html already took that one's tabindex away, but
    // a block highlighted outside the hook ({{< highlight >}}) still has it,
    // so every <pre> but the scroller loses it here.
    const scroller = block.querySelector('.lntable .lntd:last-child pre') || block.querySelector('pre');
    block.querySelectorAll('pre[tabindex]').forEach(pre => {
      if (pre !== scroller) pre.removeAttribute('tabindex');
    });
    if (scroller) {
      scrollers.push(scroller);
      resizeObserver.observe(scroller);
    }

    const code = scroller || block.querySelector('code');
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'code-copy-btn';
    btn.textContent = copyLabel;
    btn.addEventListener('click', () => {
      copyWithFeedback(code?.textContent ?? '', btn, copyLabel, setText);
    });
    block.append(btn);
  });

  // A font swap or an interactive code_vars edit changes how wide the lines
  // are without changing the <pre>'s own border box, so the ResizeObserver
  // does not see it; re-measure after both.
  if (scrollers.length > 0) {
    const syncAll = () => scrollers.forEach(syncTabStop);
    document.fonts.ready.then(syncAll);
    document.addEventListener(CODE_VARS_CHANGE_EVENT, syncAll);
  }
}
