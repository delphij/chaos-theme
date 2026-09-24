// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Event names shared between bundles. A module of its own, with nothing else
// in it, so that mermaid.js can import a name without pulling in theme.js.

// Fired on document whenever the effective theme is (re)applied, with
// { mode, theme } in detail.
export const THEME_CHANGE_EVENT = 'chaos:themechange';
