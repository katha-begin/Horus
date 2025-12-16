# Horus Implementation Plan V2
## Based on Real Server Directory Structure

**Date:** 2025-12-16
**Status:** Implementation Phase
**Server:** ec2-user@10.100.128.193

---

## 🎯 **Revised Architecture**

### **Data Source: File System (Not Database)**
- ✅ **Direct file system scanning** of network mount points
- ✅ **JSON metadata files** for shot information (already exists!)
- ✅ **Separate JSON files** for comments (IMPLEMENTED!)
- ✅ **Playlists** (to be created)
- ❌ **No database** for POC phase

### **Implementation Status:**
- ✅ `horus_file_system.py` - File system backend (SSH/Local)
- ✅ `horus_comments.py` - Comment backend with threaded replies
- ✅ `rv_horus_integration.py` - UI integration with comment loading/saving

### **Mount Points:**
```python
PROJECT_ROOT = "/mnt/igloo_swa_v/"  # Movies (.mov)
IMAGE_ROOT = "/mnt/igloo_swa_w/"    # Image sequences (.exr)
```

---

## 📁 **File System Structure**

### **Directory Hierarchy:**
```
{PROJECT_ROOT}/SWA/all/scene/
├── {Episode}/              # Ep01, Ep02, Ep03, Ep04
│   ├── {Sequence}/         # sq0010, sq0020, etc.
│   │   ├── {Shot}/         # SH0010, SH0020, etc.
│   │   │   ├── .{Episode}_{Sequence}_{Shot}.json  # Shot metadata (EXISTS!)
│   │   │   ├── {Department}/                      # anim, comp, lighting, etc.
│   │   │   │   ├── output/                        # Movie files (.mov)
│   │   │   │   └── version/                       # Work files (.nk, .ma)
```

### **Image Sequences:**
```
{IMAGE_ROOT}/SWA/all/scene/
├── {Episode}/
│   ├── {Sequence}/
│   │   ├── {Shot}/
│   │   │   ├── {Department}/
│   │   │   │   └── version/
│   │   │   │       └── {version}/  # v001, v002, etc.
│   │   │   │           └── *.exr   # Frame sequences
```

---

## 🗂️ **Data Storage Strategy**

### **1. Shot Metadata (Already Exists!)**
**Location:** `{PROJECT_ROOT}/SWA/all/scene/{Episode}/{Sequence}/{Shot}/.{Episode}_{Sequence}_{Shot}.json`

**Example:** `.Ep02_sq0010_SH0010.json`

**Contains:**
- Episode, Sequence, Shot identifiers
- Frame range (start_frame, end_frame, frame_count)
- Version information
- Maya scene file paths
- Timeline settings

**Action:** ✅ **Use existing files** - No changes needed!

---

### **2. Comments Storage (Per-Shot JSON)**
**Location:** `{PROJECT_ROOT}/SWA/all/scene/{Episode}/{Sequence}/{Shot}/.horus/{Shot}_comments.json`

**Example:** `/mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0010/.horus/SH0010_comments.json`

**Why Per-Shot Storage:**
- ✅ Comments stored with shot data (logical grouping)
- ✅ Easy to find comments for specific shot
- ✅ No need to load entire episode data
- ✅ Better for concurrent access (multiple users reviewing different shots)

**Structure:**
```json
{
  "version": "1.0",
  "shot_info": {
    "episode": "Ep02",
    "sequence": "sq0010",
    "shot": "SH0010"
  },
  "comments": [
    {
      "id": "uuid-comment-001",
      "parent_id": null,
      "media_file": "SH0010_comp_v007.mov",
      "department": "comp",
      "media_version": "v007",
      "user": "director.smith",
      "user_display": "Director Smith",
      "avatar": "DS",
      "text": "Great work! The lighting looks perfect.",
      "frame": 1015,
      "timestamp": "2025-12-15T10:30:00Z",
      "updated_at": "2025-12-15T10:30:00Z",
      "likes": 3,
      "liked_by": ["artist.john", "supervisor.jane"],
      "status": "open",
      "priority": "high",
      "annotation_id": null,
      "replies": [
        {
          "id": "uuid-reply-001",
          "parent_id": "uuid-comment-001",
          "user": "artist.john",
          "user_display": "Artist John",
          "avatar": "AJ",
          "text": "@director.smith Thanks! Will address the rim light notes.",
          "timestamp": "2025-12-15T11:00:00Z",
          "likes": 1,
          "liked_by": ["director.smith"],
          "replies": [
            {
              "id": "uuid-reply-002",
              "parent_id": "uuid-reply-001",
              "user": "supervisor.jane",
              "user_display": "Supervisor Jane",
              "avatar": "SJ",
              "text": "Let me know if you need help with the color grading.",
              "timestamp": "2025-12-15T11:30:00Z",
              "likes": 0,
              "liked_by": [],
              "replies": []
            }
          ]
        }
      ]
    }
  ]
}
```

**Shot Status Values (3 States Only):**
- `"submit"` - Shot submitted for review
- `"need fix"` - Requires changes
- `"approved"` - Approved for final

---

### **3. Annotations Storage (Per-Version Images)**
**Location:** `{PROJECT_ROOT}/SWA/all/scene/{Episode}/{Sequence}/{Shot}/{Department}/annotations/{Version}/{filename}.{frame}.png`

**Example:** `/mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0010/comp/annotations/v007/SH0010_comp_v007.0045.png`

**Why This Location:**
- ✅ Annotations stored alongside media files
- ✅ Version-specific annotations (different versions have different notes)
- ✅ Easy to archive/backup with shot data
- ✅ Clear file naming convention matching media files

**Annotation Metadata (stored in comments JSON):**
```json
{
  "id": "uuid-annotation-001",
  "comment_id": "uuid-comment-001",
  "media_file": "SH0010_comp_v007.mov",
  "frame": 45,
  "type": "paint",
  "image_path": "comp/annotations/v007/SH0010_comp_v007.0045.png",
  "user": "director.smith",
  "timestamp": "2025-12-15T10:30:00Z"
}
```

**Directory Structure Example:**
```
{PROJECT_ROOT}/SWA/all/scene/Ep02/sq0010/SH0010/
├── .horus/
│   └── SH0010_comments.json          # Shot comments
├── comp/
│   ├── output/
│   │   ├── SH0010_comp_v006.mov
│   │   └── SH0010_comp_v007.mov
│   └── annotations/                   # Annotation images
│       ├── v006/
│       │   └── SH0010_comp_v006.0030.png
│       └── v007/
│           ├── SH0010_comp_v007.0045.png
│           └── SH0010_comp_v007.0078.png
├── lighting/
│   ├── output/
│   │   └── SH0010_lighting_v003.mov
│   └── annotations/
│       └── v003/
│           └── SH0010_lighting_v003.0012.png
```

---

### **4. Playlists Storage (New - JSON)**
**Location:** `/mnt/igloo_swa_v/SWA/all/scene/.horus/playlists.json`

**Why Under `all/scene/`:**
- ✅ Has write permissions (777) for all users
- ✅ Shared across all users on network
- ✅ Centralized storage - single file for all playlists
- ✅ No sync issues between machines
- ✅ Works via SSH from Windows development machines

**Structure:**
```json
{
  "playlist_id": "playlist_001",
  "name": "Daily Review - Dec 15, 2025",
  "created_by": "supervisor.jane",
  "created_at": "2025-12-15T09:00:00Z",
  "description": "Daily review for Ep02 comp shots",
  "clips": [
    {
      "clip_id": "clip_001",
      "episode": "Ep02",
      "sequence": "sq0010",
      "shot": "SH0010",
      "department": "comp",
      "version": "v007",
      "file_path": "/mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0010/comp/output/SH0010_comp_v007.mov",
      "frame_range": [1001, 1043],
      "comment_count": 3,
      "shot_status": "submit"
    },
    {
      "clip_id": "clip_002",
      "episode": "Ep02",
      "sequence": "sq0010",
      "shot": "SH0020",
      "department": "comp",
      "version": "v004",
      "file_path": "/mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0020/comp/output/SH0010_comp_v004.mov",
      "frame_range": [1001, 1089],
      "comment_count": 1,
      "shot_status": "approved"
    }
  ]
}
```

---

## 🔍 **File Discovery & Filtering (Cascade Scanning)**

### **Cascade Scanning Strategy (Not Brute Force):**

**Principle:** Only scan when user navigates/expands, not entire structure at once

#### **1. Episode-Level Scan (Initial Load):**
```python
def scan_episodes(project_root="/mnt/igloo_swa_v/SWA/all/scene/"):
    """Scan for all episodes - FAST, only top level."""
    episodes = []
    for item in os.listdir(project_root):
        if item.startswith("Ep") or item.startswith("RD"):
            episodes.append({
                "name": item,
                "path": os.path.join(project_root, item),
                "type": "episode"
            })
    return sorted(episodes, key=lambda x: x["name"])
```

#### **2. Sequence-Level Scan (On Episode Selection):**
```python
def scan_sequences(episode="Ep02"):
    """Scan sequences ONLY when user selects episode."""
    path = f"/mnt/igloo_swa_v/SWA/all/scene/{episode}/"
    sequences = []
    for item in os.listdir(path):
        if item.startswith("sq"):
            sequences.append({
                "name": item,
                "episode": episode,
                "path": os.path.join(path, item),
                "type": "sequence"
            })
    return sorted(sequences, key=lambda x: x["name"])
```

#### **3. Shot-Level Scan (On Sequence Selection):**
```python
def scan_shots(episode="Ep02", sequence="sq0010"):
    """Scan shots ONLY when user selects sequence."""
    path = f"/mnt/igloo_swa_v/SWA/all/scene/{episode}/{sequence}/"
    shots = []
    for item in os.listdir(path):
        if item.startswith("SH"):
            # Load shot metadata if exists
            metadata_file = os.path.join(path, item, f".{episode}_{sequence}_{item}.json")
            metadata = {}
            if os.path.exists(metadata_file):
                with open(metadata_file) as f:
                    metadata = json.load(f)

            shots.append({
                "name": item,
                "episode": episode,
                "sequence": sequence,
                "path": os.path.join(path, item),
                "type": "shot",
                "metadata": metadata
            })
    return sorted(shots, key=lambda x: x["name"])
```

#### **4. Media File Discovery (On Shot Selection):**
```python
def find_media_files(episode, sequence, shot, department="comp"):
    """Find media files ONLY when user selects shot/department."""
    output_path = f"/mnt/igloo_swa_v/SWA/all/scene/{episode}/{sequence}/{shot}/{department}/output/"

    if not os.path.exists(output_path):
        return []

    media_files = []
    for file in os.listdir(output_path):
        if file.endswith(".mov"):
            version = extract_version_from_filename(file)
            file_full_path = os.path.join(output_path, file)

            # Check for image sequence alternative
            image_seq_path = f"/mnt/igloo_swa_w/SWA/all/scene/{episode}/{sequence}/{shot}/{department}/version/{version}/"
            has_image_seq = os.path.exists(image_seq_path)

            media_files.append({
                "file_name": file,
                "file_path": file_full_path,
                "episode": episode,
                "sequence": sequence,
                "shot": shot,
                "department": department,
                "version": version,
                "file_size": os.path.getsize(file_full_path),
                "modified_time": os.path.getmtime(file_full_path),
                "has_movie": True,
                "has_image_seq": has_image_seq,
                "image_seq_path": image_seq_path if has_image_seq else None
            })

    return sorted(media_files, key=lambda x: x["version"], reverse=True)
```

---

## 🎨 **UI Components (Keep Current Design)**

### **Widget 1: File Navigator (Left Panel)**
**Purpose:** Browse file system hierarchy

**UI Type:** **Table View (Not Tree)** - Keep current design

**Features:**
- ✅ **Table columns:** Episode | Sequence | Shot | Department | Version | Status | Modified Date | Size
- ✅ **Sorting:** Click column headers to sort (ascending/descending)
- ✅ **Pagination:** 50-100 items per page with page controls
- ✅ **Refresh button:** Reload current view
- ✅ **Filter dropdowns:** Episode, Sequence, Department, Status
- ✅ **Right-click context menu:**
  - "Open Movie (.mov)" - Load .mov file in RV
  - "Open Image Sequence (.exr)" - Load .exr sequence in RV
  - "Add to Playlist"
  - "Show in File System"
- ✅ **Double-click:** Load default (movie if available, else image sequence)
- ✅ **Status indicator:** Color-coded badges (submit=yellow, need fix=red, approved=green)

**Data Source:** Cascade file system scan (load on demand)

---

### **Widget 2: Playlist Manager (Right Panel)**
**Purpose:** Manage review playlists

**Features:**
- ✅ Create new playlist
- ✅ Add/remove clips from playlist
- ✅ Reorder clips (drag & drop)
- ✅ Show clip metadata (episode, sequence, shot, version)
- ✅ Show comment count per clip
- ✅ Save/load playlists (JSON files)
- ✅ Export playlist to RV session

**Data Source:** JSON files in `~/.horus/projects/SWA/playlists/`

---

### **Widget 3: Comments & Annotations (Bottom Panel)**
**Purpose:** Frame-accurate comments with threading

**Features:**
- ✅ Threaded comments (Facebook/Slack style)
- ✅ Reply to comments
- ✅ Frame-accurate comments (linked to frame number)
- ✅ Filter by episode, sequence, shot, department
- ✅ Sort by: timestamp, frame, priority, author
- ✅ User mentions (@username)
- ✅ Status tracking (open, resolved)
- ✅ Priority levels (high, medium, low)

**Data Source:** JSON files in `~/.horus/projects/SWA/comments/`

---

## 🔧 **Implementation Tasks**

### **Phase 1: File System Scanner (Week 1)**

#### **Task 1.1: Create FileSystemScanner Class**
```python
class FileSystemScanner:
    """Scan SWA project file system."""

    def __init__(self, project_root, image_root):
        self.project_root = project_root
        self.image_root = image_root

    def scan_episodes(self):
        """Return list of episodes."""
        pass

    def scan_sequences(self, episode):
        """Return list of sequences for episode."""
        pass

    def scan_shots(self, episode, sequence):
        """Return list of shots for sequence."""
        pass

    def scan_departments(self, episode, sequence, shot):
        """Return list of departments for shot."""
        pass

    def find_media_files(self, episode, sequence, shot, department):
        """Return list of media files with metadata."""
        pass

    def load_shot_metadata(self, episode, sequence, shot):
        """Load .{Episode}_{Sequence}_{Shot}.json file."""
        pass
```

#### **Task 1.2: Create File Navigator Widget**
- Update existing navigation UI to use FileSystemScanner
- Implement tree view with Episode → Sequence → Shot → Department
- Add filtering by episode
- Add context menu (Add to Playlist, Load in RV)

---

### **Phase 2: Playlist Management (Week 2)**

#### **Task 2.1: Create PlaylistManager Class**
```python
class PlaylistManager:
    """Manage review playlists."""

    def __init__(self, playlist_dir="~/.horus/projects/SWA/playlists/"):
        self.playlist_dir = playlist_dir

    def create_playlist(self, name, description, created_by):
        """Create new playlist."""
        pass

    def load_playlist(self, playlist_id):
        """Load playlist from JSON file."""
        pass

    def save_playlist(self, playlist):
        """Save playlist to JSON file."""
        pass

    def add_clip(self, playlist_id, clip_data):
        """Add clip to playlist."""
        pass

    def remove_clip(self, playlist_id, clip_id):
        """Remove clip from playlist."""
        pass

    def reorder_clips(self, playlist_id, clip_order):
        """Reorder clips in playlist."""
        pass

    def get_all_playlists(self):
        """Return list of all playlists."""
        pass
```

#### **Task 2.2: Update Playlist Widget**
- Implement add/remove clips functionality
- Add drag & drop reordering
- Add save/load playlist buttons
- Show clip metadata and comment count

---

### **Phase 3: Comments & Annotations System (Week 3)**

#### **Task 3.1: Create HorusCommentManager Class**
**File:** `horus_comments.py`

```python
class HorusCommentManager:
    """Manage shot-level comments and annotations.

    Comments are stored per-shot in:
    {shot_path}/.horus/{shot}_comments.json

    Annotations are stored in:
    {shot_path}/{department}/annotations/{version}/{filename}.{frame}.png
    """

    def __init__(self, file_system_provider):
        """Initialize with file system provider (local or SSH)."""
        self.fs = file_system_provider

    # ============== Comment Path Methods ==============

    def get_comment_file_path(self, episode, sequence, shot):
        """Get path to shot's comment JSON file."""
        # Returns: {root}/SWA/all/scene/{ep}/{seq}/{shot}/.horus/{shot}_comments.json
        pass

    def get_annotation_dir(self, episode, sequence, shot, department, version):
        """Get path to annotation directory."""
        # Returns: {root}/SWA/all/scene/{ep}/{seq}/{shot}/{dept}/annotations/{version}/
        pass

    def get_annotation_file_path(self, episode, sequence, shot, department, version, frame):
        """Get path to specific annotation image."""
        # Returns: {root}/.../annotations/{version}/{shot}_{dept}_{version}.{frame:04d}.png
        pass

    # ============== Comment CRUD Methods ==============

    def load_comments(self, episode, sequence, shot):
        """Load all comments for a shot."""
        pass

    def save_comments(self, episode, sequence, shot, comments_data):
        """Save comments for a shot."""
        pass

    def add_comment(self, episode, sequence, shot, media_file, user, text,
                   frame=None, priority="medium"):
        """Add new comment to shot."""
        pass

    def add_reply(self, episode, sequence, shot, parent_id, user, text):
        """Add reply to existing comment (supports nested replies)."""
        pass

    def delete_comment(self, episode, sequence, shot, comment_id):
        """Delete comment (and all nested replies)."""
        pass

    def update_comment(self, episode, sequence, shot, comment_id,
                      text=None, status=None, priority=None):
        """Update comment properties."""
        pass

    def like_comment(self, episode, sequence, shot, comment_id, user):
        """Toggle like on comment."""
        pass

    # ============== Annotation Methods ==============

    def save_annotation_image(self, episode, sequence, shot, department,
                             version, frame, image_data):
        """Save annotation PNG image from RV Paint."""
        pass

    def get_annotation_image_path(self, episode, sequence, shot, department,
                                  version, frame):
        """Get path to annotation image if exists."""
        pass

    def list_annotations(self, episode, sequence, shot, department=None, version=None):
        """List all annotations for shot/department/version."""
        pass

    def delete_annotation(self, episode, sequence, shot, department, version, frame):
        """Delete annotation image."""
        pass

    # ============== Helper Methods ==============

    def _generate_uuid(self):
        """Generate unique ID for comment/reply."""
        pass

    def _get_user_avatar(self, username):
        """Generate avatar initials from username."""
        pass

    def _find_comment_by_id(self, comments, comment_id):
        """Recursively find comment/reply by ID in nested structure."""
        pass
```

#### **Task 3.2: Integrate with Current Comments UI**
**Do NOT redesign UI** - Only connect backend to existing widgets:

1. **Load comments when media selected:**
   - On `on_media_table_double_click()` → call `load_comments()`
   - Populate `comments_container` with loaded comments

2. **Add comment functionality:**
   - Connect `add_comment_btn` → call `add_comment()`
   - Connect `add_frame_comment_btn` → call `add_comment(frame=current_frame)`

3. **Reply functionality:**
   - Connect `post_reply_btn` → call `add_reply()`
   - Show reply input when clicking "Reply" button

4. **Like functionality:**
   - Connect like button → call `like_comment()`
   - Update like count in UI

---

## 📊 **Comment Data Flow**

### **Loading Comments:**
```
User selects media → get shot info → load_comments(ep, seq, shot)
                                          ↓
                     Read {shot_path}/.horus/{shot}_comments.json
                                          ↓
                     Parse JSON → create comment widgets → display in UI
```

### **Adding Comment:**
```
User types comment → clicks "Comment" button
                          ↓
         add_comment(ep, seq, shot, media, user, text, frame)
                          ↓
         Load existing JSON → append new comment → save JSON
                          ↓
         Refresh UI with new comment
```

### **Adding Reply (with nesting):**
```
User clicks "Reply" → types reply → clicks "Post Reply"
                          ↓
         add_reply(ep, seq, shot, parent_id, user, text)
                          ↓
         Load JSON → find parent comment → append to replies[] → save JSON
                          ↓
         Refresh UI with new reply (nested under parent)
```

---

## 🚀 **Next Steps**

1. ✅ **Phase 1** - FileSystemScanner implemented (`horus_file_system.py`)
2. ⏳ **Phase 2** - PlaylistManager (pending)
3. 🔄 **Phase 3** - CommentManager (implementing now)
   - [ ] Create `horus_comments.py` module
   - [ ] Implement `HorusCommentManager` class
   - [ ] Integrate with current UI (no UI changes)
   - [ ] Test with SSH and local modes
4. ⏳ **Testing** - Test with real server data
5. ⏳ **Deployment** - Deploy to production


