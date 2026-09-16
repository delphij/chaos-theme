# Noto Sans Mono (Latin subset)

- **Project**: [Noto Sans Mono](https://fonts.google.com/noto/specimen/Noto+Sans+Mono)
- **Version**: 2.014
- **License**: SIL Open Font License 1.1 (see `LICENSE`). The upstream copyright
  line declares no Reserved Font Name, so the subset keeps the original family
  name; glyph outlines are upstream's and are not modified.
- **Purpose**: Latin/numeral layer for `--font-mono` — inline `<code>`, code
  blocks, taxonomy count pills and archive dates.

## Why a subset

`unicode-range` restricts this face to Latin-1 plus a handful of typographic
punctuation, so it never sits on the CJK path: Chinese comments inside code
blocks fall straight through to the system CJK font. The whole file is ~16 KB
and carries a `wght` 400-700 variable axis, which is smaller than shipping two
static weights (~17 KB in two requests) and avoids synthetic bolding.

## How to Update

Requires `fonttools[woff]` (`pip install 'fonttools[woff]'`):

```bash
VERSION=2.014
RANGES="U+0000-00FF,U+2010-2015,U+2018-201F,U+2026,U+2030,U+2032-2033,U+20AC,U+2190-2193,U+2212,U+2260,U+2264-2265"
DEST="themes/chaos/static/_3p/noto-sans-mono/${VERSION}"

curl -sSL -o /tmp/NotoSansMono.ttf \
  "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansmono/NotoSansMono%5Bwdth,wght%5D.ttf"
curl -sSL -o "${DEST}/LICENSE" \
  "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansmono/OFL.txt"

# Pin the width axis, keep weight 400-700, then subset to the Latin ranges.
fonttools varLib.instancer /tmp/NotoSansMono.ttf wdth=100 wght=400:700 -o /tmp/NotoSansMono-400-700.ttf
pyftsubset /tmp/NotoSansMono-400-700.ttf \
  --unicodes="${RANGES}" \
  --flavor=woff2 \
  --output-file="${DEST}/noto-sans-mono-latin.woff2"
```

Keep `unicode-range` in the `@font-face` rule in `assets/css/main.css` in sync
with `RANGES` above.

## Caching

The versioned path makes this file safe to serve with
`Cache-Control: public, max-age=31536000, immutable`.

One caveat that does not apply to the other vendored dependencies: they ship
upstream bytes verbatim, so the upstream version fully identifies them. This one
is a *subset*, so the directory name must identify the **artifact**, not just the
upstream release. If the subset changes while upstream stays at 2.014 — widening
`unicode-range`, keeping a different axis range, adding glyphs — copy the
directory to a new name (`2.014-2`, `2.014-3`, ...) and update the `url()` in
`assets/css/main.css`. Never re-subset in place: clients holding the old bytes
would not see the change for up to a year.

Do not gzip/brotli woff2 on the wire; it is already Brotli-compressed internally.

The `@font-face` rule deliberately omits a `local()` source: a locally installed
copy would most likely be a single static weight, which would then be synthetic-
bolded for the 600/700 uses. 16 KB is cheaper than getting that wrong.
