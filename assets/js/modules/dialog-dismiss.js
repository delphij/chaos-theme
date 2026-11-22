// Copyright 2026 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Fallback light-dismiss on backdrop click for browsers lacking native
// <dialog closedby="any"> (e.g. Safari). Requires both pointerdown and
// pointerup outside the dialog box so drag gestures ending on the backdrop
// do not accidentally close it.

export function addLightDismissFallback(dialog) {
  if (!dialog || 'closedBy' in HTMLDialogElement.prototype) return;
  const outside = (e) => {
    const r = dialog.getBoundingClientRect();
    return e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom;
  };
  let pressedOutside = false;
  dialog.addEventListener('pointerdown', (e) => {
    pressedOutside = outside(e);
  });
  dialog.addEventListener('pointerup', (e) => {
    if (pressedOutside && outside(e)) {
      dialog.close();
    }
    pressedOutside = false;
  });
}
