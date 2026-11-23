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
  const activePointers = new Map();
  let pinching = false;
  let pinchStartDist = 0;
  let pinchStartScale = 1;
  let prevMidX = 0;
  let prevMidY = 0;
  let dragging = false;
  let dragged = false;
  let startX = 0;
  let startY = 0;
  let startTx = 0;
  let startTy = 0;
  let lastTapTime = 0;
  let lastTapX = 0;
  let lastTapY = 0;

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

    const zoomOutBtn = makeBtn('−', labels.zoomOut, () => zoomTo(scale / 1.35), 'image-lightbox-step');
    zoomResetBtn = makeBtn('100%', labels.reset, resetZoom, 'image-lightbox-zoom');
    const zoomInBtn = makeBtn('+', labels.zoomIn, () => zoomTo(scale * 1.35), 'image-lightbox-step');

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

    const toggleZoomAt = (x, y) => {
      if (scale > 1.05) {
        resetZoom();
      } else {
        zoomTo(2.5, x, y);
      }
    };

    const beginDrag = (x, y) => {
      dragging = true;
      startX = x;
      startY = y;
      startTx = tx;
      startTy = ty;
      stage.classList.add('is-dragging');
    };

    const getPinch = () => {
      const [p1, p2] = activePointers.values();
      return {
        dist: Math.hypot(p2.x - p1.x, p2.y - p1.y) || 1,
        midX: (p1.x + p2.x) / 2,
        midY: (p1.y + p2.y) / 2,
      };
    };

    // Double-click toggles between 1x and 2.5x at the clicked point.
    imgEl.addEventListener('dblclick', (e) => {
      e.preventDefault();
      toggleZoomAt(e.clientX, e.clientY);
    });

    // Multi-touch pinch-to-zoom, single-pointer drag-to-pan, and touch double-tap.
    stage.addEventListener('pointerdown', (e) => {
      if (e.pointerType === 'mouse' && e.button !== 0) return;
      activePointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (e.pointerType === 'touch' || scale > 1) {
        try {
          stage.setPointerCapture(e.pointerId);
        } catch {
          // Ignore synthetic or already-released pointers.
        }
      }

      if (activePointers.size === 2) {
        const { dist, midX, midY } = getPinch();
        pinching = true;
        dragging = false;
        dragged = true;
        lastTapTime = 0;
        stage.classList.remove('is-dragging');
        pinchStartDist = dist;
        pinchStartScale = scale;
        prevMidX = midX;
        prevMidY = midY;
        e.preventDefault();
      } else if (activePointers.size === 1) {
        dragged = false;
        if (scale > 1) {
          beginDrag(e.clientX, e.clientY);
          e.preventDefault();
        }
      }
    });

    stage.addEventListener('pointermove', (e) => {
      if (!activePointers.has(e.pointerId)) return;
      activePointers.set(e.pointerId, { x: e.clientX, y: e.clientY });

      if (pinching && activePointers.size >= 2) {
        const { dist, midX, midY } = getPinch();
        const nextScale = pinchStartScale * (dist / pinchStartDist);
        if (scale > 1) {
          tx += midX - prevMidX;
          ty += midY - prevMidY;
        }
        const prevScale = scale;
        zoomTo(nextScale, midX, midY);
        if (scale === prevScale && scale > 1) {
          applyTransform();
        }
        prevMidX = midX;
        prevMidY = midY;
        return;
      }

      if (!dragging) return;
      const dx = e.clientX - startX;
      const dy = e.clientY - startY;
      if (Math.hypot(dx, dy) > 4) dragged = true;
      tx = startTx + dx;
      ty = startTy + dy;
      applyTransform();
    });

    const endPointer = (e, cancelled) => {
      activePointers.delete(e.pointerId);

      if (pinching) {
        if (activePointers.size < 2) {
          pinching = false;
          if (!cancelled && activePointers.size === 1 && scale > 1) {
            const [rem] = activePointers.values();
            beginDrag(rem.x, rem.y);
          }
        }
        return;
      }

      if (dragging) {
        dragging = false;
        stage.classList.remove('is-dragging');
      }

      // Touch double-tap zoom (iOS Safari does not fire dblclick under touch-action: none).
      if (
        !cancelled &&
        e.pointerType === 'touch' &&
        !dragged &&
        activePointers.size === 0 &&
        e.target === imgEl
      ) {
        const now = performance.now();
        if (
          now - lastTapTime < 300 &&
          Math.hypot(e.clientX - lastTapX, e.clientY - lastTapY) < 32
        ) {
          lastTapTime = 0;
          toggleZoomAt(e.clientX, e.clientY);
        } else {
          lastTapTime = now;
          lastTapX = e.clientX;
          lastTapY = e.clientY;
        }
      }
    };
    stage.addEventListener('pointerup', (e) => endPointer(e, false));
    stage.addEventListener('pointercancel', (e) => endPointer(e, true));

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

    dialog.addEventListener('close', () => {
      activePointers.clear();
      pinching = false;
      dragging = false;
      dragged = false;
      lastTapTime = 0;
      stage.classList.remove('is-dragging');
      resetZoom();
    });

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
