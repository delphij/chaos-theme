#!/usr/bin/env python3
"""Check syntax.css against the Chroma that the installed Hugo ships.

Chroma, Hugo's highlighter, names its token classes itself, and a Hugo
upgrade can bring a Chroma that adds a class, drops one or moves a short name
to a different token. None of that fails a build: an unmapped class just
renders as plain text. Run this after upgrading Hugo, or after editing the
syntax colours:

    python3 themes/chaos/tools/check_chroma.py

It asks `hugo gen chromastyles` for the classes of a spread of bundled
styles (no single style styles every token), then reports:

  * classes Chroma emits that syntax.css does not map (new tokens);
  * classes syntax.css maps that no style emits any more (stale);
  * classes whose token name in syntax.css's comment no longer matches
    Chroma's (a short name reassigned);
  * structural classes main.css is expected to lay out but does not;
  * --syntax-* inks below 4.5:1 on the code ground or a highlighted line,
    in either mode.

and prints the Chroma version next to the one syntax-upgrade.md records as
last verified. Exits non-zero if anything needs attention. Needs Python 3
and the `hugo` that builds the site; see assets/css/syntax-upgrade.md for
the procedure around it.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

# Bundled styles with wide token coverage. A style a future Chroma drops is
# skipped with a note; the union of the rest still covers the token set.
STYLES = [
    'github', 'github-dark', 'monokai', 'dracula', 'friendly', 'pygments',
    'emacs', 'vim', 'native', 'solarized-dark', 'xcode', 'onedark', 'nord',
    'catppuccin-latte', 'tango', 'rrt', 'paraiso-light', 'autumn', 'borland',
    'bw', 'colorful', 'manni', 'murphy', 'perldoc', 'trac', 'vs',
    'witchhazel', 'doom-one2', 'base16-snazzy',
]

# Laid out in main.css rather than coloured in syntax.css.
STRUCTURAL = {'lntable', 'lntd', 'lnlinks', 'line'}

# Wrappers, not tokens.
WRAPPERS = {'Background', 'PreWrapper'}

GENERATED = re.compile(r'/\*\s*(\w+)\s*\*/\s*\.chroma\s+\.([a-z0-9]+)\s*\{')
MAPPED = re.compile(r'\.chroma\s+\.([a-z0-9]+)\b')
COMMENT = re.compile(r'/\*\s*(\w+)')

issues = []


def issue(message):
    issues.append(message)


def hugo(args, hugo_bin):
    return subprocess.run([hugo_bin, *args], capture_output=True, text=True)


def chroma_classes(hugo_bin):
    """Map each token class to Chroma's token name, across STYLES."""
    classes = {}
    for style in STYLES:
        out = hugo(['gen', 'chromastyles', f'--style={style}'], hugo_bin)
        if out.returncode != 0:
            print(f'note: style {style} not available, skipped')
            continue
        for name, cls in GENERATED.findall(out.stdout):
            if name not in WRAPPERS:
                classes[cls] = name
    return classes


def chroma_version(hugo_bin):
    out = hugo(['env', '--logLevel', 'info'], hugo_bin).stdout
    m = re.search(r'alecthomas/chroma/v\d+="?(v[\d.]+)', out)
    return m.group(1) if m else 'unknown'


def mapped_classes(syntax_css):
    """Map each class syntax.css colours to the token name its comment gives."""
    mapped = {}
    for line in syntax_css.splitlines():
        classes = MAPPED.findall(line)
        m = COMMENT.search(line)
        name = m.group(1) if m and len(classes) == 1 else ''
        for cls in classes:
            if cls not in mapped or name:
                mapped[cls] = name
    return mapped


def custom_properties(block):
    return dict(re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', block))


def rule_block(css, selector):
    """The declarations directly inside the first `selector {`."""
    start = css.index(selector + ' {') + len(selector) + 2
    depth, i = 1, start
    while depth:
        depth += {'{': 1, '}': -1}.get(css[i], 0)
        i += 1
    body = css[start:i - 1]
    return re.sub(r'\{[^{}]*\}', '', body)   # drop nested rules


def resolve(name, props, seen=()):
    value = props[name].strip()
    m = re.fullmatch(r'var\((--[\w-]+)\)', value)
    if m and m.group(1) not in seen:
        return resolve(m.group(1), props, seen + (name,))
    return value


def rgba(value):
    """#RRGGBB or rgba(r, g, b, a) as (r, g, b, a), channels 0-1."""
    value = value.strip()
    if value.startswith('#'):
        return tuple(int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)) + (1.0,)
    r, g, b, a = (float(x) for x in re.findall(r'[\d.]+', value)[:4])
    return (r / 255, g / 255, b / 255, a)


def over(top, under):
    r, g, b, a = top
    return tuple(c * a + u * (1 - a) for c, u in zip((r, g, b), under[:3])) + (1.0,)


def contrast(x, y):
    def lum(c):
        lin = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c[:3]]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    a, b = sorted((lum(x), lum(y)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def check_contrast(tokens_css):
    tokens_css = re.sub(r'/\*.*?\*/', '', tokens_css, flags=re.S)
    light = custom_properties(rule_block(tokens_css, ':root'))
    dark = dict(light, **custom_properties(rule_block(tokens_css, 'html.dark')))
    inks = [p for p in light if p.startswith('--syntax-') and not p.endswith(('-bg', '-hl'))]
    for mode, props in (('light', light), ('dark', dark)):
        ground = rgba(resolve('--code-bg', props))
        grounds = {'code': ground,
                   'highlighted line': over(rgba(resolve('--syntax-line-hl', props)), ground)}
        for ink in inks:
            colour = rgba(resolve(ink, props))
            for where, g in grounds.items():
                ratio = contrast(colour, g)
                if ratio < 4.5:
                    issue(f'{mode}: {ink} is {ratio:.2f}:1 on the {where} ground (needs 4.5)')


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--hugo', default='hugo', help='the hugo binary (default: hugo)')
    ap.add_argument('--theme', type=Path, default=Path(__file__).resolve().parent.parent,
                    help='the theme directory (default: this script\'s theme)')
    args = ap.parse_args()

    css = args.theme / 'assets' / 'css'
    syntax_css = (css / 'syntax.css').read_text(encoding='utf-8')
    main_css = (css / 'main.css').read_text(encoding='utf-8')
    tokens_css = (css / 'tokens.css').read_text(encoding='utf-8')
    notes_md = (css / 'syntax-upgrade.md').read_text(encoding='utf-8')

    version = chroma_version(args.hugo)
    m = re.search(r'Last verified against Chroma (v[\d.]+)', notes_md)
    verified = m.group(1) if m else 'unknown'
    print(f'Chroma {version} (syntax.css last verified against {verified})')

    emitted = chroma_classes(args.hugo)
    if not emitted:
        print(f'error: {args.hugo} gen chromastyles produced no classes', file=sys.stderr)
        return 2
    mapped = mapped_classes(syntax_css)

    for cls in sorted(set(emitted) - set(mapped) - STRUCTURAL):
        issue(f'unmapped: .{cls} ({emitted[cls]}) is emitted but syntax.css does not colour it')
    for cls in sorted(set(mapped) - set(emitted)):
        issue(f'stale: syntax.css maps .{cls} ({mapped[cls] or "no name"}), which no style emits')
    for cls in sorted(set(mapped) & set(emitted)):
        if mapped[cls] and mapped[cls] != emitted[cls]:
            issue(f'renamed: .{cls} is {emitted[cls]} in Chroma but {mapped[cls]} in syntax.css')
    for cls in sorted(STRUCTURAL):
        if cls not in emitted:
            issue(f'structural: .{cls} is no longer emitted; main.css may lay out a dead class')
        elif not re.search(rf'\.{cls}\b', main_css):
            issue(f'structural: .{cls} is emitted but main.css does not lay it out')

    check_contrast(tokens_css)

    if version != verified:
        issue(f'version: update "Last verified against Chroma" in syntax-upgrade.md to {version} '
              'once the checks and the visual pass are done')

    for message in issues:
        print(message)
    if not issues:
        print(f'ok: {len(emitted)} token classes mapped, inks clear 4.5:1 in both modes')
    return 1 if issues else 0


if __name__ == '__main__':
    sys.exit(main())
