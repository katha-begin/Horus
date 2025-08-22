#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Git Branch Manager for Horus
============================

Automated Git branch management following the Horus branching strategy.
Provides commands for creating, managing, and merging branches according
to the defined workflow.

Usage:
    python scripts/git_branch_manager.py create-feature HORUS-123 "media browser enhancement"
    python scripts/git_branch_manager.py create-release 1.2.0
    python scripts/git_branch_manager.py create-hotfix 1.2.1 "critical crash fix"
"""

import os
import sys
import argparse
import subprocess
import re
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import horus_version
sys.path.insert(0, str(Path(__file__).parent.parent))

from horus_version import VersionManager, get_version_info


def run_command(cmd, check=True, capture_output=False, cwd=None):
    """Run shell command with error handling."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=check, 
            capture_output=capture_output,
            text=True,
            cwd=cwd
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e}")
        sys.exit(1)


def get_current_branch():
    """Get current git branch name."""
    result = run_command("git rev-parse --abbrev-ref HEAD", capture_output=True)
    return result.stdout.strip()


def check_branch_exists(branch_name):
    """Check if branch exists locally or remotely."""
    # Check local branches
    result = run_command(f"git branch --list {branch_name}", capture_output=True, check=False)
    if result.stdout.strip():
        return True
    
    # Check remote branches
    result = run_command(f"git branch -r --list origin/{branch_name}", capture_output=True, check=False)
    if result.stdout.strip():
        return True
    
    return False


def validate_ticket_id(ticket_id):
    """Validate ticket ID format (HORUS-XXX)."""
    pattern = r'^HORUS-\d+$'
    if not re.match(pattern, ticket_id):
        print(f"❌ Invalid ticket ID format: {ticket_id}")
        print("Expected format: HORUS-123")
        return False
    return True


def sanitize_branch_name(name):
    """Sanitize branch name to follow Git naming conventions."""
    # Replace spaces and special characters with hyphens
    name = re.sub(r'[^a-zA-Z0-9\-_]', '-', name)
    # Remove multiple consecutive hyphens
    name = re.sub(r'-+', '-', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    # Convert to lowercase
    return name.lower()


def create_feature_branch(ticket_id, description):
    """Create a new feature branch."""
    print(f"🌟 Creating feature branch for {ticket_id}")
    
    # Validate ticket ID
    if not validate_ticket_id(ticket_id):
        return False
    
    # Sanitize description
    clean_description = sanitize_branch_name(description)
    branch_name = f"feature/{ticket_id.lower()}-{clean_description}"
    
    # Check if branch already exists
    if check_branch_exists(branch_name):
        print(f"❌ Branch {branch_name} already exists!")
        return False
    
    # Ensure we're on develop and up to date
    print("📥 Switching to develop branch and pulling latest changes...")
    run_command("git checkout develop")
    run_command("git pull origin develop")
    
    # Create and checkout new branch
    print(f"🔀 Creating branch: {branch_name}")
    run_command(f"git checkout -b {branch_name}")
    
    # Push branch to remote
    run_command(f"git push -u origin {branch_name}")
    
    print(f"✅ Feature branch created: {branch_name}")
    print(f"🎯 Ready to work on {ticket_id}: {description}")
    
    return True


def create_release_branch(version):
    """Create a new release branch."""
    print(f"🚀 Creating release branch for version {version}")
    
    # Validate version format
    version_pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(version_pattern, version):
        print(f"❌ Invalid version format: {version}")
        print("Expected format: 1.2.3")
        return False
    
    branch_name = f"release/v{version}"
    
    # Check if branch already exists
    if check_branch_exists(branch_name):
        print(f"❌ Branch {branch_name} already exists!")
        return False
    
    # Ensure we're on develop and up to date
    print("📥 Switching to develop branch and pulling latest changes...")
    run_command("git checkout develop")
    run_command("git pull origin develop")
    
    # Create and checkout new branch
    print(f"🔀 Creating branch: {branch_name}")
    run_command(f"git checkout -b {branch_name}")
    
    # Update version in configuration
    print(f"📝 Updating version to {version}...")
    version_manager = VersionManager()
    major, minor, patch = map(int, version.split('.'))
    version_manager.config["major"] = major
    version_manager.config["minor"] = minor
    version_manager.config["patch"] = patch
    version_manager.config["prerelease"] = None  # Clear prerelease for release
    version_manager._save_config(version_manager.config)
    
    # Commit version update
    run_command("git add version.json")
    run_command(f'git commit -m "Prepare release {version}"')
    
    # Push branch to remote
    run_command(f"git push -u origin {branch_name}")
    
    print(f"✅ Release branch created: {branch_name}")
    print(f"🎯 Ready to prepare release {version}")
    
    return True


def create_hotfix_branch(version, description):
    """Create a new hotfix branch."""
    print(f"🔥 Creating hotfix branch for version {version}")
    
    # Validate version format
    version_pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(version_pattern, version):
        print(f"❌ Invalid version format: {version}")
        print("Expected format: 1.2.3")
        return False
    
    # Sanitize description
    clean_description = sanitize_branch_name(description)
    branch_name = f"hotfix/v{version}-{clean_description}"
    
    # Check if branch already exists
    if check_branch_exists(branch_name):
        print(f"❌ Branch {branch_name} already exists!")
        return False
    
    # Ensure we're on main and up to date
    print("📥 Switching to main branch and pulling latest changes...")
    run_command("git checkout main")
    run_command("git pull origin main")
    
    # Create and checkout new branch
    print(f"🔀 Creating branch: {branch_name}")
    run_command(f"git checkout -b {branch_name}")
    
    # Update version in configuration
    print(f"📝 Updating version to {version}...")
    version_manager = VersionManager()
    major, minor, patch = map(int, version.split('.'))
    version_manager.config["major"] = major
    version_manager.config["minor"] = minor
    version_manager.config["patch"] = patch
    version_manager.config["prerelease"] = None  # Clear prerelease for hotfix
    version_manager._save_config(version_manager.config)
    
    # Commit version update
    run_command("git add version.json")
    run_command(f'git commit -m "Prepare hotfix {version}: {description}"')
    
    # Push branch to remote
    run_command(f"git push -u origin {branch_name}")
    
    print(f"✅ Hotfix branch created: {branch_name}")
    print(f"🎯 Ready to implement hotfix {version}: {description}")
    
    return True


def setup_git_branches():
    """Set up the initial Git branch structure."""
    print("🔧 Setting up Git branch structure...")
    
    current_branch = get_current_branch()
    print(f"Current branch: {current_branch}")
    
    # Create develop branch if it doesn't exist
    if not check_branch_exists("develop"):
        print("🌱 Creating develop branch...")
        run_command("git checkout -b develop")
        run_command("git push -u origin develop")
        print("✅ Develop branch created")
    else:
        print("✅ Develop branch already exists")
    
    # Create staging branch if it doesn't exist
    if not check_branch_exists("staging"):
        print("🎭 Creating staging branch...")
        run_command("git checkout develop")
        run_command("git checkout -b staging")
        run_command("git push -u origin staging")
        print("✅ Staging branch created")
    else:
        print("✅ Staging branch already exists")
    
    # Return to original branch
    if current_branch != get_current_branch():
        run_command(f"git checkout {current_branch}")
    
    print("🎉 Git branch structure setup complete!")


def main():
    """Main branch manager function."""
    parser = argparse.ArgumentParser(description="Horus Git Branch Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up initial branch structure")
    
    # Create feature branch
    feature_parser = subparsers.add_parser("create-feature", help="Create feature branch")
    feature_parser.add_argument("ticket_id", help="Ticket ID (e.g., HORUS-123)")
    feature_parser.add_argument("description", help="Feature description")
    
    # Create release branch
    release_parser = subparsers.add_parser("create-release", help="Create release branch")
    release_parser.add_argument("version", help="Release version (e.g., 1.2.0)")
    
    # Create hotfix branch
    hotfix_parser = subparsers.add_parser("create-hotfix", help="Create hotfix branch")
    hotfix_parser.add_argument("version", help="Hotfix version (e.g., 1.2.1)")
    hotfix_parser.add_argument("description", help="Hotfix description")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🔧 Horus Git Branch Manager")
    print("=" * 40)
    
    if args.command == "setup":
        setup_git_branches()
    elif args.command == "create-feature":
        create_feature_branch(args.ticket_id, args.description)
    elif args.command == "create-release":
        create_release_branch(args.version)
    elif args.command == "create-hotfix":
        create_hotfix_branch(args.version, args.description)
    else:
        print(f"❌ Unknown command: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main()
