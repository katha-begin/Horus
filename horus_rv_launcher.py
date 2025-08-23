#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Horus-RV Launcher
================

Executable launcher for Open RV with Horus MediaBrowser integration.
This script can be compiled to horus-rv.exe using PyInstaller.

Usage:
    python horus_rv_launcher.py

Or compile to executable:
    pyinstaller --onefile --name horus-rv horus_rv_launcher.py
"""

import os
import sys
import subprocess
from pathlib import Path


def find_openrv_executable():
    """Find Open RV executable."""
    possible_paths = [
        r"C:\OpenRv\_build\stage\app\bin\rv.exe",
        r"C:\OpenRV\bin\rv.exe",
        r"C:\Program Files\OpenRV\bin\rv.exe",
        r"C:\Program Files (x86)\OpenRV\bin\rv.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None


def find_project_directory():
    """Find the Horus project directory."""
    possible_paths = [
        r"C:\Users\ADMIN\Documents\augment-projects\Horus",
        os.path.dirname(os.path.abspath(__file__)),  # Same directory as this script
        os.getcwd()  # Current working directory
    ]

    for path in possible_paths:
        integration_script = os.path.join(path, "rv_horus_integration.py")
        if os.path.exists(integration_script):
            return path

    return None


def check_horus_database():
    """Check if Horus database is available."""
    horus_db_path = r"C:\Users\ADMIN\Documents\dev\Montu\data\json_db"
    return os.path.exists(horus_db_path)


def main():
    """Main launcher function."""
    print("=" * 60)
    print("🎬 Horus-RV Launcher")
    print("   Open RV with Horus MediaBrowser Integration")
    print("=" * 60)
    print()
    
    # Find Open RV executable
    print("🔍 Searching for Open RV...")
    rv_exe = find_openrv_executable()
    
    if not rv_exe:
        print("❌ ERROR: Open RV executable not found!")
        print()
        print("Please ensure Open RV is installed in one of these locations:")
        print("  • C:\\OpenRv\\_build\\stage\\app\\bin\\rv.exe")
        print("  • C:\\OpenRV\\bin\\rv.exe")
        print("  • C:\\Program Files\\OpenRV\\bin\\rv.exe")
        print("  • C:\\Program Files (x86)\\OpenRV\\bin\\rv.exe")
        print()
        input("Press Enter to exit...")
        return 1
    
    print(f"✅ Found Open RV: {rv_exe}")
    
    # Find project directory
    print("🔍 Searching for Horus project...")
    project_dir = find_project_directory()

    if not project_dir:
        print("❌ ERROR: Horus project directory not found!")
        print()
        print("Please ensure rv_horus_integration.py exists in one of these locations:")
        print("  • C:\\Users\\ADMIN\\Documents\\augment-projects\\Horus\\")
        print("  • Same directory as this executable")
        print("  • Current working directory")
        print()
        input("Press Enter to exit...")
        return 1
    
    print(f"✅ Found project: {project_dir}")
    
    # Check integration script
    integration_script = os.path.join(project_dir, "rv_horus_integration.py")
    if not os.path.exists(integration_script):
        print(f"❌ ERROR: Integration script not found: {integration_script}")
        print()
        input("Press Enter to exit...")
        return 1

    print(f"✅ Found integration script: rv_horus_integration.py")

    # Check Horus database
    print("🔍 Checking Horus database...")
    if check_horus_database():
        print("✅ Horus database found")
    else:
        print("⚠️  WARNING: Horus database not found at C:\\Users\\ADMIN\\Documents\\dev\\Montu\\data\\json_db")
        print("   MediaBrowser will work in filesystem-only mode")

    print()
    print("🚀 Launching Open RV with Horus MediaBrowser integration...")
    print()
    
    try:
        # Change to project directory
        os.chdir(project_dir)
        
        # Build command
        python_code = "exec(open('rv_horus_integration.py').read())"
        cmd = [rv_exe, "-pyeval", python_code]
        
        # Launch Open RV
        print(f"Executing: {' '.join(cmd)}")
        print()
        
        # Run the command
        result = subprocess.run(cmd, cwd=project_dir)
        
        print()
        print("🎬 Open RV session ended")
        return result.returncode
        
    except KeyboardInterrupt:
        print()
        print("⚠️  Launch cancelled by user")
        return 1
        
    except Exception as e:
        print(f"❌ ERROR launching Open RV: {e}")
        print()
        input("Press Enter to exit...")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
