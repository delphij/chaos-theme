#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_search_index.py: Offline search index generator for Chaos theme.

Scans Hugo content directory, extracts post metadata, performs Chinese & English
tokenization using Jieba, and generates a compact inverted index JSON file
for client-side full-text search.
"""

import argparse
import glob
import json
import os
import re
import sys
import warnings

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

# Minimal Chinese stop words
STOP_WORDS = {
    "的", "了", "和", "是", "在", "我", "有", "也", "就", "不", "人", "都",
    "一", "一个", "上", "很", "到", "说", "要", "去", "你", "会", "着",
    "没有", "看", "好", "自己", "这", "那", "与", "及", "等", "之", "为",
    "以", "所", "其", "但", "而", "则", "又", "或", "把", "被", "从", "对",
    "向", "给", "让", "得", "过", "只", "更", "已", "再", "便", "若", "虽",
}


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
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", " ", text)
    # Remove inline code
    text = re.sub(r"`[^`]+`", " ", text)
    # Remove headings marker
    text = re.sub(r"^[#\s]+", " ", text, flags=re.MULTILINE)
    # Remove blockquotes, table borders, bold/italic markers
    text = re.sub(r"[*_~>|=-]", " ", text)
    # Collapse multiple whitespaces
    return re.sub(r"\s+", " ", text).strip()


def parse_frontmatter(content: str):
    """Extracts frontmatter and body from Markdown string."""
    fm_match = re.match(r"^(?:---|\+\+\+)\s*\n([\s\S]*?)\n(?:---|\+\+\+)\s*\n([\s\S]*)$", content)
    if not fm_match:
        return {}, content

    fm_raw, body = fm_match.groups()
    meta = {}

    # Extract title
    m = re.search(r'^(?:title)\s*[:=]\s*["\']?(.*?)["\']?\s*$', fm_raw, re.MULTILINE | re.IGNORECASE)
    if m:
        meta["title"] = m.group(1).strip("\"' ")

    # Extract date
    m = re.search(r'^(?:date)\s*[:=]\s*["\']?(.*?)["\']?\s*$', fm_raw, re.MULTILINE | re.IGNORECASE)
    if m:
        d = m.group(1).strip("\"' ")
        meta["date"] = d.split("T")[0]

    # Extract draft
    m = re.search(r'^(?:draft)\s*[:=]\s*(true|false)\s*$', fm_raw, re.MULTILINE | re.IGNORECASE)
    if m:
        meta["draft"] = m.group(1).lower() == "true"
    else:
        meta["draft"] = False

    # Extract description
    m = re.search(r'^(?:description)\s*[:=]\s*["\']?(.*?)["\']?\s*$', fm_raw, re.MULTILINE | re.IGNORECASE)
    if m:
        meta["description"] = m.group(1).strip("\"' ")

    # Extract custom url or slug
    m = re.search(r'^(?:url|slug)\s*[:=]\s*["\']?(.*?)["\']?\s*$', fm_raw, re.MULTILINE | re.IGNORECASE)
    if m:
        meta["slug"] = m.group(1).strip("\"' ")

    # Extract tags (TOML / YAML array)
    m = re.search(r'tags\s*[:=]\s*\[(.*?)\]', fm_raw, re.DOTALL | re.IGNORECASE)
    if m:
        meta["tags"] = [t.strip("\"' ") for t in m.group(1).split(",") if t.strip("\"' ")]
    else:
        # YAML list format: - tag
        tags_yaml = re.findall(r'^\s*-\s*["\']?(.*?)["\']?\s*$', fm_raw, re.MULTILINE)
        if tags_yaml and "tags" in fm_raw.lower():
            meta["tags"] = tags_yaml
        else:
            meta["tags"] = []

    # Extract categories
    m = re.search(r'categories\s*[:=]\s*\[(.*?)\]', fm_raw, re.DOTALL | re.IGNORECASE)
    if m:
        meta["categories"] = [c.strip("\"' ") for c in m.group(1).split(",") if c.strip("\"' ")]
    else:
        meta["categories"] = []

    return meta, body


def compute_post_url(filepath: str, base_content_dir: str, meta: dict, base_url: str) -> str:
    """Computes clean URL matching Hugo's default output path."""
    if "slug" in meta and meta["slug"].startswith("/"):
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


def tokenize(text: str) -> set:
    """Segments text into lowercase searchable tokens, skipping stop words."""
    tokens = set()
    if not text:
        return tokens

    # Pre-extract alphanumeric tokens with technical symbols (e.g. Google+, C++, C#, .NET)
    for sym in re.findall(r"\b[a-zA-Z0-9_\-\.]+(?:\+\+|[+#])", text):
        tokens.add(sym.lower())

    for word in jieba.cut_for_search(text):
        w = word.strip().lower()
        if not w:
            continue
        # Skip pure whitespace, single-letter punctuation or stop words
        if w in STOP_WORDS:
            continue
        # Only retain words with meaningful length (>= 2 chars, or alphanumeric/CJK non-stopword)
        if len(w) == 1 and not re.match(r"[\u4e00-\u9fa5a-zA-Z0-9\+#]", w):
            continue
        tokens.add(w)
    return tokens



def main():
    parser = argparse.ArgumentParser(description="Build offline search index for Chaos theme.")
    parser.add_argument("--content", default="content", help="Path to Hugo content directory (default: content)")
    parser.add_argument("--output", default="assets/search-index.json", help="Path to output search-index.json (default: assets/search-index.json)")
    parser.add_argument("--base-url", default="/", help="Base URL for site links (default: /)")
    parser.add_argument("--max-body-chars", type=int, default=3000, help="Max body characters to index per post (default: 3000)")
    args = parser.parse_args()

    content_dir = os.path.abspath(args.content)
    if not os.path.isdir(content_dir):
        sys.stderr.write(f"Content directory not found: {content_dir}\n")
        sys.exit(1)

    print(f"Scanning markdown files in {content_dir}...")
    files = glob.glob(os.path.join(content_dir, "**", "*.md"), recursive=True)

    parsed_posts = []
    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to read {filepath}: {e}\n")
            continue

        meta, body = parse_frontmatter(content)
        if meta.get("draft", False):
            continue

        title = meta.get("title", "")
        if not title:
            title = os.path.splitext(os.path.basename(filepath))[0]

        date = meta.get("date", "")
        tags = meta.get("tags", [])
        for tag in tags:
            if any(ch in tag for ch in "+#"):
                jieba.add_word(tag.strip().lower())
        categories = meta.get("categories", [])
        url = compute_post_url(filepath, content_dir, meta, args.base_url)

        clean_body = clean_markdown(body)
        summary = meta.get("description", "")
        if not summary:
            summary = clean_body[:160]

        parsed_posts.append({
            "title": title,
            "url": url,
            "date": date,
            "summary": summary,
            "tags": tags,
            "categories": categories,
            "clean_body": clean_body,
        })

    # Sort posts chronologically: newer posts first
    parsed_posts.sort(key=lambda p: (p["date"] or "", p["title"]), reverse=True)

    docs = []
    index = {}

    for post in parsed_posts:
        doc_id = len(docs)
        docs.append({
            "id": doc_id,
            "title": post["title"],
            "url": post["url"],
            "date": post["date"],
            "summary": post["summary"],
            "tags": post["tags"],
            "categories": post["categories"],
        })

        # Tokenize fields
        doc_tokens = set()

        # Title tokens
        doc_tokens.update(tokenize(post["title"]))

        # Tag & category tokens
        for tag in post["tags"]:
            doc_tokens.update(tokenize(tag))
        for cat in post["categories"]:
            doc_tokens.update(tokenize(cat))

        # Body tokens (up to max_body_chars)
        doc_tokens.update(tokenize(post["clean_body"][: args.max_body_chars]))

        for token in doc_tokens:
            if token not in index:
                index[token] = []
            index[token].append(doc_id)

    # Sort index keys alphabetically for deterministic output
    sorted_index = {k: sorted(index[k]) for k in sorted(index.keys())}

    payload = {
        "docs": docs,
        "index": sorted_index,
    }

    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    file_size_kb = os.path.getsize(output_path) / 1024
    print(f"Successfully generated search index:")
    print(f"  - Total indexed posts: {len(docs)}")
    print(f"  - Total unique terms:  {len(sorted_index)}")
    print(f"  - Output file:         {output_path} ({file_size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
