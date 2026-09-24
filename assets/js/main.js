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

initTheme();
initOverlays();
initScrollSpy();
initPrintFootnotes();
initCodeCopy();
