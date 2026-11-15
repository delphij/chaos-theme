// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Event names shared between bundles. A module of its own, with nothing else
// in it, so that mermaid.js and code-vars.js can import a name without pulling
// in theme.js or code-copy.js.

// Fired on document whenever the effective theme is (re)applied, with
// { mode, theme } in detail.
export const THEME_CHANGE_EVENT = 'chaos:themechange';

// Fired on document whenever code-vars.js updates interactive parameter text
// inside code blocks, which may change whether a code <pre> overflows.
export const CODE_VARS_CHANGE_EVENT = 'chaos:codevarschange';
