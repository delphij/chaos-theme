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

import shutil
import sys
from pathlib import Path

from .core import Action, BaseModule, Job


class Processor:
    """Main processor for auxmark tool."""

    def __init__(self, modules: list[BaseModule], verbose: bool = False, dry_run: bool = False):
        """
        Initialize processor.

        Args:
            modules: List of active modules
            verbose: Enable verbose logging
            dry_run: Don't modify files
        """
        self.modules = modules
        self.verbose = verbose
        self.dry_run = dry_run
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

            # Move file
            shutil.move(str(file_path), str(new_file))

            self.log(f"Expanded successfully: {new_file}")
            self.expanded_files.add(new_file)

            return new_file

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
        # Skip if already expanded
        if file_path in self.expanded_files:
            self.log(f"Skipping already-expanded file: {file_path}")
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
                    module.todo_files.add(file_path)
                    self.log(f"  [{module.name}] Tagged for post-processing")

                elif action == Action.TAG_WITH_PREPROCESS:
                    module.todo_files.add(file_path)
                    job = Job(
                        file_path=file_path,
                        line_no=line_no,
                        line=line,
                        module_name=module.name,
                        metadata=metadata
                    )
                    module.jobs.append(job)
                    self.log(f"  [{module.name}] Tagged with preprocessing job")

                elif action == Action.EXPAND:
                    file_needs_expand = True
                    expand_module = module
                    self.log(f"  [{module.name}] Requesting file expand")

        # Handle EXPAND action
        if file_needs_expand:
            new_file = self.expand_file(file_path)
            if new_file and not self.dry_run:
                # Discard preprocessing jobs for old file path
                for module in self.modules:
                    module.jobs = [j for j in module.jobs if j.file_path != file_path]
                    if file_path in module.todo_files:
                        module.todo_files.remove(file_path)
                self.log(f"  Discarded jobs for old path, will requeue: {new_file}")
                # Requeue the new file for processing
                self.files_to_process.append(new_file)

    def run_preprocessing(self) -> None:
        """
        Run preprocessing jobs for all modules.

        Phase 1: Single-threaded execution.
        """
        total_jobs = sum(len(m.jobs) for m in self.modules)
        if total_jobs == 0:
            self.log("No preprocessing jobs to run")
            return

        self.log(f"Running {total_jobs} preprocessing jobs (single-threaded)...")

        completed = 0
        failed = 0

        for module in self.modules:
            if not module.jobs:
                continue

            self.log(f"[{module.name}] Processing {len(module.jobs)} jobs...")

            for job in module.jobs:
                if self.dry_run:
                    print(f"[DRY-RUN] Would run preprocessing: {job.file_path}:{job.line_no}")
                    completed += 1
                    continue

                try:
                    success = module.preprocess(job)
                    if success:
                        completed += 1
                    else:
                        failed += 1
                        print(f"Preprocessing failed for {job.file_path}:{job.line_no}", file=sys.stderr)
                except Exception as e:
                    failed += 1
                    print(f"Error in preprocessing {job.file_path}:{job.line_no}: {e}", file=sys.stderr)

        self.log(f"Preprocessing complete: {completed} succeeded, {failed} failed")

    def run_postprocessing(self) -> None:
        """
        Run post-processing for all modules.

        Each module receives its TODO files for final processing.
        """
        total_files = sum(len(m.todo_files) for m in self.modules)
        if total_files == 0:
            self.log("No post-processing needed")
            return

        self.log(f"Running post-processing on {total_files} files...")

        for module in self.modules:
            if not module.todo_files:
                continue

            self.log(f"[{module.name}] Post-processing {len(module.todo_files)} files...")

            for file_path in module.todo_files:
                if self.dry_run:
                    print(f"[DRY-RUN] Would run post-processing: {file_path}")
                    continue

                try:
                    success = module.postprocess(file_path)
                    if not success:
                        print(f"Post-processing failed for {file_path}", file=sys.stderr)
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
