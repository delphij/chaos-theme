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
Main processing logic for auxmark tool.

Handles file scanning, line-by-line processing, expand operations,
preprocessing jobs, and post-processing.
"""

import subprocess
import sys
from pathlib import Path

from .core import Action, BaseModule, Job, PostprocessLine
from .worker import RateLimitedWorkerPool


class Processor:
    """Main processor for auxmark tool."""

    def __init__(
        self,
        modules: list[BaseModule],
        verbose: bool = False,
        dry_run: bool = False,
        max_workers: int = 4,
        rate_limit_delay: float = 1.0
    ):
        """
        Initialize processor.

        Args:
            modules: List of active modules
            verbose: Enable verbose logging
            dry_run: Don't modify files
            max_workers: Maximum number of concurrent workers
            rate_limit_delay: Minimum delay between requests to same domain (seconds)
        """
        self.modules = modules
        self.verbose = verbose
        self.dry_run = dry_run
        self.max_workers = max_workers
        self.rate_limit_delay = rate_limit_delay
        self.expanded_files: set[Path] = set()
        self.files_to_process: list[Path] = []

    def log(self, message: str) -> None:
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[auxmark] {message}")

    def expand_file(self, file_path: Path) -> Path | None:
        """
        Convert file.md to file/index.md (Hugo page bundle).

        Args:
            file_path: Path to file.md

        Returns:
            Path to new index.md file, or None if dry-run or error
        """
        if file_path.name == 'index.md':
            print(f"Warning: {file_path} is already index.md, skipping expand", file=sys.stderr)
            return None

        # Calculate new path: path/to/file.md -> path/to/file/index.md
        new_dir = file_path.parent / file_path.stem
        new_file = new_dir / 'index.md'

        self.log(f"Expanding: {file_path} -> {new_file}")

        if self.dry_run:
            print(f"[DRY-RUN] Would expand: {file_path} -> {new_file}")
            return new_file

        try:
            # Create directory
            new_dir.mkdir(parents=True, exist_ok=True)

            # Move file using git mv for better history tracking
            result = subprocess.run(
                ['git', 'mv', str(file_path), str(new_file)],
                capture_output=True,
                text=True,
                check=True
            )

            self.log(f"Expanded successfully: {new_file}")
            # Mark old file as expanded so it won't be processed again in this run
            self.expanded_files.add(file_path)

            return new_file

        except subprocess.CalledProcessError as e:
            print(f"Error expanding {file_path}: git mv failed: {e.stderr}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error expanding {file_path}: {e}", file=sys.stderr)
            return None

    def process_file(self, file_path: Path) -> None:
        """
        Process a single markdown file.

        Scans each line with all modules and dispatches actions.

        Args:
            file_path: Path to markdown file
        """
        # Skip if this file was already processed and expanded in this run
        # (the old path after moving to index.md)
        if file_path in self.expanded_files:
            self.log(f"Skipping file that was moved during expansion: {file_path}")
            return

        self.log(f"Processing: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            return

        file_needs_expand = False
        expand_module = None

        # Scan each line
        for line_no, line in enumerate(lines):
            for module in self.modules:
                # Check if line matches module's regex
                if not module.regex.search(line):
                    continue

                # Probe the line
                action, metadata = module.probe(file_path, line_no, line)

                if action == Action.IGNORE:
                    continue

                elif action == Action.TAG:
                    # Line needs postprocessing only
                    pp_line = PostprocessLine(
                        file_path=file_path,
                        line_no=line_no,
                        line=line,
                        metadata=metadata
                    )
                    module.postprocess_lines.append(pp_line)
                    self.log(f"  [{module.name}] Tagged for post-processing")

                elif action == Action.TAG_WITH_PREPROCESS_ONLY:
                    # Line needs preprocessing only, no postprocessing
                    job = Job(
                        file_path=file_path,
                        line_no=line_no,
                        line=line,
                        module_name=module.name,
                        metadata=metadata
                    )
                    module.jobs.append(job)
                    self.log(f"  [{module.name}] Tagged with preprocessing only")

                elif action == Action.TAG_WITH_PREPROCESS_AND_POSTPROCESS:
                    # Line needs both preprocessing and postprocessing
                    job = Job(
                        file_path=file_path,
                        line_no=line_no,
                        line=line,
                        module_name=module.name,
                        metadata=metadata
                    )
                    module.jobs.append(job)
                    pp_line = PostprocessLine(
                        file_path=file_path,
                        line_no=line_no,
                        line=line,
                        metadata=metadata
                    )
                    module.postprocess_lines.append(pp_line)
                    self.log(f"  [{module.name}] Tagged with preprocessing and post-processing")

                elif action == Action.EXPAND:
                    file_needs_expand = True
                    expand_module = module
                    self.log(f"  [{module.name}] Requesting file expand")

        # Handle EXPAND action
        if file_needs_expand:
            new_file = self.expand_file(file_path)
            if new_file and not self.dry_run:
                # Discard preprocessing jobs and postprocess lines for old file path
                for module in self.modules:
                    module.jobs = [j for j in module.jobs if j.file_path != file_path]
                    module.postprocess_lines = [
                        pp for pp in module.postprocess_lines if pp.file_path != file_path
                    ]
                self.log(f"  Discarded jobs for old path, will requeue: {new_file}")
                # Requeue the new file for processing
                self.files_to_process.append(new_file)

    def run_preprocessing(self) -> None:
        """
        Run preprocessing jobs for all modules using worker pool.

        Uses multi-threaded execution with per-domain rate limiting.
        """
        total_jobs = sum(len(m.jobs) for m in self.modules)
        if total_jobs == 0:
            self.log("No preprocessing jobs to run")
            return

        if self.max_workers == 1:
            self.log(f"Running {total_jobs} preprocessing jobs (single-threaded)...")
        else:
            self.log(f"Running {total_jobs} preprocessing jobs ({self.max_workers} workers, rate limit: {self.rate_limit_delay}s/domain)...")

        completed = 0
        failed = 0

        # Dry-run mode: just log what would be done
        if self.dry_run:
            for module in self.modules:
                for job in module.jobs:
                    print(f"[DRY-RUN] Would run preprocessing: {job.file_path}:{job.line_no}")
                    completed += 1
            self.log(f"Preprocessing complete: {completed} jobs (dry-run)")
            return

        # Use worker pool for actual execution
        with RateLimitedWorkerPool(
            max_workers=self.max_workers,
            rate_limit_delay=self.rate_limit_delay,
            verbose=self.verbose
        ) as pool:
            # Submit all jobs and collect futures
            futures = []
            job_info = []  # Track (future, module, job) for error reporting

            for module in self.modules:
                if not module.jobs:
                    continue

                self.log(f"[{module.name}] Processing {len(module.jobs)} jobs...")

                for job in module.jobs:
                    future = pool.submit_job(job, module)
                    futures.append(future)
                    job_info.append((future, module, job))

            # Wait for all jobs to complete and collect results
            for future, module, job in job_info:
                try:
                    success = future.result()
                    if success:
                        completed += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                    print(
                        f"Error in preprocessing {job.file_path}:{job.line_no}: {e}",
                        file=sys.stderr
                    )
                    if self.verbose:
                        import traceback
                        traceback.print_exc()

        self.log(f"Preprocessing complete: {completed} succeeded, {failed} failed")

    def run_postprocessing(self) -> None:
        """
        Run post-processing for all modules (line-oriented).

        Algorithm:
        1. Group postprocess_lines by file
        2. For each file:
           - Read all lines
           - Build lookup: line_no -> list of (module, metadata)
           - Process lines: call module.postprocess() for tagged lines
           - Write to temp file and replace original atomically
        """
        # Group postprocess_lines by file
        files_to_process: dict[Path, list[tuple[BaseModule, PostprocessLine]]] = {}

        for module in self.modules:
            for pp_line in module.postprocess_lines:
                if pp_line.file_path not in files_to_process:
                    files_to_process[pp_line.file_path] = []
                files_to_process[pp_line.file_path].append((module, pp_line))

        if not files_to_process:
            self.log("No post-processing needed")
            return

        total_lines = sum(len(v) for v in files_to_process.values())
        self.log(f"Running post-processing on {len(files_to_process)} files ({total_lines} lines)...")

        # Process each file
        for file_path, tagged_lines in files_to_process.items():
            self.log(f"Post-processing: {file_path} ({len(tagged_lines)} lines)")

            if self.dry_run:
                print(f"[DRY-RUN] Would post-process {len(tagged_lines)} lines in {file_path}")
                continue

            try:
                # Read file
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # Build lookup: line_no -> list of (module, metadata)
                line_map: dict[int, list[tuple[BaseModule, dict]]] = {}
                for module, pp_line in tagged_lines:
                    if pp_line.line_no not in line_map:
                        line_map[pp_line.line_no] = []
                    line_map[pp_line.line_no].append((module, pp_line.metadata))

                # Process lines
                new_lines = []
                for line_no, line in enumerate(lines):
                    if line_no in line_map:
                        # Line is tagged - call each module's postprocess
                        for module, metadata in line_map[line_no]:
                            line = module.postprocess(file_path, line_no, line, metadata)
                            self.log(f"  [{module.name}] Rewrote line {line_no}")
                    new_lines.append(line)

                # Write to temp file and replace atomically
                temp_file = file_path.with_suffix('.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                temp_file.replace(file_path)

                self.log(f"  ✓ Updated: {file_path}")

            except Exception as e:
                print(f"Error in post-processing {file_path}: {e}", file=sys.stderr)

        self.log("Post-processing complete")

    def process_all(self, files: list[Path]) -> None:
        """
        Main processing pipeline.

        Args:
            files: List of markdown files to process
        """
        self.files_to_process = files.copy()
        processed_count = 0

        # Main loop with dynamic file list (handles EXPAND operations)
        while self.files_to_process:
            file_path = self.files_to_process.pop(0)
            self.process_file(file_path)
            processed_count += 1

        self.log(f"Scanned {processed_count} files")

        # Run preprocessing jobs
        self.run_preprocessing()

        # Run post-processing
        self.run_postprocessing()
