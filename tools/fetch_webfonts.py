#!/usr/bin/env python3
"""Fetch and assemble pinned woff2 webfont slices from a JSON descriptor.

Reads a JSON descriptor (default: `themes/chaos/assets/data/webfonts.json`,
shared with the Hugo opt-in partial `head/webfonts.html`), verifies each
entry's pinned SHA-512 checksum before touching disk, and installs atomically
under:

    <out>/<slug>/<version>/
      font.css
      *.woff2
      LICENSE* (preserved from upstream)
      .ready

Two entry types are supported:
  - `type: "npm"` (default): pure Python stdlib; downloads a pre-sliced npm
    tarball, extracts only the `.woff2` files referenced by its CSS entry, and
    emits a compact `font.css`.
  - `type: "otf"`: downloads a single pinned OTF/TTF file (e.g. Adobe's
    `SourceHanSerifCN-Regular.otf`) and slices it into `.woff2` unicode-range
    chunks using `fonttools` + `brotli`, preserving full horizontal & vertical
    OpenType tables (`vert,vrt2,vhal,vkrn,vpal,halt,kern,palt,locl,ccmp`) and
    locking core punctuation/ASCII into slice 0 so vertical glyph
    substitution and `text-spacing-trim` work across adjacent punctuation.

Subsequent runs skip any font whose `<slug>/<version>/.ready` marker already
matches `(sha512, version, type, url_base, css_schema)` with zero network calls
(and without needing `fonttools`). Pass `--force` to rebuild.
"""

from __future__ import annotations

import argparse
import base64
from concurrent.futures import ProcessPoolExecutor
import hashlib
import io
import json
import os
import posixpath
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

USER_AGENT = "chaos-fetch-webfonts/1.0 (+https://github.com/delphij/chaos-theme)"
DEFAULT_DESCRIPTOR = Path(__file__).resolve().parent.parent / "assets" / "data" / "webfonts.json"
DEFAULT_FREQ_DICT = Path(__file__).resolve().parent / "vendor" / "jieba" / "dict.txt"
CSS_SCHEMA = 1
BASE32HEX = "0123456789abcdefghijklmnopqrstuv"

# Han-only unicode ranges for `--font-em` emphasis aliases (matching tokens.css).
# Excludes ASCII/Latin (so `var(--font-em-latin)` supplies true italic) and
# full-width CJK punctuation (so body sans-serif keeps OpenType `chws` trimming).
HAN_EM_RANGES: tuple[tuple[int, int], ...] = (
    (0x2E80, 0x2FDF),
    (0x3005, 0x3007),
    (0x3021, 0x3029),
    (0x3038, 0x303B),
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
    (0x20000, 0x323AF),
)

LICENSE_FILENAMES = {
    "LICENSE",
    "LICENSE.txt",
    "LICENSE.md",
    "OFL.txt",
    "ARPHICPL.TXT",
    "NOTICE",
}

PRESERVED_OT_FEATURES = [
    "vert",
    "vrt2",
    "vhal",
    "vkrn",
    "vpal",
    "halt",
    "kern",
    "palt",
    "locl",
    "ccmp",
    "liga",
]

COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
FONT_FACE_RE = re.compile(r"@font-face\s*\{([^}]*)\}", re.S | re.I)
WOFF2_URL_RE = re.compile(
    r"url\(\s*['\"]?([^)'\"]+\.woff2)['\"]?\s*\)(?:\s*format\(\s*['\"]woff2['\"]\s*\))?",
    re.I,
)
SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def encode_b32(raw: bytes) -> str:
    return base64.b32encode(raw).decode("ascii").rstrip("=").lower()


def cache_key_from_sha512(sha512: str) -> str:
    """Derive a full 103-char lowercase RFC 4648 base32 key from `sha512-...`."""
    _, _, b64 = sha512.partition("-")
    return encode_b32(base64.b64decode(b64))


def cache_key_from_url(url: str) -> str:
    """Derive a full 103-char lowercase RFC 4648 base32 key from a URL's SHA-512."""
    return encode_b32(hashlib.sha512(url.encode("utf-8")).digest())


def default_cache_dir() -> Path:
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg) if xdg else Path.home() / ".cache"
    return base / "chaos-webfonts"


def http_get_bytes(url: str, timeout: int = 120) -> bytes:
    if not url.startswith("https://"):
        raise ValueError(f"Refusing non-HTTPS URL: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def verify_sha512(data: bytes, expected_integrity: str) -> None:
    if not expected_integrity:
        raise ValueError("Descriptor entry is missing required `sha512` checksum")
    algo, _, expected = expected_integrity.partition("-")
    if algo != "sha512" or not expected:
        raise ValueError(f"Unsupported checksum format (expected sha512-...): {expected_integrity}")
    actual = base64.b64encode(hashlib.sha512(data).digest()).decode("ascii")
    if actual != expected:
        raise ValueError(
            f"SHA-512 checksum mismatch! expected={expected[:16]}... actual={actual[:16]}..."
        )


def fetch_verified_bytes(url: str, sha512: str, cache_path: Path, label: str) -> bytes:
    """Return verified upstream bytes, reusing `cache_path` whenever its SHA-512
    matches (even under `--force`), and re-downloading whenever missing or
    corrupted/mismatched."""
    if cache_path.is_file():
        cached = cache_path.read_bytes()
        try:
            verify_sha512(cached, sha512)
            print(f"CACHE {label} <- {cache_path}")
            return cached
        except ValueError:
            print(
                f"CACHE-STALE {label}: checksum mismatch in {cache_path}, re-fetching",
                file=sys.stderr,
            )

    print(f"FETCH {label} <- {url}")
    data = http_get_bytes(url)
    verify_sha512(data, sha512)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{cache_path.name}-", dir=cache_path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp_name, cache_path)
    except Exception:
        Path(tmp_name).unlink(missing_ok=True)
        raise
    return data


def validate_segment(label: str, value: str) -> str:
    if not value or value in (".", "..") or not SAFE_NAME_RE.match(value):
        raise ValueError(f"Unsafe {label!r} in descriptor: {value!r}")
    return value


def encode_base32hex(n: int) -> str:
    """Encode a non-negative integer in lowercase RFC 4648 base32hex (0-9a-v).
    Case-insensitive filesystem safe; keeps 0-9 for the 10 hottest slices,
    1-char names for all 32 hottest slices (Core Punct + Tier 1 + Tier 2),
    and 2-char names up to 1023 slices."""
    if n == 0:
        return "0"
    chars: list[str] = []
    while n:
        n, rem = divmod(n, 32)
        chars.append(BASE32HEX[rem])
    return "".join(reversed(chars))


def format_unicode_range(codepoints: list[int]) -> str:
    """Compact a sorted list of Unicode codepoints into a CSS unicode-range string."""
    if not codepoints:
        return ""
    ranges: list[str] = []
    start = prev = codepoints[0]
    for cp in codepoints[1:]:
        if cp == prev + 1:
            prev = cp
        else:
            ranges.append(f"U+{start:X}" if start == prev else f"U+{start:X}-{prev:X}")
            start = prev = cp
    ranges.append(f"U+{start:X}" if start == prev else f"U+{start:X}-{prev:X}")
    return ",".join(ranges)


def is_cjk_ideograph(cp: int) -> bool:
    return (
        0x3400 <= cp <= 0x4DBF
        or 0x4E00 <= cp <= 0x9FFF
        or 0xF900 <= cp <= 0xFAFF
        or 0x20000 <= cp <= 0x323AF
    )


def is_core_punct_or_ascii(cp: int) -> bool:
    """Core ASCII, CJK/vertical punctuation, and emphasis marks locked into slice 0."""
    return (
        0x0020 <= cp <= 0x007E
        or cp == 0x00B7  # middle dot ·
        or 0x2000 <= cp <= 0x206F  # general punctuation (—, …, “”, etc.)
        or cp in (0x25CB, 0x25CF, 0x25E6)  # circle/dot emphasis marks (○, ●, ◦)
        or 0x3000 <= cp <= 0x303F  # CJK symbols & punctuation (、。「」『』《》)
        or 0xFE10 <= cp <= 0xFE1F  # vertical forms
        or 0xFE30 <= cp <= 0xFE4F  # CJK compatibility forms
        or 0xFF00 <= cp <= 0xFFEF  # halfwidth & fullwidth forms (：；！？（）)
    )


def gb2312_tier(cp: int) -> int:
    """Return 1 for GB2312 Level-1 (3755 common chars), 2 for Level-2, 3 otherwise."""
    try:
        b = chr(cp).encode("gb2312")
    except UnicodeEncodeError:
        return 3
    if len(b) == 2:
        if 0xB0 <= b[0] <= 0xD7:
            return 1
        if 0xD8 <= b[0] <= 0xF7:
            return 2
    return 3


def load_static_han_freq(dict_path: Path = DEFAULT_FREQ_DICT) -> dict[int, int]:
    """Load deterministic Han character frequencies from the theme's vendored
    `tools/vendor/jieba/dict.txt` (word frequencies aggregated per Han char).
    Guarantees reproducible, immutable-cache-safe slices across all machines."""
    if not dict_path.is_file():
        return {}
    freq: dict[int, int] = {}
    with dict_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 2 or not parts[1].isdigit():
                continue
            weight = int(parts[1])
            for ch in parts[0]:
                cp = ord(ch)
                if is_cjk_ideograph(cp):
                    freq[cp] = freq.get(cp, 0) + weight
    return freq


def build_tiered_slices(all_cps: list[int], corpus_freq: dict[int, int]) -> list[list[int]]:
    """Build frequency-tiered unicode slices:
    - Slice 0: Core ASCII + all CJK/vertical punctuation (locked together for
      OpenType `vert`/`vrt2`/`vhal`/`vkrn` across adjacent punctuation).
    - Han Tier 1 (top 1000): 250-char chunks (hit on almost every post, cached).
    - Han Tier 2 (next 2500): 128-char chunks (common vocabulary).
    - Han Tier 3 (remaining rare Han): 64-char chunks (tiny fetch on rare chars).
    - Last slice: Remaining non-Han symbols (Kana, Cyrillic, box-drawing, etc.).
    """
    core_punct = [cp for cp in all_cps if is_core_punct_or_ascii(cp)]
    other_non_han = [
        cp for cp in all_cps if not is_cjk_ideograph(cp) and not is_core_punct_or_ascii(cp)
    ]
    han = [cp for cp in all_cps if is_cjk_ideograph(cp)]

    # Sort Han by: corpus frequency descending, then GB2312 tier ascending, then codepoint.
    han.sort(key=lambda cp: (-corpus_freq.get(cp, 0), gb2312_tier(cp), cp))

    slices: list[list[int]] = []
    if core_punct:
        slices.append(sorted(core_punct))

    tier1 = han[:1000]
    tier2 = han[1000:3500]
    tier3 = han[3500:]

    for i in range(0, len(tier1), 250):
        slices.append(sorted(tier1[i : i + 250]))
    for i in range(0, len(tier2), 128):
        slices.append(sorted(tier2[i : i + 128]))
    for i in range(0, len(tier3), 64):
        slices.append(sorted(tier3[i : i + 64]))
    other_non_han.sort()
    for i in range(0, len(other_non_han), 128):
        slices.append(other_non_han[i : i + 128])
    return slices


def intersect_unicode_range(urange_str: str, allowed: tuple[tuple[int, int], ...]) -> str:
    """Intersect a CSS unicode-range string with `allowed` (lo, hi) intervals."""
    out: list[tuple[int, int]] = []
    for token in urange_str.split(","):
        token = token.strip().upper()
        if not token.startswith("U+"):
            continue
        body = token[2:]
        if "?" in body:
            lo = int(body.replace("?", "0"), 16)
            hi = int(body.replace("?", "F"), 16)
        elif "-" in body:
            a, b = body.split("-", 1)
            lo, hi = int(a, 16), int(b, 16)
        else:
            lo = hi = int(body, 16)
        for alo, ahi in allowed:
            ilo = max(lo, alo)
            ihi = min(hi, ahi)
            if ilo <= ihi:
                out.append((ilo, ihi))
    if not out:
        return ""
    out.sort()
    merged: list[list[int]] = [[out[0][0], out[0][1]]]
    for lo, hi in out[1:]:
        if lo <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    return ",".join(
        f"U+{lo:X}" if lo == hi else f"U+{lo:X}-{hi:X}" for lo, hi in merged
    )


def build_em_alias_rules(rules: list[str], family: str, em_size_adjust: str = "106%") -> list[str]:
    """Emit Han-only `italic` + `size-adjust` `@font-face` aliases reusing
    the same `.woff2` slice URLs for `--font-em` (zero extra network/disk cost)."""
    em_family = f"{family} Em"
    em_rules: list[str] = []
    for rule in rules:
        src_m = re.search(r"src:(url\([^)]+\)\s*format\('woff2'\))", rule)
        ur_m = re.search(r"unicode-range:([^;}]+)", rule)
        if not src_m or not ur_m:
            continue
        han_ur = intersect_unicode_range(ur_m.group(1), HAN_EM_RANGES)
        if not han_ur:
            continue
        em_rules.append(
            f"@font-face{{font-family:'{em_family}';font-style:italic;font-weight:400;"
            f"size-adjust:{em_size_adjust};font-display:swap;src:{src_m.group(1)};unicode-range:{han_ur}}}"
        )
    return em_rules


def process_css(
    css_text: str,
    css_member_dir: str,
    url_base: str,
    em_family: str = "",
) -> tuple[str, dict[str, str]]:
    """Strip comments and non-woff2 fallbacks, rewrite URLs, and collect woff2 map."""
    cleaned = COMMENT_RE.sub("", css_text)
    woff2_members: dict[str, str] = {}
    rules: list[str] = []

    for match in FONT_FACE_RE.finditer(cleaned):
        body = match.group(1)
        url_match = WOFF2_URL_RE.search(body)
        if not url_match:
            continue

        rel_href = url_match.group(1).strip()
        tar_path = posixpath.normpath(posixpath.join(css_member_dir, rel_href))
        if tar_path.startswith("/") or tar_path.startswith(".."):
            raise ValueError(f"Unsafe relative font path in CSS: {rel_href!r}")
        filename = validate_segment("woff2 filename", posixpath.basename(tar_path))
        woff2_members[tar_path] = filename

        decls: list[str] = []
        has_display = False
        for raw_decl in body.split(";"):
            raw_decl = raw_decl.strip()
            if not raw_decl or ":" not in raw_decl:
                continue
            prop, val = raw_decl.split(":", 1)
            prop = prop.strip().lower()
            val = re.sub(r"\s+", " ", val.strip())
            if prop == "src":
                decls.append(f"src:url('{filename}') format('woff2')")
            elif prop == "font-display":
                decls.append("font-display:swap")
                has_display = True
            elif prop == "unicode-range":
                val = re.sub(r"\s*,\s*", ",", val)
                decls.append(f"unicode-range:{val}")
            else:
                decls.append(f"{prop}:{val}")
        if not has_display:
            decls.append("font-display:swap")
        rules.append("@font-face{" + ";".join(decls) + "}")

    if not rules:
        raise RuntimeError("No @font-face rules with .woff2 sources found in CSS")

    if em_family:
        rules.extend(build_em_alias_rules(rules, em_family))

    return "\n".join(rules) + "\n", woff2_members


def assemble_from_npm(
    spec: dict, tmp_dir: Path, url_base: str, cache_dir: Path
) -> tuple[int, int, list[str], str]:
    css_entry = str(spec.get("css", ""))
    tarball_url = str(spec.get("tarball", ""))
    sha512 = str(spec.get("sha512", ""))
    if not css_entry or not tarball_url or not sha512:
        raise ValueError(f"Incomplete npm descriptor entry for {spec.get('slug')!r}")

    label = f"{spec['slug']}@{spec['version']}"
    cache_path = cache_dir / cache_key_from_sha512(sha512)
    tar_bytes = fetch_verified_bytes(tarball_url, sha512, cache_path, label)

    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:gz") as tf:
        members = {m.name: m for m in tf.getmembers() if m.isfile()}

        css_member = f"package/{css_entry.lstrip('/')}"
        if css_member not in members:
            raise FileNotFoundError(
                f"CSS entry {css_member!r} not found in {spec['slug']}@{spec['version']}"
            )
        css_text = tf.extractfile(members[css_member]).read().decode("utf-8")
        css_dir = posixpath.dirname(css_member)
        em_family = str(spec.get("family", "")) if spec.get("role") in ("kai", "serif") else ""
        minified_css, woff2_map = process_css(css_text, css_dir, url_base, em_family=em_family)

        total_bytes = 0
        for tar_path, filename in sorted(woff2_map.items()):
            if tar_path not in members:
                raise FileNotFoundError(f"Referenced slice {tar_path!r} missing from tarball")
            blob = tf.extractfile(members[tar_path]).read()
            (tmp_dir / filename).write_bytes(blob)
            total_bytes += len(blob)

        licenses_saved: list[str] = []
        for lic in sorted(LICENSE_FILENAMES):
            lic_member = f"package/{lic}"
            if lic_member in members:
                (tmp_dir / lic).write_bytes(tf.extractfile(members[lic_member]).read())
                licenses_saved.append(lic)

    return len(woff2_map), total_bytes, licenses_saved, minified_css


_WORKER_FONT_BYTES: bytes = b""
_WORKER_FEATURES: list[str] = []


def _init_slice_worker(source_path: str, features: list[str]) -> None:
    import logging

    global _WORKER_FONT_BYTES, _WORKER_FEATURES
    logging.getLogger("fontTools").setLevel(logging.ERROR)
    _WORKER_FONT_BYTES = Path(source_path).read_bytes()
    _WORKER_FEATURES = list(features)


def _slice_one_chunk(task: tuple[int, list[int], str, str, str, str]) -> tuple[int, int, str]:
    from fontTools import subset as ft_subset
    from fontTools.ttLib import TTFont

    idx, cps, tmp_dir_str, family, filename, size_adjust = task
    out_woff2 = Path(tmp_dir_str) / filename
    options = ft_subset.Options(
        flavor="woff2",
        layout_features=_WORKER_FEATURES,
        desubroutinize=False,
        drop_tables=["DSIG"],
        hinting=False,
    )
    font = TTFont(io.BytesIO(_WORKER_FONT_BYTES))
    subsetter = ft_subset.Subsetter(options=options)
    subsetter.populate(unicodes=cps)
    subsetter.subset(font)
    font.save(str(out_woff2))
    font.close()

    size = out_woff2.stat().st_size
    urange = format_unicode_range(cps)
    sa = f"size-adjust:{size_adjust};" if size_adjust else ""
    rule = (
        f"@font-face{{font-family:'{family}';font-style:normal;font-weight:400;"
        f"{sa}font-display:swap;src:url('{filename}') format('woff2');unicode-range:{urange}}}"
    )
    return idx, size, rule


def assemble_from_otf(
    spec: dict,
    tmp_dir: Path,
    url_base: str,
    cache_dir: Path,
    jobs: int,
) -> tuple[int, int, list[str], str]:
    try:
        import logging

        from fontTools import subset as ft_subset  # noqa: F401
        from fontTools.ttLib import TTFont

        logging.getLogger("fontTools").setLevel(logging.ERROR)
    except ImportError as exc:
        raise RuntimeError(
            "Slicing `type: otf` fonts requires `fonttools` and `brotli` "
            "(e.g. `pip install fonttools brotli`)."
        ) from exc

    otf_url = str(spec.get("url", ""))
    sha512 = str(spec.get("sha512", ""))
    family = str(spec.get("family", ""))
    if not otf_url or not sha512 or not family:
        raise ValueError(f"Incomplete otf descriptor entry for {spec.get('slug')!r}")

    label = f"{spec['slug']}@{spec['version']}"
    source_path = cache_dir / cache_key_from_sha512(sha512)
    fetch_verified_bytes(otf_url, sha512, source_path, label)

    base_font = TTFont(str(source_path))
    all_cps = sorted(base_font.getBestCmap().keys())
    base_font.close()

    han_freq = load_static_han_freq()
    slices = build_tiered_slices(all_cps, han_freq)
    worker_count = max(1, min(jobs, len(slices)))

    print(
        f"SLICE {label}: {len(all_cps)} codepoints -> "
        f"{len(slices)} woff2 slices (slice 0: {len(slices[0])} core punct/ASCII, "
        f"ranked Han: {len(han_freq)}, jobs: {worker_count})"
    )

    size_adjust = str(spec.get("sizeAdjust", ""))
    em_size_adjust = str(spec.get("emSizeAdjust", "106%"))
    tasks = [
        (idx, cps, str(tmp_dir), family, f"{encode_base32hex(idx)}.woff2", size_adjust)
        for idx, cps in enumerate(slices)
    ]

    if worker_count == 1:
        _init_slice_worker(str(source_path), PRESERVED_OT_FEATURES)
        results = [_slice_one_chunk(t) for t in tasks]
    else:
        with ProcessPoolExecutor(
            max_workers=worker_count,
            initializer=_init_slice_worker,
            initargs=(str(source_path), PRESERVED_OT_FEATURES),
        ) as pool:
            results = list(pool.map(_slice_one_chunk, tasks, chunksize=4))

    results.sort(key=lambda item: item[0])
    total_bytes = sum(size for _, size, _ in results)
    rules = [rule for _, _, rule in results]

    if spec.get("role") in ("kai", "serif"):
        rules.extend(build_em_alias_rules(rules, family, em_size_adjust=em_size_adjust))

    css_text = "\n".join(rules) + "\n"

    licenses_saved: list[str] = []
    lic_url = str(spec.get("licenseUrl", ""))
    if lic_url:
        lic_cache = cache_dir / cache_key_from_url(lic_url)
        if lic_cache.is_file() and lic_cache.stat().st_size > 0:
            lic_bytes = lic_cache.read_bytes()
        else:
            lic_bytes = http_get_bytes(lic_url, timeout=30)
            lic_cache.parent.mkdir(parents=True, exist_ok=True)
            lic_cache.write_bytes(lic_bytes)
        (tmp_dir / "LICENSE.txt").write_bytes(lic_bytes)
        licenses_saved.append("LICENSE.txt")

    return len(slices), total_bytes, licenses_saved, css_text


def build_readme_txt(spec: dict, slice_count: int, licenses_saved: list[str]) -> str:
    """Generate a plain-text provenance & modification notice for the font directory."""
    source_url = str(spec.get("url") or spec.get("tarball") or "")
    lines = [
        f"Font Family: {spec.get('family', '')}",
        f"Version:     {spec.get('version', '')}",
        f"Source:      {source_url}",
        f"SHA-512:     {spec.get('sha512', '')}",
        f"Slices:      {slice_count} WOFF2 unicode-range subsets (base32hex named)",
        "",
        "Modification Notice:",
        "Subsetted into frequency-tiered WOFF2 unicode-range slices with OpenType",
        "layout features preserved by Chaos theme's tools/fetch_webfonts.py.",
        "No glyph outlines were altered.",
    ]
    if licenses_saved:
        lines.extend(["", f"License:     See {', '.join(licenses_saved)} in this directory."])
    return "\n".join(lines) + "\n"


def install_font(
    spec: dict,
    out_dir: Path,
    css_out_dir: Path,
    url_prefix: str,
    force: bool,
    cache_dir: Path,
    jobs: int,
) -> dict:
    slug = validate_segment("slug", str(spec.get("slug", "")))
    version = validate_segment("version", str(spec.get("version", "")))
    kind = str(spec.get("type", "npm"))
    sha512 = str(spec.get("sha512", ""))
    size_adjust = str(spec.get("sizeAdjust", ""))
    em_size_adjust = str(spec.get("emSizeAdjust", "106%"))

    target_dir = out_dir / slug / version
    css_path = css_out_dir / slug / version / "font.css"
    marker_path = target_dir / ".ready"
    url_base = f"{url_prefix.rstrip('/')}/{slug}/{version}" if url_prefix else ""

    if not force and marker_path.is_file() and css_path.is_file():
        try:
            existing = json.loads(marker_path.read_text(encoding="utf-8"))
            if (
                existing.get("sha512") == sha512
                and existing.get("version") == version
                and existing.get("type") == kind
                and existing.get("url_base") == url_base
                and existing.get("css_schema") == CSS_SCHEMA
                and existing.get("size_adjust") == size_adjust
                and existing.get("em_size_adjust") == em_size_adjust
            ):
                print(f"SKIP {slug}@{version} (verified at {target_dir})")
                return existing
        except (OSError, json.JSONDecodeError):
            pass

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / slug).mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(prefix=f".{slug}-{version}-", dir=out_dir / slug))
    try:
        if kind == "npm":
            slice_count, total_bytes, licenses_saved, css_text = assemble_from_npm(
                spec, tmp_dir, url_base, cache_dir
            )
        elif kind == "otf":
            slice_count, total_bytes, licenses_saved, css_text = assemble_from_otf(
                spec, tmp_dir, url_base, cache_dir, jobs
            )
        else:
            raise ValueError(f"Unsupported font descriptor type: {kind!r}")

        (tmp_dir / "README.txt").write_text(
            build_readme_txt(spec, slice_count, licenses_saved),
            encoding="utf-8",
        )

        css_path.parent.mkdir(parents=True, exist_ok=True)
        fd, css_tmp = tempfile.mkstemp(prefix=".font-", suffix=".css", dir=css_path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(css_text)
            os.replace(css_tmp, css_path)
        except Exception:
            Path(css_tmp).unlink(missing_ok=True)
            raise

        info = {
            "slug": slug,
            "family": spec.get("family", ""),
            "role": spec.get("role", ""),
            "type": kind,
            "version": version,
            "sha512": sha512,
            "url_base": url_base,
            "css_schema": CSS_SCHEMA,
            "size_adjust": size_adjust,
            "em_size_adjust": em_size_adjust,
            "css_path": str(css_path),
            "slices": slice_count,
            "woff2_bytes": total_bytes,
            "licenses": licenses_saved,
        }
        (tmp_dir / ".ready").write_text(
            json.dumps(info, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        if target_dir.exists():
            shutil.rmtree(target_dir)
        os.replace(tmp_dir, target_dir)
        print(
            f"OK   {slug}@{version}: {slice_count} woff2 slices "
            f"({total_bytes / 1024 / 1024:.2f} MiB), {css_path} "
            f"({css_path.stat().st_size / 1024:.1f} KiB)"
        )
        return info
    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise


def cleanup_stale(
    specs: list[dict],
    out_dir: Path,
    css_out_dir: Path,
) -> int:
    """Remove any files or directories under `out_dir` and `css_out_dir` that do
    not belong to the active `(slug, version)` entries in the descriptor."""
    expected: dict[str, set[str]] = {}
    for spec in specs:
        slug = validate_segment("slug", str(spec.get("slug", "")))
        version = validate_segment("version", str(spec.get("version", "")))
        expected.setdefault(slug, set()).add(version)

    removed = 0
    for root, keep_top_files in ((out_dir, {"manifest.json"}), (css_out_dir, set())):
        if not root.is_dir():
            continue
        for entry in sorted(root.iterdir()):
            if entry.name in keep_top_files and entry.is_file():
                continue
            if entry.name not in expected or not entry.is_dir():
                if entry.is_dir() and not entry.is_symlink():
                    shutil.rmtree(entry)
                else:
                    entry.unlink()
                print(f"CLEAN {entry}")
                removed += 1
                continue
            for sub in sorted(entry.iterdir()):
                if sub.name not in expected[entry.name] or not sub.is_dir():
                    if sub.is_dir() and not sub.is_symlink():
                        shutil.rmtree(sub)
                    else:
                        sub.unlink()
                    print(f"CLEAN {sub}")
                    removed += 1
    return removed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch and assemble pinned woff2 webfont slices from a JSON descriptor."
    )
    parser.add_argument(
        "--descriptor",
        type=Path,
        default=DEFAULT_DESCRIPTOR,
        help=f"Path to webfonts JSON descriptor (default: {DEFAULT_DESCRIPTOR})",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("static/_fonts"),
        help="Output directory for .woff2 slices and licenses (default: static/_fonts)",
    )
    parser.add_argument(
        "--css-out",
        type=Path,
        default=Path("assets/_fonts"),
        help="Output directory for Hugo Pipes font.css sheets (default: assets/_fonts)",
    )
    parser.add_argument(
        "--url-prefix",
        default=None,
        help="Override descriptor urlPrefix (default: descriptor's urlPrefix, usually /_fonts)",
    )
    parser.add_argument(
        "--jobs",
        "-j",
        type=int,
        default=os.cpu_count() or 1,
        help="Parallel worker processes for OTF/TTF slicing (default: CPU count)",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=default_cache_dir(),
        help="Directory for SHA-512 verified upstream download cache (default: $XDG_CACHE_HOME/chaos-webfonts or ~/.cache/chaos-webfonts)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild slices even if target directory is already verified (reuses SHA-512 verified cache)",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove stale font directories/files under --out and --css-out not in the descriptor",
    )
    args = parser.parse_args(argv)

    descriptor = json.loads(args.descriptor.read_text(encoding="utf-8"))
    url_prefix = descriptor.get("urlPrefix", "/_fonts") if args.url_prefix is None else args.url_prefix
    specs = descriptor.get("fonts") or []
    if not specs:
        print(f"No fonts defined in {args.descriptor}", file=sys.stderr)
        return 2

    results: list[dict] = []
    for spec in specs:
        results.append(
            install_font(
                spec=spec,
                out_dir=args.out,
                css_out_dir=args.css_out,
                url_prefix=url_prefix,
                force=args.force,
                cache_dir=args.cache_dir,
                jobs=args.jobs,
            )
        )

    manifest_path = args.out / "manifest.json"
    manifest_path.write_text(
        json.dumps({"urlPrefix": url_prefix, "fonts": results}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    if args.cleanup:
        cleanup_stale(specs, args.out, args.css_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
