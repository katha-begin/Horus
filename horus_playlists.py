"""
Horus Playlist Manager
Manages playlists for VFX review sessions.

Storage: {PROJECT_ROOT}/SWA/.horus/playlists.json
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional


PLAYLIST_FILE_VERSION = "1.0"


class HorusPlaylistManager:
    """Manage review playlists stored in project .horus directory."""

    def __init__(self):
        self.fs = None  # HorusFileSystem instance
        self._cache = None  # Cached playlists

    def set_file_system(self, fs):
        """Set the file system provider."""
        self.fs = fs
        self._cache = None  # Clear cache when fs changes

    def _generate_uuid(self) -> str:
        """Generate unique ID for playlist/clip."""
        return str(uuid.uuid4())

    def _get_timestamp(self) -> str:
        """Get current UTC timestamp in ISO format."""
        return datetime.utcnow().isoformat() + "Z"

    # ========================================================================
    # Load/Save Methods
    # ========================================================================

    def load_playlists(self) -> List[Dict]:
        """Load all playlists from storage."""
        if self._cache is not None:
            return self._cache

        if not self.fs:
            print("⚠️ No file system provider for playlists")
            return []

        playlists = self.fs.load_playlists()
        self._cache = playlists if playlists else []
        print(f"📋 Loaded {len(self._cache)} playlists from backend")
        return self._cache

    def save_playlists(self) -> bool:
        """Save all playlists to storage."""
        if not self.fs:
            print("⚠️ No file system provider for playlists")
            return False

        if self._cache is None:
            return True  # Nothing to save

        result = self.fs.save_playlists(self._cache)
        if result:
            print(f"✅ Saved {len(self._cache)} playlists to backend")
        else:
            print("❌ Failed to save playlists")
        return result

    def refresh(self):
        """Force reload from storage."""
        self._cache = None
        return self.load_playlists()

    # ========================================================================
    # Playlist CRUD Methods
    # ========================================================================

    def create_playlist(self, name: str, created_by: str = "unknown",
                       description: str = "", playlist_type: str = "user_created") -> Optional[str]:
        """Create a new playlist. Returns playlist ID if successful."""
        playlists = self.load_playlists()

        playlist_id = self._generate_uuid()
        timestamp = self._get_timestamp()

        new_playlist = {
            "_id": playlist_id,
            "name": name,
            "project_id": "SWA",
            "created_by": created_by,
            "created_at": timestamp,
            "updated_at": timestamp,
            "description": description,
            "type": playlist_type,
            "status": "active",
            "settings": {
                "auto_play": True,
                "loop": False,
                "frame_rate": 24
            },
            "clips": [],
            "metadata": {
                "clip_count": 0,
                "total_frames": 0
            }
        }

        playlists.append(new_playlist)
        self._cache = playlists

        if self.save_playlists():
            print(f"✅ Created playlist: {name} ({playlist_id})")
            return playlist_id
        return None

    def get_playlist(self, playlist_id: str) -> Optional[Dict]:
        """Get playlist by ID."""
        playlists = self.load_playlists()
        for playlist in playlists:
            if playlist.get("_id") == playlist_id:
                return playlist
        return None

    def update_playlist(self, playlist_id: str, updates: Dict) -> bool:
        """Update playlist properties."""
        playlist = self.get_playlist(playlist_id)
        if not playlist:
            return False

        # Update allowed fields
        allowed_fields = ["name", "description", "status", "settings"]
        for field in allowed_fields:
            if field in updates:
                playlist[field] = updates[field]

        playlist["updated_at"] = self._get_timestamp()
        return self.save_playlists()

    def delete_playlist(self, playlist_id: str) -> bool:
        """Delete a playlist."""
        playlists = self.load_playlists()

        for i, playlist in enumerate(playlists):
            if playlist.get("_id") == playlist_id:
                name = playlist.get("name", "Unknown")
                playlists.pop(i)
                self._cache = playlists
                if self.save_playlists():
                    print(f"✅ Deleted playlist: {name}")
                    return True
                return False
        return False

    # ========================================================================
    # Clip Management Methods
    # ========================================================================

    def add_clip(self, playlist_id: str, media_data: Dict) -> Optional[str]:
        """Add a clip to playlist. Returns clip ID if successful."""
        playlist = self.get_playlist(playlist_id)
        if not playlist:
            print(f"❌ Playlist not found: {playlist_id}")
            return None

        clip_id = self._generate_uuid()
        clips = playlist.get("clips", [])

        # Calculate position (add to end)
        position = len(clips)

        new_clip = {
            "clip_id": clip_id,
            "episode": media_data.get("episode", ""),
            "sequence": media_data.get("sequence", ""),
            "shot": media_data.get("shot", ""),
            "department": media_data.get("department", ""),
            "version": media_data.get("version", ""),
            "file_path": media_data.get("file_path", ""),
            "file_name": media_data.get("file_name", ""),
            "frame_range": media_data.get("frame_range", [1001, 1100]),
            "position": position,
            "added_at": self._get_timestamp()
        }

        clips.append(new_clip)
        playlist["clips"] = clips
        playlist["updated_at"] = self._get_timestamp()

        # Update metadata
        playlist["metadata"] = {
            "clip_count": len(clips),
            "total_frames": sum(
                (c.get("frame_range", [0, 0])[1] - c.get("frame_range", [0, 0])[0] + 1)
                for c in clips
            )
        }

        if self.save_playlists():
            print(f"✅ Added clip to playlist: {media_data.get('file_name', clip_id)}")
            return clip_id
        return None

    def remove_clip(self, playlist_id: str, clip_id: str) -> bool:
        """Remove a clip from playlist."""
        playlist = self.get_playlist(playlist_id)
        if not playlist:
            return False

        clips = playlist.get("clips", [])
        for i, clip in enumerate(clips):
            if clip.get("clip_id") == clip_id:
                clips.pop(i)
                break
        else:
            return False  # Clip not found

        # Reindex positions
        for i, clip in enumerate(clips):
            clip["position"] = i

        playlist["clips"] = clips
        playlist["updated_at"] = self._get_timestamp()

        # Update metadata
        playlist["metadata"] = {
            "clip_count": len(clips),
            "total_frames": sum(
                (c.get("frame_range", [0, 0])[1] - c.get("frame_range", [0, 0])[0] + 1)
                for c in clips
            )
        }

        return self.save_playlists()

    def reorder_clips(self, playlist_id: str, clip_order: List[str]) -> bool:
        """Reorder clips in playlist by providing ordered list of clip IDs."""
        playlist = self.get_playlist(playlist_id)
        if not playlist:
            return False

        clips = playlist.get("clips", [])

        # Build lookup by clip_id
        clip_lookup = {c["clip_id"]: c for c in clips}

        # Reorder based on provided order
        new_clips = []
        for i, clip_id in enumerate(clip_order):
            if clip_id in clip_lookup:
                clip = clip_lookup[clip_id]
                clip["position"] = i
                new_clips.append(clip)

        # Add any clips not in the order list (shouldn't happen but be safe)
        for clip in clips:
            if clip["clip_id"] not in clip_order:
                clip["position"] = len(new_clips)
                new_clips.append(clip)

        playlist["clips"] = new_clips
        playlist["updated_at"] = self._get_timestamp()

        return self.save_playlists()

    def get_clip(self, playlist_id: str, clip_id: str) -> Optional[Dict]:
        """Get a specific clip from playlist."""
        playlist = self.get_playlist(playlist_id)
        if not playlist:
            return None

        for clip in playlist.get("clips", []):
            if clip.get("clip_id") == clip_id:
                return clip
        return None

    def update_clip(self, playlist_id: str, clip_id: str, updates: Dict) -> bool:
        """Update clip properties."""
        clip = self.get_clip(playlist_id, clip_id)
        if not clip:
            return False

        # Update allowed fields
        allowed_fields = ["version", "file_path", "frame_range", "notes"]
        for field in allowed_fields:
            if field in updates:
                clip[field] = updates[field]

        playlist = self.get_playlist(playlist_id)
        playlist["updated_at"] = self._get_timestamp()

        return self.save_playlists()


# ============================================================================
# Global Instance
# ============================================================================

_playlist_manager: Optional[HorusPlaylistManager] = None


def get_playlist_manager() -> HorusPlaylistManager:
    """Get or create the global HorusPlaylistManager instance."""
    global _playlist_manager
    if _playlist_manager is None:
        _playlist_manager = HorusPlaylistManager()
    return _playlist_manager
