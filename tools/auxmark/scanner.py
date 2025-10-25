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
File scanner for finding Markdown files under git control.
"""

import subprocess
import sys
from pathlib import Path


def find_git_root() -> Path | None:
    """
    Find the git repository root directory.

    Returns:
        Path to git root, or None if not in a git repo
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        print("Error: git command not found", file=sys.stderr)
        return None


def scan_markdown_files(root: Path | None = None) -> list[Path]:
    """
    Find all Markdown files under git control.

    Args:
        root: Git repository root (auto-detected if None)

    Returns:
        List of Path objects for .md files under git control
    """
    if root is None:
        root = find_git_root()
        if root is None:
            print("Error: Not in a git repository", file=sys.stderr)
            return []

    try:
        result = subprocess.run(
            ['git', 'ls-files', '*.md', '**/*.md'],
            cwd=root,
            capture_output=True,
            text=True,
            check=True
        )

        files = []
        for line in result.stdout.strip().split('\n'):
            if line:
                file_path = root / line
                if file_path.exists() and file_path.suffix == '.md':
                    files.append(file_path)

        return files

    except subprocess.CalledProcessError as e:
        print(f"Error running git ls-files: {e}", file=sys.stderr)
        return []
    except FileNotFoundError:
        print("Error: git command not found", file=sys.stderr)
        return []
