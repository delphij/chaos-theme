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
    """Extracts frontmatter and body from Markdown string."""
    fm_match = re.match(r"^(?:---|\+\+\+)\s*\n([\s\S]*?)\n(?:---|\+\+\+)\s*\n([\s\S]*)$", content)
    if not fm_match:
        return {}, content

    fm_raw, body = fm_match.groups()
    meta = {}

    def parse_bool(key: str) -> bool:
        m = re.search(rf'^(?:{key})\s*[:=]\s*(true|false)\s*$', fm_raw, re.MULTILINE | re.IGNORECASE)
        return m.group(1).lower() == "true" if m else False

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
    meta["draft"] = parse_bool("draft")

    # Extract noindex / private (Tier 3: completely exclude from search engines and on-site search)
    m_robots = re.search(r'^(?:robots)\s*[:=]\s*["\']?(.*?)["\']?\s*$', fm_raw, re.MULTILINE | re.IGNORECASE)
    has_noindex_robots = bool(m_robots and "noindex" in m_robots.group(1).lower())
    meta["noindex"] = parse_bool("noindex") or parse_bool("private") or has_noindex_robots

    # Extract searchHidden / search_hidden / search = false (Tier 2: exclude from on-site search only)
    m_search = re.search(r'^(?:search)\s*[:=]\s*(true|false)\s*$', fm_raw, re.MULTILINE | re.IGNORECASE)
    search_disabled = bool(m_search and m_search.group(1).lower() == "false")
    meta["search_hidden"] = parse_bool("searchHidden") or parse_bool("search_hidden") or search_disabled

    # Extract deprecated / outdated (Tier 1: penalize search score and mark badge)
    meta["deprecated"] = parse_bool("deprecated") or parse_bool("outdated")

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
    parser.add_argument("--output", default="assets/search-index.json", help="Path to output Tier 1 / core search-index.json (default: assets/search-index.json)")
    parser.add_argument("--output-body", default="", help="Path to output Tier 2 / body search-index.json (default: auto derived as <stem>-body.json)")
    parser.add_argument("--single-file", action="store_true", help="Generate legacy monolithic single-file index instead of two-tier")
    parser.add_argument("--base-url", default="/", help="Base URL for site links (default: /)")
    parser.add_argument("--max-body-chars", type=int, default=6000, help="Max body characters to index per post (default: 6000)")
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
        if meta.get("noindex", False) or meta.get("search_hidden", False):
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

    # Sort posts chronologically: newer posts first
    parsed_posts.sort(key=lambda p: (p["date"] or "", p["title"]), reverse=True)

    docs = []
    tier1_index = {}
    tier2_index = {}

    for post in parsed_posts:
        doc_id = len(docs)
        doc_entry = {
            "id": doc_id,
            "title": post["title"],
            "url": post["url"],
            "date": post["date"],
            "tags": post["tags"],
            "categories": post["categories"],
        }
        if post["summary"]:
            doc_entry["summary"] = post["summary"]
        if post.get("deprecated"):
            doc_entry["deprecated"] = True
        docs.append(doc_entry)

        # Tier 1 tokens: Title, Tags, Categories
        tier1_tokens = set()
        tier1_tokens.update(tokenize(post["title"]))
        for tag in post["tags"]:
            tier1_tokens.update(tokenize(tag))
        for cat in post["categories"]:
            tier1_tokens.update(tokenize(cat))

        for token in tier1_tokens:
            if token not in tier1_index:
                tier1_index[token] = []
            tier1_index[token].append(doc_id)

        # Body tokens: up to max_body_chars
        body_tokens = tokenize(post["clean_body"][: args.max_body_chars])

        if args.single_file:
            # Monolithic index: combine all tokens into tier1_index
            for token in body_tokens:
                if token not in tier1_tokens:
                    if token not in tier1_index:
                        tier1_index[token] = []
                    tier1_index[token].append(doc_id)
        else:
            # Two-tier disjoint index: only record body tokens that are NOT in tier1_tokens for this doc
            tier2_tokens = body_tokens - tier1_tokens
            for token in tier2_tokens:
                if token not in tier2_index:
                    tier2_index[token] = []
                tier2_index[token].append(doc_id)

    # Sort index keys alphabetically for deterministic output
    sorted_tier1_index = {k: sorted(tier1_index[k]) for k in sorted(tier1_index.keys())}

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    t1_payload = {
        "docs": docs,
        "index": sorted_tier1_index,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(t1_payload, f, ensure_ascii=False, separators=(",", ":"))

    t1_size_kb = os.path.getsize(output_path) / 1024

    if args.single_file:
        print("Successfully generated monolithic search index:")
        print(f"  - Total indexed posts: {len(docs)}")
        print(f"  - Total unique terms:  {len(sorted_tier1_index)}")
        print(f"  - Output file:         {output_path} ({t1_size_kb:.1f} KB)")
    else:
        sorted_tier2_index = {k: sorted(tier2_index[k]) for k in sorted(tier2_index.keys())}
        os.makedirs(os.path.dirname(output_body_path), exist_ok=True)
        t2_payload = {
            "index": sorted_tier2_index,
        }
        with open(output_body_path, "w", encoding="utf-8") as f:
            json.dump(t2_payload, f, ensure_ascii=False, separators=(",", ":"))

        t2_size_kb = os.path.getsize(output_body_path) / 1024

        # Sanity check: Ensure strict disjointness between Tier 1 and Tier 2 posting lists
        conflicts = 0
        for term, doc_ids in sorted_tier1_index.items():
            if term in sorted_tier2_index:
                overlap = set(doc_ids) & set(sorted_tier2_index[term])
                if overlap:
                    conflicts += len(overlap)

        print("Successfully generated two-tier search index:")
        print(f"  - Total indexed posts: {len(docs)}")
        print(f"  - Tier 1 (Core):       {output_path} ({t1_size_kb:.1f} KB, {len(sorted_tier1_index)} terms)")
        print(f"  - Tier 2 (Body):       {output_body_path} ({t2_size_kb:.1f} KB, {len(sorted_tier2_index)} terms)")
        print(f"  - Disjoint check:      {conflicts} overlapping posting pairs (strictly 0)")


if __name__ == "__main__":
    main()
