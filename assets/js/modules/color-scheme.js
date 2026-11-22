// Copyright 2026 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Shared helper for resolving whether the active page color scheme is dark,
// reading <meta name="color-scheme"> ("dark" | "light" | "light dark") and
// falling back to the OS preference when set to "light dark".

export const systemDark = window.matchMedia('(prefers-color-scheme: dark)');

export function isDarkScheme() {
  const scheme = document.querySelector('meta[name="color-scheme"]')?.content;
  return scheme === 'dark' || (scheme !== 'light' && systemDark.matches);
}
