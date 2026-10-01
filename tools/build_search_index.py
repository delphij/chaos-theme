#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_search_index.py: Offline search index generator for Chaos theme.

Scans Hugo content directory, extracts post metadata, performs Chinese & English
tokenization using Jieba, and generates a compact inverted index JSON file
for client-side full-text search. The index is two strings, the terms and
their posting lists (see pack_index); assets/js/search.js is the decoder.
"""

import argparse
import glob
import json
import os
import re
import sys
import warnings
from collections import defaultdict

# Suppress invalid escape sequence warnings from vendored jieba on Python 3.12+
warnings.filterwarnings("ignore", category=SyntaxWarning, module=".*jieba.*")

# Try importing system-installed jieba first; fallback to vendored copy
try:
    import jieba
except ImportError:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    vendor_dir = os.path.join(script_dir, "vendor")
    if os.path.exists(os.path.join(vendor_dir, "jieba")):
        sys.path.insert(0, vendor_dir)
        import jieba
    else:
        sys.stderr.write(
            "Error: 'jieba' not found in system Python or themes/chaos/tools/vendor/jieba.\n"
        )
        sys.exit(1)

# Regular expression for exact cryptographic hashes (MD5, SHA-1, SHA-256)
HEX_HASH_RE = re.compile(r"^[0-9a-fA-F]{32}$|^[0-9a-fA-F]{40}$|^[0-9a-fA-F]{64}$")


def load_stopwords_file(filepath: str) -> set:
    """Reads stopwords from file, ignoring comments starting with '#' and blank lines."""
    words = set()
    if not filepath or not os.path.isfile(filepath):
        return words
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                words.add(line.lower())
    except Exception as e:
        sys.stderr.write(f"Warning: Failed to read stopwords from {filepath}: {e}\n")
    return words


def clean_markdown(text: str) -> str:
    """Strips Markdown syntax, shortcodes, and HTML tags from text."""
    # Remove Hugo shortcodes {{< ... >}} or {{% ... %}}
    text = re.sub(r"\{\{[%<].*?[%>]\}\}", " ", text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove images ![alt](url)
    text = re.sub(r"!\[.*?\]\(.*?\)", " ", text)
    # Convert links [text](url) -> text
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    # Remove code fence markers (```lang ... ```) but preserve technical code content!
    text = re.sub(r"```[a-zA-Z0-9_\-\.]*", " ", text)
    # Remove inline code backticks while preserving code identifier text
    text = re.sub(r"`([^`]+)`", r" \1 ", text)
    text = re.sub(r"`", " ", text)
    # Remove headings marker
    text = re.sub(r"^[#\s]+", " ", text, flags=re.MULTILINE)
    # Remove blockquotes, table borders, bold/italic markers
    text = re.sub(r"[*_~>|=-]", " ", text)
    # Collapse multiple whitespaces
    return re.sub(r"\s+", " ", text).strip()


def parse_frontmatter(content: str):
    """Extracts the front matter fields the index needs, and the body.

    Read with regular expressions rather than a YAML or TOML parser, so that
    the script needs nothing beyond the standard library and the vendored
    jieba. That covers what posts are written with -- `key: value` or
    `key = value`, inline arrays and YAML block lists -- and not nested tables
    or multi-line strings.
    """
    fm_match = re.match(r"^(?:---|\+\+\+)\s*\n([\s\S]*?)\n(?:---|\+\+\+)\s*\n([\s\S]*)$", content)
    if not fm_match:
        return {}, content

    fm_raw, body = fm_match.groups()

    def unquote(value: str) -> str:
        return value.strip("\"' ")

    def scalar(key: str) -> str:
        """The value of `key` (a regex, so `a|b` reads either), or an empty string."""
        m = re.search(rf'^(?:{key})\s*[:=]\s*["\']?(.*?)["\']?\s*$', fm_raw, re.MULTILINE | re.IGNORECASE)
        return unquote(m.group(1)) if m else ""

    def flag(key: str) -> bool:
        return scalar(key).lower() == "true"

    def items(key: str) -> list:
        """The values of an inline array `key: [a, b]`, or of a YAML block list."""
        m = re.search(rf"^[ \t]*{key}\s*[:=]\s*\[(.*?)\]", fm_raw, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        if m:
            values = m.group(1).split(",")
        else:
            m = re.search(rf"^[ \t]*{key}[ \t]*:[ \t]*\n((?:[ \t]*-[ \t]+.*(?:\n|$))+)", fm_raw, re.MULTILINE | re.IGNORECASE)
            values = re.findall(r"^[ \t]*-[ \t]+(.*)$", m.group(1), re.MULTILINE) if m else []
        return [unquote(v) for v in values if unquote(v)]

    meta = {
        "title": scalar("title"),
        "date": scalar("date").split("T")[0],
        "description": scalar("description"),
        "slug": scalar("url|slug"),
        "tags": items("tags"),
        "categories": items("categories"),
        "draft": flag("draft"),
        # Three ways to keep a post out, or down. noindex / private / robots:
        # out of search engines and of this index alike.
        "noindex": flag("noindex") or flag("private") or "noindex" in scalar("robots").lower(),
        # searchHidden / search_hidden / search = false: out of this index only.
        "search_hidden": flag("searchHidden") or flag("search_hidden") or scalar("search").lower() == "false",
        # deprecated / outdated: indexed, but ranked lower and badged.
        "deprecated": flag("deprecated") or flag("outdated"),
    }
    return meta, body


def compute_post_url(filepath: str, base_content_dir: str, meta: dict, base_url: str) -> str:
    """Computes clean URL matching Hugo's default output path."""
    if meta.get("slug", "").startswith("/"):
        return meta["slug"]

    rel = os.path.relpath(filepath, base_content_dir)
    # Strip posts/ prefix if present
    if rel.startswith("posts/"):
        rel = rel[6:]

    if rel.endswith("/index.md"):
        slug_path = rel[:-9]
    elif rel.endswith(".md"):
        slug_path = rel[:-3]
    else:
        slug_path = rel

    # Hugo defaults to /posts/<slug>/
    url = f"/posts/{slug_path}/"
    if base_url and base_url != "/":
        url = base_url.rstrip("/") + url
    return url


# Common technical terms with symbols that should be preserved intact
TECH_SYMBOLS = [
    "google+", "c++", "c#", ".net", "notepad++", "g++", "clang++", "tcp/ip"
]
for _ts in TECH_SYMBOLS:
    jieba.add_word(_ts)


def is_valid_token(w: str, stop_words: set) -> bool:
    """Evaluates if a token is valid for the search inverted index.

    Filters out:
    1. Pure punctuation or strings lacking any alphanumeric or CJK character.
    2. Words in the active stop words set.
    3. Machine-generated hashes (MD5, SHA-1, SHA-256) and extreme token lengths (> 64).
    4. Pure integers whose significant digits < 3 (filters 0-9 and leading-zero fragments,
       while preserving HTTP status codes like 404, RFC numbers like 821/3522, and years).
    5. Anything holding whitespace, which separates the terms in the index.
    """
    if not w or w in stop_words:
        return False
    # Terms are joined by spaces in the index, so none may hold whitespace
    if any(ch.isspace() for ch in w):
        return False
    # Must contain at least one semantic character (CJK, Latin letter, or digit)
    if not re.search(r"[\u4e00-\u9fa5a-zA-Z0-9]", w):
        return False
    # Exclude machine hashes and extreme run lengths
    if len(w) > 64 or HEX_HASH_RE.match(w):
        return False
    # Pure numbers: require at least 3 significant digits
    if w.isdigit():
        if len(w.lstrip("0")) < 3:
            return False
    return True


# The 64 digits of a posting list. assets/js/search.js holds the same string.
POSTING_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"


def encode_postings(doc_ids: list) -> str:
    """Encodes ascending doc ids as text: the gap from each id to the next, less one.

    A gap is written least significant digit first in base 32; a digit with 32
    added has another after it. Nearby ids -- most of them, in a list sorted by
    date -- take one character each instead of a decimal number and a comma.
    """
    out = []
    prev = -1
    for doc_id in doc_ids:
        gap = doc_id - prev - 1
        prev = doc_id
        while gap > 31:
            out.append(POSTING_DIGITS[32 | (gap & 31)])
            gap >>= 5
        out.append(POSTING_DIGITS[gap])
    return "".join(out)


def pack_index(index: dict) -> dict:
    """Packs {term: [doc ids]} into two space-joined strings, in the same order.

    Two strings parse far faster in the browser than an array per term, and
    search.js decodes a posting list only when a query asks for its term. The
    terms are sorted so that the same content always builds the same file.
    """
    terms = sorted(index)
    return {
        "terms": " ".join(terms),
        "postings": " ".join(encode_postings(index[term]) for term in terms),
    }


def tokenize(text: str, stop_words: set) -> set:
    """Segments text into lowercase searchable tokens, skipping stop words and invalid tokens."""
    tokens = set()
    if not text:
        return tokens

    # Pre-extract alphanumeric tokens with technical symbols (e.g. Google+, C++, C#, .NET)
    for sym in re.findall(r"\b[a-zA-Z0-9_\-\.]+(?:\+\+|[+#])", text):
        s = sym.lower()
        if is_valid_token(s, stop_words):
            tokens.add(s)

    for word in jieba.cut_for_search(text):
        w = word.strip().lower()
        if is_valid_token(w, stop_words):
            tokens.add(w)
    return tokens



def main():
    parser = argparse.ArgumentParser(description="Build offline search index for Chaos theme.")
    parser.add_argument("--content", default="content", help="Path to Hugo content directory (default: content)")
    parser.add_argument("--output", default="assets/search-index.json", help="Path to output Tier 1 / core search-index.json (default: assets/search-index.json)")
    parser.add_argument("--output-body", default="", help="Path to output Tier 2 / body search-index.json (default: auto derived as <stem>-body.json)")
    parser.add_argument("--single-file", action="store_true", help="Generate legacy monolithic single-file index instead of two-tier")
    parser.add_argument("--base-url", default="/", help="Base URL for site links (default: /)")
    parser.add_argument("--max-body-chars", type=int, default=0, help="Max body characters to index per post; 0 indexes the whole body (default: 0)")
    parser.add_argument("--stopwords", default="", help="Path to custom stopwords file (overrides default)")
    parser.add_argument("--extra-stopwords", default="", help="Path to extra stopwords file (augments default)")
    args = parser.parse_args()

    content_dir = os.path.abspath(args.content)
    if not os.path.isdir(content_dir):
        sys.stderr.write(f"Content directory not found: {content_dir}\n")
        sys.exit(1)

    output_path = os.path.abspath(args.output)
    if args.output_body:
        output_body_path = os.path.abspath(args.output_body)
    else:
        root, ext = os.path.splitext(output_path)
        output_body_path = f"{root}-body{ext or '.json'}"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_stopwords_file = os.path.join(script_dir, "stopwords.txt")

    # --stopwords replaces the theme's list outright, so the site's own
    # data/stopwords.txt is added only to the default one.
    stop_words = load_stopwords_file(args.stopwords or default_stopwords_file)
    if not args.stopwords:
        auto_site_stopwords = os.path.join(os.path.dirname(content_dir), "data", "stopwords.txt")
        site_words = load_stopwords_file(auto_site_stopwords)
        if site_words:
            print(f"Loaded {len(site_words)} extra stopwords from {auto_site_stopwords}")
            stop_words.update(site_words)

    if args.extra_stopwords:
        extra_words = load_stopwords_file(args.extra_stopwords)
        if extra_words:
            print(f"Loaded {len(extra_words)} extra stopwords from {args.extra_stopwords}")
            stop_words.update(extra_words)

    print(f"Active stop words: {len(stop_words)} terms")
    print(f"Scanning markdown files in {content_dir}...")
    files = glob.glob(os.path.join(content_dir, "**", "*.md"), recursive=True)

    parsed_posts = []
    for filepath in files:
        # A section's or the home page's own content, not a post
        if os.path.basename(filepath) == "_index.md":
            continue
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to read {filepath}: {e}\n")
            continue

        meta, body = parse_frontmatter(content)
        if meta.get("draft", False):
            continue
        if meta.get("noindex", False) or meta.get("search_hidden", False):
            continue

        title = meta.get("title", "")
        if not title:
            title = os.path.splitext(os.path.basename(filepath))[0]

        date = meta.get("date", "")
        tags = meta.get("tags", [])
        # A tag with a symbol in it (C++, C#) is taught to jieba as one word.
        # Every post is read before any is tokenized below, so the word holds
        # in all of them, whichever post carried the tag.
        for tag in tags:
            if any(ch in tag for ch in "+#"):
                jieba.add_word(tag.strip().lower())
        categories = meta.get("categories", [])
        url = compute_post_url(filepath, content_dir, meta, args.base_url)

        clean_body = clean_markdown(body)
        # Only retain summary if explicitly set in front matter to keep docs payload compact
        summary = meta.get("description", "").strip()

        parsed_posts.append({
            "title": title,
            "url": url,
            "date": date,
            "summary": summary,
            "tags": tags,
            "categories": categories,
            "clean_body": clean_body,
            "deprecated": meta.get("deprecated", False),
        })

    # Newest first, and a post's position is its doc id. search.js breaks a tie
    # in score by the lower id, so by the newer post; and posts on a subject
    # tend to come close together in time, which keeps the gaps in a posting
    # list small.
    parsed_posts.sort(key=lambda p: (p["date"] or "", p["title"]), reverse=True)

    # Two tiers, so that the dialog is usable after a small download. Tier 1
    # has the documents and the terms of their titles, tags and categories;
    # tier 2 the terms of their bodies, several times the size, which
    # search.js fetches afterwards.
    docs = []
    tier1_index = defaultdict(list)
    tier2_index = defaultdict(list)

    for doc_id, post in enumerate(parsed_posts):
        doc_entry = {
            "title": post["title"],
            "url": post["url"],
            "date": post["date"],
            "tags": post["tags"],
        }
        if post["summary"]:
            doc_entry["summary"] = post["summary"]
        if post.get("deprecated"):
            doc_entry["deprecated"] = True
        docs.append(doc_entry)

        tier1_tokens = set()
        for text in (post["title"], *post["tags"], *post["categories"]):
            tier1_tokens |= tokenize(text, stop_words)
        # The whole body unless the site asks for a limit: a word past the
        # limit cannot be found, however plainly the post says it.
        body = post["clean_body"]
        if args.max_body_chars > 0:
            body = body[: args.max_body_chars]
        body_tokens = tokenize(body, stop_words)

        for token in tier1_tokens:
            tier1_index[token].append(doc_id)
        # A term the post has in tier 1 stays out of its tier 2 list: search.js
        # joins a term's two lists, and a doc id in both would be counted twice.
        for token in body_tokens - tier1_tokens:
            tier2_index[token].append(doc_id)

    if args.single_file:
        # The same two tiers in one file. A term's lists do not overlap, but
        # their ids interleave, and encode_postings wants them ascending.
        for token, doc_ids in tier2_index.items():
            tier1_index[token] = sorted(tier1_index[token] + doc_ids)

    def write_index(path: str, payload: dict) -> float:
        """Writes one index file and returns its size in KB."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        return os.path.getsize(path) / 1024

    t1_size_kb = write_index(output_path, {"docs": docs, **pack_index(tier1_index)})

    if args.single_file:
        print("Successfully generated monolithic search index:")
        print(f"  - Total indexed posts: {len(docs)}")
        print(f"  - Total unique terms:  {len(tier1_index)}")
        print(f"  - Output file:         {output_path} ({t1_size_kb:.1f} KB)")
    else:
        t2_size_kb = write_index(output_body_path, pack_index(tier2_index))
        print("Successfully generated two-tier search index:")
        print(f"  - Total indexed posts: {len(docs)}")
        print(f"  - Tier 1 (Core):       {output_path} ({t1_size_kb:.1f} KB, {len(tier1_index)} terms)")
        print(f"  - Tier 2 (Body):       {output_body_path} ({t2_size_kb:.1f} KB, {len(tier2_index)} terms)")


if __name__ == "__main__":
    main()
