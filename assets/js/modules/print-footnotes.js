// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// While printing, turns an article's Markdown footnotes and external links
// into one sequence of notes, numbered in the order they appear and listed
// under one heading ahead of the post footer, and puts the page back
// afterwards. The screen is never touched.
//
// A footnote keeps the author's text; a link's note is its URL. A link inside
// a footnote takes its URL in brackets instead of a note of its own, so a note
// never points at another note. A footnote referenced twice keeps one number.

// Cached DOM references for performance
const printNotes = document.getElementById('print-references');
const articlePost = document.querySelector('article.post');

const BACK = '↩︎';  // ↩ as text, as Goldmark marks its back-links

// Everything beforeprint changes, so that afterprint can undo exactly that.
let restore = [];

function undo() {
  restore.reverse().forEach(step => step());
  restore = [];
  printNotes.replaceChildren();
}

// The footnote list Goldmark renders: hidden in print while the notes stand in.
function footnoteSection() {
  return articlePost.querySelector('.footnotes');
}

// Brackets for a URL set after its link text: full-width in CJK prose.
const CJK_PAGE = /^(zh|ja|ko)\b/i.test(document.documentElement.lang);
const bracketed = url => (CJK_PAGE ? `\uFF08${url}\uFF09` : ` (${url})`);

// A copy of a footnote's text for the notes list: its back-link dropped with
// the no-break space Goldmark puts before it, and each external link inside it
// followed by its URL in brackets.
function footnoteBody(item) {
  const copy = item.cloneNode(true);
  copy.querySelectorAll('.footnote-backref').forEach(back => {
    const before = back.previousSibling;
    if (before?.nodeType === Node.TEXT_NODE) {
      before.textContent = before.textContent.replace(/[\s\u00A0]+$/, '');
    }
    back.remove();
  });
  copy.querySelectorAll('a[href*="://"]').forEach(link => {
    if (link.textContent.trim() !== link.href) {
      link.after(bracketed(link.href));
    }
  });
  copy.querySelectorAll('[id]').forEach(el => el.removeAttribute('id'));
  return [...copy.childNodes];
}

function numberNotes() {
  const notes = [];
  const footnoteNumbers = new Map();

  const marks = articlePost.querySelectorAll('a.footnote-ref, a[href*="://"]');
  for (const mark of marks) {
    if (mark.closest('.footnotes')) continue;

    if (mark.classList.contains('footnote-ref')) {
      const target = mark.getAttribute('href');
      let num = footnoteNumbers.get(target);
      if (num === undefined) {
        const item = articlePost.querySelector(`.footnotes li[id="${CSS.escape(target.slice(1))}"]`);
        if (!item) continue;
        num = notes.length + 1;
        footnoteNumbers.set(target, num);
        // The sup Goldmark wraps the mark in carries the id to come back to.
        notes.push({ backId: mark.parentElement.id, body: footnoteBody(item) });
      }
      const text = mark.textContent;
      mark.textContent = String(num);
      mark.setAttribute('href', `#print-note-${num}`);
      restore.push(() => {
        mark.textContent = text;
        mark.setAttribute('href', target);
      });
      continue;
    }

    const num = notes.length + 1;
    const backId = `print-note-ref-${num}`;
    const sup = document.createElement('sup');
    sup.id = backId;
    sup.className = 'print-note-ref';
    const ref = document.createElement('a');
    ref.href = `#print-note-${num}`;
    ref.textContent = String(num);
    sup.append(ref);
    mark.after(sup);
    restore.push(() => sup.remove());
    notes.push({ backId, body: [document.createTextNode(mark.href)] });
  }
  return notes;
}

export function initPrintFootnotes() {
  window.addEventListener('beforeprint', () => {
    if (!printNotes || !articlePost) return;
    // A second beforeprint with no afterprint between would number twice.
    undo();

    const notes = numberNotes();
    if (notes.length === 0) return;

    const heading = document.createElement('h2');
    heading.textContent = printNotes.dataset.heading || 'Notes';

    const list = document.createElement('ol');
    list.append(...notes.map(({ backId, body }, index) => {
      const li = document.createElement('li');
      li.id = `print-note-${index + 1}`;
      const back = document.createElement('a');
      back.href = `#${backId}`;
      back.className = 'print-note-backref';
      back.textContent = BACK;
      li.append(...body);
      // At the end of the note's last paragraph, not on a line of its own.
      const last = body.findLast(node => node.nodeType === Node.ELEMENT_NODE);
      (last?.tagName === 'P' ? last : li).append(' ', back);
      return li;
    }));
    printNotes.replaceChildren(heading, list);

    const section = footnoteSection();
    if (section) {
      section.hidden = true;
      restore.push(() => { section.hidden = false; });
    }
  });

  window.addEventListener('afterprint', () => {
    if (printNotes) undo();
  });
}
