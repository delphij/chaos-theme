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
from pathlib import Path

from . import ModuleRegistry, Processor, find_git_root, scan_markdown_files
from .config import load_config
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
    parser.add_argument(
        '--config',
        type=str,
        help='Path to config file (default: auto-discover .auxmark.toml)',
        default=None
    )
    parser.add_argument(
        '--workers',
        type=int,
        help='Number of concurrent workers (default: 4, use 1 for single-threaded)',
        default=None
    )

    args = parser.parse_args()

    # Find git root
    git_root = find_git_root()
    if not git_root:
        print("Error: Not in a git repository", file=sys.stderr)
        return 1

    if args.verbose:
        print(f"[auxmark] Git root: {git_root}")

    # Load configuration
    config_path = Path(args.config) if args.config else None
    config = load_config(config_path=config_path, git_root=git_root)

    if args.verbose:
        if config_path:
            print(f"[auxmark] Loaded config from: {config_path}")
        elif args.config is None:
            from .config import find_config_file
            found_config = find_config_file(git_root)
            if found_config:
                print(f"[auxmark] Loaded config from: {found_config}")
            else:
                print("[auxmark] No config file found, using defaults")

    # CLI arguments override config file
    if args.verbose:
        config['general']['verbose'] = True
    if args.dry_run:
        config['general']['dry_run'] = True

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

    # Instantiate modules with configuration
    modules = ModuleRegistry.instantiate_all(config)

    # Get worker pool configuration
    worker_config = config.get('worker', {})
    max_workers = worker_config.get('max_workers', 4)
    rate_limit_delay = worker_config.get('rate_limit_delay', 1.0)

    # CLI argument overrides config
    if args.workers is not None:
        max_workers = args.workers

    # Create processor
    processor = Processor(
        modules,
        verbose=args.verbose,
        dry_run=args.dry_run,
        max_workers=max_workers,
        rate_limit_delay=rate_limit_delay
    )

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
