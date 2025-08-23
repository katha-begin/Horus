"""
Horus Resource Utilities
========================

Utility functions for resource management and file operations.
"""

import os
import sys


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        import sys
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def extract_sequence_from_filename(filename):
    """Extract sequence from filename."""
    import re
    
    # Pattern for ep01_sq0010_sh0020 format
    pattern = r'ep\d+_sq(\d+)_'
    match = re.search(pattern, filename.lower())
    if match:
        return f"sq{match.group(1)}"
    
    # Fallback patterns
    patterns = [
        r'seq(\d+)',
        r'sequence(\d+)',
        r'sq(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename.lower())
        if match:
            return f"seq{match.group(1)}"
    
    return "unknown"


def extract_shot_from_filename(filename):
    """Extract shot from filename."""
    import re
    
    # Pattern for ep01_sq0010_sh0020 format
    pattern = r'ep\d+_sq\d+_sh(\d+)'
    match = re.search(pattern, filename.lower())
    if match:
        return f"sh{match.group(1)}"
    
    # Fallback patterns
    patterns = [
        r'shot(\d+)',
        r'sh(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename.lower())
        if match:
            return f"shot{match.group(1)}"
    
    return "unknown"
