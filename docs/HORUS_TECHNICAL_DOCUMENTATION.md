# Horus VFX Review Application - Technical Documentation

**Version:** 0.1.0-dev  
**Last Updated:** 2025-12-17  
**Project:** SWA Animation Pipeline  

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Directory Structure](#3-directory-structure)
4. [Data Storage](#4-data-storage)
5. [File System Backend](#5-file-system-backend)
6. [Status Management](#6-status-management)
7. [Comments System](#7-comments-system)
8. [Playlist System](#8-playlist-system)
9. [UI Components](#9-ui-components)
10. [API Reference](#10-api-reference)

---

## 1. System Overview

### 1.1 Purpose

Horus is a VFX review application built on Open RV 3.0.0 for the SWA animation pipeline. It provides:
- **Media browsing** across episodes, sequences, and shots
- **Status management** for shot versions (wip, approved, submit, need fix, on hold)
- **Comments and annotations** for review feedback
- **Playlist creation** for dailies and client reviews
- **Timeline editing** with OTIO integration

### 1.2 Technology Stack

- **Platform:** Open RV 3.0.0 (Python 3.9+)
- **UI Framework:** PySide2 (Qt 5.15+)
- **File System:** SSH-based remote access + local mount support
- **Data Format:** JSON files
- **Timeline:** OpenTimelineIO (OTIO)

### 1.3 Access Methods

**SSH Access (Primary):**
- Host: `10.100.128.193`
- User: `ec2-user`
- Key: `~/.ssh/CaveTeam.pem`

**Local Mount (Alternative):**
- Windows: `V:/` (project), `W:/` (images)
- Linux: `/mnt/igloo_swa_v/` (project), `/mnt/igloo_swa_w/` (images)

---

## 2. Architecture

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Open RV 3.0.0                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         rv_horus_integration.py (UI Layer)           │   │
│  │  - Navigator Widget (Media Browser)                  │   │
│  │  - Timeline Widget (Playlist Editor)                 │   │
│  │  - Comments Widget (Review Feedback)                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Backend Layer                           │   │
│  │  ┌────────────────┐  ┌────────────────┐             │   │
│  │  │ horus_file_    │  │ horus_         │             │   │
│  │  │ system.py      │  │ playlists.py   │             │   │
│  │  │ (File Access)  │  │ (Playlist Mgmt)│             │   │
│  │  └────────────────┘  └────────────────┘             │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         File System Providers                        │   │
│  │  ┌──────────────┐  ┌──────────────┐                 │   │
│  │  │ SSHProvider  │  │ LocalProvider│                 │   │
│  │  └──────────────┘  └──────────────┘                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │   Remote Server (10.100.128.193)    │
        │   /mnt/igloo_swa_v/SWA/all/scene/   │
        └─────────────────────────────────────┘
```

### 2.2 Key Modules

| Module | Purpose | Lines |
|--------|---------|-------|
| `rv_horus_integration.py` | UI widgets and RV integration | 6,208 |
| `horus_file_system.py` | File system abstraction layer | 1,098 |
| `horus_playlists.py` | Playlist CRUD operations | 309 |
| `horus_version.py` | Version management | 229 |
| `horus_rv_launcher.py` | Application launcher | ~200 |

---

## 3. Directory Structure

### 3.1 Project Directory Layout

```
/mnt/igloo_swa_v/SWA/all/scene/
├── Ep01/                           # Episode 01
│   ├── .horus/                     # Episode-level Horus data
│   │   └── status/                 # Status cache per sequence
│   │       ├── sq0010_status.json
│   │       ├── sq0020_status.json
│   │       └── sq0030_status.json
│   ├── sq0010/                     # Sequence 0010
│   │   ├── SH0010/                 # Shot 0010
│   │   │   ├── .horus/             # Shot-level Horus data
│   │   │   │   └── SH0010_comments.json
│   │   │   ├── comp/               # Compositing department
│   │   │   │   ├── output/         # Rendered movies
│   │   │   │   │   ├── SH0010_comp_v001.mov
│   │   │   │   │   ├── SH0010_comp_v002.mov
│   │   │   │   │   └── SH0010_comp_v003.mov
│   │   │   │   ├── version/        # Work files
│   │   │   │   └── annotations/    # Annotation images
│   │   │   │       ├── v001/
│   │   │   │       ├── v002/
│   │   │   │       └── v003/
│   │   │   ├── lighting/
│   │   │   ├── anim/
│   │   │   └── fx/
│   │   ├── SH0020/
│   │   └── SH0030/
│   ├── sq0020/
│   └── sq0030/
├── Ep02/
├── Ep03/
├── Ep04/
└── .horus/                         # Project-level Horus data
    └── playlists.json              # All playlists
```

### 3.2 File Naming Conventions

**Media Files:**
- Format: `{Shot}_{Department}_{Version}.{ext}`
- Example: `SH0010_comp_v003.mov`

**Status Files:**
- Format: `{Sequence}_status.json`
- Location: `{Episode}/.horus/status/`
- Example: `Ep01/.horus/status/sq0010_status.json`

**Comment Files:**
- Format: `{Shot}_comments.json`
- Location: `{Episode}/{Sequence}/{Shot}/.horus/`
- Example: `Ep01/sq0010/SH0010/.horus/SH0010_comments.json`

**Annotation Images:**
- Format: `{Shot}_{Department}_{Version}.{frame}.png`
- Location: `{Episode}/{Sequence}/{Shot}/{Department}/annotations/{Version}/`
- Example: `Ep01/sq0010/SH0010/comp/annotations/v003/SH0010_comp_v003.0045.png`

---

## 4. Data Storage

### 4.1 Storage Strategy

**Distributed Storage:**
- Status data: Per-sequence JSON files (performance optimization)
- Comments: Per-shot JSON files (logical grouping)
- Playlists: Single project-level JSON file (shared resource)

**Benefits:**
- ✅ Parallel access (multiple users can work on different sequences)
- ✅ Reduced file size (no need to load entire project data)
- ✅ Better performance (only load what's needed)
- ✅ Easier backup (granular file-level backups)

### 4.2 Status Storage Schema

**File:** `{Episode}/.horus/status/{Sequence}_status.json`

```json
{
  "version": "1.0",
  "episode": "Ep01",
  "sequence": "sq0010",
  "last_updated": "2025-12-17T10:30:00Z",
  "statuses": {
    "SH0010_comp_v003": {
      "current_status": "approved",
      "last_changed": "2025-12-17T10:30:00Z",
      "last_changed_by": "john.doe",
      "history": [
        {
          "status": "wip",
          "changed_at": "2025-12-15T09:00:00Z",
          "changed_by": "artist.name"
        },
        {
          "status": "submit",
          "changed_at": "2025-12-16T14:30:00Z",
          "changed_by": "artist.name"
        },
        {
          "status": "approved",
          "changed_at": "2025-12-17T10:30:00Z",
          "changed_by": "john.doe"
        }
      ]
    },
    "SH0010_lighting_v002": {
      "current_status": "need fix",
      "last_changed": "2025-12-17T11:00:00Z",
      "last_changed_by": "supervisor.name",
      "history": [...]
    }
  }
}
```

**Status Values:**
- `wip` - Work in progress (default for new shots)
- `approved` - Approved for final
- `submit` - Submitted for review
- `need fix` - Requires changes
- `on hold` - Temporarily paused

**Key Format:** `{Shot}_{Department}_{Version}`
- Example: `SH0010_comp_v003`

### 4.3 Comments Storage Schema

**File:** `{Episode}/{Sequence}/{Shot}/.horus/{Shot}_comments.json`

```json
{
  "version": "1.0",
  "shot_info": {
    "episode": "Ep01",
    "sequence": "sq0010",
    "shot": "SH0010"
  },
  "comments": [
    {
      "_id": "comment_001",
      "parent_id": null,
      "media_file": "SH0010_comp_v003.mov",
      "frame_number": 45,
      "timecode": "00:00:01:21",
      "user_id": "john.doe",
      "user_name": "John Doe",
      "content": "The lighting looks great in this shot!",
      "created_at": "2025-12-17T10:30:00Z",
      "updated_at": "2025-12-17T10:30:00Z",
      "is_resolved": false,
      "thread_depth": 0,
      "mention_users": [],
      "reactions": {
        "like": ["jane.smith", "mike.wilson"],
        "approve": ["supervisor.name"]
      }
    },
    {
      "_id": "comment_002",
      "parent_id": "comment_001",
      "media_file": "SH0010_comp_v003.mov",
      "frame_number": 45,
      "user_id": "jane.smith",
      "user_name": "Jane Smith",
      "content": "@john.doe Agreed! The rim light is perfect.",
      "created_at": "2025-12-17T10:35:00Z",
      "updated_at": "2025-12-17T10:35:00Z",
      "is_resolved": false,
      "thread_depth": 1,
      "mention_users": ["john.doe"],
      "reactions": {}
    }
  ],
  "annotations": [
    {
      "_id": "annotation_001",
      "media_file": "SH0010_comp_v003.mov",
      "frame_number": 45,
      "annotation_type": "rectangle",
      "coordinates": {
        "x": 100,
        "y": 150,
        "width": 200,
        "height": 100
      },
      "style_properties": {
        "stroke_color": "#ff0000",
        "stroke_width": 2,
        "fill_color": "transparent"
      },
      "content": "Fix edge here",
      "user_id": "john.doe",
      "user_name": "John Doe",
      "created_at": "2025-12-17T10:30:00Z",
      "is_visible": true,
      "layer_name": "default"
    }
  ]
}
```

**Annotation Types:**
- `rectangle` - Rectangular selection
- `circle` - Circular selection
- `arrow` - Directional arrow
- `text` - Text label
- `freehand` - Free-form drawing

### 4.4 Playlist Storage Schema

**File:** `/mnt/igloo_swa_v/SWA/all/scene/.horus/playlists.json`

```json
[
  {
    "_id": "playlist_001",
    "name": "Daily Animation Review - Dec 17",
    "project_id": "SWA",
    "created_by": "supervisor.name",
    "created_at": "2025-12-17T09:00:00Z",
    "updated_at": "2025-12-17T10:30:00Z",
    "description": "Daily review for animation department",
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
        "_id": "clip_001",
        "name": "SH0010_comp_v003",
        "episode": "Ep01",
        "sequence": "sq0010",
        "shot": "SH0010",
        "department": "comp",
        "version": "v003",
        "file_path": "/mnt/igloo_swa_v/SWA/all/scene/Ep01/sq0010/SH0010/comp/output/SH0010_comp_v003.mov",
        "media_type": "video",
        "position": 0,
        "duration": 120,
        "in_point": 0,
        "out_point": 120,
        "track": 1,
        "status": "approved",
        "color": "#1f4e79",
        "notes": "Final approved version",
        "added_at": "2025-12-17T09:15:00Z"
      },
      {
        "_id": "clip_002",
        "name": "SH0020_lighting_v002",
        "episode": "Ep01",
        "sequence": "sq0010",
        "shot": "SH0020",
        "department": "lighting",
        "version": "v002",
        "file_path": "/mnt/igloo_swa_v/SWA/all/scene/Ep01/sq0010/SH0020/lighting/output/SH0020_lighting_v002.mov",
        "media_type": "video",
        "position": 120,
        "duration": 96,
        "in_point": 0,
        "out_point": 96,
        "track": 1,
        "status": "submit",
        "color": "#1f4e79",
        "notes": "Waiting for review",
        "added_at": "2025-12-17T09:20:00Z"
      }
    ],
    "tracks": [
      {
        "track_id": 1,
        "name": "Video Track 1",
        "type": "video",
        "height": 45,
        "locked": false,
        "muted": false,
        "solo": false,
        "color": "#1f4e79"
      }
    ]
  }
]
```

**Playlist Types:**
- `daily_review` - Daily review sessions
- `episode` - Full episode sequence
- `sequence` - Individual sequence cuts
- `department` - Department-specific reviews
- `client` - Client presentation cuts
- `user_created` - Custom user playlists

---

## 5. File System Backend

### 5.1 Architecture

The file system backend (`horus_file_system.py`) provides an abstraction layer that supports both SSH and local file access through a provider pattern.

```python
# Abstract base class
class FileSystemProvider(ABC):
    @abstractmethod
    def list_directory(self, path: str) -> List[str]
    @abstractmethod
    def file_exists(self, path: str) -> bool
    @abstractmethod
    def read_file(self, path: str) -> str
    @abstractmethod
    def write_file(self, path: str, content: str) -> bool
    @abstractmethod
    def get_file_info(self, path: str) -> Dict

# Concrete implementations
class SSHFileSystemProvider(FileSystemProvider):
    """SSH-based remote file access"""

class LocalFileSystemProvider(FileSystemProvider):
    """Local mount file access"""
```

### 5.2 Access Mode Detection

```python
from horus_file_system import get_horus_fs

# Auto-detect best access method
fs = get_horus_fs()
print(f"Access mode: {fs.access_mode}")  # "ssh" or "local"
print(f"Project root: {fs.project_root}")
```

**Detection Priority:**
1. Check `PREFERRED_ACCESS_MODE` setting (default: "ssh")
2. Try SSH connection to `10.100.128.193`
3. Fall back to local mount (`V:/` or `/mnt/igloo_swa_v/`)
4. Return "none" if both fail

### 5.3 Configuration

```python
# horus_file_system.py configuration
LINUX_PROJECT_ROOT = "/mnt/igloo_swa_v"
LINUX_IMAGE_ROOT = "/mnt/igloo_swa_w"
WINDOWS_PROJECT_ROOT = "V:"
WINDOWS_IMAGE_ROOT = "W:"

SSH_HOST = "10.100.128.193"
SSH_USER = "ec2-user"
SSH_KEY_PATH = "~/.ssh/CaveTeam.pem"  # Auto-detected

PROJECT_NAME = "SWA"
SCENE_PATH = "all/scene"
HORUS_DATA_PATH = ".horus"

PREFERRED_ACCESS_MODE = "ssh"  # Force SSH for development
```

### 5.4 Performance Optimizations

**In-Memory Caching:**
```python
class HorusFileSystem:
    def __init__(self):
        self.status_cache = {}  # Sequence status cache
        self.media_cache = {}   # Media file listings
```

**Sequence-Level Status Cache:**
- Load entire sequence status once
- Cache in memory for duration of session
- Reduces file reads from O(n) to O(1) per shot

**Media Listing Cache:**
- Cache directory listings
- Refresh only when needed
- Reduces SSH round-trips

---

## 6. Status Management

### 6.1 Status Workflow

```
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐
│   wip   │───▶│ submit  │───▶│ approved │    │ on hold  │
└─────────┘    └─────────┘    └──────────┘    └──────────┘
                    │               │
                    ▼               │
               ┌──────────┐         │
               │need fix  │◀────────┘
               └──────────┘
                    │
                    ▼
               ┌─────────┐
               │   wip   │
               └─────────┘
```

### 6.2 API Usage

```python
from horus_file_system import get_horus_fs

fs = get_horus_fs()

# Get status for a specific version
status = fs.get_shot_status(
    episode="Ep01",
    sequence="sq0010",
    shot="SH0010",
    department="comp",
    version="v003"
)
print(f"Status: {status}")  # "approved"

# Set status (saves to JSON with history)
success = fs.set_shot_status(
    episode="Ep01",
    sequence="sq0010",
    shot="SH0010",
    department="comp",
    version="v003",
    status="approved"
)
```

### 6.3 Status History

Every status change is recorded with:
- **User:** From `os.environ.get('USER')` or `os.environ.get('USERNAME')`
- **Timestamp:** UTC ISO format
- **Full History:** Array of all previous status changes

**Benefits:**
- ✅ Audit trail for all status changes
- ✅ Track who approved/rejected shots
- ✅ Revert to previous status if needed
- ✅ Generate reports on review progress

---

## 7. Comments System

### 7.1 Comment Threading

Comments support nested threading with unlimited depth:

```
Comment 1 (depth 0)
├── Reply 1.1 (depth 1)
│   ├── Reply 1.1.1 (depth 2)
│   └── Reply 1.1.2 (depth 2)
└── Reply 1.2 (depth 1)
```

### 7.2 Features

- **Frame-Accurate:** Comments linked to specific frame numbers
- **User Mentions:** `@username` with autocomplete
- **Reactions:** Like, approve, reject, etc.
- **Resolve Status:** Mark comments as resolved
- **Real-Time:** WebSocket support for live collaboration (planned)

### 7.3 Annotation Storage

**Vector Annotations:** Stored as JSON coordinates
- Shapes: rectangle, circle, arrow, text
- Scalable and editable
- Small file size

**Raster Annotations:** Stored as PNG images
- Freehand drawings
- Complex annotations
- Location: `{Shot}/{Department}/annotations/{Version}/`

---

## 8. Playlist System

### 8.1 Playlist Manager

```python
from horus_playlists import get_playlist_manager

pm = get_playlist_manager()
pm.set_file_system(fs)  # Connect to file system backend

# Load all playlists
playlists = pm.load_playlists()

# Create new playlist
playlist_id = pm.create_playlist(
    name="Daily Review - Dec 17",
    created_by="supervisor.name",
    description="Animation dailies",
    playlist_type="daily_review"
)

# Add clip to playlist
pm.add_clip(
    playlist_id=playlist_id,
    clip_data={
        "name": "SH0010_comp_v003",
        "episode": "Ep01",
        "sequence": "sq0010",
        "shot": "SH0010",
        "department": "comp",
        "version": "v003",
        "file_path": "/path/to/SH0010_comp_v003.mov",
        "status": "approved"
    }
)

# Save changes
pm.save_playlists()
```

### 8.2 OTIO Integration

Playlists can be exported to OpenTimelineIO format for use in other applications:

```python
from horus_playlists import get_playlist_manager
import opentimelineio as otio

pm = get_playlist_manager()
playlist = pm.get_playlist(playlist_id)

# Convert to OTIO timeline
timeline = otio.schema.Timeline(name=playlist['name'])

for clip in playlist['clips']:
    otio_clip = otio.schema.Clip(
        name=clip['name'],
        media_reference=otio.schema.ExternalReference(
            target_url=clip['file_path']
        )
    )
    timeline.video_tracks()[0].append(otio_clip)

# Export as EDL
otio.adapters.write_to_file(timeline, "output.edl")
```

### 8.3 Playlist Operations

**CRUD Operations:**
- `create_playlist()` - Create new playlist
- `get_playlist()` - Retrieve playlist by ID
- `update_playlist()` - Update playlist properties
- `delete_playlist()` - Delete playlist

**Clip Operations:**
- `add_clip()` - Add clip to playlist
- `remove_clip()` - Remove clip from playlist
- `reorder_clips()` - Change clip order
- `update_clip()` - Update clip properties

---

## 9. UI Components

### 9.1 Navigator Widget (Media Browser)

**Features:**
- Episode/Sequence/Shot hierarchy browser
- Department and version filtering
- Status dropdown for each version
- Search and filter capabilities
- Thumbnail preview
- Double-click to load in RV

**Table Columns:**
1. **Name:** `{Episode}_{Shot}` format (e.g., "Ep01_SH0010")
2. **Department:** comp, lighting, anim, fx, etc.
3. **Version:** v001, v002, v003, etc.
4. **Status:** Dropdown (wip, approved, submit, need fix, on hold)

**Context Menu:**
- Add to Playlist
- Load in RV
- Show Comments
- Refresh

### 9.2 Timeline Widget (Playlist Editor)

**Features:**
- Playlist selection dropdown with autocomplete
- Timeline table showing clips
- Status management per clip
- Drag-and-drop reordering (planned)
- Export to EDL/OTIO

**Table Columns:**
1. **Name:** `{Episode}_{Shot}` format
2. **Department:** Department name
3. **Version:** Version number
4. **Status:** Dropdown (same as Navigator)

**Context Menu:**
- Remove from Playlist
- Create New Playlist with Selection
- Add to Another Playlist
- Load in RV

### 9.3 Comments Widget (Review Feedback)

**Features:**
- Frame-accurate comments
- Threaded conversations
- User mentions (@username)
- Reactions (like, approve, reject)
- Annotation tools (rectangle, circle, arrow, text, freehand)
- Resolve/unresolve comments

**UI Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ 💬 Comments (23)                    [Sort: Latest ▼]   │
├─────────────────────────────────────────────────────────┤
│ 👤 John Doe • 2 hours ago • Frame 45                    │
│    The lighting in this shot looks great!               │
│    👍 5  💬 Reply  ✅ Resolve                          │
│    │                                                    │
│    ├─ 👤 Jane Smith • 1 hour ago                       │
│    │     @john.doe Agreed! Color temp is perfect.      │
│    │     👍 2  💬 Reply                                 │
│    │                                                    │
│    └─ 👤 Mike Wilson • 30 min ago                      │
│          Can we get a version without the rim light?   │
│          👍 1  💬 Reply                                 │
├─────────────────────────────────────────────────────────┤
│ 💭 Add a comment...                        [📎] [😊]   │
└─────────────────────────────────────────────────────────┘
```

---

## 10. API Reference

### 10.1 HorusFileSystem

**Initialization:**
```python
from horus_file_system import get_horus_fs

fs = get_horus_fs()  # Singleton instance with auto-detection
```

**Directory Listing:**
```python
# List episodes
episodes = fs.list_episodes()
# Returns: [{"name": "Ep01", "path": "..."}, ...]

# List sequences in episode
sequences = fs.list_sequences("Ep01")

# List shots in sequence
shots = fs.list_shots("Ep01", "sq0010")

# List media files
media = fs.list_media("Ep01", "sq0010", "SH0010", "comp")
# Returns: [{"name": "SH0010_comp_v003.mov", "version": "v003", ...}, ...]
```

**Status Management:**
```python
# Get status
status = fs.get_shot_status("Ep01", "sq0010", "SH0010", "comp", "v003")

# Set status
success = fs.set_shot_status("Ep01", "sq0010", "SH0010", "comp", "v003", "approved")
```

**Comments:**
```python
# Load comments
comments = fs.load_shot_comments("Ep01", "sq0010", "SH0010")

# Save comments
success = fs.save_shot_comments("Ep01", "sq0010", "SH0010", comments_data)
```

**Playlists:**
```python
# Load playlists
playlists = fs.load_playlists()

# Save playlists
success = fs.save_playlists(playlists_data)
```

### 10.2 HorusPlaylistManager

**Initialization:**
```python
from horus_playlists import get_playlist_manager

pm = get_playlist_manager()  # Singleton instance
pm.set_file_system(fs)       # Connect to file system
```

**Playlist CRUD:**
```python
# Create
playlist_id = pm.create_playlist(name, created_by, description, playlist_type)

# Read
playlist = pm.get_playlist(playlist_id)
all_playlists = pm.load_playlists()

# Update
pm.update_playlist(playlist_id, {"name": "New Name"})

# Delete
pm.delete_playlist(playlist_id)
```

**Clip Operations:**
```python
# Add clip
pm.add_clip(playlist_id, clip_data)

# Remove clip
pm.remove_clip(playlist_id, clip_id)

# Reorder clips
pm.reorder_clips(playlist_id, [clip_id_1, clip_id_2, clip_id_3])

# Update clip
pm.update_clip(playlist_id, clip_id, {"status": "approved"})
```

### 10.3 Version Management

```python
from horus_version import VersionManager

vm = VersionManager()

# Get version string
version = vm.get_version_string()  # "0.1.0-dev+20251217.abc123"

# Bump version
vm.bump_patch()  # 0.1.0 -> 0.1.1
vm.bump_minor()  # 0.1.1 -> 0.2.0
vm.bump_major()  # 0.2.0 -> 1.0.0

# Set prerelease
vm.set_prerelease("beta.1")  # 1.0.0-beta.1

# Get version info
info = vm.get_version_info()
# Returns: {"major": 1, "minor": 0, "patch": 0, "prerelease": "beta.1", ...}
```

---

## Appendix A: File Paths Quick Reference

| Data Type | Path Template | Example |
|-----------|---------------|---------|
| **Status Cache** | `{Episode}/.horus/status/{Sequence}_status.json` | `Ep01/.horus/status/sq0010_status.json` |
| **Comments** | `{Episode}/{Sequence}/{Shot}/.horus/{Shot}_comments.json` | `Ep01/sq0010/SH0010/.horus/SH0010_comments.json` |
| **Playlists** | `.horus/playlists.json` | `/mnt/igloo_swa_v/SWA/all/scene/.horus/playlists.json` |
| **Media Files** | `{Episode}/{Sequence}/{Shot}/{Dept}/output/{Shot}_{Dept}_{Version}.mov` | `Ep01/sq0010/SH0010/comp/output/SH0010_comp_v003.mov` |
| **Annotations** | `{Episode}/{Sequence}/{Shot}/{Dept}/annotations/{Version}/{Shot}_{Dept}_{Version}.{Frame}.png` | `Ep01/sq0010/SH0010/comp/annotations/v003/SH0010_comp_v003.0045.png` |

---

## Appendix B: Status Values

| Status | Description | Color | Typical Use |
|--------|-------------|-------|-------------|
| **wip** | Work in progress | Gray | Default for new shots, artist working |
| **submit** | Submitted for review | Yellow | Ready for supervisor review |
| **approved** | Approved for final | Green | Approved by supervisor, ready for delivery |
| **need fix** | Requires changes | Red | Supervisor requested changes |
| **on hold** | Temporarily paused | Orange | Waiting for assets, blocked, etc. |

---

**End of Documentation**


