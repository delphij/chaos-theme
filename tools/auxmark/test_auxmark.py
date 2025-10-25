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


def test_image_localizer_expand():
    """Test that image localizer requests EXPAND for non-index.md files."""
    print("\n[Test 5] Image localizer - EXPAND action")

    site_root = create_test_site()

    try:
        # Create a non-index.md file with external image
        content_dir = site_root / "content" / "posts"
        post = content_dir / "image-post.md"
        post.write_text("""+++
title = "Post with Image"
date = 2024-01-04T12:00:00Z
+++

External image:
![Test](https://via.placeholder.com/150)
""")

        # Add to git
        subprocess.run(["git", "add", "."], cwd=site_root, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add image post"],
            cwd=site_root,
            check=True,
            capture_output=True
        )

        # Run with image localizer only
        returncode, stdout, stderr = run_auxmark(
            site_root,
            "--module", "image",
            "--dry-run",
            "--verbose"
        )

        if returncode != 0:
            print(f"STDERR:\n{stderr}")
            print("✗ FAILED: Non-zero return code")
            return False

        # Should request expand
        if "[image_localizer] Requesting file expand" not in stdout:
            print("✗ FAILED: EXPAND action not requested")
            return False

        # Should show expand would happen
        if "Would expand:" not in stdout or "image-post/index.md" not in stdout:
            print("✗ FAILED: Expand operation not shown")
            return False

        print("✓ PASSED: Image localizer correctly requests EXPAND")
        return True

    finally:
        shutil.rmtree(site_root)


def test_image_localizer_detection():
    """Test that image localizer detects external images correctly."""
    print("\n[Test 6] Image localizer - detection logic")

    site_root = create_test_site()

    try:
        # Create index.md with various image types
        content_dir = site_root / "content" / "posts"
        article_dir = content_dir / "article"
        article_dir.mkdir()
        index_md = article_dir / "index.md"
        index_md.write_text("""+++
title = "Article with Images"
date = 2024-01-05T12:00:00Z
+++

External image:
![Image1](https://example.com/image1.jpg)

Multiple on one line:
![A](https://example.com/a.png) and ![B](https://example.com/b.gif)

Local image (should be ignored):
![Local](./local.png)

Relative image (should be ignored):
![Relative](images/foo.jpg)
""")

        # Add to git
        subprocess.run(["git", "add", "."], cwd=site_root, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add article"],
            cwd=site_root,
            check=True,
            capture_output=True
        )

        # Run with image localizer only
        returncode, stdout, stderr = run_auxmark(
            site_root,
            "--module", "image",
            "--dry-run",
            "--verbose"
        )

        if returncode != 0:
            print(f"STDERR:\n{stderr}")
            print("✗ FAILED: Non-zero return code")
            return False

        # Count detected images (should find 3 external images on 2 lines)
        preprocessing_count = stdout.count("[image_localizer] Tagged with preprocessing and post-processing")
        if preprocessing_count != 2:  # 2 lines with external images
            print(f"✗ FAILED: Expected 2 lines tagged, found {preprocessing_count}")
            return False

        # Should have 2 preprocessing jobs (one per line, even though line 2 has 2 images)
        job_count = stdout.count("[image_localizer] Processing 2 jobs")
        if job_count != 1:
            print(f"✗ FAILED: Expected 2 preprocessing jobs (one per line)")
            print(f"STDOUT:\n{stdout}")
            return False

        print("✓ PASSED: Image localizer correctly detects external images")
        return True

    finally:
        shutil.rmtree(site_root)


def test_image_localizer_postprocessing():
    """Test that postprocessing would rewrite URLs."""
    print("\n[Test 7] Image localizer - postprocessing")

    site_root = create_test_site()

    try:
        # Create index.md with external image
        content_dir = site_root / "content" / "posts"
        article_dir = content_dir / "article2"
        article_dir.mkdir()
        index_md = article_dir / "index.md"
        index_md.write_text("""+++
title = "Article"
date = 2024-01-06T12:00:00Z
+++

![Test](https://example.com/test.jpg)
""")

        # Add to git
        subprocess.run(["git", "add", "."], cwd=site_root, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add article2"],
            cwd=site_root,
            check=True,
            capture_output=True
        )

        # Run with image localizer (dry-run)
        returncode, stdout, stderr = run_auxmark(
            site_root,
            "--module", "image",
            "--dry-run",
            "--verbose"
        )

        if returncode != 0:
            print(f"STDERR:\n{stderr}")
            print("✗ FAILED: Non-zero return code")
            return False

        # Should have preprocessing job
        if "[image_localizer] Processing 1 jobs" not in stdout:
            print("✗ FAILED: No preprocessing jobs found")
            return False

        # Should mention postprocessing
        if "post-processing on 1 files (1 lines)" not in stdout:
            print("✗ FAILED: Postprocessing not planned")
            print(f"STDOUT:\n{stdout}")
            return False

        print("✓ PASSED: Image localizer plans postprocessing")
        return True

    finally:
        shutil.rmtree(site_root)


def test_image_localizer_real_download():
    """Test actual image download and URL rewriting with real JPEG."""
    print("\n[Test 8] Image localizer - real download and rewrite")

    site_root = create_test_site()

    try:
        # Create index.md with real external image
        content_dir = site_root / "content" / "posts"
        article_dir = content_dir / "real_image"
        article_dir.mkdir()
        index_md = article_dir / "index.md"

        # Use picsum.photos for reliable test image
        original_content = """+++
title = "Real Image Test"
date = 2024-01-07T12:00:00Z
+++

This has a real image from the internet:

![Sample Image](https://picsum.photos/200/300.jpg)

End of content.
"""
        index_md.write_text(original_content)

        # Add to git
        subprocess.run(["git", "add", "."], cwd=site_root, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add real image test"],
            cwd=site_root,
            check=True,
            capture_output=True
        )

        # Run with image localizer (NOT dry-run - actually download)
        returncode, stdout, stderr = run_auxmark(
            site_root,
            "--module", "image",
            "--verbose"
        )

        if returncode != 0:
            print(f"STDERR:\n{stderr}")
            print("✗ FAILED: Non-zero return code")
            return False

        # Verify image was downloaded
        # Should be converted to WebP
        webp_files = list(article_dir.glob("*.webp"))
        jpg_files = list(article_dir.glob("*.jpg"))

        if not webp_files and not jpg_files:
            print("✗ FAILED: No image file downloaded")
            print(f"Files in directory: {list(article_dir.iterdir())}")
            return False

        # Prefer WebP if Pillow is available, otherwise JPG
        if webp_files:
            downloaded_file = webp_files[0]
            expected_extension = ".webp"
            print(f"  ✓ Image converted to WebP: {downloaded_file.name}")
        else:
            downloaded_file = jpg_files[0]
            expected_extension = ".jpg"
            print(f"  ✓ Image downloaded as JPEG: {downloaded_file.name}")

        # Verify file exists and has content
        if not downloaded_file.exists() or downloaded_file.stat().st_size == 0:
            print("✗ FAILED: Downloaded file is empty or doesn't exist")
            return False

        print(f"  ✓ Downloaded file size: {downloaded_file.stat().st_size} bytes")

        # Verify URL was rewritten in markdown
        rewritten_content = index_md.read_text()

        # Should no longer contain the original URL
        if "https://picsum.photos/200/300.jpg" in rewritten_content:
            print("✗ FAILED: Original URL still present in markdown")
            print(f"Content:\n{rewritten_content}")
            return False

        # Should contain reference to local file (without ./ prefix)
        local_filename = downloaded_file.name
        expected_reference = f"![Sample Image]({local_filename})"

        if expected_reference not in rewritten_content:
            print(f"✗ FAILED: Expected reference '{expected_reference}' not found in markdown")
            print(f"Content:\n{rewritten_content}")
            return False

        print(f"  ✓ URL correctly rewritten to: {local_filename}")
        print("✓ PASSED: Real image downloaded and URL rewritten correctly")
        return True

    except Exception as e:
        print(f"✗ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        shutil.rmtree(site_root)


def test_image_localizer_partial_failure():
    """Test that partial failures are handled correctly."""
    print("\n[Test 9] Image localizer - partial failure handling")

    site_root = create_test_site()

    try:
        # Create index.md with one valid and one invalid image
        content_dir = site_root / "content" / "posts"
        article_dir = content_dir / "partial_test"
        article_dir.mkdir()
        index_md = article_dir / "index.md"

        # Use one valid URL and one invalid URL
        original_content = """+++
title = "Partial Failure Test"
date = 2024-01-08T12:00:00Z
+++

Valid image: ![Valid](https://picsum.photos/100/100.jpg)

Invalid image: ![Invalid](https://invalid-domain-that-does-not-exist-12345.com/image.jpg)

Another valid: ![Valid2](https://picsum.photos/150/150.jpg)
"""
        index_md.write_text(original_content)

        # Add to git
        subprocess.run(["git", "add", "."], cwd=site_root, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add partial test"],
            cwd=site_root,
            check=True,
            capture_output=True
        )

        # Run with image localizer (NOT dry-run)
        returncode, stdout, stderr = run_auxmark(
            site_root,
            "--module", "image",
            "--verbose"
        )

        # Should complete even with partial failure (non-zero might be acceptable)
        # The key is that it should process what it can

        # Check what files were created
        webp_files = list(article_dir.glob("*.webp"))
        jpg_files = list(article_dir.glob("*.jpg"))
        downloaded_files = webp_files + jpg_files

        # Should have 2 successful downloads (not 3)
        if len(downloaded_files) != 2:
            print(f"✗ FAILED: Expected 2 downloaded files, found {len(downloaded_files)}")
            print(f"Files: {[f.name for f in downloaded_files]}")
            return False

        print(f"  ✓ Downloaded {len(downloaded_files)} successful images")

        # Check file content
        rewritten_content = index_md.read_text()

        # Should contain at least one local reference
        has_local_reference = any(
            f"![]({f.name})" in rewritten_content or f"![Valid]({f.name})" in rewritten_content or f"![Valid2]({f.name})" in rewritten_content
            for f in downloaded_files
        )

        if not has_local_reference:
            print("✗ FAILED: No local references found in rewritten content")
            print(f"Content:\n{rewritten_content}")
            return False

        # Should still contain the invalid URL (unchanged)
        if "invalid-domain-that-does-not-exist-12345.com" not in rewritten_content:
            print("✗ FAILED: Invalid URL was removed (should remain unchanged)")
            print(f"Content:\n{rewritten_content}")
            return False

        print("  ✓ Successfully downloaded images rewritten to local references")
        print("  ✓ Failed download URL remains unchanged")
        print("✓ PASSED: Partial failure handled correctly")
        return True

    except Exception as e:
        print(f"✗ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        shutil.rmtree(site_root)


def test_image_localizer_with_title():
    """Test that optional title in image syntax is preserved."""
    print("\n[Test 10] Image localizer - preserve optional title")

    site_root = create_test_site()

    try:
        # Create index.md with images having optional titles
        content_dir = site_root / "content" / "posts"
        article_dir = content_dir / "title_test"
        article_dir.mkdir()
        index_md = article_dir / "index.md"

        original_content = """+++
title = "Title Preservation Test"
date = 2024-01-09T12:00:00Z
+++

Image with title: ![Sample](https://picsum.photos/200/200.jpg "This is a sample image")

Image without title: ![Another](https://picsum.photos/250/250.jpg)

Image with single quote title: ![Third](https://picsum.photos/300/300.jpg 'Single quote title')
"""
        index_md.write_text(original_content)

        # Add to git
        subprocess.run(["git", "add", "."], cwd=site_root, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add title test"],
            cwd=site_root,
            check=True,
            capture_output=True
        )

        # Run with image localizer
        returncode, stdout, stderr = run_auxmark(
            site_root,
            "--module", "image",
            "--verbose"
        )

        if returncode != 0:
            print(f"STDERR:\n{stderr}")
            print("✗ FAILED: Non-zero return code")
            return False

        # Check file content
        rewritten_content = index_md.read_text()

        # Should NOT contain original URLs
        if "https://picsum.photos/200/200.jpg" in rewritten_content:
            print("✗ FAILED: Original URL still present")
            print(f"Content:\n{rewritten_content}")
            return False

        # Should contain local references with preserved titles
        if '"This is a sample image"' not in rewritten_content:
            print("✗ FAILED: Double-quoted title not preserved")
            print(f"Content:\n{rewritten_content}")
            return False

        if "'Single quote title'" not in rewritten_content:
            print("✗ FAILED: Single-quoted title not preserved")
            print(f"Content:\n{rewritten_content}")
            return False

        # Verify local files were created
        webp_files = list(article_dir.glob("*.webp"))
        jpg_files = list(article_dir.glob("*.jpg"))
        downloaded_files = webp_files + jpg_files

        if len(downloaded_files) != 3:
            print(f"✗ FAILED: Expected 3 images, found {len(downloaded_files)}")
            return False

        # Check that local filename is used with title
        has_local_with_title = False
        for f in downloaded_files:
            if f']({f.name} "' in rewritten_content or f']({f.name} \'' in rewritten_content:
                has_local_with_title = True
                break

        if not has_local_with_title:
            print("✗ FAILED: No local filename found with preserved title")
            print(f"Content:\n{rewritten_content}")
            return False

        print("  ✓ Double-quoted title preserved")
        print("  ✓ Single-quoted title preserved")
        print("  ✓ Local filenames used with titles")
        print("✓ PASSED: Optional titles preserved correctly")
        return True

    except Exception as e:
        print(f"✗ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False
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
        test_image_localizer_expand,
        test_image_localizer_detection,
        test_image_localizer_postprocessing,
        test_image_localizer_real_download,
        test_image_localizer_partial_failure,
        test_image_localizer_with_title,
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
