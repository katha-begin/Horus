#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build with Version Script
========================

Automated build script for Horus VFX Review Application that includes
automatic version bumping and build metadata generation.

Usage:
    python scripts/build_with_version.py
    python scripts/build_with_version.py --bump-build
    python scripts/build_with_version.py --release
"""

import os
import sys
import argparse
import subprocess
import shutil
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


def clean_build_directories():
    """Clean previous build artifacts."""
    directories_to_clean = ["build", "dist"]
    
    for dir_name in directories_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name} directory...")
            shutil.rmtree(dir_name)
    
    print("✅ Build directories cleaned")


def create_build_info_file():
    """Create build information file."""
    version_info = get_version_info()
    
    build_info = {
        "build_timestamp": datetime.now().isoformat(),
        "version": version_info["version"],
        "version_with_build": version_info["version_with_build"],
        "git_hash": version_info.get("git_hash"),
        "git_branch": version_info.get("git_branch"),
        "build_machine": os.environ.get("COMPUTERNAME", "unknown"),
        "python_version": sys.version,
        "platform": sys.platform
    }
    
    # Write build info to file
    import json
    with open("build_info.json", "w") as f:
        json.dump(build_info, f, indent=2)
    
    print("✅ Created build_info.json")
    return build_info


def update_spec_file_with_version():
    """Update PyInstaller spec file with current version."""
    spec_file = "horus-rv.spec"
    
    if not os.path.exists(spec_file):
        print(f"⚠️  Spec file {spec_file} not found, skipping version update")
        return
    
    version_info = get_version_info()
    version = version_info["version"]
    
    # Read spec file
    with open(spec_file, "r") as f:
        content = f.read()
    
    # Update version information in spec file
    # This is a simple replacement - in a real scenario you might want more sophisticated parsing
    if "version=" in content:
        import re
        content = re.sub(
            r'version=[\'""][^"\']*[\'"]',
            f'version="{version}"',
            content
        )
        
        with open(spec_file, "w") as f:
            f.write(content)
        
        print(f"✅ Updated {spec_file} with version {version}")


def build_executable():
    """Build executable using PyInstaller."""
    print("🔨 Building executable with PyInstaller...")
    
    # Use spec file if it exists, otherwise use direct command
    if os.path.exists("horus-rv.spec"):
        cmd = "pyinstaller horus-rv.spec"
    else:
        cmd = "pyinstaller --onefile --name horus-rv horus_rv_launcher.py"
    
    run_command(cmd)
    print("✅ Executable built successfully")


def create_distribution_package():
    """Create distribution package with version information."""
    version_info = get_version_info()
    version = version_info["version"]
    
    # Create distribution directory
    dist_dir = f"dist/horus-{version}"
    os.makedirs(dist_dir, exist_ok=True)
    
    # Copy executable
    if os.path.exists("dist/horus-rv.exe"):
        shutil.copy2("dist/horus-rv.exe", f"{dist_dir}/horus-rv.exe")
    
    # Copy configuration files
    config_files = [
        "version.json",
        "build_info.json",
        "swa_project_config.json",
        "README.md"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            shutil.copy2(config_file, f"{dist_dir}/{config_file}")
    
    # Copy sample database
    if os.path.exists("sample_db"):
        shutil.copytree("sample_db", f"{dist_dir}/sample_db")
    
    # Create archive
    archive_name = f"horus-{version}-{sys.platform}"
    shutil.make_archive(f"dist/{archive_name}", "zip", dist_dir)
    
    print(f"✅ Created distribution package: dist/{archive_name}.zip")


def main():
    """Main build function."""
    parser = argparse.ArgumentParser(description="Horus Build Tool with Version Management")
    parser.add_argument(
        "--bump-build",
        action="store_true",
        help="Automatically bump build number before building"
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Build release version (clears prerelease identifier)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build directories before building"
    )
    parser.add_argument(
        "--no-package",
        action="store_true",
        help="Skip creating distribution package"
    )
    parser.add_argument(
        "--version-only",
        action="store_true",
        help="Only update version, don't build"
    )
    
    args = parser.parse_args()
    
    print("🔧 Horus Build Tool")
    print("=" * 40)
    
    # Initialize version manager
    version_manager = VersionManager()
    
    # Show current version
    current_version = version_manager.get_version_string()
    print(f"Current version: {current_version}")
    
    # Handle version updates
    if args.release:
        print("🚀 Preparing release build...")
        version_manager.set_prerelease(None)
        new_version = version_manager.get_version_string()
        print(f"✅ Cleared prerelease identifier: {new_version}")
    
    if args.bump_build:
        print("📈 Bumping build number...")
        new_version = version_manager.bump_version("build")
        print(f"✅ Build number bumped: {new_version}")
    
    if args.version_only:
        print("✅ Version update complete")
        return
    
    # Clean build directories
    if args.clean:
        clean_build_directories()
    
    # Create build info
    build_info = create_build_info_file()
    print(f"Building version: {build_info['version_with_build']}")
    
    # Update spec file
    update_spec_file_with_version()
    
    # Build executable
    build_executable()
    
    # Create distribution package
    if not args.no_package:
        create_distribution_package()
    
    print(f"\n🎉 Build completed successfully!")
    print(f"Version: {build_info['version_with_build']}")
    print(f"Build timestamp: {build_info['build_timestamp']}")
    
    if os.path.exists("dist/horus-rv.exe"):
        file_size = os.path.getsize("dist/horus-rv.exe") / (1024 * 1024)
        print(f"Executable size: {file_size:.1f} MB")


if __name__ == "__main__":
    main()
