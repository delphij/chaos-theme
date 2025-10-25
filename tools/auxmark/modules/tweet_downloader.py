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
"""

import re
import sys
from pathlib import Path

# Import the module interface from fetch_x_embed.py
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from fetch_x_embed import fetch_tweet_cached, extract_tweet_id

from ..core import Action, BaseModule, Job


class TweetDownloaderModule(BaseModule):
    """Module for downloading and caching X/Twitter embeds."""

    name = "tweet_downloader"
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

            # Request preprocessing
            metadata = {
                'user': user,
                'tweet_id': tweet_id
            }

            return (Action.TAG_WITH_PREPROCESS, metadata)

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
                force_refresh=False
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
