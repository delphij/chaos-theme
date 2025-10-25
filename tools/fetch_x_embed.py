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
X (Twitter) Embed Fetcher and Cacher - CLI Wrapper

Fetches oEmbed data from X's public API and caches it locally for Hugo.
Sanitizes HTML to remove tracking scripts and external dependencies.

This is a standalone CLI tool that uses the auxmark tweet_downloader module
as its core engine.

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
import subprocess
import sys
from pathlib import Path

# Add auxmark to path and import core functions
sys.path.insert(0, str(Path(__file__).parent))
from auxmark.modules.tweet_downloader import process_single_tweet, process_batch


def find_git_root() -> Path | None:
    """Find the git repository root directory."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def main() -> int:
    """Main entrypoint for fetch_x_embed CLI."""
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

    # Auto-detect Hugo site root
    if args.data_dir is None:
        git_root = find_git_root()
        if not git_root:
            print("Error: Not in a git repository and --data-dir not specified", file=sys.stderr)
            return 1

        site_root = git_root
        data_dir = site_root / 'data' / 'x_embeds'
    else:
        # If data_dir is provided, derive site_root from it
        data_dir = args.data_dir
        site_root = data_dir.parent.parent

    # Ensure data directory exists
    data_dir.mkdir(parents=True, exist_ok=True)

    # Determine defang setting
    defang = not args.no_defang

    # Process input
    success = False

    if args.batch:
        success = process_batch(
            batch_file=args.batch,
            data_dir=data_dir,
            site_root=site_root,
            defang=defang,
            force=args.refresh
        )
    elif args.input:
        success = process_single_tweet(
            tweet_input=args.input,
            data_dir=data_dir,
            site_root=site_root,
            defang=defang,
            lang=None,  # Auto-detected
            force=args.refresh
        )
    else:
        parser.print_help()
        return 1

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
