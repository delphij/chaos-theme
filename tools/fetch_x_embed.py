#!/usr/bin/env python3
# Copyright 2025 The Hugo Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
X (Twitter) Embed Fetcher and Cacher

Fetches oEmbed data from X's public API and caches it locally for Hugo.
Sanitizes HTML to remove tracking scripts and external dependencies.

Usage:
    ./fetch_x_embed.py <tweet_url_or_id>
    ./fetch_x_embed.py --batch <file_with_urls>
    ./fetch_x_embed.py --refresh <tweet_id>

Examples:
    ./fetch_x_embed.py https://x.com/username/status/1234567890
    ./fetch_x_embed.py 1234567890
    ./fetch_x_embed.py --batch tweets.txt
"""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib import request, parse, error
from html.parser import HTMLParser


class ScriptStripper(HTMLParser):
    """HTML parser that removes script tags and sanitizes content."""

    def __init__(self):
        super().__init__()
        self.result = []
        self.skip_tag = False

    def handle_starttag(self, tag, attrs):
        # Skip script tags entirely
        if tag == 'script':
            self.skip_tag = True
            return

        # Remove event handlers (onclick, onload, etc.)
        sanitized_attrs = [
            (key, value) for key, value in attrs
            if not key.startswith('on')
        ]

        # For iframes and img, we might want to keep them but mark for review
        if tag in ('iframe', 'embed'):
            # Comment out iframes (user can decide to restore later)
            self.result.append(f'<!-- iframe removed: {tag} ')
            return

        # Reconstruct tag
        if sanitized_attrs:
            attrs_str = ' '.join(f'{k}="{v}"' for k, v in sanitized_attrs)
            self.result.append(f'<{tag} {attrs_str}>')
        else:
            self.result.append(f'<{tag}>')

    def handle_endtag(self, tag):
        if tag == 'script':
            self.skip_tag = False
            return
        if tag in ('iframe', 'embed'):
            self.result.append(' -->')
            return
        self.result.append(f'</{tag}>')

    def handle_data(self, data):
        if not self.skip_tag:
            self.result.append(data)

    def handle_startendtag(self, tag, attrs):
        if tag == 'script':
            return
        if tag in ('iframe', 'embed'):
            self.result.append(f'<!-- self-closing {tag} removed -->')
            return
        # Remove event handlers
        sanitized_attrs = [(k, v) for k, v in attrs if not k.startswith('on')]
        if sanitized_attrs:
            attrs_str = ' '.join(f'{k}="{v}"' for k, v in sanitized_attrs)
            self.result.append(f'<{tag} {attrs_str} />')
        else:
            self.result.append(f'<{tag} />')

    def get_sanitized_html(self) -> str:
        return ''.join(self.result)


def detect_hugo_language(site_root: Path) -> str | None:
    """
    Detect Hugo site's languageCode from config files.

    Maps Hugo language codes to X supported language codes.
    X supported languages: https://developer.x.com/en/docs/x-for-websites/supported-languages
    """
    # X language code mapping (Hugo languageCode -> X lang parameter)
    lang_map = {
        'ar': 'ar',     # Arabic
        'bn': 'bn',     # Bengali
        'cs': 'cs',     # Czech
        'da': 'da',     # Danish
        'de': 'de',     # German
        'el': 'el',     # Greek
        'en': 'en',     # English
        'en-us': 'en',
        'en-gb': 'en-gb',
        'es': 'es',     # Spanish
        'fa': 'fa',     # Persian
        'fi': 'fi',     # Finnish
        'fil': 'fil',   # Filipino
        'fr': 'fr',     # French
        'he': 'he',     # Hebrew
        'hi': 'hi',     # Hindi
        'hu': 'hu',     # Hungarian
        'id': 'id',     # Indonesian
        'it': 'it',     # Italian
        'ja': 'ja',     # Japanese
        'ja-jp': 'ja',
        'ko': 'ko',     # Korean
        'ko-kr': 'ko',
        'msa': 'msa',   # Malay
        'nl': 'nl',     # Dutch
        'no': 'no',     # Norwegian
        'pl': 'pl',     # Polish
        'pt': 'pt',     # Portuguese
        'ro': 'ro',     # Romanian
        'ru': 'ru',     # Russian
        'sv': 'sv',     # Swedish
        'th': 'th',     # Thai
        'tr': 'tr',     # Turkish
        'uk': 'uk',     # Ukrainian
        'ur': 'ur',     # Urdu
        'vi': 'vi',     # Vietnamese
        'zh-cn': 'zh-cn',  # Simplified Chinese
        'zh-tw': 'zh-tw',  # Traditional Chinese
    }

    # Try to find and read config file
    for config_file in ['hugo.toml', 'config.toml']:
        config_path = site_root / config_file
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple regex to extract languageCode
                    match = re.search(r'languageCode\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
                    if match:
                        hugo_lang = match.group(1).lower()
                        x_lang = lang_map.get(hugo_lang)
                        if x_lang:
                            print(f"Detected Hugo languageCode: {hugo_lang} -> X lang: {x_lang}")
                            return x_lang
            except Exception:
                # If we can't read the config, just continue
                pass

    return None


def extract_tweet_id(input_str: str) -> str | None:
    """
    Extract tweet ID from various input formats.

    Supports:
    - https://x.com/username/status/1234567890
    - https://twitter.com/username/status/1234567890
    - 1234567890 (raw ID)
    """
    # If it's already just digits, return it
    if input_str.isdigit():
        return input_str

    # Try to extract from URL
    patterns = [
        r'(?:x\.com|twitter\.com)/\w+/status/(\d+)',
        r'status/(\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, input_str)
        if match:
            return match.group(1)

    return None


def fetch_oembed(tweet_id: str, defang: bool = True, lang: str | None = None) -> dict | None:
    """
    Fetch oEmbed data from X's public API.

    Args:
        tweet_id: The tweet ID to fetch
        defang: If True, request omit_script to avoid receiving script tags
        lang: X language code (e.g., 'en', 'zh-cn')
    """
    tweet_url = f'https://x.com/i/status/{tweet_id}'

    # Build query parameters
    params = {'url': tweet_url}

    # Only request omit_script if we're going to defang anyway
    if defang:
        params['omit_script'] = 'true'

    if lang:
        params['lang'] = lang

    query = parse.urlencode(params)
    oembed_url = f'https://publish.x.com/oembed?{query}'

    try:
        with request.urlopen(oembed_url, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data
            else:
                print(f"Error: HTTP {response.status}", file=sys.stderr)
                return None
    except error.URLError as e:
        print(f"Error fetching oEmbed data: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}", file=sys.stderr)
        return None


def sanitize_html(html: str) -> str:
    """Remove scripts and sanitize HTML content."""
    parser = ScriptStripper()
    parser.feed(html)
    return parser.get_sanitized_html()


def save_embed_data(tweet_id: str, oembed_data: dict, data_dir: Path, defang: bool = True):
    """Save oEmbed data to data directory."""
    # Save full JSON
    json_path = data_dir / f'{tweet_id}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(oembed_data, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON: {json_path}")

    # Save HTML (sanitized if defang=True)
    if 'html' in oembed_data:
        html_content = oembed_data['html']
        if defang:
            html_content = sanitize_html(html_content)

        html_path = data_dir / f'{tweet_id}.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Saved HTML: {html_path} (defanged={defang})")


def process_single_tweet(tweet_input: str, data_dir: Path, defang: bool = True,
                         lang: str | None = None, force: bool = False) -> bool:
    """Process a single tweet URL or ID."""
    tweet_id = extract_tweet_id(tweet_input)
    if not tweet_id:
        print(f"Error: Could not extract tweet ID from '{tweet_input}'", file=sys.stderr)
        return False

    # Check if already cached
    json_path = data_dir / f'{tweet_id}.json'
    if json_path.exists() and not force:
        print(f"Tweet {tweet_id} already cached. Use --refresh to update.")
        return True

    print(f"Fetching tweet {tweet_id}...")
    oembed_data = fetch_oembed(tweet_id, defang=defang, lang=lang)

    if oembed_data:
        save_embed_data(tweet_id, oembed_data, data_dir, defang)
        return True
    else:
        print(f"Failed to fetch tweet {tweet_id}", file=sys.stderr)
        return False


def process_batch(batch_file: Path, data_dir: Path, defang: bool = True,
                  lang: str | None = None, force: bool = False) -> bool:
    """Process multiple tweets from a file (one URL/ID per line)."""
    if not batch_file.exists():
        print(f"Error: Batch file '{batch_file}' not found", file=sys.stderr)
        return False

    with open(batch_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    success_count = 0
    for line in lines:
        if process_single_tweet(line, data_dir, defang, lang, force):
            success_count += 1

    print(f"\nProcessed {success_count}/{len(lines)} tweets successfully")
    return success_count == len(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Fetch and cache X (Twitter) embeds for Hugo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('input', nargs='?', help='Tweet URL or ID')
    parser.add_argument('--batch', type=Path, help='Process multiple tweets from file')
    parser.add_argument('--refresh', action='store_true', help='Refresh existing cache')
    parser.add_argument('--no-defang', action='store_true', help='Keep scripts (not recommended)')
    parser.add_argument('--data-dir', type=Path, default=None,
                        help='Data directory (default: auto-detect Hugo site root)')

    args = parser.parse_args()

    # Auto-detect Hugo site root (look for config.toml/hugo.toml)
    if args.data_dir is None:
        script_dir = Path(__file__).parent
        # Assume script is in themes/chaos/tools, so go up 3 levels to site root
        site_root = script_dir.parent.parent.parent
        args.data_dir = site_root / 'data' / 'x_embeds'
    else:
        # If data_dir is provided, derive site_root from it
        site_root = args.data_dir.parent.parent

    # Ensure data directory exists
    args.data_dir.mkdir(parents=True, exist_ok=True)

    # Determine defang setting
    defang = not args.no_defang

    # Detect Hugo site language
    lang = detect_hugo_language(site_root)

    # Process input
    if args.batch:
        success = process_batch(args.batch, args.data_dir, defang, lang, args.refresh)
    elif args.input:
        success = process_single_tweet(args.input, args.data_dir, defang, lang, args.refresh)
    else:
        parser.print_help()
        return 1

    return 0 if success else 1


# Module Interface for auxmark
# =============================================================================

def fetch_tweet_cached(
    tweet_id: str,
    data_dir: Path,
    site_root: Path | None = None,
    defang: bool = True,
    cache_max_age_days: int = 30,
    force_refresh: bool = False
) -> bool:
    """
    Fetch and cache a tweet (module-friendly interface).

    This function is designed to be called by the auxmark tweet_downloader module.
    It checks cache age and only fetches if needed.

    Args:
        tweet_id: The tweet ID to fetch
        data_dir: Path to data directory (e.g., site_root/data/x_embeds)
        site_root: Path to Hugo site root (for language detection)
        defang: Remove scripts and tracking (default: True)
        cache_max_age_days: Maximum age of cache in days (default: 30)
        force_refresh: Force re-fetch even if cache exists (default: False)

    Returns:
        True if successful (cached or fetched), False otherwise
    """
    from datetime import datetime, timedelta

    json_path = data_dir / f'{tweet_id}.json'

    # Check if cache exists and is fresh
    if json_path.exists() and not force_refresh:
        try:
            age = datetime.now() - datetime.fromtimestamp(json_path.stat().st_mtime)
            if age < timedelta(days=cache_max_age_days):
                # Cache is fresh, skip
                return True
        except Exception:
            # If we can't check age, proceed to fetch
            pass

    # Detect language if site_root provided
    lang = None
    if site_root:
        lang = detect_hugo_language(site_root)

    # Fetch and save
    return process_single_tweet(
        tweet_id,
        data_dir,
        defang=defang,
        lang=lang,
        force=force_refresh
    )


if __name__ == '__main__':
    sys.exit(main())
