"""
Horus Playlist Manager
Manages playlist storage and operations using HorusFileSystem backend.
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
import uuid


class HorusPlaylistManager:
    """Manage playlists with file system backend."""
    
    def __init__(self):
        self.fs = None  # Will be set by set_file_system()
        self.playlists_cache = []  # In-memory cache
    
    def set_file_system(self, file_system):
        """Set the file system backend."""
        self.fs = file_system
        print(f"📋 HorusPlaylistManager: File system set ({file_system.access_mode if file_system else 'None'})")
    
    def load_playlists(self) -> List[Dict]:
        """Load all playlists from file system."""
        if not self.fs:
            print("⚠️ HorusPlaylistManager: No file system backend available")
            return []
        
        try:
            playlists = self.fs.load_playlists()
            self.playlists_cache = playlists
            print(f"✅ HorusPlaylistManager: Loaded {len(playlists)} playlists")
            return playlists
        except Exception as e:
            print(f"❌ HorusPlaylistManager: Error loading playlists: {e}")
            return []
    
    def save_playlists(self) -> bool:
        """Save all playlists to file system."""
        if not self.fs:
            print("⚠️ HorusPlaylistManager: No file system backend available")
            return False
        
        try:
            result = self.fs.save_playlists(self.playlists_cache)
            if result:
                print(f"✅ HorusPlaylistManager: Saved {len(self.playlists_cache)} playlists")
            return result
        except Exception as e:
            print(f"❌ HorusPlaylistManager: Error saving playlists: {e}")
            return False
    
    def get_playlist(self, playlist_id: str) -> Optional[Dict]:
        """Get playlist by ID."""
        for playlist in self.playlists_cache:
            if playlist.get("_id") == playlist_id:
                return playlist
        return None
    
    def create_playlist(self, name: str, created_by: str = "user",
                       description: str = "", playlist_type: str = "user_created") -> Optional[str]:
        """Create a new playlist."""
        import os
        
        playlist_id = f"playlist_{uuid.uuid4().hex[:8]}"
        current_time = datetime.utcnow().isoformat() + "Z"
        
        playlist = {
            "_id": playlist_id,
            "name": name,
            "project_id": "proj_001",
            "created_by": created_by,
            "created_at": current_time,
            "updated_at": current_time,
            "description": description,
            "type": playlist_type,
            "status": "draft",
            "settings": {
                "auto_play": True,
                "loop": False,
                "show_timecode": True,
                "default_track_height": 60,
                "timeline_zoom": 1.0,
                "color_coding_enabled": True
            },
            "clips": [],
            "tracks": [
                {
                    "track_id": 1,
                    "name": "Video Track 1",
                    "type": "video",
                    "height": 60,
                    "locked": False,
                    "muted": False,
                    "solo": False,
                    "color": "#2d2d2d"
                }
            ],
            "metadata": {}
        }
        
        self.playlists_cache.append(playlist)
        
        if self.save_playlists():
            print(f"✅ Created playlist: {name} ({playlist_id})")
            return playlist_id
        else:
            # Remove from cache if save failed
            self.playlists_cache.pop()
            print(f"❌ Failed to save playlist: {name}")
            return None
    
    def add_clip(self, playlist_id: str, clip_data: Dict) -> Optional[str]:
        """Add clip to playlist."""
        playlist = self.get_playlist(playlist_id)
        if not playlist:
            print(f"❌ Playlist not found: {playlist_id}")
            return None
        
        clip_id = f"clip_{uuid.uuid4().hex[:8]}"
        current_time = datetime.utcnow().isoformat() + "Z"
        
        clip = {
            "clip_id": clip_id,
            "name": clip_data.get("name", "Unknown"),
            "shot": clip_data.get("shot", ""),
            "episode": clip_data.get("episode", ""),
            "sequence": clip_data.get("sequence", ""),
            "department": clip_data.get("department", ""),
            "version": clip_data.get("version", "v001"),
            "status": clip_data.get("status", "wip"),
            "file_path": clip_data.get("file_path", ""),
            "added_at": current_time
        }
        
        playlist["clips"].append(clip)
        playlist["updated_at"] = current_time
        
        if self.save_playlists():
            print(f"✅ Added clip to playlist: {clip_id}")
            return clip_id
        else:
            # Remove from cache if save failed
            playlist["clips"].pop()
            print(f"❌ Failed to save clip to playlist")
            return None


# Global singleton instance
_playlist_manager: Optional[HorusPlaylistManager] = None

def get_playlist_manager() -> HorusPlaylistManager:
    """Get or create the global playlist manager instance."""
    global _playlist_manager
    if _playlist_manager is None:
        _playlist_manager = HorusPlaylistManager()
    return _playlist_manager

