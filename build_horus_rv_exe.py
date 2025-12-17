#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build Script for Horus-RV Executable
====================================

This script builds horus-rv.exe using PyInstaller.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_pyinstaller():
    """Check if PyInstaller is available."""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Install PyInstaller."""
    try:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return True
    except subprocess.CalledProcessError:
        return False


def build_executable():
    """Build the executable using PyInstaller with all necessary files."""
    try:
        print("Building horus-rv.exe...")

        # Check which files exist and build the data files list
        data_files = []

        # Core Python files (must exist)
        core_files = [
            "rv_horus_integration.py",
            "horus_file_system.py",
            "horus_comments.py",
            "horus_playlists.py",
            "horus_version.py",
        ]

        for f in core_files:
            if os.path.exists(f):
                data_files.append(f"--add-data={f};.")
                print(f"  ✓ Including: {f}")
            else:
                print(f"  ⚠ Warning: {f} not found")

        # Config files (optional)
        config_files = [
            "version.json",
            "swa_project_config.json",
        ]

        for f in config_files:
            if os.path.exists(f):
                data_files.append(f"--add-data={f};.")
                print(f"  ✓ Including: {f}")

        # Sample database (optional)
        if os.path.isdir("sample_db"):
            data_files.append("--add-data=sample_db;sample_db")
            print("  ✓ Including: sample_db/")

        # PyInstaller command with additional data files
        cmd = [
            "python", "-m", "PyInstaller",
            "--onefile",                    # Single executable file
            "--name", "horus-rv",          # Output name
            "--console",                   # Keep console window
            "--icon=NONE",                 # No icon for now
            "--hidden-import", "PySide2.QtWidgets",    # Ensure PySide2 is included
            "--hidden-import", "PySide2.QtCore",       # Ensure PySide2 is included
            "--hidden-import", "PySide2.QtGui",        # Ensure PySide2 is included
            "--hidden-import", "paramiko",             # SSH support
            "--hidden-import", "json",
            "--hidden-import", "re",
            "--hidden-import", "datetime",
        ] + data_files + [
            "horus_rv_launcher.py"         # Source script
        ]

        print(f"\n📦 Running PyInstaller...")

        # Run PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Build successful!")

            # Check if executable was created
            exe_path = Path("dist") / "horus-rv.exe"
            if exe_path.exists():
                print(f"✅ Executable created: {exe_path.absolute()}")
                print(f"   Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
                return True
            else:
                print("❌ Executable not found in dist/ directory")
                return False
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except Exception as e:
        print(f"❌ Error building executable: {e}")
        return False


def main():
    """Main build process."""
    print("=" * 60)
    print("🔨 Building Horus-RV Executable")
    print("=" * 60)
    print()

    # Check if source file exists
    if not os.path.exists("horus_rv_launcher.py"):
        print("❌ ERROR: horus_rv_launcher.py not found!")
        return 1
    
    # Check PyInstaller
    if not check_pyinstaller():
        print("PyInstaller not found. Installing...")
        if not install_pyinstaller():
            print("❌ Failed to install PyInstaller")
            return 1
        print("✅ PyInstaller installed")
    else:
        print("✅ PyInstaller found")
    
    # Build executable
    if build_executable():
        print()
        print("🎉 SUCCESS: horus-rv.exe built successfully!")
        print()
        print("📋 Usage:")
        print("   1. Copy horus-rv.exe to your desired location")
        print("   2. Double-click horus-rv.exe to launch")
        print("   3. Or run from command line: horus-rv.exe")
        print()
        print("📁 Files created:")
        print("   • dist/horus-rv.exe - The executable")
        print("   • build/ - Build files (can be deleted)")
        print("   • horus-rv.spec - PyInstaller spec (can be deleted)")
        return 0
    else:
        print()
        print("❌ Build failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
