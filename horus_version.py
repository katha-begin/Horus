#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Horus Version Management
=======================

Centralized version management for the Horus VFX Review Application.
Implements semantic versioning (MAJOR.MINOR.PATCH) with build metadata.

Version Format: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
Examples:
    - 1.0.0 (stable release)
    - 1.0.0-alpha.1 (pre-release)
    - 1.0.0+20240822.abc123 (with build metadata)
    - 1.0.0-beta.2+20240822.def456 (pre-release with build metadata)
"""

import os
import json
import subprocess
import datetime
from typing import Dict, Optional, Tuple
from pathlib import Path

# Version Configuration
VERSION_CONFIG_FILE = "version.json"

# Default version configuration
DEFAULT_VERSION_CONFIG = {
    "major": 0,
    "minor": 1,
    "patch": 0,
    "prerelease": "dev",
    "build_number": 0,
    "version_scheme": "semantic"
}


class VersionManager:
    """Manages application versioning for Horus."""
    
    def __init__(self, config_file: str = VERSION_CONFIG_FILE):
        """Initialize version manager with configuration file."""
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load version configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Ensure all required keys exist
                for key, default_value in DEFAULT_VERSION_CONFIG.items():
                    if key not in config:
                        config[key] = default_value
                return config
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load version config: {e}")
                return DEFAULT_VERSION_CONFIG.copy()
        else:
            # Create default config file
            self._save_config(DEFAULT_VERSION_CONFIG)
            return DEFAULT_VERSION_CONFIG.copy()
    
    def _save_config(self, config: Dict) -> None:
        """Save version configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save version config: {e}")
    
    def get_version_string(self, include_build: bool = True) -> str:
        """Get formatted version string."""
        version = f"{self.config['major']}.{self.config['minor']}.{self.config['patch']}"
        
        if self.config.get('prerelease'):
            version += f"-{self.config['prerelease']}"
            if self.config.get('build_number', 0) > 0:
                version += f".{self.config['build_number']}"
        
        if include_build:
            build_metadata = self._get_build_metadata()
            if build_metadata:
                version += f"+{build_metadata}"
        
        return version
    
    def _get_build_metadata(self) -> str:
        """Generate build metadata string."""
        metadata_parts = []
        
        # Add build date
        build_date = datetime.datetime.now().strftime("%Y%m%d")
        metadata_parts.append(build_date)
        
        # Add git hash if available
        git_hash = self._get_git_hash()
        if git_hash:
            metadata_parts.append(git_hash[:7])  # Short hash
        
        return ".".join(metadata_parts) if metadata_parts else ""
    
    def _get_git_hash(self) -> Optional[str]:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def _get_git_branch(self) -> Optional[str]:
        """Get current git branch name."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def bump_version(self, bump_type: str = "patch") -> str:
        """Bump version number and save configuration."""
        if bump_type == "major":
            self.config["major"] += 1
            self.config["minor"] = 0
            self.config["patch"] = 0
        elif bump_type == "minor":
            self.config["minor"] += 1
            self.config["patch"] = 0
        elif bump_type == "patch":
            self.config["patch"] += 1
        elif bump_type == "build":
            self.config["build_number"] += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")
        
        self._save_config(self.config)
        return self.get_version_string()
    
    def set_prerelease(self, prerelease: Optional[str]) -> str:
        """Set prerelease identifier."""
        self.config["prerelease"] = prerelease
        self._save_config(self.config)
        return self.get_version_string()
    
    def get_version_info(self) -> Dict:
        """Get comprehensive version information."""
        return {
            "version": self.get_version_string(include_build=False),
            "version_with_build": self.get_version_string(include_build=True),
            "major": self.config["major"],
            "minor": self.config["minor"],
            "patch": self.config["patch"],
            "prerelease": self.config.get("prerelease"),
            "build_number": self.config.get("build_number", 0),
            "build_date": datetime.datetime.now().isoformat(),
            "git_hash": self._get_git_hash(),
            "git_branch": self._get_git_branch(),
            "build_metadata": self._get_build_metadata()
        }


# Global version manager instance
_version_manager = VersionManager()

# Convenience functions for external use
__version__ = _version_manager.get_version_string()
__build_date__ = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_version() -> str:
    """Get current version string."""
    return _version_manager.get_version_string()

def get_version_info() -> Dict:
    """Get comprehensive version information."""
    return _version_manager.get_version_info()

def bump_version(bump_type: str = "patch") -> str:
    """Bump version and return new version string."""
    return _version_manager.bump_version(bump_type)

def set_prerelease(prerelease: Optional[str]) -> str:
    """Set prerelease identifier."""
    return _version_manager.set_prerelease(prerelease)


if __name__ == "__main__":
    """Command-line interface for version management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Horus Version Management")
    parser.add_argument("--show", action="store_true", help="Show current version")
    parser.add_argument("--info", action="store_true", help="Show detailed version info")
    parser.add_argument("--bump", choices=["major", "minor", "patch", "build"], 
                       help="Bump version number")
    parser.add_argument("--prerelease", type=str, help="Set prerelease identifier")
    parser.add_argument("--clear-prerelease", action="store_true", 
                       help="Clear prerelease identifier")
    
    args = parser.parse_args()
    
    if args.show:
        print(get_version())
    elif args.info:
        info = get_version_info()
        for key, value in info.items():
            print(f"{key}: {value}")
    elif args.bump:
        new_version = bump_version(args.bump)
        print(f"Version bumped to: {new_version}")
    elif args.prerelease:
        new_version = set_prerelease(args.prerelease)
        print(f"Prerelease set to: {new_version}")
    elif args.clear_prerelease:
        new_version = set_prerelease(None)
        print(f"Prerelease cleared: {new_version}")
    else:
        print(f"Horus VFX Review Application v{get_version()}")
