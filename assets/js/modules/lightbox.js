// Copyright 2026 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.

import { addLightDismissFallback } from './dialog-dismiss.js';

/**
 * Progressive-enhancement lightbox for article images (`a[data-lightbox]`).
 * Left-clicking an image opens a native `<dialog>` overlay supporting wheel /
 * pinch zoom anchored at the pointer, drag-to-pan when zoomed, double-click
 * zoom toggle, keyboard zoom (+ / - / 0), Esc / backdrop dismiss, and a
 * direct original-file link. Middle-click, modifier-click, and no-JS
 * environments retain the plain `<a href>`.
 */
export function initLightbox() {
  const triggers = document.querySelectorAll('a[data-lightbox]');
  if (!triggers.length || typeof HTMLDialogElement === 'undefined') return;

  const MIN_SCALE = 1;
  const MAX_SCALE = 8;
  const ds = document.body.dataset;
  const labels = {
    preview: ds.lightboxPreview || 'Image preview',
    zoomIn: ds.lightboxZoomIn || 'Zoom in',
    zoomOut: ds.lightboxZoomOut || 'Zoom out',
    reset: ds.lightboxReset || 'Reset zoom',
    open: ds.lightboxOpen || 'Open original',
    close: ds.lightboxClose || 'Close',
  };

  let dialog = null;
  let stage = null;
  let imgEl = null;
  let captionEl = null;
  let zoomResetBtn = null;
  let openLink = null;

  let scale = 1;
  let baseW = 0;
  let baseH = 0;
  let tx = 0;
  let ty = 0;
  let dragging = false;
  let dragged = false;
  let startX = 0;
  let startY = 0;
  let startTx = 0;
  let startTy = 0;

  const clampPan = () => {
    if (scale <= 1) {
      tx = 0;
      ty = 0;
      return;
    }
    const maxX = Math.max(0, (baseW * scale - stage.clientWidth) / 2);
    const maxY = Math.max(0, (baseH * scale - stage.clientHeight) / 2);
    tx = Math.min(maxX, Math.max(-maxX, tx));
    ty = Math.min(maxY, Math.max(-maxY, ty));
  };

  const applyTransform = () => {
    clampPan();
    if (scale <= 1) {
      imgEl.style.maxWidth = '';
      imgEl.style.maxHeight = '';
      imgEl.style.width = '';
      imgEl.style.height = '';
      imgEl.style.transform = '';
    } else {
      // Resize layout dimensions rather than CSS scale() so browsers
      // re-rasterize SVG vectors sharply at the zoomed resolution.
      imgEl.style.maxWidth = 'none';
      imgEl.style.maxHeight = 'none';
      imgEl.style.width = `${baseW * scale}px`;
      imgEl.style.height = `${baseH * scale}px`;
      imgEl.style.transform = `translate(${tx}px, ${ty}px)`;
    }
    stage.classList.toggle('is-zoomed', scale > 1);
    zoomResetBtn.textContent = `${Math.round(scale * 100)}%`;
  };

  const resetZoom = () => {
    scale = 1;
    baseW = 0;
    baseH = 0;
    tx = 0;
    ty = 0;
    applyTransform();
  };

  const zoomTo = (nextScale, clientX, clientY) => {
    const clamped = Math.min(MAX_SCALE, Math.max(MIN_SCALE, nextScale));
    if (clamped === scale) return;
    if (clamped <= 1) {
      resetZoom();
      return;
    }
    if (scale === 1) {
      baseW = imgEl.offsetWidth;
      baseH = imgEl.offsetHeight;
      if (!baseW || !baseH) return;
    }
    if (typeof clientX === 'number' && typeof clientY === 'number') {
      const rect = stage.getBoundingClientRect();
      const px = clientX - (rect.left + rect.width / 2);
      const py = clientY - (rect.top + rect.height / 2);
      const ratio = clamped / scale;
      tx = px - (px - tx) * ratio;
      ty = py - (py - ty) * ratio;
    } else {
      const ratio = clamped / scale;
      tx *= ratio;
      ty *= ratio;
    }
    scale = clamped;
    applyTransform();
  };

  const makeBtn = (text, label, onClick, extraClass = '') => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = extraClass
      ? `image-lightbox-btn ${extraClass}`
      : 'image-lightbox-btn';
    btn.textContent = text;
    btn.title = label;
    btn.setAttribute('aria-label', label);
    btn.addEventListener('click', onClick);
    return btn;
  };

  const ensureDialog = () => {
    if (dialog) return dialog;
    dialog = document.createElement('dialog');
    dialog.className = 'image-lightbox';
    dialog.setAttribute('closedby', 'any');
    dialog.setAttribute('aria-label', labels.preview);

    const toolbar = document.createElement('div');
    toolbar.className = 'image-lightbox-bar';

    captionEl = document.createElement('span');
    captionEl.className = 'image-lightbox-caption';

    const actions = document.createElement('div');
    actions.className = 'image-lightbox-actions';

    const zoomOutBtn = makeBtn('−', labels.zoomOut, () => zoomTo(scale / 1.35));
    zoomResetBtn = makeBtn('100%', labels.reset, resetZoom, 'image-lightbox-zoom');
    const zoomInBtn = makeBtn('+', labels.zoomIn, () => zoomTo(scale * 1.35));

    openLink = document.createElement('a');
    openLink.className = 'image-lightbox-btn';
    openLink.target = '_blank';
    openLink.rel = 'noopener';
    openLink.textContent = '↗';
    openLink.title = labels.open;
    openLink.setAttribute('aria-label', labels.open);

    const closeBtn = makeBtn('×', labels.close, () => dialog.close());

    actions.append(zoomOutBtn, zoomResetBtn, zoomInBtn, openLink, closeBtn);
    toolbar.append(captionEl, actions);

    stage = document.createElement('div');
    stage.className = 'image-lightbox-stage';

    imgEl = document.createElement('img');
    imgEl.className = 'image-lightbox-img';
    imgEl.draggable = false;
    stage.append(imgEl);

    dialog.append(toolbar, stage);

    // Wheel / trackpad pinch zoom anchored at the cursor.
    dialog.addEventListener(
      'wheel',
      (e) => {
        e.preventDefault();
        const factor = Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0025));
        zoomTo(scale * factor, e.clientX, e.clientY);
      },
      { passive: false }
    );

    // Double-click toggles between 1x and 2.5x at the clicked point.
    imgEl.addEventListener('dblclick', (e) => {
      e.preventDefault();
      if (scale > 1.05) {
        resetZoom();
      } else {
        zoomTo(2.5, e.clientX, e.clientY);
      }
    });

    // Pointer drag to pan when zoomed in.
    stage.addEventListener('pointerdown', (e) => {
      if (e.button !== 0 || scale <= 1) return;
      dragging = true;
      dragged = false;
      startX = e.clientX;
      startY = e.clientY;
      startTx = tx;
      startTy = ty;
      stage.setPointerCapture(e.pointerId);
      stage.classList.add('is-dragging');
      e.preventDefault();
    });

    stage.addEventListener('pointermove', (e) => {
      if (!dragging) return;
      const dx = e.clientX - startX;
      const dy = e.clientY - startY;
      if (Math.hypot(dx, dy) > 3) dragged = true;
      tx = startTx + dx;
      ty = startTy + dy;
      applyTransform();
    });

    const endDrag = () => {
      if (!dragging) return;
      dragging = false;
      stage.classList.remove('is-dragging');
    };
    stage.addEventListener('pointerup', endDrag);
    stage.addEventListener('pointercancel', endDrag);

    // Keyboard zoom shortcuts while open.
    dialog.addEventListener('keydown', (e) => {
      if (e.key === '+' || e.key === '=') {
        e.preventDefault();
        zoomTo(scale * 1.35);
      } else if (e.key === '-' || e.key === '_') {
        e.preventDefault();
        zoomTo(scale / 1.35);
      } else if (e.key === '0') {
        e.preventDefault();
        resetZoom();
      }
    });

    // Dismiss on empty stage click, unless finishing a pan drag.
    stage.addEventListener('click', (e) => {
      if (dragged) {
        dragged = false;
        return;
      }
      if (e.target === stage) {
        dialog.close();
      }
    });

    addLightDismissFallback(dialog);

    dialog.addEventListener('close', resetZoom);

    window.addEventListener('resize', () => {
      if (dialog?.open && scale > 1) {
        applyTransform();
      }
    });

    document.body.append(dialog);
    return dialog;
  };

  document.addEventListener('click', (e) => {
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) {
      return;
    }
    const target = e.target instanceof Element ? e.target : null;
    const link = target?.closest('a[data-lightbox]');
    if (!link) return;
    const thumb = link.querySelector('img');
    if (!thumb) return;

    e.preventDefault();
    const dlg = ensureDialog();
    imgEl.src = link.href;
    imgEl.alt = thumb.alt || '';
    imgEl.classList.toggle('svg-adapt', thumb.classList.contains('svg-adapt'));
    captionEl.textContent = thumb.alt || '';
    openLink.href = link.href;
    resetZoom();
    dlg.showModal();
  });
}
