# Horus Data Model Design
## JSON-Based Data Architecture for Media Review Application

**Project:** Horus  
**Version:** 2.0  
**Date:** 2025-01-22  

---

## 1. Overview

The Horus application uses a lightweight JSON-based data storage system for:
- **Playlists**: Collections of media clips organized for review
- **Comments**: Frame-accurate comments and review notes
- **Annotations**: Visual annotations exported from RV
- **Media Metadata**: Cached metadata for quick access

### Design Principles
- **Project-based organization**: All data scoped to projects
- **File path as primary key**: Media identified by file paths
- **Multi-extension support**: Support for image sequences and video files
- **Lightweight storage**: JSON files for easy backup and version control
- **RV integration**: Direct export of RV annotations

---

## 2. Directory Structure

```
sample_db/
├── project_configs.json          # Project configurations
├── horus_playlists.json          # Playlist definitions
├── media_metadata.json           # Cached media metadata
├── comments.json                 # Comments and review notes
├── annotations.json              # RV annotations export
└── user_preferences.json         # User settings
```

---

## 3. Data Schemas

### 3.1 Project Configuration Schema

```json
{
  "_id": "SWA",
  "name": "SWA Animation Project",
  "description": "Main production project",
  "status": "active",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-22T00:00:00Z",
  
  "templates": {
    "shot_template": "V:/SWA/all/scene/{episode}/{sequence}/{shot}/{task}/version/",
    "render_template": "V:/SWA/all/render/{episode}/{sequence}/{shot}/{task}/version/",
    "comp_template": "V:/SWA/all/comp/{episode}/{sequence}/{shot}/{task}/version/"
  },
  
  "drive_mapping": {
    "project_root": "V:/SWA",
    "render_root": "V:/SWA/all/render",
    "source_root": "V:/SWA/all/scene"
  },
  
  "media_extensions": {
    "image_sequences": [".exr", ".dpx", ".tif", ".tiff", ".png", ".jpg"],
    "video_files": [".mov", ".mp4", ".avi", ".mxf"],
    "supported_formats": ["exr", "dpx", "mov", "mp4"]
  },
  
  "departments": ["animation", "lighting", "compositing", "fx", "modeling"],
  "sequences": ["sq0010", "sq0020", "sq0030"],
  "episodes": ["Ep00", "Ep01", "Ep02"],
  
  "settings": {
    "frame_rate": 24,
    "resolution": "1920x1080",
    "color_space": "Rec709"
  }
}
```

### 3.2 Playlist Schema

```json
{
  "_id": "playlist_001",
  "name": "Daily Animation Review",
  "project_id": "SWA",
  "created_by": "animation_supervisor",
  "created_at": "2025-01-22T10:00:00Z",
  "updated_at": "2025-01-22T15:30:00Z",
  "description": "Daily review session",
  "type": "daily_review",
  "status": "active",
  
  "settings": {
    "auto_play": true,
    "loop": false,
    "show_timecode": true,
    "default_track_height": 45,
    "timeline_zoom": 1.0,
    "color_coding_enabled": true
  },
  
  "clips": [
    {
      "clip_id": "clip_001",
      "file_path": "/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov",
      "media_type": "video",
      "position": 0,
      "duration": 120,
      "in_point": 0,
      "out_point": 120,
      "track": 1,
      
      "metadata": {
        "department": "animation",
        "sequence": "sq0010",
        "shot": "sh0010",
        "version": "v003",
        "task": "animation",
        "artist": "john_doe",
        "approval_status": "approved"
      },
      
      "display": {
        "color": "#1f4e79",
        "thumbnail_path": "/cache/thumbnails/clip_001.jpg"
      },
      
      "notes": "Hero character performance approved",
      "added_at": "2025-01-22T10:15:00Z"
    }
  ],
  
  "tracks": [
    {
      "track_id": 1,
      "name": "Animation Track",
      "type": "video",
      "height": 45,
      "locked": false,
      "muted": false,
      "solo": false,
      "color": "#1f4e79"
    }
  ],
  
  "metadata": {
    "total_duration": 2148,
    "clip_count": 15,
    "departments": ["animation"],
    "sequences": ["sq0010", "sq0015", "sq0020"],
    "last_played_position": 0,
    "playback_settings": {
      "frame_rate": 24,
      "resolution": "1920x1080",
      "color_space": "Rec709"
    }
  }
}
```

### 3.3 Media Metadata Schema

```json
{
  "_id": "media_001",
  "file_path": "/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov",
  "project_id": "SWA",
  "media_type": "video",

  "file_info": {
    "filename": "sh0010_anim_v003.mov",
    "extension": ".mov",
    "size_bytes": 524288000,
    "created_at": "2025-01-20T14:30:00Z",
    "modified_at": "2025-01-20T14:35:00Z"
  },

  "media_properties": {
    "width": 1920,
    "height": 1080,
    "frame_rate": 24.0,
    "duration_frames": 120,
    "duration_seconds": 5.0,
    "codec": "ProRes 422 HQ",
    "color_space": "Rec709",
    "has_alpha": false
  },

  "sequence_info": {
    "is_sequence": false,
    "frame_range": null,
    "frame_padding": null,
    "sequence_pattern": null
  },

  "project_metadata": {
    "department": "animation",
    "sequence": "sq0010",
    "shot": "sh0010",
    "version": "v003",
    "task": "animation",
    "artist": "john_doe",
    "approval_status": "approved",
    "tags": ["hero", "character", "performance"]
  },

  "thumbnail": {
    "path": "/cache/thumbnails/media_001.jpg",
    "generated_at": "2025-01-20T14:36:00Z"
  },

  "indexed_at": "2025-01-22T10:00:00Z"
}
```

### 3.4 Comments Schema

```json
{
  "_id": "comment_001",
  "parent_id": null,
  "media_path": "/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov",
  "playlist_id": "playlist_001",
  "project_id": "SWA",

  "frame_reference": {
    "frame_number": 45,
    "timecode": "00:00:01:21",
    "timestamp_seconds": 1.875
  },

  "user_info": {
    "user_id": "animation_supervisor",
    "user_name": "John Smith",
    "user_email": "john.smith@studio.com",
    "user_avatar": "/avatars/john_smith.jpg"
  },

  "content": {
    "text": "The eye line doesn't match the previous shot",
    "content_type": "text",
    "mentions": ["@jane_doe"],
    "attachments": []
  },

  "status": {
    "state": "open",
    "priority": "high",
    "category": "animation",
    "assigned_to": "jane_doe"
  },

  "threading": {
    "thread_depth": 0,
    "reply_count": 2,
    "replies": ["comment_002", "comment_003"]
  },

  "reactions": {
    "likes": 3,
    "reactions": [
      {"user_id": "jane_doe", "type": "thumbs_up", "timestamp": "2025-01-22T11:00:00Z"}
    ]
  },

  "created_at": "2025-01-22T10:30:00Z",
  "updated_at": "2025-01-22T11:00:00Z",
  "is_resolved": false
}
```

### 3.5 RV Annotations Schema

```json
{
  "_id": "annotation_001",
  "media_path": "/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov",
  "project_id": "SWA",
  "frame_number": 45,

  "annotation_type": "rectangle",

  "coordinates": {
    "x": 450,
    "y": 320,
    "width": 200,
    "height": 150,
    "normalized": {
      "x": 0.234375,
      "y": 0.296296,
      "width": 0.104167,
      "height": 0.138889
    }
  },

  "style": {
    "color": "#ff0000",
    "line_width": 3,
    "opacity": 0.8,
    "fill_opacity": 0.2,
    "line_style": "solid"
  },

  "content": {
    "text": "Fix eye line",
    "font_size": 14,
    "font_family": "Arial"
  },

  "user_info": {
    "user_id": "animation_supervisor",
    "user_name": "John Smith",
    "created_at": "2025-01-22T10:35:00Z"
  },

  "rv_export": {
    "rv_version": "2.0.0",
    "export_format": "json",
    "exported_at": "2025-01-22T10:40:00Z",
    "rv_node_data": {
      "node_type": "RVPaint",
      "node_name": "paint_001",
      "properties": {}
    }
  },

  "linked_comment_id": "comment_001",
  "is_visible": true,
  "layer_name": "default"
}
```

---

## 4. Application Components

### 4.1 Directory Browser Component

**Purpose**: Navigate file system and discover media files

**Features**:
- Project-based root directory navigation
- Multi-extension filtering (image sequences, video files)
- Thumbnail preview generation
- Metadata extraction and caching
- Drag-and-drop to playlist

**Data Flow**:
```
File System → Directory Browser → Media Metadata Cache → Playlist
```

### 4.2 Playlist Manager Component

**Purpose**: Organize media clips for review sessions

**Features**:
- Create/edit/delete playlists
- Add/remove media clips
- Reorder clips in timeline
- Multi-track support
- Playlist templates (daily review, department review, client delivery)
- Export playlist to RV session

**Data Flow**:
```
Directory Browser → Playlist Manager → horus_playlists.json → RV Session
```

### 4.3 Comments & Annotations Component

**Purpose**: Frame-accurate review and annotation

**Features**:
- Frame-specific comments
- Threaded discussions
- Visual annotations (shapes, arrows, text)
- RV annotation import/export
- Status tracking (open, resolved)
- Priority levels

**Data Flow**:
```
RV Annotations → Export → annotations.json → Comments Widget
Comments Widget → Save → comments.json
```

---

## 5. Data Manager API

### 5.1 Playlist Operations

```python
class PlaylistManager:
    """Manage playlist data operations."""

    def create_playlist(self, name: str, project_id: str, **kwargs) -> dict:
        """Create a new playlist."""
        pass

    def get_playlist(self, playlist_id: str) -> dict:
        """Retrieve playlist by ID."""
        pass

    def update_playlist(self, playlist_id: str, updates: dict) -> bool:
        """Update playlist properties."""
        pass

    def delete_playlist(self, playlist_id: str) -> bool:
        """Delete a playlist."""
        pass

    def add_clip_to_playlist(self, playlist_id: str, file_path: str,
                            metadata: dict) -> dict:
        """Add media clip to playlist."""
        pass

    def remove_clip_from_playlist(self, playlist_id: str, clip_id: str) -> bool:
        """Remove clip from playlist."""
        pass

    def reorder_clips(self, playlist_id: str, clip_order: list) -> bool:
        """Reorder clips in playlist."""
        pass

    def export_to_rv(self, playlist_id: str) -> str:
        """Export playlist to RV session file."""
        pass
```

### 5.2 Media Metadata Operations

```python
class MediaMetadataManager:
    """Manage media metadata cache."""

    def index_media_file(self, file_path: str, project_id: str) -> dict:
        """Index a media file and extract metadata."""
        pass

    def get_media_metadata(self, file_path: str) -> dict:
        """Retrieve cached metadata for media file."""
        pass

    def update_metadata(self, file_path: str, updates: dict) -> bool:
        """Update media metadata."""
        pass

    def search_media(self, project_id: str, filters: dict) -> list:
        """Search media files by filters."""
        pass

    def detect_image_sequence(self, directory: str) -> list:
        """Detect image sequences in directory."""
        pass
```

### 5.3 Comments Operations

```python
class CommentsManager:
    """Manage comments and review notes."""

    def create_comment(self, media_path: str, frame_number: int,
                      content: str, **kwargs) -> dict:
        """Create a new comment."""
        pass

    def get_comments_for_media(self, media_path: str) -> list:
        """Get all comments for a media file."""
        pass

    def get_comments_for_frame(self, media_path: str, frame_number: int) -> list:
        """Get comments for specific frame."""
        pass

    def reply_to_comment(self, parent_id: str, content: str, **kwargs) -> dict:
        """Reply to an existing comment."""
        pass

    def update_comment_status(self, comment_id: str, status: str) -> bool:
        """Update comment status (open/resolved)."""
        pass

    def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment."""
        pass
```

### 5.4 RV Annotations Operations

```python
class RVAnnotationsManager:
    """Manage RV annotations import/export."""

    def export_rv_annotations(self, media_path: str) -> list:
        """Export annotations from RV for current media."""
        pass

    def import_annotations_to_rv(self, media_path: str,
                                annotations: list) -> bool:
        """Import annotations into RV."""
        pass

    def save_annotation(self, media_path: str, frame_number: int,
                       annotation_data: dict) -> dict:
        """Save a single annotation."""
        pass

    def get_annotations_for_frame(self, media_path: str,
                                 frame_number: int) -> list:
        """Get all annotations for a specific frame."""
        pass

    def delete_annotation(self, annotation_id: str) -> bool:
        """Delete an annotation."""
        pass
```

---

## 6. Implementation Guidelines

### 6.1 File Path Logic

**Path Normalization**:
```python
import os
from pathlib import Path

def normalize_path(file_path: str) -> str:
    """Normalize file path for cross-platform compatibility."""
    return str(Path(file_path).resolve()).replace('\\', '/')

def get_relative_path(file_path: str, project_root: str) -> str:
    """Get relative path from project root."""
    return str(Path(file_path).relative_to(project_root))
```

**Image Sequence Detection**:
```python
import re

def detect_sequence_pattern(file_path: str) -> dict:
    """Detect if file is part of an image sequence."""
    filename = os.path.basename(file_path)

    # Pattern: filename.####.ext or filename_####.ext
    pattern = r'(.+?)[\._](\d+)(\.\w+)$'
    match = re.match(pattern, filename)

    if match:
        base_name, frame_num, extension = match.groups()
        padding = len(frame_num)

        return {
            'is_sequence': True,
            'base_name': base_name,
            'frame_number': int(frame_num),
            'padding': padding,
            'extension': extension,
            'pattern': f"{base_name}.{'#' * padding}{extension}"
        }

    return {'is_sequence': False}

def get_sequence_files(directory: str, pattern: dict) -> list:
    """Get all files in an image sequence."""
    if not pattern['is_sequence']:
        return []

    files = []
    for file in os.listdir(directory):
        if re.match(pattern['pattern'].replace('#', r'\d'), file):
            files.append(os.path.join(directory, file))

    return sorted(files)
```

### 6.2 Multi-Extension Support

```python
class MediaExtensionHandler:
    """Handle different media file extensions."""

    IMAGE_SEQUENCES = ['.exr', '.dpx', '.tif', '.tiff', '.png', '.jpg']
    VIDEO_FILES = ['.mov', '.mp4', '.avi', '.mxf', '.r3d']

    @classmethod
    def is_image_sequence(cls, file_path: str) -> bool:
        """Check if file is an image sequence format."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in cls.IMAGE_SEQUENCES

    @classmethod
    def is_video_file(cls, file_path: str) -> bool:
        """Check if file is a video format."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in cls.VIDEO_FILES

    @classmethod
    def get_media_type(cls, file_path: str) -> str:
        """Determine media type."""
        if cls.is_image_sequence(file_path):
            return 'image_sequence'
        elif cls.is_video_file(file_path):
            return 'video'
        else:
            return 'unknown'
```

### 6.3 JSON Data Storage

```python
import json
from datetime import datetime
from typing import Any

class JSONDataStore:
    """Simple JSON-based data storage."""

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load(self, filename: str) -> list:
        """Load data from JSON file."""
        file_path = self.data_dir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save(self, filename: str, data: Any) -> bool:
        """Save data to JSON file."""
        file_path = self.data_dir / filename
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving {filename}: {e}")
            return False

    def append(self, filename: str, item: dict) -> bool:
        """Append item to JSON array."""
        data = self.load(filename)
        data.append(item)
        return self.save(filename, data)

    def update(self, filename: str, item_id: str, updates: dict) -> bool:
        """Update item in JSON array by ID."""
        data = self.load(filename)
        for item in data:
            if item.get('_id') == item_id:
                item.update(updates)
                item['updated_at'] = datetime.utcnow().isoformat() + 'Z'
                return self.save(filename, data)
        return False

    def delete(self, filename: str, item_id: str) -> bool:
        """Delete item from JSON array by ID."""
        data = self.load(filename)
        data = [item for item in data if item.get('_id') != item_id]
        return self.save(filename, data)
```

---

## 7. Workflow Examples

### 7.1 Creating a Playlist from Directory Browser

```python
# User workflow:
# 1. Browse to directory in Directory Browser
# 2. Select media files (Ctrl+Click for multi-select)
# 3. Click "Add to Playlist" button
# 4. Choose existing playlist or create new one

# Implementation:
def add_media_to_playlist(file_paths: list, playlist_id: str):
    """Add multiple media files to playlist."""
    playlist_manager = PlaylistManager()
    media_manager = MediaMetadataManager()

    for file_path in file_paths:
        # Index media file if not already cached
        metadata = media_manager.get_media_metadata(file_path)
        if not metadata:
            metadata = media_manager.index_media_file(file_path, project_id)

        # Add to playlist
        playlist_manager.add_clip_to_playlist(
            playlist_id=playlist_id,
            file_path=file_path,
            metadata=metadata
        )
```

### 7.2 Exporting RV Annotations

```python
# User workflow:
# 1. Review media in RV with annotations
# 2. Click "Export Annotations" button
# 3. Annotations saved to database
# 4. Linked to comments if applicable

# Implementation:
def export_rv_annotations_workflow(media_path: str):
    """Export annotations from RV to database."""
    rv_manager = RVAnnotationsManager()
    comments_manager = CommentsManager()

    # Export from RV
    annotations = rv_manager.export_rv_annotations(media_path)

    # Save each annotation
    for annotation in annotations:
        # Save annotation
        saved_annotation = rv_manager.save_annotation(
            media_path=media_path,
            frame_number=annotation['frame_number'],
            annotation_data=annotation
        )

        # Create linked comment if annotation has text
        if annotation.get('content', {}).get('text'):
            comment = comments_manager.create_comment(
                media_path=media_path,
                frame_number=annotation['frame_number'],
                content=annotation['content']['text'],
                linked_annotation_id=saved_annotation['_id']
            )
```

### 7.3 Loading Playlist in RV

```python
# User workflow:
# 1. Select playlist from Playlist Manager
# 2. Click "Load in RV" button
# 3. RV opens with all clips loaded in sequence

# Implementation:
def load_playlist_in_rv(playlist_id: str):
    """Load playlist clips into RV session."""
    import rv.commands as rvc

    playlist_manager = PlaylistManager()
    playlist = playlist_manager.get_playlist(playlist_id)

    # Clear current RV session
    rvc.clearEverything()

    # Load each clip in order
    for clip in sorted(playlist['clips'], key=lambda x: x['position']):
        file_path = clip['file_path']

        # Handle image sequences vs video files
        if MediaExtensionHandler.is_image_sequence(file_path):
            # Load as sequence
            sequence_info = detect_sequence_pattern(file_path)
            if sequence_info['is_sequence']:
                directory = os.path.dirname(file_path)
                sequence_files = get_sequence_files(directory, sequence_info)
                rvc.addSource(sequence_files)
        else:
            # Load single video file
            rvc.addSource(file_path)

    print(f"Loaded {len(playlist['clips'])} clips into RV")
```

---

## 8. Database File Structure

### 8.1 Recommended File Organization

```
sample_db/
├── project_configs.json          # Project settings and templates
├── horus_playlists.json          # All playlists
├── media_metadata.json           # Cached media metadata
├── comments.json                 # All comments and replies
├── annotations.json              # RV annotations
├── user_preferences.json         # User settings
└── cache/
    └── thumbnails/               # Generated thumbnails
        ├── media_001.jpg
        ├── media_002.jpg
        └── ...
```

### 8.2 Backup and Version Control

```python
def backup_database(backup_dir: str):
    """Create backup of all JSON database files."""
    import shutil
    from datetime import datetime

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = Path(backup_dir) / f"horus_backup_{timestamp}"
    backup_path.mkdir(parents=True, exist_ok=True)

    # Copy all JSON files
    for json_file in Path('sample_db').glob('*.json'):
        shutil.copy2(json_file, backup_path / json_file.name)

    print(f"Backup created: {backup_path}")
```

---

## 9. Summary

This data model provides:

✅ **Project-based organization** with flexible path templates
✅ **Multi-extension support** for image sequences and video files
✅ **Playlist management** with add/remove/reorder capabilities
✅ **Frame-accurate comments** with threading and status tracking
✅ **RV annotation export** with full metadata preservation
✅ **Lightweight JSON storage** for easy backup and version control
✅ **Simple API** for all data operations

The design is optimized for VFX workflows while remaining simple and maintainable.
```


