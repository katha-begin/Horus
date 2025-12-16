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


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def find_openrv_executable():
    """Find Open RV executable."""
    possible_paths = [
        r"D:\Program Files\stage\app\bin\rv.exe",  # Test path - PRIORITY
        r"C:\OpenRv\_build\stage\app\bin\rv.exe",
        r"C:\OpenRV\bin\rv.exe",
        r"C:\Program Files\OpenRV\bin\rv.exe",
        r"C:\Program Files (x86)\OpenRV\bin\rv.exe",
        r"T:\software\OpenRV\_build\stage\app\bin\rv.exe"
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
        print("  • D:\\Program Files\\stage\\app\\bin\\rv.exe (Test path)")
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
        
        # Build command with integration code using temporary file approach
        # Try to read from bundled resources first (for executable)
        try:
            integration_script_path = get_resource_path("rv_horus_integration.py")
            if os.path.exists(integration_script_path):
                with open(integration_script_path, 'r', encoding='utf-8') as f:
                    integration_code = f.read()
                print(f"✅ Loaded integration script from bundled resources")
            else:
                # Fallback to local file (for development)
                local_script_path = os.path.join(project_dir, "rv_horus_integration.py")
                if os.path.exists(local_script_path):
                    with open(local_script_path, 'r', encoding='utf-8') as f:
                        integration_code = f.read()
                    print(f"✅ Loaded integration script from local file")
                else:
                    raise FileNotFoundError("Integration script not found")

            # Modify the integration code to use bundled resources
            integration_code = update_integration_paths(integration_code)

            # Add project directory to sys.path at the beginning of the script
            # This ensures horus_file_system can be imported
            sys_path_inject = f'''
import sys
import os
# Add project directory to path for imports
project_dir = r"{project_dir}"
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)
os.chdir(project_dir)
print(f"📁 Working directory: {{os.getcwd()}}")
print(f"📁 Python path includes: {{project_dir}}")

'''
            integration_code = sys_path_inject + integration_code

            # Create temporary file to avoid command line length limits
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(integration_code)
                temp_script_path = temp_file.name

            print(f"✅ Created temporary script: {temp_script_path}")
            print(f"   Script size: {len(integration_code)} characters")

            # Verify the script has all necessary functions
            required_functions = [
                'create_search_panel', 'create_media_grid_panel', 'create_comments_panel',
                'create_timeline_panel', 'create_timeline_playlist_panel',
                'load_timeline_playlist_data', 'populate_playlist_tree', 'create_new_playlist'
            ]
            missing_functions = []
            for func in required_functions:
                if f"def {func}(" not in integration_code:
                    missing_functions.append(func)

            if missing_functions:
                print(f"⚠️  WARNING: Missing functions in integration script:")
                for func in missing_functions:
                    print(f"   - {func}")
                print("   This may cause UI panels to not load properly")
            else:
                print(f"✅ All required functions found in integration script")

            # Check for Timeline Playlist feature flag
            if "ENABLE_TIMELINE_PLAYLIST = True" in integration_code:
                print(f"✅ Timeline Playlist feature is enabled")
            else:
                print(f"⚠️  Timeline Playlist feature flag not found or disabled")

        except Exception as e:
            print(f"❌ ERROR: Could not load integration script: {e}")
            print("   Please ensure rv_horus_integration.py is available")
            input("Press Enter to exit...")
            return 1

        # Build command with flags and integration script
        cmd = [
            rv_exe,
            "-flags", "ModeManagerPreload=horus_mode",
            "-pyeval", f"exec(open(r'{temp_script_path}', encoding='utf-8').read())"
        ]
        
        # Launch Open RV
        print(f"Executing: {' '.join(cmd)}")
        print()
        
        # Run the command
        try:
            result = subprocess.run(cmd, cwd=project_dir)
            return_code = result.returncode
        finally:
            # Clean up temporary file
            try:
                if 'temp_script_path' in locals():
                    os.unlink(temp_script_path)
                    print(f"✅ Cleaned up temporary script")
            except Exception as cleanup_error:
                print(f"Warning: Could not clean up temporary file: {cleanup_error}")

        print()
        print("🎬 Open RV session ended")
        return return_code
        
    except KeyboardInterrupt:
        print()
        print("⚠️  Launch cancelled by user")
        return 1
        
    except Exception as e:
        print(f"❌ ERROR launching Open RV: {e}")
        print()
        input("Press Enter to exit...")
        return 1


def update_integration_paths(integration_code):
    """Update file paths in integration code to use bundled resources."""
    # Replace relative paths with resource paths for bundled files
    updated_code = integration_code

    # Update sample_db paths to use bundled resources
    sample_db_path = get_resource_path("sample_db").replace("\\", "/")
    updated_code = updated_code.replace(
        'os.path.join("sample_db"',
        f'os.path.join(r"{sample_db_path}"'
    )

    # Update src/packages paths to use bundled resources
    src_path = get_resource_path("src").replace("\\", "/")
    updated_code = updated_code.replace(
        'os.path.join(project_root, \'src\', \'packages\'',
        f'os.path.join(r"{src_path}", "packages"'
    )

    # Fix any remaining path issues with raw strings
    updated_code = updated_code.replace(
        'media_browser_path = os.path.join(',
        'media_browser_path = os.path.join('
    )

    # Add resource path function to the integration code
    resource_function = '''
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        import sys
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

'''

    # Insert the resource function at the beginning after imports
    import_end = updated_code.find('\n\n# Global references')
    if import_end != -1:
        updated_code = updated_code[:import_end] + '\n' + resource_function + updated_code[import_end:]

    # Fix the specific media_browser_path line that's causing syntax error
    import re
    updated_code = re.sub(
        r'media_browser_path = os\.path\.join\("([^"]+)"',
        lambda m: f'media_browser_path = os.path.join(r"{m.group(1).replace(chr(92), "/")}"',
        updated_code
    )

    return updated_code


def get_embedded_integration_code():
    """Get embedded integration code for executable distribution."""
    # This will be populated with the actual rv_horus_integration.py content
    # when building the executable
    return '''
# Embedded Horus-RV Integration Code
print("Loading embedded Horus-RV integration...")
print("ERROR: Integration code not properly embedded!")
print("Please ensure the build process includes rv_horus_integration.py")
'''


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
