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
auxmark - Auxiliary Markdown Processing Tool for Hugo

A modular tool for processing Markdown files under git control.
Supports preprocessing (downloading, fetching), file expansion (page bundles),
and post-processing (rewriting).
"""

__version__ = "0.1.0"

from .core import Action, BaseModule, Job, ModuleRegistry
from .processor import Processor
from .scanner import find_git_root, scan_markdown_files

__all__ = [
    "Action",
    "BaseModule",
    "Job",
    "ModuleRegistry",
    "Processor",
    "find_git_root",
    "scan_markdown_files",
]
