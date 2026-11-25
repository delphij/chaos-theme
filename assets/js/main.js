// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Entry point. Each feature lives in its own module under modules/ and
// exposes a single init; this file is only the wiring, so what the theme
// runs on a page can be read in one screen.
//
// Bundled by js.Build (esbuild, built into Hugo) via _partials/foot/script.html,
// which also fixes the syntax floor. No Node toolchain is involved: `hugo`
// alone builds the theme.

import { initTheme } from './modules/theme.js';
import { initOverlays } from './modules/overlay.js';
import { initScrollSpy } from './modules/scrollspy.js';
import { initPrintFootnotes } from './modules/print-footnotes.js';
import { initCodeCopy } from './modules/code-copy.js';
import { initHeadingCopy } from './modules/heading-copy.js';
import { initBilingualSelect } from './modules/bilingual-select.js';
import { initLightbox } from './modules/lightbox.js';
import { initTaskLists } from './modules/task-list.js';
import { initSidebar } from './modules/sidebar.js';
import { initTagCounts } from './modules/tag-counts.js';

initTheme();
initOverlays();
initScrollSpy();
initPrintFootnotes();
initCodeCopy();
initHeadingCopy();
initBilingualSelect();
initLightbox();
initTaskLists();
initSidebar();
initTagCounts();
