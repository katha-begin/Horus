"""
Horus Comments & Annotations Backend
Manages shot-level comments and annotation images.

Comments Storage:
    {shot_path}/.horus/{shot}_comments.json

Annotations Storage:
    {shot_path}/{department}/annotations/{version}/{filename}.{frame}.png

Usage:
    from horus_comments import get_comment_manager

    cm = get_comment_manager()
    comments = cm.load_comments("Ep02", "sq0010", "SH0010")
    cm.add_comment("Ep02", "sq0010", "SH0010", "SH0010_comp_v007.mov",
                   "john.doe", "Great lighting!", frame=45)
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


# ============================================================================
# Configuration
# ============================================================================

COMMENT_FILE_VERSION = "1.0"
HORUS_DIR = ".horus"
ANNOTATIONS_DIR = "annotations"

# Current user (placeholder - should come from environment/config)
def get_current_user():
    """Get current username from environment."""
    return os.environ.get("HORUS_USER", os.environ.get("USERNAME", "unknown.user"))


# ============================================================================
# Comment Manager Class
# ============================================================================

class HorusCommentManager:
    """Manage shot-level comments and annotations.

    Comments are stored per-shot in:
        {shot_path}/.horus/{shot}_comments.json

    Annotations are stored in:
        {shot_path}/{department}/annotations/{version}/{filename}.{frame}.png
    """

    def __init__(self, file_system=None):
        """Initialize with optional file system provider."""
        self.fs = file_system
        self._cache = {}  # Cache loaded comments

    def set_file_system(self, file_system):
        """Set the file system provider."""
        self.fs = file_system

    # ============== Path Methods ==============

    def get_shot_path(self, episode: str, sequence: str, shot: str) -> str:
        """Get base path to shot directory."""
        if self.fs:
            return f"{self.fs.scene_base}/{episode}/{sequence}/{shot}"
        return ""

    def get_comment_file_path(self, episode: str, sequence: str, shot: str) -> str:
        """Get path to shot's comment JSON file."""
        shot_path = self.get_shot_path(episode, sequence, shot)
        return f"{shot_path}/{HORUS_DIR}/{shot}_comments.json"

    def get_annotation_dir(self, episode: str, sequence: str, shot: str,
                          department: str, version: str) -> str:
        """Get path to annotation directory."""
        shot_path = self.get_shot_path(episode, sequence, shot)
        return f"{shot_path}/{department}/{ANNOTATIONS_DIR}/{version}"

    def get_annotation_file_path(self, episode: str, sequence: str, shot: str,
                                 department: str, version: str, frame: int) -> str:
        """Get path to specific annotation image."""
        ann_dir = self.get_annotation_dir(episode, sequence, shot, department, version)
        filename = f"{shot}_{department}_{version}.{frame:04d}.png"
        return f"{ann_dir}/{filename}"

    # ============== Comment CRUD Methods ==============

    def load_comments(self, episode: str, sequence: str, shot: str) -> Dict:
        """Load all comments for a shot."""
        cache_key = f"{episode}_{sequence}_{shot}"

        # Return from cache if available
        if cache_key in self._cache:
            return self._cache[cache_key]

        comment_path = self.get_comment_file_path(episode, sequence, shot)

        try:
            if self.fs and self.fs.file_exists(comment_path):
                content = self.fs.read_file(comment_path)
                data = json.loads(content)
                self._cache[cache_key] = data
                return data
        except Exception as e:
            print(f"Error loading comments: {e}")

        # Return empty structure if file doesn't exist
        return self._create_empty_comments(episode, sequence, shot)

    def _create_empty_comments(self, episode: str, sequence: str, shot: str) -> Dict:
        """Create empty comments structure."""
        return {
            "version": COMMENT_FILE_VERSION,
            "shot_info": {
                "episode": episode,
                "sequence": sequence,
                "shot": shot
            },
            "comments": []
        }

    def save_comments(self, episode: str, sequence: str, shot: str,
                     comments_data: Dict) -> bool:
        """Save comments for a shot."""
        comment_path = self.get_comment_file_path(episode, sequence, shot)

        try:
            # Ensure .horus directory exists
            horus_dir = f"{self.get_shot_path(episode, sequence, shot)}/{HORUS_DIR}"

            content = json.dumps(comments_data, indent=2, ensure_ascii=False)

            if self.fs:
                # Create directory if needed
                self.fs.ensure_directory(horus_dir)
                result = self.fs.write_file(comment_path, content)

                if result:
                    # Update cache
                    cache_key = f"{episode}_{sequence}_{shot}"
                    self._cache[cache_key] = comments_data

                return result

            return False

        except Exception as e:
            print(f"Error saving comments: {e}")
            return False

    def add_comment(self, episode: str, sequence: str, shot: str,
                   media_file: str, user: str, text: str,
                   frame: int = None, priority: str = "medium",
                   department: str = None, version: str = None) -> Optional[str]:
        """Add new comment to shot. Returns comment ID if successful."""

        # Load existing comments
        data = self.load_comments(episode, sequence, shot)

        # Generate comment ID
        comment_id = self._generate_uuid()

        # Extract department and version from media_file if not provided
        if not department or not version:
            dept, ver = self._parse_media_file(media_file)
            department = department or dept
            version = version or ver

        # Create comment object
        comment = {
            "id": comment_id,
            "parent_id": None,
            "media_file": media_file,
            "department": department,
            "media_version": version,
            "user": user,
            "user_display": self._format_user_display(user),
            "avatar": self._get_user_avatar(user),
            "text": text,
            "frame": frame,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "likes": 0,
            "liked_by": [],
            "status": "open",
            "priority": priority,
            "annotation_id": None,
            "replies": []
        }

        # Add to comments list
        data["comments"].append(comment)

        # Save
        if self.save_comments(episode, sequence, shot, data):
            return comment_id

        return None

    def add_reply(self, episode: str, sequence: str, shot: str,
                 parent_id: str, user: str, text: str) -> Optional[str]:
        """Add reply to existing comment. Supports nested replies."""

        # Load existing comments
        data = self.load_comments(episode, sequence, shot)

        # Find parent comment/reply
        parent = self._find_comment_by_id(data["comments"], parent_id)
        if not parent:
            print(f"Parent comment not found: {parent_id}")
            return None

        # Generate reply ID
        reply_id = self._generate_uuid()

        # Create reply object
        reply = {
            "id": reply_id,
            "parent_id": parent_id,
            "user": user,
            "user_display": self._format_user_display(user),
            "avatar": self._get_user_avatar(user),
            "text": text,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "likes": 0,
            "liked_by": [],
            "replies": []
        }

        # Add to parent's replies
        parent["replies"].append(reply)

        # Save
        if self.save_comments(episode, sequence, shot, data):
            return reply_id

        return None

    def delete_comment(self, episode: str, sequence: str, shot: str,
                      comment_id: str) -> bool:
        """Delete comment (and all nested replies)."""

        data = self.load_comments(episode, sequence, shot)

        # Try to remove from top-level comments
        for i, comment in enumerate(data["comments"]):
            if comment["id"] == comment_id:
                data["comments"].pop(i)
                return self.save_comments(episode, sequence, shot, data)

            # Try to remove from replies (recursive)
            if self._remove_reply_by_id(comment["replies"], comment_id):
                return self.save_comments(episode, sequence, shot, data)

        return False

    def _remove_reply_by_id(self, replies: List, reply_id: str) -> bool:
        """Recursively remove reply by ID."""
        for i, reply in enumerate(replies):
            if reply["id"] == reply_id:
                replies.pop(i)
                return True
            if self._remove_reply_by_id(reply.get("replies", []), reply_id):
                return True
        return False

    def update_comment(self, episode: str, sequence: str, shot: str,
                      comment_id: str, text: str = None,
                      status: str = None, priority: str = None) -> bool:
        """Update comment properties."""

        data = self.load_comments(episode, sequence, shot)
        comment = self._find_comment_by_id(data["comments"], comment_id)

        if not comment:
            return False

        if text is not None:
            comment["text"] = text
        if status is not None:
            comment["status"] = status
        if priority is not None:
            comment["priority"] = priority

        comment["updated_at"] = datetime.utcnow().isoformat() + "Z"

        return self.save_comments(episode, sequence, shot, data)

    def like_comment(self, episode: str, sequence: str, shot: str,
                    comment_id: str, user: str) -> bool:
        """Toggle like on comment."""

        data = self.load_comments(episode, sequence, shot)
        comment = self._find_comment_by_id(data["comments"], comment_id)

        if not comment:
            return False

        liked_by = comment.get("liked_by", [])

        if user in liked_by:
            # Unlike
            liked_by.remove(user)
            comment["likes"] = max(0, comment.get("likes", 1) - 1)
        else:
            # Like
            liked_by.append(user)
            comment["likes"] = comment.get("likes", 0) + 1

        comment["liked_by"] = liked_by

        return self.save_comments(episode, sequence, shot, data)

    # ============== Annotation Methods ==============

    def save_annotation_image(self, episode: str, sequence: str, shot: str,
                             department: str, version: str, frame: int,
                             image_data: bytes) -> Optional[str]:
        """Save annotation PNG image from RV Paint. Returns path if successful."""

        ann_path = self.get_annotation_file_path(episode, sequence, shot,
                                                  department, version, frame)
        ann_dir = self.get_annotation_dir(episode, sequence, shot, department, version)

        try:
            if self.fs:
                self.fs.ensure_directory(ann_dir)
                if self.fs.write_binary_file(ann_path, image_data):
                    return ann_path
        except Exception as e:
            print(f"Error saving annotation: {e}")

        return None

    def list_annotations(self, episode: str, sequence: str, shot: str,
                        department: str = None, version: str = None) -> List[Dict]:
        """List all annotations for shot/department/version."""

        annotations = []
        shot_path = self.get_shot_path(episode, sequence, shot)

        # List departments to check
        departments = [department] if department else self._list_departments(episode, sequence, shot)

        for dept in departments:
            ann_base = f"{shot_path}/{dept}/{ANNOTATIONS_DIR}"

            if not self.fs or not self.fs.file_exists(ann_base):
                continue

            # List versions
            versions = [version] if version else self.fs.list_directory(ann_base)

            for ver in versions:
                ver_dir = f"{ann_base}/{ver}"
                if not self.fs.file_exists(ver_dir):
                    continue

                # List PNG files
                files = self.fs.list_directory(ver_dir)
                for f in files:
                    if f.endswith('.png'):
                        # Parse frame number from filename
                        frame = self._parse_frame_from_filename(f)
                        annotations.append({
                            "department": dept,
                            "version": ver,
                            "frame": frame,
                            "filename": f,
                            "path": f"{ver_dir}/{f}"
                        })

        return annotations

    def _list_departments(self, episode: str, sequence: str, shot: str) -> List[str]:
        """List departments in a shot directory."""
        shot_path = self.get_shot_path(episode, sequence, shot)
        if self.fs:
            items = self.fs.list_directory(shot_path)
            # Filter to known department names
            depts = ["anim", "comp", "lighting", "layout", "fx", "hero"]
            return [d for d in items if d in depts]
        return []

    def _parse_frame_from_filename(self, filename: str) -> int:
        """Parse frame number from annotation filename."""
        # Format: {shot}_{dept}_{version}.{frame}.png
        try:
            parts = filename.replace('.png', '').split('.')
            if len(parts) >= 2:
                return int(parts[-1])
        except:
            pass
        return 0

    # ============== Helper Methods ==============

    def _generate_uuid(self) -> str:
        """Generate unique ID for comment/reply."""
        return str(uuid.uuid4())

    def _get_user_avatar(self, username: str) -> str:
        """Generate avatar initials from username."""
        if not username:
            return "??"
        parts = username.replace(".", " ").replace("_", " ").split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return username[:2].upper()

    def _format_user_display(self, username: str) -> str:
        """Format username for display."""
        if not username:
            return "Unknown"
        parts = username.replace(".", " ").replace("_", " ").split()
        return " ".join(p.capitalize() for p in parts)

    def _parse_media_file(self, media_file: str) -> tuple:
        """Parse department and version from media filename."""
        # Format: {shot}_{department}_{version}.mov
        # Example: SH0010_comp_v007.mov
        try:
            name = media_file.replace('.mov', '').replace('.exr', '')
            parts = name.split('_')
            if len(parts) >= 3:
                version = parts[-1]  # v007
                department = parts[-2]  # comp
                return department, version
        except:
            pass
        return None, None

    def _find_comment_by_id(self, comments: List, comment_id: str) -> Optional[Dict]:
        """Recursively find comment/reply by ID in nested structure."""
        for comment in comments:
            if comment.get("id") == comment_id:
                return comment
            # Search in replies
            found = self._find_comment_by_id(comment.get("replies", []), comment_id)
            if found:
                return found
        return None

    def clear_cache(self):
        """Clear comment cache."""
        self._cache = {}


# ============================================================================
# Singleton Instance
# ============================================================================

_comment_manager = None

def get_comment_manager() -> HorusCommentManager:
    """Get singleton comment manager instance."""
    global _comment_manager
    if _comment_manager is None:
        _comment_manager = HorusCommentManager()
    return _comment_manager

