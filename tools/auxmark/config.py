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
Configuration management for auxmark tool.

Loads configuration from .auxmark.toml files with fallback to defaults.
"""

import sys
from pathlib import Path
from typing import Any

# Python 3.11+ has tomllib in stdlib
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: Python 3.11+ required, or install tomli: pip install tomli", file=sys.stderr)
        sys.exit(1)


# Default configuration
DEFAULT_CONFIG = {
    'general': {
        'verbose': False,
        'dry_run': False,
    },
    'modules': {
        'image_localizer': {
            'enabled': True,
            'convert_to_webp': True,
            'max_retries': 3,
            'retry_delay': 1.0,
            'retry_backoff': 2.0,
            'timeout': 30,
            # Domain filtering
            'allowlist': [],  # Empty = block all; ["*"] = allow all; or specific domains
            'allow_subdomains': False,
            'blocklist': [],  # Known-bad domains to skip silently
            'block_subdomains': False,
        },
        'tweet_downloader': {
            'enabled': True,
            'cache_max_age_days': 30,
            'defang': True,
            'lang': 'auto',
            'data_dir': 'data/x_embeds',
            'max_retries': 3,
            'retry_delay': 1.0,
            'timeout': 30,
        },
    },
    'worker': {
        'max_workers': 4,
        'rate_limit_delay': 1.0,
    },
}


def find_config_file(git_root: Path) -> Path | None:
    """
    Find .auxmark.toml config file.

    Search order:
    1. Hugo site root (git_root)
    2. Theme directory (git_root/themes/chaos)

    Args:
        git_root: Git repository root

    Returns:
        Path to config file if found, None otherwise
    """
    # Search in site root
    site_config = git_root / '.auxmark.toml'
    if site_config.exists():
        return site_config

    # Search in theme directory
    theme_config = git_root / 'themes' / 'chaos' / '.auxmark.toml'
    if theme_config.exists():
        return theme_config

    return None


def load_config(config_path: Path | None = None, git_root: Path | None = None) -> dict[str, Any]:
    """
    Load configuration from .auxmark.toml or use defaults.

    Args:
        config_path: Optional explicit path to config file
        git_root: Git repository root (used for auto-discovery)

    Returns:
        Configuration dictionary with defaults merged
    """
    # Start with defaults
    config = _deep_copy_dict(DEFAULT_CONFIG)

    # Find config file if not explicitly provided
    if config_path is None and git_root is not None:
        config_path = find_config_file(git_root)

    # Load config file if found
    if config_path is not None:
        if not config_path.exists():
            print(f"Warning: Config file not found: {config_path}", file=sys.stderr)
            return config

        try:
            with open(config_path, 'rb') as f:
                user_config = tomllib.load(f)

            # Merge user config with defaults
            config = _deep_merge_dict(config, user_config)

        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}", file=sys.stderr)
            print("Using default configuration", file=sys.stderr)

    return config


def _deep_copy_dict(d: dict) -> dict:
    """Deep copy a dictionary."""
    result = {}
    for key, value in d.items():
        if isinstance(value, dict):
            result[key] = _deep_copy_dict(value)
        else:
            result[key] = value
    return result


def _deep_merge_dict(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries.

    Args:
        base: Base dictionary (defaults)
        override: Override dictionary (user config)

    Returns:
        Merged dictionary
    """
    result = _deep_copy_dict(base)

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dicts
            result[key] = _deep_merge_dict(result[key], value)
        else:
            # Override value
            result[key] = value

    return result


def get_module_config(config: dict[str, Any], module_name: str) -> dict[str, Any]:
    """
    Get configuration for a specific module.

    Args:
        config: Full configuration dict
        module_name: Name of module (e.g., 'image_localizer')

    Returns:
        Module-specific configuration dict
    """
    return config.get('modules', {}).get(module_name, {})


def is_module_enabled(config: dict[str, Any], module_name: str) -> bool:
    """
    Check if a module is enabled in configuration.

    Args:
        config: Full configuration dict
        module_name: Name of module

    Returns:
        True if module is enabled (default: True if not specified)
    """
    module_config = get_module_config(config, module_name)
    return module_config.get('enabled', True)
