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
Core infrastructure for auxmark tool.

Provides BaseModule interface, ModuleRegistry, and Action types.
"""

import re
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any


class Action(Enum):
    """Actions that modules can return from probe()."""
    IGNORE = auto()                              # Not interested in this line
    TAG = auto()                                 # Line needs postprocessing only
    TAG_WITH_PREPROCESS_ONLY = auto()            # Line needs preprocessing only, no postprocessing
    TAG_WITH_PREPROCESS_AND_POSTPROCESS = auto() # Line needs both preprocessing and postprocessing
    EXPAND = auto()                              # Convert file.md -> file/index.md


@dataclass
class Job:
    """Represents a preprocessing job."""
    file_path: Path
    line_no: int
    line: str
    module_name: str
    metadata: dict[str, Any]


@dataclass
class PostprocessLine:
    """Represents a line tagged for postprocessing."""
    file_path: Path
    line_no: int
    line: str
    metadata: dict[str, Any]


class BaseModule:
    """
    Base class for all auxmark modules.

    Modules should inherit this class and implement:
    - name: Unique module identifier
    - regex: Pattern to match lines (use .* for match-all, optimize later)
    - probe(): Analyze line and return Action
    - preprocess(): Optional preprocessing (download, fetch, etc.)
    - postprocess(): Optional file rewriting
    """

    name: str = "base"
    regex: re.Pattern = re.compile(".*")

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize module with optional configuration."""
        self.config = config or {}
        self.postprocess_lines: list[PostprocessLine] = []
        self.jobs: list[Job] = []

    def probe(self, file_path: Path, line_no: int, line: str) -> tuple[Action, dict[str, Any]]:
        """
        Analyze a line and decide what action to take.

        Args:
            file_path: Path to the markdown file being scanned
            line_no: Line number (0-indexed)
            line: Content of the line

        Returns:
            Tuple of (Action, metadata_dict)
            metadata_dict is passed to preprocess() if needed
        """
        return (Action.IGNORE, {})

    def preprocess(self, job: Job) -> bool:
        """
        Execute preprocessing task (download, fetch API, etc.).

        Args:
            job: Job object containing file path, line info, and metadata

        Returns:
            True if successful, False otherwise
        """
        return True

    def postprocess(self, file_path: Path, line_no: int, line: str, metadata: dict[str, Any]) -> str:
        """
        Rewrite a single line (line-oriented postprocessing).

        Args:
            file_path: Path to file being processed
            line_no: Line number (0-indexed)
            line: Original line content
            metadata: Context data from probe phase

        Returns:
            Rewritten line (or original if no changes needed)
        """
        return line


class ModuleRegistry:
    """Registry for managing modules."""

    _modules: dict[str, type[BaseModule]] = {}

    @classmethod
    def register(cls, module_class: type[BaseModule]) -> None:
        """
        Register a module class.

        Args:
            module_class: Class inheriting from BaseModule
        """
        name = module_class.name
        if name in cls._modules:
            raise ValueError(f"Module '{name}' is already registered")
        cls._modules[name] = module_class

    @classmethod
    def get(cls, name: str) -> type[BaseModule] | None:
        """Get a module class by name."""
        return cls._modules.get(name)

    @classmethod
    def get_all(cls) -> dict[str, type[BaseModule]]:
        """Get all registered modules."""
        return cls._modules.copy()

    @classmethod
    def instantiate_all(cls, config: dict[str, Any] | None = None) -> list[BaseModule]:
        """
        Instantiate all registered modules.

        Args:
            config: Optional configuration dict

        Returns:
            List of instantiated module objects
        """
        modules = []
        for module_class in cls._modules.values():
            module_config = (config or {}).get(module_class.name, {})
            modules.append(module_class(module_config))
        return modules
