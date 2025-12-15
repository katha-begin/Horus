# Horus Implementation Guide
## Step-by-Step Implementation for Directory Browser, Playlist, and RV Integration

**Project:** Horus  
**Version:** 2.0  
**Date:** 2025-01-22  

---

## 1. Implementation Roadmap

### Phase 1: Data Layer (Week 1)
- [ ] Create JSON data store manager
- [ ] Implement playlist data operations
- [ ] Implement comments data operations
- [ ] Implement annotations data operations
- [ ] Add media metadata caching

### Phase 2: Directory Browser (Week 2)
- [ ] Create directory tree widget
- [ ] Implement file system scanning
- [ ] Add thumbnail generation
- [ ] Add multi-extension filtering
- [ ] Implement drag-and-drop

### Phase 3: Playlist Manager (Week 3)
- [ ] Create playlist UI widget
- [ ] Implement add/remove clips
- [ ] Add clip reordering
- [ ] Implement RV session export
- [ ] Add playlist templates

### Phase 4: RV Integration (Week 4)
- [ ] Implement RV annotation export
- [ ] Create annotation import
- [ ] Link annotations to comments
- [ ] Add RV session loading
- [ ] Test end-to-end workflow

---

## 2. Quick Start Implementation

### 2.1 Create Data Manager Package

**File**: `src/packages/horus_database/python/horus_database/data_manager.py`

```python
"""
Horus Data Manager
Simple JSON-based data storage for playlists, comments, and annotations.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import uuid


class HorusDataManager:
    """Manage all Horus data operations."""
    
    def __init__(self, data_dir: str = "sample_db"):
        """Initialize data manager with data directory."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Data file paths
        self.playlists_file = self.data_dir / "horus_playlists.json"
        self.comments_file = self.data_dir / "comments.json"
        self.annotations_file = self.data_dir / "annotations.json"
        self.metadata_file = self.data_dir / "media_metadata.json"
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Create empty JSON files if they don't exist."""
        for file_path in [self.playlists_file, self.comments_file, 
                         self.annotations_file, self.metadata_file]:
            if not file_path.exists():
                self._save_json(file_path, [])
    
    def _load_json(self, file_path: Path) -> List[Dict]:
        """Load data from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return []
    
    def _save_json(self, file_path: Path, data: List[Dict]) -> bool:
        """Save data to JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
            return False
    
    # Playlist Operations
    
    def create_playlist(self, name: str, project_id: str, **kwargs) -> Dict:
        """Create a new playlist."""
        playlist = {
            "_id": kwargs.get('playlist_id', f"playlist_{uuid.uuid4().hex[:8]}"),
            "name": name,
            "project_id": project_id,
            "created_by": kwargs.get('created_by', 'user'),
            "created_at": datetime.utcnow().isoformat() + 'Z',
            "updated_at": datetime.utcnow().isoformat() + 'Z',
            "description": kwargs.get('description', f"New playlist: {name}"),
            "type": kwargs.get('type', 'review'),
            "status": kwargs.get('status', 'active'),
            "settings": {
                "auto_play": True,
                "loop": False,
                "show_timecode": True,
                "default_track_height": 45,
                "timeline_zoom": 1.0,
                "color_coding_enabled": True
            },
            "clips": [],
            "tracks": [],
            "metadata": {}
        }
        
        playlists = self._load_json(self.playlists_file)
        playlists.append(playlist)
        self._save_json(self.playlists_file, playlists)
        
        return playlist
    
    def get_playlist(self, playlist_id: str) -> Optional[Dict]:
        """Get playlist by ID."""
        playlists = self._load_json(self.playlists_file)
        for playlist in playlists:
            if playlist.get('_id') == playlist_id:
                return playlist
        return None
    
    def get_all_playlists(self, project_id: Optional[str] = None) -> List[Dict]:
        """Get all playlists, optionally filtered by project."""
        playlists = self._load_json(self.playlists_file)
        if project_id:
            return [p for p in playlists if p.get('project_id') == project_id]
        return playlists
    
    def update_playlist(self, playlist_id: str, updates: Dict) -> bool:
        """Update playlist properties."""
        playlists = self._load_json(self.playlists_file)
        for playlist in playlists:
            if playlist.get('_id') == playlist_id:
                playlist.update(updates)
                playlist['updated_at'] = datetime.utcnow().isoformat() + 'Z'
                return self._save_json(self.playlists_file, playlists)
        return False
    
    def delete_playlist(self, playlist_id: str) -> bool:
        """Delete a playlist."""
        playlists = self._load_json(self.playlists_file)
        playlists = [p for p in playlists if p.get('_id') != playlist_id]
        return self._save_json(self.playlists_file, playlists)
```

This is the foundation. Let me continue with more implementation details...

