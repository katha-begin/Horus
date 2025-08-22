#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Release Manager for Horus
=========================

Automated release management system for the Horus VFX Review Application.
Handles release preparation, tagging, changelog generation, and distribution.

Usage:
    python scripts/release_manager.py prepare 1.2.0
    python scripts/release_manager.py finalize 1.2.0
    python scripts/release_manager.py hotfix 1.2.1
"""

import os
import sys
import json
import argparse
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

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


def get_git_commits_since_tag(since_tag: str) -> List[Dict]:
    """Get git commits since a specific tag."""
    try:
        # Get commits since tag
        cmd = f'git log {since_tag}..HEAD --pretty=format:"%H|%s|%an|%ad" --date=short'
        result = run_command(cmd, capture_output=True)
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) >= 4:
                    commits.append({
                        'hash': parts[0],
                        'subject': parts[1],
                        'author': parts[2],
                        'date': parts[3]
                    })
        return commits
    except:
        return []


def get_latest_tag() -> Optional[str]:
    """Get the latest git tag."""
    try:
        result = run_command("git describe --tags --abbrev=0", capture_output=True)
        return result.stdout.strip()
    except:
        return None


def parse_commit_message(message: str) -> Dict:
    """Parse commit message to extract type, scope, and description."""
    # Pattern for conventional commits: type(scope): description
    pattern = r'^(\w+)(?:\(([^)]+)\))?: (.+)$'
    match = re.match(pattern, message)
    
    if match:
        return {
            'type': match.group(1),
            'scope': match.group(2) or '',
            'description': match.group(3),
            'breaking': 'BREAKING CHANGE' in message or '!' in match.group(1)
        }
    else:
        return {
            'type': 'other',
            'scope': '',
            'description': message,
            'breaking': False
        }


def generate_changelog(version: str, commits: List[Dict]) -> str:
    """Generate changelog from commits."""
    changelog = f"# Release {version}\n\n"
    changelog += f"**Release Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    # Categorize commits
    categories = {
        'feat': {'title': '🚀 New Features', 'commits': []},
        'fix': {'title': '🐛 Bug Fixes', 'commits': []},
        'perf': {'title': '⚡ Performance Improvements', 'commits': []},
        'refactor': {'title': '♻️ Code Refactoring', 'commits': []},
        'docs': {'title': '📚 Documentation', 'commits': []},
        'test': {'title': '🧪 Testing', 'commits': []},
        'chore': {'title': '🔧 Maintenance', 'commits': []},
        'ci': {'title': '👷 CI/CD', 'commits': []},
        'style': {'title': '💄 Style Changes', 'commits': []},
        'other': {'title': '📦 Other Changes', 'commits': []}
    }
    
    breaking_changes = []
    
    for commit in commits:
        parsed = parse_commit_message(commit['subject'])
        commit_type = parsed['type']
        
        if parsed['breaking']:
            breaking_changes.append(commit)
        
        if commit_type in categories:
            categories[commit_type]['commits'].append({
                **commit,
                'parsed': parsed
            })
        else:
            categories['other']['commits'].append({
                **commit,
                'parsed': parsed
            })
    
    # Add breaking changes section if any
    if breaking_changes:
        changelog += "## ⚠️ BREAKING CHANGES\n\n"
        for commit in breaking_changes:
            parsed = parse_commit_message(commit['subject'])
            scope_text = f"**{parsed['scope']}**: " if parsed['scope'] else ""
            changelog += f"- {scope_text}{parsed['description']}\n"
        changelog += "\n"
    
    # Add categorized changes
    for category, data in categories.items():
        if data['commits']:
            changelog += f"## {data['title']}\n\n"
            for commit in data['commits']:
                parsed = commit['parsed']
                scope_text = f"**{parsed['scope']}**: " if parsed['scope'] else ""
                changelog += f"- {scope_text}{parsed['description']} ({commit['hash'][:7]})\n"
            changelog += "\n"
    
    # Add contributors
    contributors = list(set(commit['author'] for commit in commits))
    if contributors:
        changelog += "## 👥 Contributors\n\n"
        for contributor in sorted(contributors):
            changelog += f"- {contributor}\n"
        changelog += "\n"
    
    return changelog


def create_release_notes(version: str) -> str:
    """Create release notes for a version."""
    print(f"📝 Generating release notes for version {version}...")
    
    # Get latest tag
    latest_tag = get_latest_tag()
    if not latest_tag:
        print("⚠️  No previous tags found, generating notes from all commits")
        # Get all commits if no tags exist
        try:
            result = run_command('git log --pretty=format:"%H|%s|%an|%ad" --date=short', capture_output=True)
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        commits.append({
                            'hash': parts[0],
                            'subject': parts[1],
                            'author': parts[2],
                            'date': parts[3]
                        })
        except:
            commits = []
    else:
        print(f"📊 Generating notes since tag: {latest_tag}")
        commits = get_git_commits_since_tag(latest_tag)
    
    if not commits:
        print("⚠️  No commits found for release notes")
        return f"# Release {version}\n\n**Release Date:** {datetime.now().strftime('%Y-%m-%d')}\n\nNo changes since last release.\n"
    
    changelog = generate_changelog(version, commits)
    
    # Save changelog to file
    changelog_file = f"CHANGELOG-{version}.md"
    with open(changelog_file, 'w', encoding='utf-8') as f:
        f.write(changelog)
    
    print(f"✅ Release notes saved to: {changelog_file}")
    return changelog


def prepare_release(version: str):
    """Prepare a new release."""
    print(f"🚀 Preparing release {version}")
    
    # Validate version format
    version_pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(version_pattern, version):
        print(f"❌ Invalid version format: {version}")
        print("Expected format: 1.2.3")
        return False
    
    # Check if we're on develop branch
    result = run_command("git rev-parse --abbrev-ref HEAD", capture_output=True)
    current_branch = result.stdout.strip()
    
    if current_branch != "develop":
        print(f"❌ Must be on develop branch to prepare release (currently on {current_branch})")
        return False
    
    # Ensure develop is up to date
    print("📥 Pulling latest changes from develop...")
    run_command("git pull origin develop")
    
    # Create release branch
    release_branch = f"release/v{version}"
    print(f"🌿 Creating release branch: {release_branch}")
    run_command(f"git checkout -b {release_branch}")
    
    # Update version
    print(f"📝 Updating version to {version}...")
    version_manager = VersionManager()
    major, minor, patch = map(int, version.split('.'))
    version_manager.config["major"] = major
    version_manager.config["minor"] = minor
    version_manager.config["patch"] = patch
    version_manager.config["prerelease"] = None  # Clear prerelease for release
    version_manager._save_config(version_manager.config)
    
    # Generate release notes
    changelog = create_release_notes(version)
    
    # Commit changes
    run_command("git add version.json")
    run_command(f"git add CHANGELOG-{version}.md")
    run_command(f'git commit -m "Prepare release {version}"')
    
    # Push release branch
    run_command(f"git push -u origin {release_branch}")
    
    print(f"✅ Release {version} prepared successfully!")
    print(f"🎯 Next steps:")
    print(f"   1. Test the release branch thoroughly")
    print(f"   2. Run: python scripts/release_manager.py finalize {version}")
    
    return True


def finalize_release(version: str):
    """Finalize a release by merging to main and creating tags."""
    print(f"🏁 Finalizing release {version}")
    
    release_branch = f"release/v{version}"
    tag_name = f"v{version}"
    
    # Check if we're on the release branch
    result = run_command("git rev-parse --abbrev-ref HEAD", capture_output=True)
    current_branch = result.stdout.strip()
    
    if current_branch != release_branch:
        print(f"❌ Must be on release branch {release_branch} (currently on {current_branch})")
        return False
    
    # Ensure release branch is up to date
    print(f"📥 Pulling latest changes from {release_branch}...")
    run_command(f"git pull origin {release_branch}")
    
    # Merge to main
    print("🔀 Merging to main branch...")
    run_command("git checkout main")
    run_command("git pull origin main")
    run_command(f"git merge --no-ff {release_branch} -m 'Release {version}'")
    
    # Create tag
    print(f"🏷️  Creating tag {tag_name}...")
    run_command(f'git tag -a {tag_name} -m "Release version {version}"')
    
    # Push main and tags
    run_command("git push origin main")
    run_command(f"git push origin {tag_name}")
    
    # Merge back to develop
    print("🔄 Merging back to develop...")
    run_command("git checkout develop")
    run_command("git pull origin develop")
    run_command(f"git merge --no-ff {release_branch} -m 'Merge release {version} back to develop'")
    run_command("git push origin develop")
    
    # Clean up release branch
    print(f"🧹 Cleaning up release branch...")
    run_command(f"git branch -d {release_branch}")
    run_command(f"git push origin --delete {release_branch}")
    
    print(f"🎉 Release {version} finalized successfully!")
    print(f"🏷️  Tag created: {tag_name}")
    print(f"📦 Ready for distribution")
    
    return True


def create_hotfix(version: str, description: str):
    """Create and finalize a hotfix release."""
    print(f"🔥 Creating hotfix {version}: {description}")
    
    # Validate version format
    version_pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(version_pattern, version):
        print(f"❌ Invalid version format: {version}")
        print("Expected format: 1.2.3")
        return False
    
    # Start from main branch
    print("📥 Starting from main branch...")
    run_command("git checkout main")
    run_command("git pull origin main")
    
    # Create hotfix branch
    hotfix_branch = f"hotfix/v{version}-{description.replace(' ', '-').lower()}"
    print(f"🌿 Creating hotfix branch: {hotfix_branch}")
    run_command(f"git checkout -b {hotfix_branch}")
    
    # Update version
    print(f"📝 Updating version to {version}...")
    version_manager = VersionManager()
    major, minor, patch = map(int, version.split('.'))
    version_manager.config["major"] = major
    version_manager.config["minor"] = minor
    version_manager.config["patch"] = patch
    version_manager.config["prerelease"] = None
    version_manager._save_config(version_manager.config)
    
    # Commit version update
    run_command("git add version.json")
    run_command(f'git commit -m "Prepare hotfix {version}: {description}"')
    
    # Push hotfix branch
    run_command(f"git push -u origin {hotfix_branch}")
    
    print(f"✅ Hotfix {version} prepared successfully!")
    print(f"🎯 Next steps:")
    print(f"   1. Implement the hotfix")
    print(f"   2. Test thoroughly")
    print(f"   3. Run: python scripts/release_manager.py finalize-hotfix {version}")
    
    return True


def main():
    """Main release manager function."""
    parser = argparse.ArgumentParser(description="Horus Release Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Prepare release
    prepare_parser = subparsers.add_parser("prepare", help="Prepare a new release")
    prepare_parser.add_argument("version", help="Release version (e.g., 1.2.0)")
    
    # Finalize release
    finalize_parser = subparsers.add_parser("finalize", help="Finalize a release")
    finalize_parser.add_argument("version", help="Release version (e.g., 1.2.0)")
    
    # Create hotfix
    hotfix_parser = subparsers.add_parser("hotfix", help="Create a hotfix")
    hotfix_parser.add_argument("version", help="Hotfix version (e.g., 1.2.1)")
    hotfix_parser.add_argument("description", help="Hotfix description")
    
    # Generate changelog
    changelog_parser = subparsers.add_parser("changelog", help="Generate changelog")
    changelog_parser.add_argument("version", help="Version for changelog")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🚀 Horus Release Manager")
    print("=" * 40)
    
    if args.command == "prepare":
        prepare_release(args.version)
    elif args.command == "finalize":
        finalize_release(args.version)
    elif args.command == "hotfix":
        create_hotfix(args.version, args.description)
    elif args.command == "changelog":
        create_release_notes(args.version)
    else:
        print(f"❌ Unknown command: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main()
