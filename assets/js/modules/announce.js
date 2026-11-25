// Copyright 2026 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Polite screen-reader announcements via an existing aria-live region.
//
// A live region must already be in the accessibility tree when its text
// changes; a node inserted with its text in place is often not read at all
// (VoiceOver, NVDA with Firefox). That is why #theme-announcement (baseof.html)
// and #searchStatus (search.html, inside the modal <dialog> because showModal()
// makes #theme-announcement inert) are written into the markup empty.

// The gap between clearing the region and writing it. Long enough that the
// empty state is seen as a change of its own; short enough not to be noticed.
// A timer rather than requestAnimationFrame, which does not run while the
// page produces no frames (a background tab, headless Chrome) and so could
// hold an announcement back indefinitely.
const ANNOUNCE_DELAY = 100;

export function createAnnouncer(region) {
  let timer = null;
  let lastKey = '';

  function announce(message, dedupeKey) {
    if (!region || !message) return;
    if (dedupeKey !== undefined) {
      if (dedupeKey === lastKey) return;
      lastKey = dedupeKey;
    }
    clearTimeout(timer);
    // Clear first and write a moment later, so repeating the same message
    // (copying twice, or a new query with the same result count) is still a
    // change that assistive technologies report.
    region.textContent = '';
    timer = setTimeout(() => {
      region.textContent = message;
    }, ANNOUNCE_DELAY);
  }

  function reset() {
    lastKey = '';
    if (!region) return;
    clearTimeout(timer);
    region.textContent = '';
  }

  return { announce, reset };
}

const pageAnnouncer = createAnnouncer(document.getElementById('theme-announcement'));

export function announce(message) {
  pageAnnouncer.announce(message);
}
