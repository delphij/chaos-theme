// Automatic multi-sheet pagination for `.vertical` CJK blocks.
//
// When a vertical-rl block exceeds the available width (or an explicit
// `data-cols` column cap), split its content into vertically stacked
// `.vertical` sheets inside a `.vertical-book` wrapper so long classical
// passages read like sequential pages without horizontal scrollbars.
// Re-paginates smoothly on container resize; degrades cleanly to a single
// scrollable block when JS is unavailable.

const EPSILON = 2;

function getSheetBudget(el, availWidth) {
  const cols = parseInt(el.dataset.cols || '', 10);
  if (cols > 0) {
    const cs = getComputedStyle(el);
    const colW = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 2.3;
    const padX = parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight);
    return Math.min(availWidth, Math.floor(cols * colW + padX));
  }
  return availWidth;
}

function makeSheet(template, maxW) {
  const sheet = template.cloneNode(false);
  sheet.innerHTML = '';
  sheet.style.maxWidth = `${maxW}px`;
  return sheet;
}

function overflows(sheet, maxW) {
  return sheet.scrollWidth > Math.min(sheet.clientWidth, maxW) + EPSILON;
}

// Split a single <p> that alone exceeds `maxW` at safe inline boundaries
// (never cutting inside <ruby>, <em>, or <span class="jiazhu">).
function splitParagraph(p, sheet, makeNextSheet, maxW) {
  const nodes = Array.from(p.childNodes);
  let curSheet = sheet;
  let curP = p.cloneNode(false);
  curSheet.appendChild(curP);

  const openContinuation = () => {
    curSheet = makeNextSheet();
    curP = p.cloneNode(false);
    curP.classList.remove('taitou-1', 'taitou-2');
    curSheet.appendChild(curP);
  };

  for (const node of nodes) {
    if (node.nodeType === Node.TEXT_NODE) {
      let rest = node.textContent || '';
      while (rest.length > 0) {
        const probe = document.createTextNode(rest);
        curP.appendChild(probe);
        if (!overflows(curSheet, maxW)) {
          rest = '';
          break;
        }
        curP.removeChild(probe);

        // Binary search longest prefix that fits in `curSheet`.
        let lo = 0;
        let hi = rest.length;
        while (lo < hi) {
          const mid = Math.ceil((lo + hi) / 2);
          const t = document.createTextNode(rest.slice(0, mid));
          curP.appendChild(t);
          const fits = !overflows(curSheet, maxW);
          curP.removeChild(t);
          if (fits) {
            lo = mid;
          } else {
            hi = mid - 1;
          }
        }

        if (lo === 0) {
          if (curP.childNodes.length === 0) {
            // Even one char overflows an ultra-narrow container; force progress.
            curP.appendChild(document.createTextNode(rest.slice(0, 1)));
            rest = rest.slice(1);
          } else {
            openContinuation();
          }
        } else {
          curP.appendChild(document.createTextNode(rest.slice(0, lo)));
          rest = rest.slice(lo);
          if (rest.length > 0) {
            openContinuation();
          }
        }
      }
    } else {
      const clone = node.cloneNode(true);
      curP.appendChild(clone);
      if (overflows(curSheet, maxW) && curP.childNodes.length > 1) {
        curP.removeChild(clone);
        openContinuation();
        curP.appendChild(clone);
      }
    }
  }

  return curSheet;
}

// Keep interlinear side commentary (`.pangpi-text`) inside the sheet's
// vertical content bounds and prevent consecutive notes in the same column
// from overlapping each other.
function placeSideNotes(sheet) {
  const notes = Array.from(sheet.querySelectorAll('.pangpi-text'));
  if (!notes.length) return;

  const cs = getComputedStyle(sheet);
  const colW = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 2.75;
  const rect = sheet.getBoundingClientRect();
  const minTop = rect.top + parseFloat(cs.paddingTop);
  const maxBot = rect.bottom - parseFloat(cs.paddingBottom);

  for (const el of notes) {
    el.style.removeProperty('transform');
  }

  // Group side notes by column.
  const cols = [];
  for (const el of notes) {
    const r = el.getBoundingClientRect();
    const cx = (r.left + r.right) / 2;
    let col = cols.find((c) => Math.abs(c.cx - cx) < colW * 0.45);
    if (!col) {
      col = { cx, items: [] };
      cols.push(col);
    }
    col.items.push({ el, top: r.top, height: r.height });
  }

  const gap = 6;
  for (const col of cols) {
    col.items.sort((a, b) => a.top - b.top);
    // Shift each note slightly upward so it sits alongside the preceding
    // annotated phrase rather than spilling exclusively below it.
    const placed = col.items.map((it) => ({
      ...it,
      y: Math.max(minTop, Math.min(it.top - it.height * 0.45, maxBot - it.height)),
    }));
    // Forward pass: push down if colliding with the previous note.
    for (let i = 1; i < placed.length; i++) {
      const prevBot = placed[i - 1].y + placed[i - 1].height + gap;
      if (placed[i].y < prevBot) {
        placed[i].y = prevBot;
      }
    }
    // Backward pass: if the last note pushed past the bottom edge, pull up.
    for (let i = placed.length - 1; i >= 0; i--) {
      const limit = i === placed.length - 1 ? maxBot : placed[i + 1].y - gap;
      if (placed[i].y + placed[i].height > limit) {
        placed[i].y = Math.max(minTop, limit - placed[i].height);
      }
    }
    for (const it of placed) {
      const dy = Math.round(it.y - it.top);
      if (dy !== 0) {
        it.el.style.transform = `translateY(${dy}px)`;
      }
    }
  }
}

function layoutBook(book, template, originalChildren) {
  book.classList.remove('is-paged');
  const availW = Math.floor(book.clientWidth);
  if (availW <= 0) return;

  const maxW = getSheetBudget(template, availW);
  const hasColCap = parseInt(template.dataset.cols || '', 10) > 0;

  // Fast path: render all children in a single sheet first.
  const firstSheet = makeSheet(template, maxW);
  for (const child of originalChildren) {
    firstSheet.appendChild(child.cloneNode(true));
  }
  book.replaceChildren(firstSheet);

  if (!overflows(firstSheet, maxW)) {
    firstSheet.style.removeProperty('max-width');
    placeSideNotes(firstSheet);
    return;
  }

  // Paginate across multiple stacked sheets of uniform geometry.
  const sheets = [];
  const pushSheet = () => {
    const s = makeSheet(template, maxW);
    sheets.push(s);
    book.appendChild(s);
    return s;
  };

  book.replaceChildren();
  let cur = pushSheet();

  for (const child of originalChildren) {
    const clone = child.cloneNode(true);
    cur.appendChild(clone);
    if (!overflows(cur, maxW)) continue;

    // Move to a fresh sheet if current sheet already holds earlier paragraphs.
    if (cur.childNodes.length > 1) {
      cur.removeChild(clone);
      cur = pushSheet();
      cur.appendChild(clone);
      if (!overflows(cur, maxW)) continue;
    }

    // Single paragraph alone still overflows `maxW`: split inside it.
    if (clone.nodeName === 'P') {
      cur.removeChild(clone);
      cur = splitParagraph(clone, cur, pushSheet, maxW);
    }
  }

  if (sheets.length > 1) {
    book.classList.add('is-paged');
  }
  for (const s of sheets) {
    s.style.removeProperty('max-width');
    if (sheets.length > 1 && hasColCap) {
      s.style.width = `${maxW}px`;
    }
    placeSideNotes(s);
  }
}

export function initVerticalSheets() {
  const blocks = document.querySelectorAll('blockquote.vertical');
  if (!blocks.length) return;

  const entries = [];
  for (const block of blocks) {
    const template = block.cloneNode(false);
    const originalChildren = Array.from(block.children).map((c) => c.cloneNode(true));
    if (!originalChildren.length) continue;

    const book = document.createElement('div');
    book.className = 'vertical-book';
    block.replaceWith(book);

    const entry = { book, template, originalChildren, lastWidth: 0 };
    entries.push(entry);
    layoutBook(book, template, originalChildren);
    entry.lastWidth = Math.floor(book.clientWidth);
  }

  if (!entries.length) return;

  const relayoutAll = () => {
    for (const entry of entries) {
      layoutBook(entry.book, entry.template, entry.originalChildren);
      entry.lastWidth = Math.floor(entry.book.clientWidth);
    }
  };

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(relayoutAll);
  }

  window.addEventListener('beforeprint', relayoutAll);
  window.addEventListener('afterprint', relayoutAll);

  if (typeof ResizeObserver === 'undefined') return;

  const ro = new ResizeObserver((items) => {
    for (const item of items) {
      const entry = entries.find((e) => e.book === item.target);
      if (!entry) continue;
      const w = Math.floor(item.contentRect.width);
      if (Math.abs(w - entry.lastWidth) < 2) continue;
      entry.lastWidth = w;
      layoutBook(entry.book, entry.template, entry.originalChildren);
    }
  });

  for (const entry of entries) {
    ro.observe(entry.book);
  }
}
