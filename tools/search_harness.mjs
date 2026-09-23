#!/usr/bin/env node
// Copyright 2025 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Runs assets/js/search.js against a real search index in a stubbed DOM, so
// the search can be exercised and, more usefully, two versions of it compared
// before and after a change.
//
// A maintainer's tool. It needs Node, which nothing else in this theme does:
// `hugo` builds the theme on its own and a site never runs this.
//
//   List what a query returns:
//     node tools/search_harness.mjs --index path/to/search-index.json \
//          --query "some term"
//
//   Check a change to search.js against the version it replaces:
//     git show HEAD:assets/js/search.js > /tmp/search-old.js
//     node tools/search_harness.mjs --index path/to/search-index.json \
//          --body path/to/search-index-body.json \
//          --compare /tmp/search-old.js
//
// The index is whatever tools/build_search_index.py produced -- a built site
// has it under assets/ or, fingerprinted, in public/.
//
// With no --query, queries are derived from the index itself: terms sampled
// across the frequency range, a multi-term query, a single character and one
// string that matches nothing. Nothing about any particular site is baked in.
//
// Two things this learned the hard way, both preserved deliberately:
//
//   - every run gets its own copy of the index. search.js merges the body
//     index into the core one in place, so a shared object leaves the next run
//     starting from an already-merged index, concatenating the posting lists a
//     second time and shifting every idf.
//   - --compare runs each file against itself first. A comparison between two
//     files says nothing until the harness is known to be repeatable, and the
//     first version of this was not.

import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const THEME = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DEFAULT_SCRIPT = path.join(THEME, 'assets', 'js', 'search.js');

// ---------------------------------------------------------------- DOM stubs

function makeEl(dataset = {}) {
  return {
    dataset,
    value: '',
    innerHTML: '',
    open: true,
    _listeners: {},
    addEventListener(type, fn) { (this._listeners[type] ??= []).push(fn); },
    dispatch(type, event = {}) {
      for (const fn of this._listeners[type] || []) fn({ preventDefault() {}, ...event });
    },
    getAttribute(name) {
      const key = name.replace(/^data-/, '').replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      return this.dataset[key] ?? null;
    },
    querySelectorAll: () => [],
    getBoundingClientRect: () => ({ top: 0, left: 0, width: 100, height: 100 }),
    showModal() {}, close() {}, focus() {}, setAttribute() {}, removeAttribute() {},
    scrollIntoView() {},
    classList: { add() {}, remove() {}, toggle() {} }
  };
}

const settle = async ticks => { for (let i = 0; i < ticks; i++) await new Promise(r => setTimeout(r, 10)); };

// ------------------------------------------------------------------ the run

// Returns { query: [url, ...] } in the order the script rendered them.
export async function run({ script, index, body, queries }) {
  let markBodyDelivered;
  const bodyDelivered = new Promise(resolve => { markBodyDelivered = resolve; });

  const dialog = makeEl({
    indexUrl: '/search-index.json',
    ...(body ? { bodyIndexUrl: '/search-index-body.json' } : {}),
    msgLoading: 'loading', msgEmpty: 'empty', msgError: 'error', msgDeprecated: 'deprecated'
  });
  const input = makeEl();
  const results = makeEl();
  const elements = {
    searchDialog: dialog, searchInput: input, searchResults: results,
    searchClose: makeEl(), searchToggle: makeEl()
  };

  const context = {
    document: { getElementById: id => elements[id] ?? null, addEventListener() {} },
    window: {},                       // no requestIdleCallback: takes the setTimeout path
    setTimeout, clearTimeout, console, structuredClone,
    Math, Object, Array, String, Number, RegExp, Set, Map, JSON, Error, Promise,
    fetch: async url => {
      const isBody = url.includes('body');
      if (isBody && !body) throw new Error('no body index configured');
      return {
        ok: true,
        json: async () => {
          const data = structuredClone(isBody ? body : index);
          if (isBody) markBodyDelivered();
          return data;
        }
      };
    }
  };
  context.globalThis = context;
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(script, 'utf8'), context, { filename: script });

  elements.searchToggle.dispatch('click');
  await settle(20);
  if (body) {
    await bodyDelivered;
    await settle(20);
  }

  const out = {};
  for (const query of queries) {
    input.value = query;
    input.dispatch('input');
    await settle(25);                 // the script debounces input by 150ms
    out[query] = [...results.innerHTML.matchAll(/href="([^"]+)"/g)].map(m => m[1]);
  }
  return out;
}

// -------------------------------------------------------- derived queries

// Sampled from the index so the harness carries no site's content.
function deriveQueries(index, count = 12) {
  const terms = Object.entries(index.index || {})
    .filter(([term, ids]) => Array.isArray(ids) && term.length >= 1)
    .sort((a, b) => b[1].length - a[1].length);
  if (terms.length === 0) return ['nothing-matches-this-qzx'];

  const picks = [];
  const wanted = Math.min(count - 3, terms.length);
  for (let i = 0; i < wanted; i++) {
    // Spread across the frequency range: common terms through rare ones.
    picks.push(terms[Math.floor((i * (terms.length - 1)) / Math.max(1, wanted - 1))][0]);
  }
  const unique = [...new Set(picks)];
  return [
    ...unique,
    unique.slice(0, 2).join(' '),     // multi-token
    terms[0][0].slice(0, 1),          // a single character
    'nothing-matches-this-qzx'        // no results
  ];
}

// ------------------------------------------------------------------- CLI

function parseArgs(argv) {
  const opts = { queries: [] };
  for (let i = 0; i < argv.length; i++) {
    const [flag, inline] = argv[i].split(/=(.*)/s);
    const value = () => (inline !== undefined ? inline : argv[++i]);
    switch (flag) {
      case '--index': opts.index = value(); break;
      case '--body': opts.body = value(); break;
      case '--script': opts.script = value(); break;
      case '--compare': opts.compare = value(); break;
      case '--query': opts.queries.push(value()); break;
      case '-h': case '--help': opts.help = true; break;
      default: throw new Error(`unknown argument: ${flag}`);
    }
  }
  return opts;
}

function usage() {
  console.log(fs.readFileSync(fileURLToPath(import.meta.url), 'utf8')
    .split('\n').filter(l => l.startsWith('//')).slice(4).map(l => l.slice(3)).join('\n'));
}

async function main() {
  let opts;
  try {
    opts = parseArgs(process.argv.slice(2));
  } catch (err) {
    console.error(err.message);
    return 2;
  }
  if (opts.help) { usage(); return 0; }
  if (!opts.index) { console.error('--index is required (see --help)'); return 2; }

  const index = JSON.parse(fs.readFileSync(opts.index, 'utf8'));
  const body = opts.body ? JSON.parse(fs.readFileSync(opts.body, 'utf8')) : null;
  const script = opts.script || DEFAULT_SCRIPT;
  const queries = opts.queries.length ? opts.queries : deriveQueries(index);

  if (!opts.compare) {
    const out = await run({ script, index, body, queries });
    for (const q of queries) {
      console.log(`\n${q}  (${out[q].length})`);
      for (const url of out[q].slice(0, 10)) console.log(`  ${url}`);
    }
    return 0;
  }

  const differs = (a, b) => queries.filter(q => JSON.stringify(a[q]) !== JSON.stringify(b[q]));
  const label = { old: opts.compare, new: script };

  // A comparison means nothing until each side is repeatable on its own.
  for (const side of ['old', 'new']) {
    const base = { script: label[side], index, body, queries };
    const unstable = differs(await run(base), await run(base));
    if (unstable.length) {
      console.error(`harness is not repeatable for ${label[side]}: ${unstable.join(', ')}`);
      return 2;
    }
    console.log(`  repeatable  ${label[side]}`);
  }

  const before = await run({ script: label.old, index, body, queries });
  const after = await run({ script: label.new, index, body, queries });
  const changed = differs(before, after);

  // A query with one result cannot show a change in ranking, only one in
  // matching. If most of them are like that the comparison proves very
  // little -- which is easy to miss, because it still reports "identical".
  // Usually the fix is --body: the core index alone matches far less.
  const thin = queries.filter(q => before[q].length <= 1).length;
  if (thin > queries.length / 2) {
    console.warn(`  weak: ${thin} of ${queries.length} queries return 0 or 1 result, so `
      + `ranking changes cannot show${body ? '' : '. Try --body with the body index'}`);
  }
  for (const q of queries) {
    const same = !changed.includes(q);
    console.log(`  ${same ? 'same      ' : 'DIFFERS   '} ${String(before[q].length).padStart(3)} result(s)  ${q}`);
    if (!same) {
      console.log(`      before: ${before[q].slice(0, 5).join(' ')}`);
      console.log(`      after:  ${after[q].slice(0, 5).join(' ')}`);
    }
  }
  console.log(`\n${changed.length ? `${changed.length} of ${queries.length} queries differ` : `identical over ${queries.length} queries`}`);
  return changed.length ? 1 : 0;
}

process.exit(await main());
