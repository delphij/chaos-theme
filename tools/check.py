#!/usr/bin/env python3
"""Self-checks for the Chaos theme.

Catches the classes of mistake this theme has actually shipped, each of which
was found by hand and none of which a build error would have surfaced. Run it
after a build:

    python3 themes/chaos/tools/check.py --public public

Needs nothing but Python 3, which tools/build_search_index.py already requires,
so it is cheap enough to belong in a build rather than in someone's habits: a
site's build script should run it after hugo and before anything
post-processes the output. It is not part of `hugo` itself, and `hugo` alone
still builds the theme.

Hugo already covers what it can, and the build runs it under
--printI18nWarnings --printPathWarnings --panicOnWarning. What is here is what
Hugo has no opinion about.
"""

import argparse
import re
import sys
from pathlib import Path

CJK = re.compile(r'[㐀-䶿一-鿿぀-ヿ가-힯]')

failures = []
notes = []


def fail(check, message):
    failures.append((check, message))


def strip_comments(text, suffix):
    """Remove comments so a check sees only what the file actually emits."""
    if suffix in ('.html', '.xsl'):
        # Go template comments, which is where this theme documents itself.
        text = re.sub(r'\{\{-?\s*/\*.*?\*/\s*-?\}\}', '', text, flags=re.S)
        text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    if suffix in ('.js', '.css', '.html', '.xsl'):
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    if suffix == '.js':
        text = re.sub(r'(?m)^\s*//.*$', '', text)
    return text


def check_i18n_parity(theme):
    """Every language file defines exactly the same keys."""
    files = sorted((theme / 'i18n').glob('*.toml'))
    if not files:
        return
    keys = {f.name: {m.group(1) for m in re.finditer(r'(?m)^([A-Za-z0-9_]+)\s*=', f.read_text(encoding='utf-8'))}
            for f in files}
    reference = 'en-us.toml' if 'en-us.toml' in keys else files[0].name
    for name, ks in sorted(keys.items()):
        missing = keys[reference] - ks
        extra = ks - keys[reference]
        if missing:
            fail('i18n-parity', f'{name} is missing {len(missing)}: {", ".join(sorted(missing))}')
        if extra:
            fail('i18n-parity', f'{name} has {len(extra)} not in {reference}: {", ".join(sorted(extra))}')
    notes.append(f'i18n-parity: {len(files)} files, {len(keys[reference])} keys each')


def check_i18n_unused(theme):
    """No translated string that nothing renders.

    Three such strings had accumulated, one of them marking an error path that
    was never built.
    """
    ref = theme / 'i18n' / 'en-us.toml'
    if not ref.exists():
        return
    haystack = '\n'.join(p.read_text(encoding='utf-8', errors='replace')
                         for d in ('layouts', 'assets')
                         for p in (theme / d).rglob('*') if p.is_file())
    unused = [m.group(1) for m in re.finditer(r'(?m)^([A-Za-z0-9_]+)\s*=', ref.read_text(encoding='utf-8'))
              if m.group(1) not in haystack]
    if unused:
        fail('i18n-unused', f'{len(unused)} key(s) nothing references: {", ".join(unused)}')


def check_version_parity(theme):
    """theme.toml and hugo.toml declare the same minimum Hugo version.

    hugo.toml defines min under [module.hugoVersion], while theme.toml
    defines min_version. If one is bumped without the other, users or tools
    reading either file see conflicting minimum version requirements.
    """
    theme_toml = theme / 'theme.toml'
    hugo_toml = theme / 'hugo.toml'
    if not (theme_toml.exists() and hugo_toml.exists()):
        return

    m_theme = re.search(r'(?m)^\s*min_version\s*=\s*["\']([^"\']+)["\']', theme_toml.read_text(encoding='utf-8'))
    m_hugo = re.search(r'(?m)^\s*min\s*=\s*["\']([^"\']+)["\']', hugo_toml.read_text(encoding='utf-8'))

    v_theme = m_theme.group(1) if m_theme else None
    v_hugo = m_hugo.group(1) if m_hugo else None

    if not v_theme:
        fail('version-parity', 'theme.toml is missing min_version')
    elif not v_hugo:
        fail('version-parity', 'hugo.toml is missing [module.hugoVersion].min')
    elif v_theme != v_hugo:
        fail('version-parity', f'minimum Hugo version mismatch: theme.toml has {v_theme}, hugo.toml has {v_hugo}')
    else:
        notes.append(f'version-parity: Hugo >={v_theme}')


def check_no_cjk_literals(theme):
    """No CJK outside comments.

    A five-language theme that falls back to Chinese is worse than one that
    falls back to the untranslated string. Comments are exempt: the palette
    names its colours in Japanese, and several files quote CJK to explain what
    they do.
    """
    offenders = []
    for d in ('layouts', 'assets'):
        for p in sorted((theme / d).rglob('*')):
            if not p.is_file() or p.suffix not in ('.html', '.js', '.css', '.xsl'):
                continue
            body = strip_comments(p.read_text(encoding='utf-8', errors='replace'), p.suffix)
            for n, line in enumerate(body.split('\n'), 1):
                if CJK.search(line):
                    offenders.append(f'{p.relative_to(theme)}:{n}')
    if offenders:
        fail('cjk-literal', f'{len(offenders)}: {", ".join(offenders[:6])}')


def check_no_authored_inline_js(theme):
    """Scripts the theme writes live in assets/, not inside a template.

    The Mermaid glue sat inline for as long as it did because nothing said
    otherwise: it never reached js.Build, so it had no syntax target, no source
    map, no integrity hash, and could not be linted. Short blocks are fine --
    config objects, JSON-LD, a vendored loader -- so this only objects once a
    block is long enough to be code worth building.
    """
    limit = 8
    for p in sorted((theme / 'layouts').rglob('*')):
        if not p.is_file() or p.suffix not in ('.html', '.xsl'):
            continue
        text = p.read_text(encoding='utf-8', errors='replace')
        for m in re.finditer(r'<script([^>]*)>(.*?)</script>', text, flags=re.S):
            attrs, body = m.group(1), m.group(2)
            if 'src=' in attrs or 'ld+json' in attrs or 'speculationrules' in attrs:
                continue
            # A block that is one template action is a file from assets/.
            if len(re.sub(r'\{\{.*?\}\}', '', body, flags=re.S).strip(' \n\t[]<!CDATA') or '') == 0:
                continue
            lines = [l for l in body.strip().split('\n') if l.strip()]
            if len(lines) > limit:
                n = text[:m.start()].count('\n') + 1
                fail('inline-js', f'{p.relative_to(theme)}:{n} has {len(lines)} lines of script; '
                                  f'put it in assets/js/ and load it through foot/script.html')


def check_nav_active(public):
    """The menu's active entry is the page's own.

    `aria-current="page"` is a per-page statement, so any template that renders
    the header once and reuses it -- partialCached keyed on anything but the
    page -- ships one page's highlight to every other page, silently and
    nondeterministically, because Hugo renders pages in parallel. Nothing in a
    build objects: the markup is valid, just wrong, and wrong in a way that
    reaches screen readers.

    The converse is checked too, because it is the same statement read the
    other way and it is what an unresolvable menu says: entries configured
    with `url` rather than `pageRef` carry no page for Hugo to compare, so
    `IsMenuCurrent` is false everywhere and no page ever marks its own entry.
    """
    attrs_re = re.compile(r'''([\w:-]+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))''')
    nav_re = re.compile(r'<nav[^>]*main-links[^>]*>(.*?)</nav>', re.S)
    canonical_re = re.compile(r'<link[^>]*rel=["\']?canonical["\']?[^>]*>', re.I)
    pager_re = re.compile(r'(?:^|/)page/\d+/$')

    def attrs(tag):
        return {m.group(1).lower(): (m.group(2) or m.group(3) or m.group(4) or '')
                for m in attrs_re.finditer(tag)}

    def split_url(url):
        """Host (empty when relative) and path, the path ending in a slash and
        a pager folded onto the page it pages."""
        host = ''
        m = re.match(r'[a-z]+://([^/]*)', url, flags=re.I)
        if m:
            host, url = m.group(1), url[m.end():]
        path = (url.split('?')[0].split('#')[0]) or '/'
        if not path.endswith('/'):
            path += '/'
        return host, pager_re.sub('/', path)

    checked = 0
    wrong, unmarked = [], []
    for f in sorted(public.rglob('*.html')):
        text = f.read_text(encoding='utf-8', errors='replace')
        nav = nav_re.search(text)
        if not nav:
            continue
        entries = [attrs(a) for a in re.findall(r'<a\s[^>]*>', nav.group(1))]
        entries = [a for a in entries if a.get('href')]
        if not entries:
            continue
        # The canonical link is what the page says its own URL is, and that is
        # what a menu entry has to agree with. A page without one -- 404.html
        # -- has no URL to compare against and is left alone.
        m = canonical_re.search(text)
        if not m:
            continue
        host, own = split_url(attrs(m.group(0)).get('href', ''))
        where = f.relative_to(public)
        # An off-site entry -- the feed link, someone else's page -- is nobody's
        # current page however its path reads.
        here = [split_url(a['href']) for a in entries]
        here = [path for h, path in here if h in ('', host)]
        marked = [split_url(a['href'])[1] for a in entries
                  if a.get('aria-current') == 'page']
        mine = [path for path in here if path == own]
        checked += 1
        if len(marked) > 1:
            wrong.append(f'{where} marks {len(marked)} entries')
        wrong += [f'{where} marks {href}, not {own}' for href in marked if href != own]
        if mine and not marked:
            unmarked.append(f'{where} ({mine[0]})')
    # One failure per kind: a header rendered once gets every page wrong, and a
    # menu Hugo cannot resolve misses every page it names. Either way the list
    # is as long as the site, and the first few say all of it.
    if wrong:
        fail('nav-active', f'{len(wrong)} page(s) mark a menu entry that is not their own '
                           f'-- is the header partialCached? {"; ".join(wrong[:3])}')
    if unmarked:
        fail('nav-active', f'{len(unmarked)} page(s) leave their own menu entry unmarked; '
                           f'entries need pageRef rather than url for Hugo to recognise '
                           f'them: {"; ".join(unmarked[:3])}')
    notes.append(f'nav-active: {checked} page(s) with a menu')


def check_feed_whitespace(public):
    """No template indentation inside the feeds.

    A render hook's output goes verbatim into .Content, which the feeds carry
    inside CDATA, and the XML minifier does not descend into character data --
    so a pretty-printed hook ships its indentation to every reader. Only the
    HTML page hid this, because --minify collapses it there.

    Space-indented tags are the signature: this theme's templates indent with
    spaces, while hand-written HTML in posts uses tabs.

    Only the CDATA sections are scanned. The feed's own elements are indented
    too unless the site was built with --minify, and that indentation is
    harmless -- counting it made the check fail on every unminified build.
    """
    for name in ('atom.xml', 'index.xml'):
        f = public / name
        if not f.exists():
            continue
        text = f.read_text(encoding='utf-8', errors='replace')
        hits = [h for cdata in re.findall(r'<!\[CDATA\[(.*?)\]\]>', text, re.S)
                for h in re.findall(r'\n +<[a-zA-Z/]', cdata)]
        if hits:
            fail('feed-whitespace', f'{name} carries {len(hits)} space-indented tag(s); '
                                    f'a template is emitting whitespace into .Content')
        else:
            notes.append(f'feed-whitespace: {name} clean')


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--public', type=Path, default=None,
                    help='built site, for the checks that read output (default: skip them)')
    args = ap.parse_args()

    theme = Path(__file__).resolve().parent.parent

    check_i18n_parity(theme)
    check_i18n_unused(theme)
    check_version_parity(theme)
    check_no_cjk_literals(theme)
    check_no_authored_inline_js(theme)
    if args.public:
        public = args.public.resolve()
        check_feed_whitespace(public)
        check_nav_active(public)
    else:
        notes.append('feed-whitespace: skipped (no --public)')
        notes.append('nav-active: skipped (no --public)')

    for n in notes:
        print(f'  ok    {n}')
    for check, message in failures:
        print(f'  FAIL  {check}: {message}', file=sys.stderr)

    if failures:
        print(f'\n{len(failures)} check(s) failed', file=sys.stderr)
        return 1
    print(f'\nall checks passed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
