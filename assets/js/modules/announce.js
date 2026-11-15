// Copyright 2026 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Polite screen-reader announcements through #theme-announcement (baseof.html).
//
// A modal <dialog> needs its own live region inside the dialog, since
// showModal() makes #theme-announcement inert and assistive technologies stop
// reporting changes in an inert region; search.js keeps a copy of this helper
// bound to #searchStatus (search.js also runs as a classic script under
// tools/search_harness.mjs and cannot import ES modules).
//
// A live region must already be in the accessibility tree when its text
// changes; a node inserted with its text in place is often not read at all
// (VoiceOver, NVDA with Firefox). That is why #theme-announcement is written
// into baseof.html empty, and why callers announce through here rather than
// give role="status" to markup they are about to insert.

const region = document.getElementById('theme-announcement');
let timer = null;

// The gap between clearing the region and writing it. Long enough that the
// empty state is seen as a change of its own; short enough not to be noticed.
// A timer rather than requestAnimationFrame, which does not run while the
// page produces no frames (a background tab, headless Chrome) and so could
// hold an announcement back indefinitely.
const ANNOUNCE_DELAY = 100;

export function announce(message) {
  if (!region || !message) return;
  clearTimeout(timer);
  // Clear first and write a moment later, so repeating the same message
  // (copying twice) is still a change that assistive technologies report.
  region.textContent = '';
  timer = setTimeout(() => {
    region.textContent = message;
  }, ANNOUNCE_DELAY);
}
