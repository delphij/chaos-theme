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
auxmark - Auxiliary Markdown Processing Tool

Main CLI entrypoint for the auxmark tool.
"""

import argparse
import sys

from . import ModuleRegistry, Processor, find_git_root, scan_markdown_files
from .modules import ImageLocalizerModule, TweetDownloaderModule


def main() -> int:
    """Main entrypoint for auxmark CLI."""
    parser = argparse.ArgumentParser(
        description="Auxiliary Markdown processing tool for Hugo sites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  auxmark                    # Process all markdown files
  auxmark --verbose          # Show detailed progress
  auxmark --dry-run          # Show what would be done without doing it
  auxmark --module tweet     # Run only tweet_downloader module

Phase 1: Hardcoded module registration (tweet_downloader only)
        """
    )

    parser.add_argument(
        '--module',
        type=str,
        help='Comma-separated list of modules to run (default: all)',
        default=None
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    # Find git root
    git_root = find_git_root()
    if not git_root:
        print("Error: Not in a git repository", file=sys.stderr)
        return 1

    if args.verbose:
        print(f"[auxmark] Git root: {git_root}")

    # Register modules (hardcoded for Phase 1)
    ModuleRegistry.register(ImageLocalizerModule)
    ModuleRegistry.register(TweetDownloaderModule)

    if args.verbose:
        print(f"[auxmark] Registered modules: {list(ModuleRegistry.get_all().keys())}")

    # Filter modules if --module specified
    if args.module:
        requested = set(m.strip() for m in args.module.split(','))
        available = set(ModuleRegistry.get_all().keys())

        # Allow short names (e.g., "tweet" for "tweet_downloader")
        module_map = {
            'image': 'image_localizer',
            'tweet': 'tweet_downloader',
        }

        # Expand short names
        expanded = set()
        for mod in requested:
            if mod in available:
                expanded.add(mod)
            elif mod in module_map and module_map[mod] in available:
                expanded.add(module_map[mod])
            else:
                print(f"Warning: Unknown module '{mod}', skipping", file=sys.stderr)

        if not expanded:
            print("Error: No valid modules specified", file=sys.stderr)
            return 1

        # Unregister modules not in the requested set
        all_modules = ModuleRegistry.get_all().copy()
        for name in all_modules:
            if name not in expanded:
                ModuleRegistry._modules.pop(name)

        if args.verbose:
            print(f"[auxmark] Active modules: {list(ModuleRegistry.get_all().keys())}")

    # Scan for markdown files
    if args.verbose:
        print("[auxmark] Scanning for markdown files...")

    files = scan_markdown_files(git_root)

    if not files:
        print("No markdown files found under git control", file=sys.stderr)
        return 1

    if args.verbose:
        print(f"[auxmark] Found {len(files)} markdown files")

    # Instantiate modules
    modules = ModuleRegistry.instantiate_all()

    # Create processor
    processor = Processor(modules, verbose=args.verbose, dry_run=args.dry_run)

    # Process all files
    try:
        processor.process_all(files)
    except KeyboardInterrupt:
        print("\n[auxmark] Interrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"[auxmark] Fatal error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    print("[auxmark] Done!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
