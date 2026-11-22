// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// While printing, turns an article's Markdown footnotes and cross-page links
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
// Standard-port https:// (and a bare origin's trailing slash) is stripped in
// visible text while keeping the full href on <a class="print-url"> so saved
// PDFs remain clickable and explicit http://, ftp:// or :port URLs stay intact.
const [OPEN, CLOSE] = /^(zh|ja|ko)\b/i.test(document.documentElement.lang)
  ? ['\uFF08', '\uFF09']
  : [' (', ')'];
const BARE_URL_RE = /^[a-z][a-z0-9+.-]*:\/\//i;
const HTTPS_ORIGIN_RE = /^https:\/\/([^/@:?#]+)(?:\/?$|([/?#].*))/;
const CHROME_SELECTOR = '.meta, .footnotes, .series-nav, .post-footer, .print-only, #remark42, .pager';

const displayUrl = url => url.replace(HTTPS_ORIGIN_RE, '$1$2');

function isNoteLink(link, pageUrl) {
  return Boolean(link.textContent.trim()) &&
         /^(https?:|ftp:|telnet:)/i.test(link.protocol) &&
         link.href.split('#')[0] !== pageUrl;
}

function urlLink(link) {
  const a = document.createElement('a');
  a.className = 'print-url';
  a.href = link.href;
  a.textContent = displayUrl(link.href);
  return a;
}

// A copy of a footnote's text for the notes list: its back-link dropped with
// the no-break space Goldmark puts before it, and each cross-page link inside
// it followed by its URL in brackets.
function footnoteBody(item, pageUrl) {
  const copy = item.cloneNode(true);
  copy.querySelectorAll('.footnote-backref').forEach(back => {
    const before = back.previousSibling;
    if (before?.nodeType === Node.TEXT_NODE) {
      before.textContent = before.textContent.replace(/[\s\u00A0]+$/, '');
    }
    back.remove();
  });
  copy.querySelectorAll('a[href]').forEach(link => {
    if (!isNoteLink(link, pageUrl)) return;
    if (displayUrl(link.textContent.trim()) === displayUrl(link.href)) {
      link.replaceWith(urlLink(link));
    } else {
      link.after(OPEN, urlLink(link), CLOSE);
    }
  });
  copy.querySelectorAll('[id]').forEach(el => el.removeAttribute('id'));
  return [...copy.childNodes];
}

function numberNotes() {
  const notes = [];
  const footnoteNumbers = new Map();
  const pageUrl = location.href.split('#')[0];

  for (const mark of articlePost.querySelectorAll('a[href]')) {
    if (mark.closest(CHROME_SELECTOR)) continue;
    // Do not number links inside a <details> that stayed closed on paper.
    if (mark.closest('details:not([open])')) continue;

    if (mark.classList.contains('footnote-ref')) {
      const target = mark.getAttribute('href');
      let num = footnoteNumbers.get(target);
      if (num === undefined) {
        const item = articlePost.querySelector(`.footnotes li[id="${CSS.escape(target.slice(1))}"]`);
        if (!item) continue;
        num = notes.length + 1;
        footnoteNumbers.set(target, num);
        // The sup Goldmark wraps the mark in carries the id to come back to.
        notes.push({ backId: mark.parentElement.id, body: footnoteBody(item, pageUrl) });
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

    if (!isNoteLink(mark, pageUrl)) continue;

    const isBareUrl = BARE_URL_RE.test(mark.textContent.trim());
    if (isBareUrl) mark.classList.add('print-url');
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
    restore.push(() => {
      sup.remove();
      if (isBareUrl) mark.classList.remove('print-url');
    });
    notes.push({ backId, body: [urlLink(mark)] });
  }
  return notes;
}

export function initPrintFootnotes() {
  window.addEventListener('beforeprint', () => {
    if (!printNotes || !articlePost) return;
    // A second beforeprint with no afterprint between would number twice.
    undo();

    // Paper cannot be clicked: open all collapsed content disclosures (but not
    // the interactive code-vars parameter panel, which is hidden in print)
    // before numbering links so content and references stay in sync, then
    // restore them to their prior state on afterprint.
    for (const details of articlePost.querySelectorAll('details:not([open]):not(.code-vars-details)')) {
      details.open = true;
      restore.push(() => { details.open = false; });
    }

    const notes = numberNotes();
    if (notes.length === 0) return;

    const heading = document.createElement('h2');
    heading.textContent = printNotes.dataset.heading;

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
