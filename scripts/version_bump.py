#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Version Bump Script
==================

Automated version bumping script for Horus VFX Review Application.
Supports semantic versioning with automatic git tagging and commit creation.

Usage:
    python scripts/version_bump.py --bump patch
    python scripts/version_bump.py --bump minor --tag
    python scripts/version_bump.py --bump major --tag --push
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add parent directory to path to import horus_version
sys.path.insert(0, str(Path(__file__).parent.parent))

from horus_version import VersionManager, get_version_info


def run_command(cmd, check=True, capture_output=False):
    """Run shell command with error handling."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=check, 
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e}")
        sys.exit(1)


def check_git_status():
    """Check if git working directory is clean."""
    result = run_command("git status --porcelain", capture_output=True)
    if result.stdout.strip():
        print("❌ Git working directory is not clean!")
        print("Please commit or stash your changes before bumping version.")
        print("\nUncommitted changes:")
        print(result.stdout)
        return False
    return True


def create_git_tag(version, push=False):
    """Create git tag for version."""
    tag_name = f"v{version}"
    
    # Check if tag already exists
    result = run_command(f"git tag -l {tag_name}", capture_output=True, check=False)
    if result.stdout.strip():
        print(f"⚠️  Tag {tag_name} already exists!")
        return False
    
    # Create annotated tag
    commit_message = f"Release version {version}"
    run_command(f'git tag -a {tag_name} -m "{commit_message}"')
    print(f"✅ Created git tag: {tag_name}")
    
    if push:
        run_command(f"git push origin {tag_name}")
        print(f"✅ Pushed tag to remote: {tag_name}")
    
    return True


def commit_version_change(version):
    """Commit version configuration changes."""
    run_command("git add version.json")
    commit_message = f"Bump version to {version}"
    run_command(f'git commit -m "{commit_message}"')
    print(f"✅ Committed version bump: {version}")


def main():
    """Main version bump function."""
    parser = argparse.ArgumentParser(description="Horus Version Bump Tool")
    parser.add_argument(
        "--bump", 
        choices=["major", "minor", "patch", "build"],
        required=True,
        help="Type of version bump to perform"
    )
    parser.add_argument(
        "--prerelease",
        type=str,
        help="Set prerelease identifier (e.g., alpha, beta, rc)"
    )
    parser.add_argument(
        "--clear-prerelease",
        action="store_true",
        help="Clear prerelease identifier for stable release"
    )
    parser.add_argument(
        "--tag",
        action="store_true",
        help="Create git tag for the new version"
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push changes and tags to remote repository"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip git status check (use with caution)"
    )
    
    args = parser.parse_args()
    
    print("🔧 Horus Version Bump Tool")
    print("=" * 40)
    
    # Check git status unless forced
    if not args.force and not args.dry_run:
        if not check_git_status():
            sys.exit(1)
    
    # Initialize version manager
    version_manager = VersionManager()
    current_version = version_manager.get_version_string()
    
    print(f"Current version: {current_version}")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - No changes will be made")
        
        # Simulate version bump
        test_config = version_manager.config.copy()
        if args.bump == "major":
            test_config["major"] += 1
            test_config["minor"] = 0
            test_config["patch"] = 0
        elif args.bump == "minor":
            test_config["minor"] += 1
            test_config["patch"] = 0
        elif args.bump == "patch":
            test_config["patch"] += 1
        elif args.bump == "build":
            test_config["build_number"] += 1
        
        if args.prerelease:
            test_config["prerelease"] = args.prerelease
        elif args.clear_prerelease:
            test_config["prerelease"] = None
        
        # Create temporary version manager to show new version
        temp_manager = VersionManager()
        temp_manager.config = test_config
        new_version = temp_manager.get_version_string()
        
        print(f"Would bump to: {new_version}")
        
        if args.tag:
            print(f"Would create git tag: v{new_version}")
        if args.push:
            print("Would push changes to remote repository")
        
        return
    
    # Perform version bump
    print(f"\n🚀 Bumping {args.bump} version...")
    
    # Handle prerelease settings
    if args.clear_prerelease:
        version_manager.set_prerelease(None)
        print("✅ Cleared prerelease identifier")
    elif args.prerelease:
        version_manager.set_prerelease(args.prerelease)
        print(f"✅ Set prerelease to: {args.prerelease}")
    
    # Bump version
    new_version = version_manager.bump_version(args.bump)
    print(f"✅ Version bumped to: {new_version}")
    
    # Commit changes
    if not args.force:
        commit_version_change(new_version)
    
    # Create git tag
    if args.tag:
        create_git_tag(new_version, push=args.push)
    
    # Push changes
    if args.push and not args.tag:
        run_command("git push")
        print("✅ Pushed changes to remote repository")
    
    print(f"\n🎉 Version successfully updated to {new_version}")
    
    # Show version info
    print("\n📋 Version Information:")
    version_info = get_version_info()
    for key, value in version_info.items():
        if value is not None:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
