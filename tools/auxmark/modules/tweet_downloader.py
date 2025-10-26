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
X/Twitter Embed Downloader Module for auxmark.

Detects Hugo shortcodes for X/Twitter embeds and pre-caches them locally.

Core Logic:
- HTML sanitization (ScriptStripper)
- Hugo language detection
- Tweet ID extraction
- oEmbed API fetching
- Cache management

This module contains all the core logic. The standalone fetch_x_embed.py CLI
tool is a thin wrapper that uses this module.
"""

import json
import re
import sys
from datetime import datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib import error, parse, request

from ..core import Action, BaseModule, Job


# =============================================================================
# Core Functions (shared between module and CLI)
# =============================================================================

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


def fetch_oembed(
    tweet_id: str,
    defang: bool = True,
    lang: str | None = None,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    retry_backoff: float = 2.0,
    timeout: int = 30
) -> dict | None:
    """
    Fetch oEmbed data from X's public API with retry logic.

    Args:
        tweet_id: The tweet ID to fetch
        defang: If True, request omit_script to avoid receiving script tags
        lang: X language code (e.g., 'en', 'zh-cn')
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries (seconds)
        retry_backoff: Multiplier for exponential backoff
        timeout: Request timeout in seconds
    """
    import time

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

    delay = retry_delay
    last_error = None

    for attempt in range(max_retries):
        try:
            with request.urlopen(oembed_url, timeout=timeout) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if attempt > 0:
                        print(f"  ✓ Successfully fetched tweet {tweet_id} on attempt {attempt + 1}", file=sys.stderr)
                    return data
                else:
                    last_error = f"HTTP {response.status}"

                    # Determine if we should retry based on status code
                    should_retry = response.status in (429, 500, 502, 503, 504)

                    if attempt < max_retries - 1 and should_retry:
                        print(f"  ⚠ Attempt {attempt + 1}/{max_retries} failed: {last_error}", file=sys.stderr)
                        print(f"    Retrying in {delay:.1f}s...", file=sys.stderr)
                        time.sleep(delay)
                        delay *= retry_backoff
                    elif not should_retry:
                        print(f"  ✗ Permanent error ({last_error}), not retrying", file=sys.stderr)
                        return None
                    else:
                        print(f"  ✗ Failed after {max_retries} attempts: {last_error}", file=sys.stderr)
                        return None

        except (error.URLError, error.HTTPError) as e:
            last_error = str(e)
            if isinstance(e, error.HTTPError):
                last_error = f"HTTP {e.code}: {e.reason}"

            # Determine if we should retry
            should_retry = True
            if isinstance(e, error.HTTPError) and 400 <= e.code < 500 and e.code != 429:
                should_retry = False  # Client errors are permanent

            if attempt < max_retries - 1 and should_retry:
                print(f"  ⚠ Attempt {attempt + 1}/{max_retries} failed: {last_error}", file=sys.stderr)
                print(f"    Retrying in {delay:.1f}s...", file=sys.stderr)
                time.sleep(delay)
                delay *= retry_backoff
            elif not should_retry:
                print(f"  ✗ Permanent error ({last_error}), not retrying", file=sys.stderr)
                return None
            else:
                print(f"  ✗ Failed after {max_retries} attempts: {last_error}", file=sys.stderr)
                return None

        except json.JSONDecodeError as e:
            print(f"  ✗ Error decoding JSON response: {e}", file=sys.stderr)
            return None

    return None


def sanitize_html(html: str) -> str:
    """Remove scripts and sanitize HTML content."""
    parser = ScriptStripper()
    parser.feed(html)
    return parser.get_sanitized_html()


def save_embed_data(tweet_id: str, oembed_data: dict, data_dir: Path, defang: bool = True) -> None:
    """Save oEmbed data to data directory."""
    # Ensure directory exists
    data_dir.mkdir(parents=True, exist_ok=True)

    # Save full JSON
    json_path = data_dir / f'{tweet_id}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(oembed_data, f, ensure_ascii=False, indent=2)

    # Save HTML (sanitized if defang=True)
    if 'html' in oembed_data:
        html_content = oembed_data['html']
        if defang:
            html_content = sanitize_html(html_content)

        html_path = data_dir / f'{tweet_id}.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)


def process_single_tweet(
    tweet_input: str,
    data_dir: Path,
    site_root: Path | None = None,
    defang: bool = True,
    lang: str | None = None,
    force: bool = False,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    retry_backoff: float = 2.0,
    timeout: int = 30
) -> bool:
    """
    Process a single tweet URL or ID.

    Args:
        tweet_input: Tweet URL or ID
        data_dir: Directory to save cache files
        site_root: Hugo site root for language detection
        defang: Remove scripts and tracking
        lang: Language code (auto-detected if None and site_root provided)
        force: Force refresh even if cached
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries (seconds)
        retry_backoff: Multiplier for exponential backoff
        timeout: Request timeout in seconds

    Returns:
        True if successful, False otherwise
    """
    tweet_id = extract_tweet_id(tweet_input)
    if not tweet_id:
        print(f"Error: Could not extract tweet ID from '{tweet_input}'", file=sys.stderr)
        return False

    # Check if already cached
    json_path = data_dir / f'{tweet_id}.json'
    if json_path.exists() and not force:
        print(f"Tweet {tweet_id} already cached. Use --refresh to update.")
        return True

    # Auto-detect language if needed
    if lang is None and site_root:
        lang = detect_hugo_language(site_root)
        if lang:
            print(f"Detected Hugo languageCode -> X lang: {lang}")

    print(f"Fetching tweet {tweet_id}...")
    oembed_data = fetch_oembed(
        tweet_id,
        defang=defang,
        lang=lang,
        max_retries=max_retries,
        retry_delay=retry_delay,
        retry_backoff=retry_backoff,
        timeout=timeout
    )

    if oembed_data:
        save_embed_data(tweet_id, oembed_data, data_dir, defang)
        print(f"Saved JSON: {data_dir / f'{tweet_id}.json'}")
        print(f"Saved HTML: {data_dir / f'{tweet_id}.html'} (defanged={defang})")
        return True
    else:
        print(f"Failed to fetch tweet {tweet_id}", file=sys.stderr)
        return False


def process_batch(
    batch_file: Path,
    data_dir: Path,
    site_root: Path | None = None,
    defang: bool = True,
    force: bool = False
) -> bool:
    """
    Process multiple tweets from a file (one URL/ID per line).

    Args:
        batch_file: Path to file containing tweet URLs/IDs
        data_dir: Directory to save cache files
        site_root: Hugo site root for language detection
        defang: Remove scripts and tracking
        force: Force refresh even if cached

    Returns:
        True if all succeeded, False if any failed
    """
    if not batch_file.exists():
        print(f"Error: Batch file '{batch_file}' not found", file=sys.stderr)
        return False

    with open(batch_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    success_count = 0
    for line in lines:
        if process_single_tweet(line, data_dir, site_root, defang, lang=None, force=force):
            success_count += 1

    print(f"\nProcessed {success_count}/{len(lines)} tweets successfully")
    return success_count == len(lines)


def fetch_tweet_cached(
    tweet_id: str,
    data_dir: Path,
    site_root: Path | None = None,
    defang: bool = True,
    cache_max_age_days: int = 30,
    force_refresh: bool = False,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    retry_backoff: float = 2.0,
    timeout: int = 30
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
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries (seconds)
        retry_backoff: Multiplier for exponential backoff
        timeout: Request timeout in seconds

    Returns:
        True if successful (cached or fetched), False otherwise
    """
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

    # Fetch and save
    return process_single_tweet(
        tweet_id,
        data_dir,
        site_root=site_root,
        defang=defang,
        lang=None,  # Will be auto-detected
        force=force_refresh,
        max_retries=max_retries,
        retry_delay=retry_delay,
        retry_backoff=retry_backoff,
        timeout=timeout
    )


# =============================================================================
# BaseModule Implementation
# =============================================================================


class TweetDownloaderModule(BaseModule):
    """Module for downloading and caching X/Twitter embeds."""

    name = "tweet_downloader"
    description = "Cache X/Twitter embeds locally"
    # Use .* for now, optimize later
    regex = re.compile(r".*")

    # Optimized regex (for future use):
    # regex = re.compile(r'\{\{<\s*x\s+user="[^"]+"\s+id="[^"]+"\s*>\}\}')

    def __init__(self, config: dict | None = None):
        """Initialize tweet downloader module."""
        super().__init__(config)

        # Configuration defaults
        self.cache_max_age_days = self.config.get('cache_max_age_days', 30)
        self.defang = self.config.get('defang', True)
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 1.0)
        self.retry_backoff = self.config.get('retry_backoff', 2.0)
        self.timeout = self.config.get('timeout', 30)

        # Detect paths
        self.git_root = self._find_git_root()
        if self.git_root:
            self.data_dir = self.git_root / 'data' / 'x_embeds'
            self.data_dir.mkdir(parents=True, exist_ok=True)
        else:
            print("Warning: Could not detect git root for tweet_downloader", file=sys.stderr)
            self.data_dir = None

    def _find_git_root(self) -> Path | None:
        """Find git repository root."""
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True,
                text=True,
                check=True
            )
            return Path(result.stdout.strip())
        except Exception:
            return None

    def probe(self, file_path: Path, line_no: int, line: str) -> tuple[Action, dict]:
        """
        Detect Hugo X/Twitter shortcode.

        Looks for: {{< x user="username" id="1234567890" >}}
        """
        if self.data_dir is None:
            return (Action.IGNORE, {})

        # Simple pattern matching for Hugo shortcode
        # Pattern: {{< x user="..." id="..." >}}
        match = re.search(r'\{\{<\s*x\s+user="([^"]+)"\s+id="([^"]+)"\s*>\}\}', line)

        if match:
            user = match.group(1)
            tweet_id_str = match.group(2)

            # Validate that id is numeric
            tweet_id = extract_tweet_id(tweet_id_str)
            if not tweet_id:
                return (Action.IGNORE, {})

            # Request preprocessing only (no postprocessing needed)
            metadata = {
                'user': user,
                'tweet_id': tweet_id
            }

            return (Action.TAG_WITH_PREPROCESS_ONLY, metadata)

        return (Action.IGNORE, {})

    def preprocess(self, job: Job) -> bool:
        """
        Fetch and cache tweet data.

        Uses fetch_x_embed.py's module interface.
        """
        if self.data_dir is None:
            print("Error: data_dir not initialized", file=sys.stderr)
            return False

        tweet_id = job.metadata.get('tweet_id')
        if not tweet_id:
            print(f"Error: No tweet_id in job metadata", file=sys.stderr)
            return False

        print(f"  Fetching tweet {tweet_id}...")

        try:
            success = fetch_tweet_cached(
                tweet_id=tweet_id,
                data_dir=self.data_dir,
                site_root=self.git_root,
                defang=self.defang,
                cache_max_age_days=self.cache_max_age_days,
                force_refresh=False,
                max_retries=self.max_retries,
                retry_delay=self.retry_delay,
                retry_backoff=self.retry_backoff,
                timeout=self.timeout
            )

            if success:
                print(f"  ✓ Tweet {tweet_id} cached successfully")
            else:
                print(f"  ✗ Failed to cache tweet {tweet_id}", file=sys.stderr)

            return success

        except Exception as e:
            print(f"  ✗ Error caching tweet {tweet_id}: {e}", file=sys.stderr)
            return False

    def postprocess(self, file_path: Path) -> bool:
        """
        No post-processing needed.

        Hugo shortcodes read cached data directly.
        """
        return True
