// Automatic multi-sheet pagination for `.vertical` CJK blocks.
//
// When a vertical-rl block exceeds the available width (or an explicit
// `data-cols` column cap), split its content into vertically stacked
// `.vertical` sheets inside a `.vertical-book` wrapper so long classical
// passages read like sequential pages without horizontal scrollbars.
// Re-paginates smoothly on container resize; degrades cleanly to a single
// scrollable block when JS is unavailable.

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

function makeSheet(template, maxW, hasColCap) {
  const sheet = template.cloneNode(false);
  sheet.innerHTML = '';
  if (hasColCap) {
    sheet.style.width = `${maxW}px`;
  } else {
    sheet.style.maxWidth = `${maxW}px`;
  }
  return sheet;
}

const NO_START = /^[，。！？；：、」』）》”’…—]/;
const NO_END = /[「『（《“‘]$/;
const CLAUSE_END = /[，。！？；：、」』）》]/;

function overflows(sheet, maxW) {
  const limit = Math.min(sheet.clientWidth, maxW);
  if (sheet.scrollWidth > limit) return true;
  const last = sheet.lastElementChild;
  if (!last) return false;
  // Cache each sheet's content-box left edge once to avoid calling
  // getComputedStyle inside every binary-search iteration.
  if (sheet._contentLeft === undefined) {
    const padLeft = parseFloat(getComputedStyle(sheet).paddingLeft) || 0;
    sheet._contentLeft = sheet.getBoundingClientRect().left + padLeft - 0.5;
  }
  // In vertical-rl, columns grow right-to-left; Blink/WebKit omit block-end
  // padding-left from scrollWidth, so check the leftmost child against the
  // content-box left edge directly.
  return last.getBoundingClientRect().left < sheet._contentLeft;
}

// Adjust a character split index `lo` to respect CJK kinsoku (no orphan
// closing punctuation at the top of the next sheet, no dangling opening
// bracket at the bottom of the current sheet) and avoid amputating a very
// short trailing clause (e.g. "？无" | "有也。") right after punctuation.
function adjustSplitIndex(rest, lo) {
  let idx = lo;
  // Pull back if the next sheet would start with closing punctuation.
  while (idx > 1 && NO_START.test(rest.slice(idx))) {
    idx -= 1;
  }
  // Pull back if the current sheet would end with an opening quote/bracket.
  while (idx > 1 && NO_END.test(rest.slice(0, idx))) {
    idx -= 1;
  }
  // If a tiny tail (<= 4 chars) is left and a clause punctuation sits 1–3 chars
  // before `idx`, break cleanly after that punctuation instead of mid-phrase.
  const tail = rest.slice(idx);
  if (tail.length > 0 && tail.length <= 4) {
    for (let back = 1; back <= 3 && idx - back > 0; back++) {
      if (CLAUSE_END.test(rest[idx - back - 1])) {
        idx -= back;
        break;
      }
    }
  }
  return idx;
}

// Split a single <p> across sheets at safe inline boundaries (never cutting
// inside <ruby>, <em>, <sup>, or <span class="jiazhu">), continuing directly
// on `sheet` whenever space remains so paragraphs flow like woodblock pages.
function splitParagraph(p, sheet, makeNextSheet, maxW) {
  const nodes = Array.from(p.childNodes);
  let curSheet = sheet;
  let curP = p.cloneNode(false);
  curSheet.appendChild(curP);

  const moveParagraphToFreshSheet = () => {
    curSheet.removeChild(curP);
    curSheet = makeNextSheet();
    curSheet.appendChild(curP);
  };

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
            if (curSheet.childNodes.length > 1) {
              // Current sheet has no room left for a new column: move the
              // whole empty paragraph onto the next sheet before retrying.
              moveParagraphToFreshSheet();
            } else {
              // Even one char overflows an ultra-narrow container; force progress.
              curP.appendChild(document.createTextNode(rest.slice(0, 1)));
              rest = rest.slice(1);
            }
          } else {
            openContinuation();
          }
        } else {
          const cut = adjustSplitIndex(rest, lo);
          curP.appendChild(document.createTextNode(rest.slice(0, cut)));
          rest = rest.slice(cut);
          if (rest.length > 0) {
            openContinuation();
          }
        }
      }
    } else {
      const clone = node.cloneNode(true);
      curP.appendChild(clone);
      if (overflows(curSheet, maxW)) {
        if (curP.childNodes.length > 1) {
          curP.removeChild(clone);
          // Never orphan a footnote <sup> at the start of the next sheet:
          // carry its preceding character (and any Word Joiner) across with it.
          let carry = '';
          if (clone.nodeName === 'SUP' && curP.lastChild && curP.lastChild.nodeType === Node.TEXT_NODE) {
            const prev = curP.lastChild.textContent || '';
            const m = prev.match(/([^\u2060]\u2060*)$/);
            if (m && prev.length > m[1].length) {
              curP.lastChild.textContent = prev.slice(0, -m[1].length);
              carry = m[1];
            }
          }
          openContinuation();
          if (carry) {
            curP.appendChild(document.createTextNode(carry));
          }
          curP.appendChild(clone);
        } else if (curSheet.childNodes.length > 1) {
          moveParagraphToFreshSheet();
        }
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

function renderHorizontalQuote(entry) {
  const { book, stage, originalChildren } = entry;
  book.classList.remove('is-paged');
  book.classList.add('is-horizontal');
  const bq = document.createElement('blockquote');
  bq.className = 'vertical-as-quote';
  for (const child of originalChildren) {
    bq.appendChild(child.cloneNode(true));
  }
  stage.replaceChildren(bq);
}

function layoutBook(entry) {
  const { book, stage, template, originalChildren, horizontal } = entry;
  if (horizontal) {
    renderHorizontalQuote(entry);
    return;
  }

  book.classList.remove('is-paged', 'is-horizontal');
  const availW = Math.floor(book.clientWidth);
  if (availW <= 0) return;

  const maxW = getSheetBudget(template, availW);
  const hasColCap = parseInt(template.dataset.cols || '', 10) > 0;

  // Fast path: render all children in a single sheet first.
  const firstSheet = makeSheet(template, maxW, false);
  for (const child of originalChildren) {
    firstSheet.appendChild(child.cloneNode(true));
  }
  stage.replaceChildren(firstSheet);

  if (!overflows(firstSheet, maxW)) {
    firstSheet.style.removeProperty('max-width');
    placeSideNotes(firstSheet);
    return;
  }

  // Paginate across multiple stacked sheets of uniform geometry.
  // Apply `.is-paged` before measuring so every sheet has its final width and
  // fixed height during overflow checks, preventing post-layout scrollbars.
  book.classList.add('is-paged');
  const sheets = [];
  const pushSheet = () => {
    const s = makeSheet(template, maxW, hasColCap);
    sheets.push(s);
    stage.appendChild(s);
    return s;
  };

  stage.replaceChildren();
  let cur = pushSheet();

  for (const child of originalChildren) {
    const clone = child.cloneNode(true);
    cur.appendChild(clone);
    if (!overflows(cur, maxW)) continue;

    // Keep standalone metadata lines (title / attribution) intact on a new sheet.
    const keepIntact = clone.nodeName !== 'P'
      || clone.classList.contains('v-title')
      || clone.classList.contains('quote-by');

    if (keepIntact) {
      if (cur.childNodes.length > 1) {
        cur.removeChild(clone);
        cur = pushSheet();
        cur.appendChild(clone);
      }
      continue;
    }

    // Flow regular paragraphs continuously from the remaining columns of the
    // current sheet onto the next sheet (traditional woodblock pagination).
    cur.removeChild(clone);
    cur = splitParagraph(clone, cur, pushSheet, maxW);
  }

  if (sheets.length <= 1) {
    book.classList.remove('is-paged');
  }
  for (const s of sheets) {
    s.style.removeProperty('max-width');
    if (sheets.length > 1 && hasColCap) {
      s.style.width = `${maxW}px`;
    } else {
      s.style.removeProperty('width');
    }
    placeSideNotes(s);
  }
}

export function initVerticalSheets() {
  const blocks = document.querySelectorAll('blockquote.vertical');
  if (!blocks.length) return;

  const toHorizontalLabel = document.body.dataset.verticalToHorizontal || 'Switch to horizontal';
  const toVerticalLabel = document.body.dataset.verticalToVertical || 'Switch to vertical';

  const entries = [];
  const syncToggleButton = (entry) => {
    entry.toggleBtn.textContent = entry.horizontal ? toVerticalLabel : toHorizontalLabel;
  };

  for (const block of blocks) {
    const template = block.cloneNode(false);
    const originalChildren = Array.from(block.children).map((c) => c.cloneNode(true));
    if (!originalChildren.length) continue;

    const book = document.createElement('div');
    book.className = 'vertical-book';

    const toolbar = document.createElement('div');
    toolbar.className = 'vertical-toolbar';

    const toggleBtn = document.createElement('button');
    toggleBtn.type = 'button';
    toggleBtn.className = 'vertical-mode-toggle';
    toolbar.appendChild(toggleBtn);

    const stage = document.createElement('div');
    stage.className = 'vertical-stage';

    book.append(toolbar, stage);
    block.replaceWith(book);

    const entry = {
      book,
      stage,
      toggleBtn,
      template,
      originalChildren,
      horizontal: false,
      lastWidth: 0,
    };
    toggleBtn.addEventListener('click', () => {
      entry.horizontal = !entry.horizontal;
      syncToggleButton(entry);
      layoutBook(entry);
      entry.lastWidth = Math.floor(book.clientWidth);
    });
    entries.push(entry);
    syncToggleButton(entry);
    layoutBook(entry);
    entry.lastWidth = Math.floor(book.clientWidth);
  }

  if (!entries.length) return;

  const relayoutAll = () => {
    for (const entry of entries) {
      if (entry.horizontal) continue;
      layoutBook(entry);
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
      if (!entry || entry.horizontal) continue;
      const w = Math.floor(item.contentRect.width);
      if (Math.abs(w - entry.lastWidth) < 2) continue;
      entry.lastWidth = w;
      layoutBook(entry);
    }
  });

  for (const entry of entries) {
    ro.observe(entry.book);
  }
}
