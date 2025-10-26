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
Image Localizer Module for auxmark.

Detects external images in Markdown files and downloads them locally,
converting static formats to WebP for optimal performance.

Features:
- Detects Markdown image syntax: ![alt](url)
- Supports multiple images per line
- Downloads and converts to lossless WebP
- Handles naming conflicts with incrementing suffixes
- Retry with exponential backoff
- Line-oriented postprocessing to rewrite URLs
"""

import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib import error, parse, request

from ..core import Action, BaseModule, Job

# Try to import Pillow for WebP conversion
try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("Warning: Pillow not installed - WebP conversion disabled", file=sys.stderr)


class ImageLocalizerModule(BaseModule):
    """Module to download and localize external images in Markdown files."""

    name = "image_localizer"
    regex = re.compile(r'!\[(.*?)\]\((.*?)\)')

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize image localizer module."""
        super().__init__(config)
        self.convert_to_webp = config.get('convert_to_webp', True) if config else True
        self.max_retries = config.get('max_retries', 3) if config else 3
        self.retry_delay = config.get('retry_delay', 1.0) if config else 1.0
        self.retry_backoff = config.get('retry_backoff', 2.0) if config else 2.0
        self.timeout = config.get('timeout', 30) if config else 30

    def probe(self, file_path: Path, line_no: int, line: str) -> tuple[Action, dict[str, Any]]:
        """
        Detect external images in Markdown line.

        Supports Markdown image syntax: ![alt](url) or ![alt](url "title")

        Returns:
            - EXPAND if file needs to become page bundle
            - TAG_WITH_PREPROCESS_AND_POSTPROCESS if file is already expanded
            - IGNORE if no external images found
        """
        # Find all Markdown images in line
        images = []
        for match in self.regex.finditer(line):
            alt_text = match.group(1)
            url_part = match.group(2).strip()

            # Parse URL and optional title
            # Format: url "title" or url 'title' or just url
            url = url_part
            title = None

            # Check for quoted title (double or single quotes)
            if ' "' in url_part or " '" in url_part:
                # Split on first space followed by quote
                parts = url_part.split(None, 1)
                if len(parts) == 2:
                    url = parts[0]
                    title = parts[1]

            # Check if URL is external
            if url.startswith(('http://', 'https://')):
                images.append({
                    'url': url,
                    'alt_text': alt_text,
                    'title': title,  # Preserve title if present
                    'local_filename': None  # Will be set during preprocessing
                })

        if not images:
            return (Action.IGNORE, {})

        # Check if file needs to be expanded to page bundle
        if file_path.name != 'index.md':
            # File needs to be expanded first
            return (Action.EXPAND, {'images': images})

        # File is already expanded, tag for preprocessing and postprocessing
        metadata = {'images': images}
        return (Action.TAG_WITH_PREPROCESS_AND_POSTPROCESS, metadata)

    def preprocess(self, job: Job) -> bool:
        """
        Download and convert images.

        Downloads each image, converts static formats to WebP, and saves
        to the same directory as the Markdown file.

        Each image's success status is tracked independently in metadata.
        """
        images = job.metadata.get('images', [])
        if not images:
            return True

        # Determine target directory (same as Markdown file)
        target_dir = job.file_path.parent

        all_success = True
        for img_data in images:
            url = img_data['url']
            success = self._download_and_convert(url, target_dir, img_data)
            # Track success per-URL
            img_data['success'] = success
            if not success:
                all_success = False
                print(
                    f"Warning: Failed to download {url} for {job.file_path}:{job.line_no}",
                    file=sys.stderr
                )

        return all_success

    def _should_retry_error(self, error: Exception) -> bool:
        """
        Determine if an error should trigger a retry.

        Args:
            error: The exception that occurred

        Returns:
            True if should retry, False for permanent errors
        """
        # Always retry network errors and timeouts
        if isinstance(error, (error.URLError, TimeoutError)):
            # Check if it's an HTTPError with specific status code
            if isinstance(error, error.HTTPError):
                # Retry on server errors and rate limiting
                if error.code in (429, 500, 502, 503, 504):
                    return True
                # Don't retry client errors (likely permanent)
                if 400 <= error.code < 500:
                    return False
            return True
        return False

    def _download_and_convert(
        self,
        url: str,
        target_dir: Path,
        img_data: dict[str, Any]
    ) -> bool:
        """
        Download image with retry and convert to WebP if needed.

        Args:
            url: Image URL to download
            target_dir: Directory to save image
            img_data: Image metadata dict (will be updated with local_filename)

        Returns:
            True if successful, False otherwise
        """
        # Extract filename from URL
        parsed_url = parse.urlparse(url)
        original_filename = Path(parsed_url.path).name
        if not original_filename:
            original_filename = 'image.jpg'

        # Determine if conversion is needed
        ext = Path(original_filename).suffix.lower()
        should_convert = (
            self.convert_to_webp and
            HAS_PILLOW and
            ext in ('.jpg', '.jpeg', '.png', '.gif')
        )

        # Download with retry and exponential backoff
        image_data = None
        delay = self.retry_delay
        last_error = None

        for attempt in range(self.max_retries):
            try:
                with request.urlopen(url, timeout=self.timeout) as response:
                    image_data = response.read()
                    if attempt > 0:
                        print(f"  ✓ Successfully downloaded {url} on attempt {attempt + 1}", file=sys.stderr)
                    break
            except (error.URLError, error.HTTPError, TimeoutError) as e:
                last_error = e

                # Determine if we should retry
                should_retry = self._should_retry_error(e)

                # Format error message
                error_msg = str(e)
                if isinstance(e, error.HTTPError):
                    error_msg = f"HTTP {e.code}: {e.reason}"

                if attempt < self.max_retries - 1 and should_retry:
                    # Retry with backoff
                    print(
                        f"  ⚠ Attempt {attempt + 1}/{self.max_retries} failed: {error_msg}",
                        file=sys.stderr
                    )
                    print(f"    Retrying in {delay:.1f}s...", file=sys.stderr)
                    time.sleep(delay)
                    delay *= self.retry_backoff
                elif not should_retry:
                    # Permanent error, don't retry
                    print(
                        f"  ✗ Permanent error ({error_msg}), not retrying",
                        file=sys.stderr
                    )
                    return False
                else:
                    # All retries exhausted
                    print(
                        f"  ✗ Download failed after {self.max_retries} attempts: {error_msg}",
                        file=sys.stderr
                    )
                    return False

        if image_data is None:
            return False

        # Determine output filename
        if should_convert:
            base_name = Path(original_filename).stem
            output_filename = f"{base_name}.webp"
        else:
            output_filename = original_filename

        # Handle naming conflicts with incrementing suffix
        output_path = target_dir / output_filename
        if output_path.exists():
            base_name = Path(output_filename).stem
            ext = Path(output_filename).suffix
            counter = 2
            while output_path.exists():
                output_filename = f"{base_name}_{counter}{ext}"
                output_path = target_dir / output_filename
                counter += 1

        # Save and optionally convert
        actual_output_path = output_path  # Track actual path for cleanup
        try:
            if should_convert:
                # Convert to WebP using Pillow
                import io
                img = Image.open(io.BytesIO(image_data))

                # Check if GIF is animated
                is_animated = getattr(img, 'is_animated', False)
                if ext == '.gif' and is_animated:
                    # Don't convert animated GIFs
                    actual_output_path = output_path.with_suffix('.gif')
                    with open(actual_output_path, 'wb') as f:
                        f.write(image_data)
                    img_data['local_filename'] = actual_output_path.name
                else:
                    # Convert to lossless WebP
                    img.save(output_path, 'WEBP', lossless=True, quality=100)
                    img_data['local_filename'] = output_filename
            else:
                # Save without conversion
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                img_data['local_filename'] = output_filename

            return True

        except Exception as e:
            print(f"Error saving/converting image: {e}", file=sys.stderr)
            # Clean up partial file if it was created
            if actual_output_path.exists():
                try:
                    actual_output_path.unlink()
                except Exception as cleanup_error:
                    print(f"Warning: Failed to clean up partial file {actual_output_path}: {cleanup_error}", file=sys.stderr)
            return False

    def postprocess(
        self,
        file_path: Path,
        line_no: int,
        line: str,
        metadata: dict[str, Any]
    ) -> str:
        """
        Replace remote image URLs with local filenames.

        Only rewrites URLs that were successfully downloaded.
        Failed downloads remain as remote URLs.
        Preserves optional title if present.
        """
        images = metadata.get('images', [])
        if not images:
            return line

        # Build URL -> (local filename, title) mapping, only for successful downloads
        url_replacements = {}
        for img_data in images:
            # Only rewrite if download succeeded
            if img_data.get('success', False):
                url = img_data['url']
                local_filename = img_data.get('local_filename')
                title = img_data.get('title')
                if local_filename:
                    url_replacements[url] = (local_filename, title)

        # If no successful downloads, return line unchanged
        if not url_replacements:
            return line

        # Replace all successful URLs
        result = line
        for url, (local_filename, title) in url_replacements.items():
            # Construct the old and new image reference
            # Handle both with and without title
            if title:
                # Has title: ![alt](url "title") -> ![alt](local "title")
                old_ref = f']({url} {title})'
                new_ref = f']({local_filename} {title})'
            else:
                # No title: ![alt](url) -> ![alt](local)
                old_ref = f']({url})'
                new_ref = f']({local_filename})'

            result = result.replace(old_ref, new_ref)

        return result
