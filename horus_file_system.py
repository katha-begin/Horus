"""
Horus File System Backend
Supports both local mount (V:/, W:/) and SSH access to remote server.

Usage:
    fs = HorusFileSystem()
    fs.auto_detect()  # Detect available access method

    episodes = fs.list_episodes()
    sequences = fs.list_sequences("Ep02")
    shots = fs.list_shots("Ep02", "sq0010")
    media = fs.list_media("Ep02", "sq0010", "SH0010", "comp")
"""

import os
import sys
import json
import subprocess
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime


# ============================================================================
# Configuration
# ============================================================================

# Linux paths (server)
LINUX_PROJECT_ROOT = "/mnt/igloo_swa_v"
LINUX_IMAGE_ROOT = "/mnt/igloo_swa_w"

# Windows paths (mounted drives)
WINDOWS_PROJECT_ROOT = "V:"
WINDOWS_IMAGE_ROOT = "W:"

# SSH Configuration
SSH_HOST = "10.100.128.193"
SSH_USER = "ec2-user"
# SSH key path - auto-detect common locations
def _get_ssh_key_path():
    """Find SSH key in common locations."""
    import os
    possible_paths = [
        os.path.expanduser("~/.ssh/CaveTeam.pem"),
        os.path.expandvars("$USERPROFILE/.ssh/CaveTeam.pem"),
        os.path.expandvars("%USERPROFILE%/.ssh/CaveTeam.pem"),
        "C:/Users/Admin/.ssh/CaveTeam.pem",
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return None

SSH_KEY_PATH = _get_ssh_key_path()

# Project structure
PROJECT_NAME = "SWA"
SCENE_PATH = "all/scene"
HORUS_DATA_PATH = ".horus"

# Access mode preference: "auto", "local", "ssh"
# Set to "ssh" to force SSH mode even if local mount exists
PREFERRED_ACCESS_MODE = "ssh"  # Force SSH for development


# ============================================================================
# Abstract Base Class
# ============================================================================

class FileSystemProvider(ABC):
    """Abstract base class for file system access."""

    @abstractmethod
    def list_directory(self, path: str) -> List[str]:
        """List contents of a directory."""
        pass

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """Check if file exists."""
        pass

    @abstractmethod
    def read_file(self, path: str) -> str:
        """Read file contents."""
        pass

    @abstractmethod
    def write_file(self, path: str, content: str) -> bool:
        """Write content to file."""
        pass

    @abstractmethod
    def get_file_info(self, path: str) -> Dict:
        """Get file metadata (size, modified time)."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is available."""
        pass


# ============================================================================
# Local File System Provider
# ============================================================================

class LocalFileSystemProvider(FileSystemProvider):
    """Access files via local mount (V:/, W:/ on Windows)."""

    def __init__(self, project_root: str, image_root: str):
        self.project_root = project_root
        self.image_root = image_root

    def list_directory(self, path: str) -> List[str]:
        """List contents of a directory."""
        try:
            if os.path.isdir(path):
                return sorted(os.listdir(path))
            return []
        except (OSError, PermissionError) as e:
            print(f"Error listing directory {path}: {e}")
            return []

    def file_exists(self, path: str) -> bool:
        """Check if file exists."""
        return os.path.exists(path)

    def read_file(self, path: str) -> str:
        """Read file contents."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            return ""

    def write_file(self, path: str, content: str) -> bool:
        """Write content to file."""
        print(f"🔧 LocalProvider.write_file called:")
        print(f"   path: {path}")
        print(f"   content length: {len(content)} bytes")

        try:
            # Create directory if needed
            dir_path = os.path.dirname(path)
            print(f"   Creating directory: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)

            print(f"   Writing file...")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"   ✅ File written successfully")
            return True
        except Exception as e:
            print(f"   ❌ Error writing file {path}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def ensure_directory(self, path: str) -> bool:
        """Ensure directory exists."""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False

    def write_binary_file(self, path: str, data: bytes) -> bool:
        """Write binary data to file."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                f.write(data)
            return True
        except Exception as e:
            print(f"Error writing binary file {path}: {e}")
            return False

    def get_file_info(self, path: str) -> Dict:
        """Get file metadata."""
        try:
            stat = os.stat(path)
            return {
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "exists": True
            }
        except Exception:
            return {"size": 0, "modified": None, "exists": False}

    def is_available(self) -> bool:
        """Check if local mount is available."""
        return os.path.isdir(self.project_root)


# ============================================================================
# SSH File System Provider
# ============================================================================

class SSHFileSystemProvider(FileSystemProvider):
    """Access files via SSH to remote server."""

    def __init__(self, host: str, user: str, key_path: Optional[str] = None):
        self.host = host
        self.user = user
        self.key_path = key_path
        self._cache = {}  # Simple cache for directory listings
        self._cache_timeout = 30  # seconds

    def _build_ssh_command(self, remote_cmd: str) -> List[str]:
        """Build SSH command with proper arguments."""
        cmd = ["ssh"]
        if self.key_path:
            cmd.extend(["-i", self.key_path])
        cmd.extend([
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=5",
            f"{self.user}@{self.host}",
            remote_cmd
        ])
        return cmd

    def _run_ssh_command(self, remote_cmd: str, timeout: int = 10) -> Tuple[bool, str]:
        """Run SSH command and return (success, output)."""
        try:
            cmd = self._build_ssh_command(remote_cmd)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            return False, result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "SSH command timed out"
        except Exception as e:
            return False, str(e)

    def list_directory(self, path: str) -> List[str]:
        """List contents of a directory via SSH."""
        cache_key = f"ls:{path}"
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if (datetime.now() - cached_time).seconds < self._cache_timeout:
                return cached_data

        success, output = self._run_ssh_command(f"ls -1 '{path}' 2>/dev/null")
        if success and output:
            items = sorted(output.split('\n'))
            self._cache[cache_key] = (datetime.now(), items)
            return items
        return []

    def file_exists(self, path: str) -> bool:
        """Check if file exists via SSH."""
        success, output = self._run_ssh_command(f"test -e '{path}' && echo 'yes'")
        return success and output == 'yes'

    def read_file(self, path: str) -> str:
        """Read file contents via SSH."""
        success, output = self._run_ssh_command(f"cat '{path}'", timeout=30)
        return output if success else ""

    def write_file(self, path: str, content: str) -> bool:
        """Write content to file via SSH with sudo."""
        print(f"🔧 SSHProvider.write_file called:")
        print(f"   path: {path}")
        print(f"   content length: {len(content)} bytes")

        escaped = content.replace("'", "'\\''")

        # Use sudo for mkdir and write operations
        cmd = f"sudo mkdir -p $(dirname '{path}') && echo '{escaped}' | sudo tee '{path}' > /dev/null"
        print(f"   Running SSH command with sudo...")

        success, output = self._run_ssh_command(cmd)
        print(f"   SSH command result: success={success}")
        if output:
            print(f"   SSH output: {output}")

        return success

    def ensure_directory(self, path: str) -> bool:
        """Ensure directory exists via SSH."""
        cmd = f"mkdir -p '{path}'"
        success, _ = self._run_ssh_command(cmd)
        return success

    def write_binary_file(self, path: str, data: bytes) -> bool:
        """Write binary data to file via SSH using base64."""
        import base64
        try:
            b64_data = base64.b64encode(data).decode('ascii')
            cmd = f"mkdir -p $(dirname '{path}') && echo '{b64_data}' | base64 -d > '{path}'"
            success, _ = self._run_ssh_command(cmd, timeout=60)
            return success
        except Exception as e:
            print(f"Error writing binary file via SSH {path}: {e}")
            return False

    def get_file_info(self, path: str) -> Dict:
        """Get file metadata via SSH."""
        cmd = f"stat -c '%s %Y' '{path}' 2>/dev/null"
        success, output = self._run_ssh_command(cmd)
        if success and output:
            try:
                parts = output.split()
                size = int(parts[0])
                mtime = datetime.fromtimestamp(int(parts[1]))
                return {"size": size, "modified": mtime.isoformat(), "exists": True}
            except:
                pass
        return {"size": 0, "modified": None, "exists": False}

    def is_available(self) -> bool:
        """Check if SSH connection is available."""
        success, _ = self._run_ssh_command("echo 'ok'", timeout=5)
        return success

    def clear_cache(self):
        """Clear the directory listing cache."""
        self._cache.clear()



# ============================================================================
# Main Horus File System Class
# ============================================================================

class HorusFileSystem:
    """
    High-level file system API for Horus.
    Auto-detects whether to use local mount or SSH access.
    """

    def __init__(self):
        self.provider: Optional[FileSystemProvider] = None
        self.access_mode: str = "none"  # "local", "ssh", or "none"
        self.project_root: str = ""
        self.image_root: str = ""
        self.scene_base: str = ""
        self.horus_data: str = ""
        self.status_cache: Dict[str, Dict] = {}  # {episode_sequence: status_data}

    def auto_detect(self) -> bool:
        """Auto-detect available access method based on PREFERRED_ACCESS_MODE."""
        print(f"🔍 Detecting file system access (preferred: {PREFERRED_ACCESS_MODE})...")

        # If SSH is preferred, try SSH first
        if PREFERRED_ACCESS_MODE == "ssh":
            if self._try_ssh():
                return True
            # Fallback to local if SSH fails
            if self._try_local():
                return True
        # If local is preferred or auto mode
        else:
            if self._try_local():
                return True
            # Fallback to SSH if local not available
            if self._try_ssh():
                return True

        print("❌ No file system access available")
        return False

    def _try_local(self) -> bool:
        """Try to use local mount."""
        # Try Windows mount
        if sys.platform == 'win32':
            win_project = os.path.join(WINDOWS_PROJECT_ROOT, PROJECT_NAME)
            if os.path.isdir(win_project):
                self.provider = LocalFileSystemProvider(
                    WINDOWS_PROJECT_ROOT, WINDOWS_IMAGE_ROOT
                )
                self.access_mode = "local"
                self.project_root = WINDOWS_PROJECT_ROOT
                self.image_root = WINDOWS_IMAGE_ROOT
                self._setup_paths()
                print(f"✅ Using local mount: {WINDOWS_PROJECT_ROOT}")
                return True

        # Try Linux mount
        linux_project = os.path.join(LINUX_PROJECT_ROOT, PROJECT_NAME)
        if os.path.isdir(linux_project):
            self.provider = LocalFileSystemProvider(
                LINUX_PROJECT_ROOT, LINUX_IMAGE_ROOT
            )
            self.access_mode = "local"
            self.project_root = LINUX_PROJECT_ROOT
            self.image_root = LINUX_IMAGE_ROOT
            self._setup_paths()
            print(f"✅ Using local mount: {LINUX_PROJECT_ROOT}")
            return True

        return False

    def _try_ssh(self) -> bool:
        """Try to use SSH connection."""
        print("📡 Trying SSH connection...")
        ssh_provider = SSHFileSystemProvider(SSH_HOST, SSH_USER, SSH_KEY_PATH)
        if ssh_provider.is_available():
            self.provider = ssh_provider
            self.access_mode = "ssh"
            self.project_root = LINUX_PROJECT_ROOT
            self.image_root = LINUX_IMAGE_ROOT
            self._setup_paths()
            print(f"✅ Using SSH: {SSH_USER}@{SSH_HOST}")
            return True
        print("❌ SSH connection failed")
        return False

    def _setup_paths(self):
        """Setup derived paths."""
        self.scene_base = f"{self.project_root}/{PROJECT_NAME}/{SCENE_PATH}"
        # Note: horus_data is NOT used for comments anymore - comments are per-shot
        # This is only kept for potential future global data needs

    def convert_path_for_rv(self, path: str) -> str:
        """Convert path for RV playback (always use local path if mounted)."""
        if not path:
            return path
        if self.access_mode == "local":
            return path
        # For SSH mode, convert Linux path to Windows mount if available
        if sys.platform == 'win32':
            path = path.replace(LINUX_PROJECT_ROOT, WINDOWS_PROJECT_ROOT)
            path = path.replace(LINUX_IMAGE_ROOT, WINDOWS_IMAGE_ROOT)
            path = path.replace("/", "\\")
        return path

    def get_playback_path(self, media_item: Dict, prefer_image_seq: bool = True) -> str:
        """Get the appropriate file path for playback based on preference.

        Args:
            media_item: Media item dict containing mov_path and image_seq_path
            prefer_image_seq: If True, prefer image sequence; if False, prefer MOV

        Returns:
            The file path to use for playback (already converted for RV)
        """
        if prefer_image_seq:
            # Prefer image sequence, fallback to MOV
            path = media_item.get('image_seq_path') or media_item.get('mov_path')
        else:
            # Prefer MOV, fallback to image sequence
            path = media_item.get('mov_path') or media_item.get('image_seq_path')

        # Also check legacy file_path field
        if not path:
            path = media_item.get('file_path', '')

        return self.convert_path_for_rv(path) if path else ''

    # Supported image sequence formats
    IMAGE_EXTENSIONS = {'.exr', '.png', '.jpg', '.jpeg', '.tiff', '.tif', '.dpx', '.cin', '.sgi'}

    def resolve_image_sequence_pattern(self, seq_path: str) -> str:
        """Resolve image sequence pattern for RV.

        Converts: .../v003/* or .../v003/*.exr
        To: .../v003/filename.0001.exr (first frame path)

        RV can auto-detect sequences from a single frame path.
        Supports: exr, png, jpg, jpeg, tiff, tif, dpx, cin, sgi
        """
        if not seq_path or '*' not in seq_path:
            return seq_path

        # Get the folder path
        folder_path = seq_path.rsplit('/', 1)[0] if '/' in seq_path else seq_path.rsplit('\\', 1)[0]

        if self.access_mode == "ssh":
            # Find first image file in the folder
            # Filter for image extensions
            ext_pattern = '|'.join(ext.lstrip('.') for ext in self.IMAGE_EXTENSIONS)
            cmd = f"ls -1 '{folder_path}' 2>/dev/null | grep -iE '\\.({ext_pattern})$' | sort | head -1"
            success, output = self.provider._run_ssh_command(cmd, timeout=10)
            if success and output:
                first_file = output.strip()
                if first_file:
                    return f"{folder_path}/{first_file}"
        else:
            # Local: list directory and filter for image files
            import glob
            folder_path_os = folder_path.replace('/', os.sep)

            # Find all files and filter by extension
            all_files = []
            for ext in self.IMAGE_EXTENSIONS:
                pattern = os.path.join(folder_path_os, f'*{ext}')
                all_files.extend(glob.glob(pattern))
                # Also check uppercase extension
                pattern_upper = os.path.join(folder_path_os, f'*{ext.upper()}')
                all_files.extend(glob.glob(pattern_upper))

            if all_files:
                # Sort and return first file
                first_file = sorted(all_files)[0]
                return first_file.replace('\\', '/')

        return seq_path

    # ========================================================================
    # File System Wrapper Methods (for HorusCommentManager)
    # ========================================================================

    def file_exists(self, path: str) -> bool:
        """Check if file exists."""
        if not self.provider:
            return False
        return self.provider.file_exists(path)

    def read_file(self, path: str) -> str:
        """Read file contents."""
        if not self.provider:
            return ""
        return self.provider.read_file(path)

    def write_file(self, path: str, content: str) -> bool:
        """Write content to file."""
        if not self.provider:
            return False
        return self.provider.write_file(path, content)

    def ensure_directory(self, path: str) -> bool:
        """Ensure directory exists."""
        if not self.provider:
            return False
        return self.provider.ensure_directory(path)

    def write_binary_file(self, path: str, data: bytes) -> bool:
        """Write binary data to file."""
        if not self.provider:
            return False
        return self.provider.write_binary_file(path, data)

    def list_directory(self, path: str) -> List[str]:
        """List directory contents."""
        if not self.provider:
            return []
        return self.provider.list_directory(path)

    # ========================================================================
    # Directory Listing Methods
    # ========================================================================

    def list_episodes(self) -> List[Dict]:
        """List all episodes."""
        if not self.provider:
            return []

        items = self.provider.list_directory(self.scene_base)
        episodes = []
        for item in items:
            if item.startswith("Ep") or item.startswith("RD"):
                episodes.append({
                    "name": item,
                    "path": f"{self.scene_base}/{item}",
                    "type": "episode"
                })
        return episodes

    def list_sequences(self, episode: str) -> List[Dict]:
        """List sequences in an episode."""
        if not self.provider:
            return []

        path = f"{self.scene_base}/{episode}"
        items = self.provider.list_directory(path)
        sequences = []
        for item in items:
            if item.startswith("sq"):
                sequences.append({
                    "name": item,
                    "episode": episode,
                    "path": f"{path}/{item}",
                    "type": "sequence"
                })
        return sequences

    def list_shots(self, episode: str, sequence: str) -> List[Dict]:
        """List shots in a sequence."""
        if not self.provider:
            return []

        path = f"{self.scene_base}/{episode}/{sequence}"
        items = self.provider.list_directory(path)
        shots = []
        for item in items:
            if item.startswith("SH"):
                shots.append({
                    "name": item,
                    "episode": episode,
                    "sequence": sequence,
                    "path": f"{path}/{item}",
                    "type": "shot"
                })
        return shots

    def list_departments(self, episode: str, sequence: str, shot: str) -> List[str]:
        """List departments in a shot."""
        if not self.provider:
            return []

        path = f"{self.scene_base}/{episode}/{sequence}/{shot}"
        items = self.provider.list_directory(path)
        # Filter out hidden files and known non-department items
        departments = []
        for item in items:
            if not item.startswith('.') and item in ['anim', 'comp', 'lighting', 'layout', 'hero', 'fx']:
                departments.append(item)
        return departments

    def list_media_files(self, episode: str, sequence: str = None,
                         shot: str = None, department: str = None,
                         latest_only: bool = True) -> List[Dict]:
        """
        List media files with both MOV and image sequence paths.

        Returns unified records containing:
        - mov_path: Path to MOV file on V:/igloo_swa_v
        - image_seq_path: Path pattern to image sequence on W:/igloo_swa_w
        - media_type: "both", "mov_only", or "image_only"

        Uses Option C: Scan both sources and merge results.
        """
        if not self.provider:
            return []

        if not episode:
            return []

        # Build search path patterns
        ep_part = episode if episode else "*"
        seq_part = sequence if sequence else "*"
        shot_part = shot if shot else "*"
        dept_part = department if department else "*"

        # Path for MOV files (V: / igloo_swa_v)
        mov_search_path = f"{self.scene_base}/{ep_part}/{seq_part}/{shot_part}/{dept_part}/output"

        # Path for image sequences (W: / igloo_swa_w) - scan version folders
        img_scene_base = f"{self.image_root}/{PROJECT_NAME}/{SCENE_PATH}"
        img_search_path = f"{img_scene_base}/{ep_part}/{seq_part}/{shot_part}/{dept_part}/version"

        print(f"🔍 list_media_files: access_mode={self.access_mode}")
        print(f"   image_root: {self.image_root}")
        print(f"   MOV search: {mov_search_path}")
        print(f"   IMG search: {img_search_path}")

        # Use appropriate method based on access mode
        if self.access_mode == "ssh":
            return self._find_media_files_merged_ssh(
                mov_search_path, img_search_path, episode, sequence, shot, department, latest_only
            )
        else:
            return self._find_media_files_merged_local(
                mov_search_path, img_search_path, episode, sequence, shot, department, latest_only
            )

    def _find_media_files_merged_ssh(self, mov_search_path: str, img_search_path: str,
                                       episode: str, sequence: str, shot: str,
                                       department: str, latest_only: bool) -> List[Dict]:
        """Find and merge MOV files and image sequences using SSH."""
        import time
        start_time = time.time()
        print(f"🔍 _find_media_files_merged_ssh:")
        print(f"   MOV path: {mov_search_path}")
        print(f"   IMG path: {img_search_path}")

        # 1. Scan MOV files from V: drive
        mov_map = self._scan_mov_files_ssh(mov_search_path)
        print(f"   Found {len(mov_map)} MOV entries")

        # 2. Scan image sequence version folders from W: drive
        img_map = self._scan_image_seq_folders_ssh(img_search_path)
        print(f"   Found {len(img_map)} image sequence entries")

        # 3. Merge results
        merged = self._merge_media_sources(mov_map, img_map, latest_only)

        total_time = time.time() - start_time
        print(f"   Total _find_media_files_merged_ssh: {total_time:.2f}s, found {len(merged)} items")

        return merged

    def _find_media_files_merged_local(self, mov_search_path: str, img_search_path: str,
                                        episode: str, sequence: str, shot: str,
                                        department: str, latest_only: bool) -> List[Dict]:
        """Find and merge MOV files and image sequences using local file system."""
        import time
        start_time = time.time()
        print(f"🔍 _find_media_files_merged_local:")
        print(f"   MOV path: {mov_search_path}")
        print(f"   IMG path: {img_search_path}")

        # 1. Scan MOV files from V: drive
        mov_map = self._scan_mov_files_local(mov_search_path)
        print(f"   Found {len(mov_map)} MOV entries")

        # 2. Scan image sequence version folders from W: drive
        img_map = self._scan_image_seq_folders_local(img_search_path)
        print(f"   Found {len(img_map)} image sequence entries")

        # 3. Merge results
        merged = self._merge_media_sources(mov_map, img_map, latest_only)

        total_time = time.time() - start_time
        print(f"   Total _find_media_files_merged_local: {total_time:.2f}s, found {len(merged)} items")

        return merged

    def _scan_mov_files_ssh(self, search_path: str) -> Dict[str, Dict]:
        """Scan MOV files via SSH and return as dict keyed by shot_dept_version."""
        import time
        cmd = f"find {search_path} -maxdepth 1 -name '*.mov' 2>/dev/null"
        success, output = self.provider._run_ssh_command(cmd, timeout=30)

        mov_map = {}
        if not success or not output:
            return mov_map

        for file_path in output.strip().split('\n'):
            if not file_path or not file_path.endswith('.mov'):
                continue
            parsed = self._parse_mov_path(file_path)
            if parsed:
                key = f"{parsed['shot']}_{parsed['department']}_{parsed['version']}"
                mov_map[key] = parsed

        return mov_map

    def _scan_mov_files_local(self, search_path: str) -> Dict[str, Dict]:
        """Scan MOV files locally and return as dict keyed by shot_dept_version."""
        import glob
        pattern = os.path.join(search_path.replace('/', os.sep), '*.mov')
        files = glob.glob(pattern)

        mov_map = {}
        for file_path in files:
            file_path = file_path.replace('\\', '/')
            parsed = self._parse_mov_path(file_path)
            if parsed:
                key = f"{parsed['shot']}_{parsed['department']}_{parsed['version']}"
                mov_map[key] = parsed

        return mov_map

    def _scan_image_seq_folders_ssh(self, search_path: str) -> Dict[str, Dict]:
        """Scan image sequence version folders via SSH.

        Path structure: .../version/v001/, .../version/v002/
        Returns dict keyed by shot_dept_version.
        """
        import time
        # Use find with wildcards to locate all version folders
        # search_path may contain wildcards like: .../Ep01/*/SH*/*/version
        # We need to find all v* folders within any matching version directories
        cmd = f"find {search_path} -maxdepth 1 -type d -name 'v*' 2>/dev/null"
        success, output = self.provider._run_ssh_command(cmd, timeout=60)

        img_map = {}
        if not success or not output:
            # Try alternative: use shell expansion with ls
            cmd_alt = f"ls -d {search_path}/v*/ 2>/dev/null"
            success, output = self.provider._run_ssh_command(cmd_alt, timeout=60)
            if not success or not output:
                return img_map

        for folder_path in output.strip().split('\n'):
            if not folder_path:
                continue
            # Remove trailing slash if present
            folder_path = folder_path.rstrip('/')
            parsed = self._parse_image_seq_folder(folder_path)
            if parsed:
                key = f"{parsed['shot']}_{parsed['department']}_{parsed['version']}"
                img_map[key] = parsed

        return img_map

    def _scan_image_seq_folders_local(self, search_path: str) -> Dict[str, Dict]:
        """Scan image sequence version folders locally.

        Path structure: .../version/v001/, .../version/v002/
        Returns dict keyed by shot_dept_version.
        """
        import glob
        # Find version folders - search_path may contain wildcards
        # Convert to OS-specific path and add v* pattern
        search_path_os = search_path.replace('/', os.sep)
        pattern = os.path.join(search_path_os, 'v*')

        print(f"   Image seq local pattern: {pattern}")
        folders = [f for f in glob.glob(pattern) if os.path.isdir(f)]
        print(f"   Found {len(folders)} version folders")

        img_map = {}
        for folder_path in folders:
            folder_path = folder_path.replace('\\', '/')
            parsed = self._parse_image_seq_folder(folder_path)
            if parsed:
                key = f"{parsed['shot']}_{parsed['department']}_{parsed['version']}"
                img_map[key] = parsed

        return img_map

    def _parse_mov_path(self, file_path: str) -> Optional[Dict]:
        """Parse MOV file path to extract metadata."""
        parts = file_path.split('/')
        try:
            # Find episode (starts with 'Ep' or 'RD')
            ep_idx = next(i for i, p in enumerate(parts) if p.startswith('Ep') or p.startswith('RD'))
            ep = parts[ep_idx]

            # Find sequence (starts with 'sq')
            seq_idx = next(i for i in range(ep_idx + 1, len(parts)) if parts[i].startswith('sq'))
            seq = parts[seq_idx]

            # Find shot (starts with 'SH')
            sh_idx = next(i for i in range(seq_idx + 1, len(parts)) if parts[i].startswith('SH'))
            sh = parts[sh_idx]

            # Department is after shot
            dept = parts[sh_idx + 1]
            file_name = parts[-1]
            version = self._extract_version(file_name)

            return {
                "episode": ep,
                "sequence": seq,
                "shot": sh,
                "department": dept,
                "version": version,
                "file_name": file_name,
                "mov_path": file_path
            }
        except (StopIteration, IndexError):
            return None

    def _parse_image_seq_folder(self, folder_path: str) -> Optional[Dict]:
        """Parse image sequence version folder path to extract metadata.

        Path: .../Ep01/sq0010/SH0010/comp/version/v003/
        """
        parts = folder_path.rstrip('/').split('/')
        try:
            # Find episode (starts with 'Ep' or 'RD')
            ep_idx = next(i for i, p in enumerate(parts) if p.startswith('Ep') or p.startswith('RD'))
            ep = parts[ep_idx]

            # Find sequence (starts with 'sq')
            seq_idx = next(i for i in range(ep_idx + 1, len(parts)) if parts[i].startswith('sq'))
            seq = parts[seq_idx]

            # Find shot (starts with 'SH')
            sh_idx = next(i for i in range(seq_idx + 1, len(parts)) if parts[i].startswith('SH'))
            sh = parts[sh_idx]

            # Department is after shot
            dept = parts[sh_idx + 1]

            # Version is the folder name (last part)
            version = parts[-1].lower()  # v001, v002, etc.

            # Construct image sequence path pattern
            # Use wildcard - actual extension will be detected when loading
            # Supported formats: exr, png, jpg, jpeg, tiff, tif, dpx
            seq_path = f"{folder_path}/*"  # Wildcard for any format

            return {
                "episode": ep,
                "sequence": seq,
                "shot": sh,
                "department": dept,
                "version": version,
                "image_seq_path": seq_path,
                "image_seq_folder": folder_path
            }
        except (StopIteration, IndexError):
            return None

    def _merge_media_sources(self, mov_map: Dict[str, Dict], img_map: Dict[str, Dict],
                              latest_only: bool) -> List[Dict]:
        """Merge MOV and image sequence data into unified records."""
        import time

        # Get all unique keys
        all_keys = set(mov_map.keys()) | set(img_map.keys())

        # Group by shot_dept to handle latest_only filtering
        version_groups = {}  # {shot_dept: [items]}
        sequence_caches = {}  # Cache for status lookups

        for key in all_keys:
            mov_data = mov_map.get(key)
            img_data = img_map.get(key)

            # Get common fields from either source
            ep = (mov_data or img_data).get('episode')
            seq = (mov_data or img_data).get('sequence')
            sh = (mov_data or img_data).get('shot')
            dept = (mov_data or img_data).get('department')
            version = (mov_data or img_data).get('version')

            # Determine media availability
            has_mov = mov_data is not None
            has_img = img_data is not None

            if has_mov and has_img:
                media_type = "both"
            elif has_mov:
                media_type = "mov_only"
            else:
                media_type = "image_only"

            # Load status from sequence cache
            seq_key = f"{ep}_{seq}"
            if seq_key not in sequence_caches:
                sequence_caches[seq_key] = self.load_sequence_status_cache(ep, seq)

            status_key = f"{sh}_{dept}_{version}"
            status_entry = sequence_caches[seq_key].get("statuses", {}).get(status_key)
            status = status_entry.get("current_status", "wip") if status_entry else "wip"

            # Build unified record
            merged_item = {
                "name": f"{ep}_{sh}",
                "file_name": mov_data.get('file_name') if mov_data else f"{sh}_{dept}_{version}",
                "episode": ep,
                "sequence": seq,
                "shot": sh,
                "department": dept,
                "version": version,
                "status": status,
                "media_type": media_type,
                "mov_path": mov_data.get('mov_path') if mov_data else None,
                "image_seq_path": img_data.get('image_seq_path') if img_data else None,
                "image_seq_folder": img_data.get('image_seq_folder') if img_data else None,
                # Keep file_path for backward compatibility (defaults to mov_path)
                "file_path": mov_data.get('mov_path') if mov_data else img_data.get('image_seq_path')
            }

            # Group by shot_dept for version filtering
            group_key = f"{ep}_{sh}_{dept}"
            if group_key not in version_groups:
                version_groups[group_key] = []
            version_groups[group_key].append(merged_item)

        # Apply latest_only filter
        results = []
        for group_key, items in version_groups.items():
            items.sort(key=lambda x: x['version'], reverse=True)
            if latest_only:
                if items:
                    results.append(items[0])
            else:
                results.extend(items)

        return results

    # ========================================================================
    # Legacy methods (kept for backward compatibility, now unused)
    # ========================================================================

    def _find_media_files_ssh(self, search_path: str, episode: str,
                               sequence: str, shot: str, department: str,
                               latest_only: bool) -> List[Dict]:
        """Find media files using SSH find command. (LEGACY - kept for reference)"""
        import time
        start_time = time.time()

        print(f"🔍 _find_media_files_ssh: search_path={search_path}")

        # Use find command with -name pattern
        cmd = f"find {search_path} -maxdepth 1 -name '*.mov' 2>/dev/null"
        cmd_start = time.time()
        success, output = self.provider._run_ssh_command(cmd, timeout=30)
        cmd_time = time.time() - cmd_start
        print(f"   SSH find command took: {cmd_time:.2f}s")

        if not success or not output:
            print(f"   No files found or command failed")
            return []

        media_files = []
        version_map = {}
        sequence_caches = {}  # Pre-load sequence caches

        parse_start = time.time()
        for file_path in output.strip().split('\n'):
            if not file_path or not file_path.endswith('.mov'):
                continue

            # Parse path: .../Ep02/sq0020/SH0100/comp/output/file.mov
            parts = file_path.split('/')
            try:
                # Find episode (starts with 'Ep' or 'RD')
                ep_idx = next(i for i, p in enumerate(parts) if p.startswith('Ep') or p.startswith('RD'))
                ep = parts[ep_idx]

                # Find sequence (starts with 'sq')
                seq_idx = next(i for i in range(ep_idx + 1, len(parts)) if parts[i].startswith('sq'))
                seq = parts[seq_idx]

                # Find shot (starts with 'SH')
                sh_idx = next(i for i in range(seq_idx + 1, len(parts)) if parts[i].startswith('SH'))
                sh = parts[sh_idx]

                # Department is after shot
                dept = parts[sh_idx + 1]
                file_name = parts[-1]
            except (StopIteration, IndexError):
                continue

            version = self._extract_version(file_name)
            key = f"{ep}_{sh}_{dept}"

            # Pre-load sequence cache once per sequence
            seq_key = f"{ep}_{seq}"
            if seq_key not in sequence_caches:
                cache_load_start = time.time()
                sequence_caches[seq_key] = self.load_sequence_status_cache(ep, seq)
                cache_load_time = time.time() - cache_load_start
                print(f"   Loaded cache for {seq_key}: {cache_load_time:.2f}s")

            # Get status from pre-loaded cache
            status_key = f"{sh}_{dept}_{version}"
            status_entry = sequence_caches[seq_key].get("statuses", {}).get(status_key)
            status = status_entry.get("current_status", "wip") if status_entry else "wip"

            # DEBUG: Log status loading
            print(f"   🔍 Status for {status_key}: entry={status_entry is not None}, status={status}")

            media_item = {
                "file_name": file_name,
                "file_path": file_path,
                "episode": ep,
                "sequence": seq,
                "shot": sh,
                "department": dept,
                "version": version,
                "name": f"{ep}_{sh}",
                "status": status
            }

            if key not in version_map:
                version_map[key] = []
            version_map[key].append(media_item)

        parse_time = time.time() - parse_start
        print(f"   Parsing files took: {parse_time:.2f}s")

        # Apply latest_only filter
        filter_start = time.time()
        for key, versions in version_map.items():
            versions.sort(key=lambda x: x['version'], reverse=True)
            if latest_only:
                if versions:
                    media_files.append(versions[0])
            else:
                media_files.extend(versions)

        filter_time = time.time() - filter_start
        print(f"   Filtering took: {filter_time:.2f}s")

        total_time = time.time() - start_time
        print(f"   Total _find_media_files_ssh: {total_time:.2f}s, found {len(media_files)} files")

        return media_files

    def _find_media_files_local(self, search_path: str, episode: str,
                                 sequence: str, shot: str, department: str,
                                 latest_only: bool) -> List[Dict]:
        """Find media files using local glob."""
        import glob
        import time

        start_time = time.time()
        print(f"🔍 _find_media_files_local: search_path={search_path}")

        # Convert to glob pattern
        pattern = os.path.join(search_path.replace('/', os.sep), '*.mov')

        glob_start = time.time()
        files = glob.glob(pattern)
        glob_time = time.time() - glob_start
        print(f"   Glob took: {glob_time:.2f}s, found {len(files)} files")

        media_files = []
        version_map = {}
        sequence_caches = {}  # Pre-load sequence caches

        parse_start = time.time()
        for file_path in files:
            file_path = file_path.replace('\\', '/')
            parts = file_path.split('/')
            try:
                # Find episode (starts with 'Ep' or 'RD')
                ep_idx = next(i for i, p in enumerate(parts) if p.startswith('Ep') or p.startswith('RD'))
                ep = parts[ep_idx]

                # Find sequence (starts with 'sq')
                seq_idx = next(i for i in range(ep_idx + 1, len(parts)) if parts[i].startswith('sq'))
                seq = parts[seq_idx]

                # Find shot (starts with 'SH')
                sh_idx = next(i for i in range(seq_idx + 1, len(parts)) if parts[i].startswith('SH'))
                sh = parts[sh_idx]

                # Department is after shot
                dept = parts[sh_idx + 1]
                file_name = parts[-1]
            except (StopIteration, IndexError):
                continue

            version = self._extract_version(file_name)
            key = f"{ep}_{sh}_{dept}"

            # Pre-load sequence cache once per sequence
            seq_key = f"{ep}_{seq}"
            if seq_key not in sequence_caches:
                cache_load_start = time.time()
                sequence_caches[seq_key] = self.load_sequence_status_cache(ep, seq)
                cache_load_time = time.time() - cache_load_start
                print(f"   Loaded cache for {seq_key}: {cache_load_time:.2f}s")

            # Get status from pre-loaded cache
            status_key = f"{sh}_{dept}_{version}"
            status_entry = sequence_caches[seq_key].get("statuses", {}).get(status_key)
            status = status_entry.get("current_status", "wip") if status_entry else "wip"

            # DEBUG: Log status loading
            print(f"   🔍 Status for {status_key}: entry={status_entry is not None}, status={status}")

            media_item = {
                "file_name": file_name,
                "file_path": file_path,
                "episode": ep,
                "sequence": seq,
                "shot": sh,
                "department": dept,
                "version": version,
                "name": f"{ep}_{sh}",
                "status": status
            }

            if key not in version_map:
                version_map[key] = []
            version_map[key].append(media_item)

        parse_time = time.time() - parse_start
        print(f"   Parsing files took: {parse_time:.2f}s")

        # Apply latest_only filter
        filter_start = time.time()
        for key, versions in version_map.items():
            versions.sort(key=lambda x: x['version'], reverse=True)
            if latest_only:
                if versions:
                    media_files.append(versions[0])
            else:
                media_files.extend(versions)

        filter_time = time.time() - filter_start
        print(f"   Filtering took: {filter_time:.2f}s")

        total_time = time.time() - start_time
        print(f"   Total _find_media_files_local: {total_time:.2f}s, found {len(media_files)} files")

        return media_files

    def _extract_version(self, filename: str) -> str:
        """Extract version from filename (e.g., 'v007' from 'Ep02_sq0010_SH0010_v007.mov')."""
        match = re.search(r'[_-](v\d+)', filename, re.IGNORECASE)
        if match:
            return match.group(1).lower()
        return "v001"


    # ========================================================================
    # Comments & Status Methods (Per-Shot Storage)
    # ========================================================================

    def get_shot_comment_file_path(self, episode: str, sequence: str, shot: str) -> str:
        """Get path to shot's comment JSON file.

        Per spec: {PROJECT_ROOT}/SWA/all/scene/{Episode}/{Sequence}/{Shot}/.horus/{Shot}_comments.json
        Example: /mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0010/.horus/SH0010_comments.json
        """
        return f"{self.scene_base}/{episode}/{sequence}/{shot}/.horus/{shot}_comments.json"

    def get_sequence_status_file_path(self, episode: str, sequence: str) -> str:
        """Get path to sequence status cache file.

        Path: {PROJECT_ROOT}/SWA/all/scene/{Episode}/.horus/status/{Sequence}_status.json
        Example: /mnt/igloo_swa_v/SWA/all/scene/Ep01/.horus/status/sq0010_status.json
        """
        return f"{self.scene_base}/{episode}/.horus/status/{sequence}_status.json"

    def load_shot_comments(self, episode: str, sequence: str, shot: str) -> Dict:
        """Load comments for a specific shot."""
        if not self.provider:
            return {}

        path = self.get_shot_comment_file_path(episode, sequence, shot)
        content = self.provider.read_file(path)
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Error parsing shot comments file: {e}")

        # Return empty structure - status is per version in 'versions' dict
        return {
            "version": "1.0",
            "shot_info": {
                "episode": episode,
                "sequence": sequence,
                "shot": shot
            },
            "versions": {},  # Status per department_version
            "comments": []
        }

    def save_shot_comments(self, episode: str, sequence: str, shot: str, data: Dict) -> bool:
        """Save comments for a specific shot."""
        print(f"💾 save_shot_comments called:")
        print(f"   episode={episode}, sequence={sequence}, shot={shot}")

        if not self.provider:
            print(f"   ❌ No provider available")
            return False

        path = self.get_shot_comment_file_path(episode, sequence, shot)
        print(f"   File path: {path}")

        content = json.dumps(data, indent=2)
        print(f"   Content size: {len(content)} bytes")

        result = self.provider.write_file(path, content)
        print(f"   Write result: {result}")
        return result

    def load_sequence_status_cache(self, episode: str, sequence: str) -> Dict:
        """Load status cache for a sequence.

        Returns structure:
        {
          "version": "1.0",
          "episode": "Ep01",
          "sequence": "sq0010",
          "last_updated": "2025-12-17T10:30:00Z",
          "statuses": {
            "SH0010_comp_v012": {
              "current_status": "approved",
              "last_changed": "2025-12-17T10:30:00Z",
              "last_changed_by": "john.doe",
              "history": [...]
            }
          }
        }
        """
        if not self.provider:
            print(f"   ⚠️ load_sequence_status_cache: No provider available")
            return {}

        cache_key = f"{episode}_{sequence}"

        # Check in-memory cache first
        if cache_key in self.status_cache:
            print(f"   ✅ load_sequence_status_cache: Using in-memory cache for {cache_key}")
            return self.status_cache[cache_key]

        # Load from file
        path = self.get_sequence_status_file_path(episode, sequence)
        print(f"   📂 load_sequence_status_cache: Loading from {path}")

        content = self.provider.read_file(path)

        if content:
            try:
                data = json.loads(content)
                self.status_cache[cache_key] = data
                print(f"   ✅ load_sequence_status_cache: Loaded {len(data.get('statuses', {}))} statuses from file")
                return data
            except json.JSONDecodeError as e:
                print(f"   ❌ Error parsing status cache file: {e}")
        else:
            print(f"   ℹ️ load_sequence_status_cache: No status file found, using empty cache")

        # Return empty structure
        empty_cache = {
            "version": "1.0",
            "episode": episode,
            "sequence": sequence,
            "last_updated": datetime.utcnow().isoformat(),
            "statuses": {}
        }
        self.status_cache[cache_key] = empty_cache
        return empty_cache

    def save_sequence_status_cache(self, episode: str, sequence: str, cache_data: Dict) -> bool:
        """Save status cache for a sequence."""
        if not self.provider:
            return False

        cache_key = f"{episode}_{sequence}"

        # Update in-memory cache
        self.status_cache[cache_key] = cache_data

        # Update last_updated timestamp
        cache_data["last_updated"] = datetime.utcnow().isoformat()

        # Write to file
        path = self.get_sequence_status_file_path(episode, sequence)
        content = json.dumps(cache_data, indent=2)
        return self.provider.write_file(path, content)

    def get_shot_status(self, episode: str, sequence: str, shot: str,
                        department: str, version: str) -> str:
        """Get status for a specific version from sequence status cache.

        Returns "wip" if no status is set (default for all new shots).
        """
        cache_data = self.load_sequence_status_cache(episode, sequence)
        status_key = f"{shot}_{department}_{version}"

        status_entry = cache_data.get("statuses", {}).get(status_key)
        if status_entry:
            return status_entry.get("current_status", "wip")

        return "wip"  # Default status for shots without explicit status

    def set_shot_status(self, episode: str, sequence: str, shot: str,
                        department: str, version: str, status: str) -> bool:
        """Set status for a specific version in sequence status cache.

        Saves to: {Episode}/.horus/status/{Sequence}_status.json
        Keeps full history of status changes with user and timestamp.
        """
        import os

        print(f"📝 set_shot_status called:")
        print(f"   episode={episode}, sequence={sequence}, shot={shot}")
        print(f"   department={department}, version={version}, status={status}")

        # Load sequence status cache
        cache_data = self.load_sequence_status_cache(episode, sequence)
        print(f"   Loaded sequence status cache")

        # Get current user from OS environment
        current_user = os.environ.get('USER') or os.environ.get('USERNAME') or 'unknown'
        current_time = datetime.utcnow().isoformat()

        # Create status key
        status_key = f"{shot}_{department}_{version}"

        # Get or create status entry
        if status_key not in cache_data["statuses"]:
            cache_data["statuses"][status_key] = {
                "current_status": status,
                "last_changed": current_time,
                "last_changed_by": current_user,
                "history": []
            }

        # Add to history
        status_entry = cache_data["statuses"][status_key]
        status_entry["history"].append({
            "status": status,
            "changed_at": current_time,
            "changed_by": current_user
        })

        # Update current status
        status_entry["current_status"] = status
        status_entry["last_changed"] = current_time
        status_entry["last_changed_by"] = current_user

        print(f"   Updated status cache: {status_key} -> {status}")
        print(f"   Changed by: {current_user} at {current_time}")

        # Save to file
        result = self.save_sequence_status_cache(episode, sequence, cache_data)
        print(f"   Save result: {result}")
        return result

    # ========================================================================
    # Playlist Methods
    # ========================================================================

    def get_playlists_file_path(self) -> str:
        """Get path to playlists JSON file.

        Per spec: {PROJECT_ROOT}/SWA/all/scene/.horus/playlists.json
        Example: /mnt/igloo_swa_v/SWA/all/scene/.horus/playlists.json
        """
        return f"{self.project_root}/{PROJECT_NAME}/all/scene/.horus/playlists.json"

    def load_playlists(self) -> List[Dict]:
        """Load all playlists."""
        if not self.provider:
            return []

        path = self.get_playlists_file_path()
        content = self.provider.read_file(path)
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Error parsing playlists file: {e}")
        return []

    def save_playlists(self, playlists: List[Dict]) -> bool:
        """Save all playlists."""
        if not self.provider:
            return False

        path = self.get_playlists_file_path()
        content = json.dumps(playlists, indent=2)
        return self.provider.write_file(path, content)


# ============================================================================
# Global Instance
# ============================================================================

# Singleton instance
_horus_fs: Optional[HorusFileSystem] = None

def get_horus_fs() -> HorusFileSystem:
    """Get or create the global HorusFileSystem instance."""
    global _horus_fs
    if _horus_fs is None:
        _horus_fs = HorusFileSystem()
        _horus_fs.auto_detect()
    return _horus_fs


# ============================================================================
# Test / Debug
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Horus File System Test")
    print("=" * 60)

    fs = get_horus_fs()

    if fs.access_mode == "none":
        print("\n❌ No file system access available")
        print("   - Local mount not found (V:/ or /mnt/igloo_swa_v/)")
        print(f"   - SSH connection failed ({SSH_USER}@{SSH_HOST})")
    else:
        print(f"\n✅ Access mode: {fs.access_mode}")
        print(f"   Project root: {fs.project_root}")
        print(f"   Scene base: {fs.scene_base}")

        print("\n📁 Episodes:")
        episodes = fs.list_episodes()
        for ep in episodes[:5]:
            print(f"   - {ep['name']}")

        if episodes:
            ep = episodes[0]['name']
            print(f"\n📁 Sequences in {ep}:")
            sequences = fs.list_sequences(ep)
            for seq in sequences[:5]:
                print(f"   - {seq['name']}")

            if sequences:
                seq = sequences[0]['name']
                print(f"\n📁 Shots in {ep}/{seq}:")
                shots = fs.list_shots(ep, seq)
                for shot in shots[:5]:
                    print(f"   - {shot['name']}")

                print(f"\n🎬 Media files in {ep} (latest only):")
                media = fs.list_media_files(ep, latest_only=True)
                for m in media[:10]:
                    print(f"   - {m['name']} {m['version']} [{m['department']}]")



