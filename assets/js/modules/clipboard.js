// Copyright 2026 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Shared clipboard write and transient visual/spoken feedback for copy
// controls (modules/code-copy.js and modules/heading-copy.js).

import { announce } from './announce.js';

const { copiedLabel, copyFailedLabel } = document.body.dataset;
const timers = new WeakMap();

// Writes text to the clipboard, marks el with .copied or .failed for 2 s,
// announces the outcome to screen readers, and calls applyLabel(el, label)
// with the localised status string before restoring idleLabel.
//
// navigator.clipboard alone: document.execCommand is deprecated, and outside
// a secure context navigator.clipboard is undefined so the property access
// throws -- caught here alongside a rejected write so a copy that cannot
// happen says so instead of doing nothing.
export async function copyWithFeedback(text, el, idleLabel, applyLabel) {
  let ok = false;
  try {
    await navigator.clipboard.writeText(text);
    ok = true;
  } catch {
    // Reported below through the failed state and announcement.
  }
  const label = ok ? copiedLabel : copyFailedLabel;
  el.classList.toggle('copied', ok);
  el.classList.toggle('failed', !ok);
  applyLabel(el, label);
  announce(label);
  clearTimeout(timers.get(el));
  timers.set(el, setTimeout(() => {
    el.classList.remove('copied', 'failed');
    applyLabel(el, idleLabel);
  }, 2000));
  return ok;
}
