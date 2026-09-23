#!/usr/bin/env python3
"""Self-checks for the Chaos theme.

Catches the classes of mistake this theme has actually shipped, each of which
was found by hand and none of which a build error would have surfaced. Run it
after a build:

    python3 themes/chaos/tools/check.py --public public

Needs nothing but Python 3. It is a maintainer's tool: it is not part of
`hugo`, and a site never runs it.

Hugo covers what it can already, and the build script runs it under
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


def check_feed_whitespace(public):
    """No template indentation inside the feeds.

    A render hook's output goes verbatim into .Content, which the feeds carry
    inside CDATA, and the XML minifier does not descend into character data --
    so a pretty-printed hook ships its indentation to every reader. Only the
    HTML page hid this, because --minify collapses it there.

    Space-indented tags are the signature: this theme's templates indent with
    spaces, while hand-written HTML in posts uses tabs.
    """
    for name in ('atom.xml', 'index.xml'):
        f = public / name
        if not f.exists():
            continue
        hits = re.findall(r'\n +<[a-zA-Z/]', f.read_text(encoding='utf-8', errors='replace'))
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
    check_no_cjk_literals(theme)
    check_no_authored_inline_js(theme)
    if args.public:
        check_feed_whitespace(args.public.resolve())
    else:
        notes.append('feed-whitespace: skipped (no --public)')

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
