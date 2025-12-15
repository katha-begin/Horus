# Horus Implementation Plan V2
## Based on Real Server Directory Structure

**Date:** 2025-12-15  
**Status:** Planning Phase  
**Server:** ec2-user@10.100.128.193  

---

## 🎯 **Revised Architecture**

### **Data Source: File System (Not Database)**
- ✅ **Direct file system scanning** of network mount points
- ✅ **JSON metadata files** for shot information (already exists!)
- ✅ **Separate JSON files** for comments and playlists (to be created)
- ❌ **No database** for POC phase

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

### **2. Comments Storage (New - JSON)**
**Location:** `/mnt/igloo_swa_v/SWA/.horus/comments/{Episode}.json`

**Example:** `/mnt/igloo_swa_v/SWA/.horus/comments/Ep02.json`

**Why Single File Per Episode:**
- ✅ Better performance (one file read instead of hundreds)
- ✅ Centralized on server (no local storage issues)
- ✅ Easier backup and version control
- ✅ Faster filtering (all episode comments in one place)

**Structure:**
```json
{
  "episode": "Ep02",
  "shots": [
    {
      "sequence": "sq0010",
      "shot": "SH0010",
      "department": "comp",
      "version": "v007",
      "media_file": "/mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0010/comp/output/Ep02_sq0010_SH0010_v007.mov",
      "annotation_file": "/mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0010/comp/annotations/Ep02_sq0010_SH0010_comp_v007_annotations.json",
      "shot_status": "submit",
      "comments": [
        {
          "comment_id": "comment_001",
          "author": "director.smith",
          "text": "Great work! Approved.",
          "frame_number": 1015,
          "timestamp": "2025-12-15T10:30:00Z",
          "priority": "high",
          "replies": [
            {
              "reply_id": "reply_001",
              "author": "artist.john",
              "text": "Thanks! Will address the notes.",
              "timestamp": "2025-12-15T11:00:00Z"
            }
          ]
        }
      ]
    },
    {
      "sequence": "sq0010",
      "shot": "SH0020",
      "department": "comp",
      "version": "v004",
      "media_file": "/mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0020/comp/output/Ep02_sq0010_SH0020_v004.mov",
      "annotation_file": "/mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0020/comp/annotations/Ep02_sq0010_SH0020_comp_v004_annotations.json",
      "shot_status": "approved",
      "comments": []
    }
  ]
}
```

**Shot Status Values (3 States Only):**
- `"submit"` - Shot submitted for review
- `"need fix"` - Requires changes
- `"approved"` - Approved for final

---

### **3. Playlists Storage (New - JSON)**
**Location:** `/mnt/igloo_swa_v/SWA/.horus/playlists/{playlist_name}.json`

**Example:** `/mnt/igloo_swa_v/SWA/.horus/playlists/daily_review_2025-12-15.json`

**Why Under Project Root:**
- ✅ Shared across all users on network
- ✅ Centralized storage
- ✅ No sync issues between machines

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
      "file_path": "/mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0010/comp/output/Ep02_sq0010_SH0010_v007.mov",
      "annotation_file": "/mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0010/comp/annotations/Ep02_sq0010_SH0010_comp_v007_annotations.json",
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
      "file_path": "/mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0020/comp/output/Ep02_sq0010_SH0020_v004.mov",
      "annotation_file": "/mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0020/comp/annotations/Ep02_sq0010_SH0020_comp_v004_annotations.json",
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

### **Phase 3: Comments System (Week 3)**

#### **Task 3.1: Create CommentManager Class**
```python
class CommentManager:
    """Manage comments and annotations."""

    def __init__(self, comment_dir="~/.horus/projects/SWA/comments/"):
        self.comment_dir = comment_dir

    def add_comment(self, media_file, author, text, frame_number, priority="low"):
        """Add new comment."""
        pass

    def add_reply(self, comment_id, author, text):
        """Add reply to comment."""
        pass

    def get_comments_for_media(self, media_file):
        """Get all comments for media file."""
        pass

    def filter_comments(self, episode=None, sequence=None, shot=None,
                       department=None, author=None, status=None):
        """Filter comments by criteria."""
        pass

    def sort_comments(self, comments, sort_by="timestamp", reverse=False):
        """Sort comments."""
        pass

    def update_comment_status(self, comment_id, status):
        """Update comment status (open, resolved)."""
        pass
```

#### **Task 3.2: Update Comments Widget**
- Implement reply functionality
- Add filter dropdowns (episode, author, status)
- Add sort dropdown (timestamp, frame, priority)
- Add user mention autocomplete
- Add status update buttons

---

## 📊 **Filtering & Sorting Implementation**

### **Filter Comments by Episode:**
```python
def filter_comments_by_episode(episode_id="Ep02"):
    """Get all comments for an episode."""
    comment_dir = "~/.horus/projects/SWA/comments/"
    all_comments = []

    for file in os.listdir(comment_dir):
        if file.startswith(episode_id):
            with open(os.path.join(comment_dir, file)) as f:
                data = json.load(f)
                all_comments.extend(data["comments"])

    return all_comments
```

### **Sort Comments:**
```python
def sort_comments(comments, sort_by="timestamp"):
    """Sort comments by various criteria."""
    sort_keys = {
        "timestamp": lambda c: c["timestamp"],
        "frame": lambda c: c["frame_number"],
        "priority": lambda c: {"high": 3, "medium": 2, "low": 1}[c["priority"]],
        "author": lambda c: c["author"]
    }
    return sorted(comments, key=sort_keys[sort_by])
```

---

## 🚀 **Next Steps**

1. ✅ **Review this plan** - Confirm approach with team
2. ⏳ **Phase 1** - Implement FileSystemScanner and File Navigator
3. ⏳ **Phase 2** - Implement PlaylistManager and Playlist Widget
4. ⏳ **Phase 3** - Implement CommentManager and Comments Widget
5. ⏳ **Testing** - Test with real server data
6. ⏳ **Deployment** - Deploy to production


