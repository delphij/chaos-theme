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
Test suite for auxmark tool.

Creates a temporary Hugo site with sample content and runs auxmark to verify
functionality without requiring production data.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def create_test_site() -> Path:
    """
    Create a temporary Hugo site for testing.

    Returns:
        Path to temporary site root
    """
    tmpdir = Path(tempfile.mkdtemp(prefix="auxmark_test_"))
    print(f"Creating test site in: {tmpdir}")

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=tmpdir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmpdir,
        check=True,
        capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmpdir,
        check=True,
        capture_output=True
    )

    # Create Hugo config
    config = tmpdir / "hugo.toml"
    config.write_text("""
baseURL = 'https://example.org/'
languageCode = 'en-us'
title = 'Test Site'
""")

    # Create content structure
    content_dir = tmpdir / "content" / "posts"
    content_dir.mkdir(parents=True)

    # Create data directory
    data_dir = tmpdir / "data" / "x_embeds"
    data_dir.mkdir(parents=True)

    # Sample post with tweet shortcode
    post1 = content_dir / "post-with-tweet.md"
    post1.write_text("""+++
title = "Sample Post with Tweet"
date = 2024-01-01T12:00:00Z
+++

This is a sample post that embeds a tweet.

{{< x user="testuser" id="1234567890" >}}

More content here.
""")

    # Sample post without tweet
    post2 = content_dir / "regular-post.md"
    post2.write_text("""+++
title = "Regular Post"
date = 2024-01-02T12:00:00Z
+++

This is a regular post with no embeds.

Just some sample content.
""")

    # Sample post with multiple tweets
    post3 = content_dir / "multi-tweet.md"
    post3.write_text("""+++
title = "Post with Multiple Tweets"
date = 2024-01-03T12:00:00Z
+++

First tweet:
{{< x user="user1" id="1111111111" >}}

Second tweet:
{{< x user="user2" id="2222222222" >}}

Done.
""")

    # Add all files to git
    subprocess.run(["git", "add", "."], cwd=tmpdir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=tmpdir,
        check=True,
        capture_output=True
    )

    print(f"✓ Created test site with 3 sample posts")
    return tmpdir


def run_auxmark(site_root: Path, *args) -> tuple[int, str, str]:
    """
    Run auxmark tool on test site.

    Args:
        site_root: Path to test site
        *args: Additional command-line arguments

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    # Get path to auxmark.py
    auxmark_path = Path(__file__).parent.parent / "auxmark.py"

    cmd = [sys.executable, str(auxmark_path)] + list(args)

    result = subprocess.run(
        cmd,
        cwd=site_root,
        capture_output=True,
        text=True
    )

    return result.returncode, result.stdout, result.stderr


def test_dry_run():
    """Test that dry-run mode doesn't modify files."""
    print("\n[Test 1] Dry-run mode")

    site_root = create_test_site()

    try:
        # Run in dry-run mode
        returncode, stdout, stderr = run_auxmark(site_root, "--dry-run", "--verbose")

        print(f"Return code: {returncode}")

        if returncode != 0:
            print(f"STDERR:\n{stderr}")
            print("✗ FAILED: Non-zero return code")
            return False

        # Check that it detected the tweets
        if "DRY-RUN" not in stdout:
            print("✗ FAILED: Dry-run mode not active")
            return False

        # Count detected tweets
        tweet_count = stdout.count("[tweet_downloader] Tagged with preprocessing only")
        if tweet_count != 3:
            print(f"✗ FAILED: Expected 3 tweets, found {tweet_count}")
            return False

        # Verify no cache files created
        cache_dir = site_root / "data" / "x_embeds"
        cache_files = list(cache_dir.glob("*.json"))
        if cache_files:
            print(f"✗ FAILED: Cache files created in dry-run mode: {cache_files}")
            return False

        print("✓ PASSED: Detected 3 tweets, no files modified")
        return True

    finally:
        shutil.rmtree(site_root)


def test_module_selection():
    """Test module filtering with --module option."""
    print("\n[Test 2] Module selection")

    site_root = create_test_site()

    try:
        # Run with explicit module selection
        returncode, stdout, stderr = run_auxmark(
            site_root,
            "--module", "tweet",
            "--dry-run",
            "--verbose"
        )

        if returncode != 0:
            print(f"STDERR:\n{stderr}")
            print("✗ FAILED: Non-zero return code")
            return False

        if "tweet_downloader" not in stdout:
            print("✗ FAILED: Module not activated")
            return False

        print("✓ PASSED: Module selection works")
        return True

    finally:
        shutil.rmtree(site_root)


def test_file_scanning():
    """Test that only git-tracked files are scanned."""
    print("\n[Test 3] Git-aware file scanning")

    site_root = create_test_site()

    try:
        # Create an untracked file
        untracked = site_root / "content" / "posts" / "untracked.md"
        untracked.write_text("# Untracked\n{{< x user=\"test\" id=\"9999999999\" >}}")

        # Run auxmark
        returncode, stdout, stderr = run_auxmark(site_root, "--dry-run", "--verbose")

        if returncode != 0:
            print(f"STDERR:\n{stderr}")
            print("✗ FAILED: Non-zero return code")
            return False

        # Should still find only 3 tweets (not the untracked one)
        tweet_count = stdout.count("[tweet_downloader] Tagged with preprocessing only")
        if tweet_count != 3:
            print(f"✗ FAILED: Expected 3 tweets (ignoring untracked), found {tweet_count}")
            return False

        print("✓ PASSED: Only git-tracked files scanned")
        return True

    finally:
        shutil.rmtree(site_root)


def test_verbose_output():
    """Test verbose logging."""
    print("\n[Test 4] Verbose output")

    site_root = create_test_site()

    try:
        # Run without verbose
        returncode, stdout_quiet, stderr = run_auxmark(site_root, "--dry-run")

        # Run with verbose
        returncode, stdout_verbose, stderr = run_auxmark(site_root, "--dry-run", "--verbose")

        if len(stdout_verbose) <= len(stdout_quiet):
            print("✗ FAILED: Verbose mode didn't produce more output")
            return False

        if "[auxmark]" not in stdout_verbose:
            print("✗ FAILED: Missing [auxmark] log prefix")
            return False

        print("✓ PASSED: Verbose output works")
        return True

    finally:
        shutil.rmtree(site_root)


def main() -> int:
    """Run all tests."""
    print("=" * 60)
    print("auxmark Test Suite")
    print("=" * 60)
    print("\nGenerates sample data and tests core functionality")
    print("without requiring production content.\n")

    tests = [
        test_dry_run,
        test_module_selection,
        test_file_scanning,
        test_verbose_output,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
