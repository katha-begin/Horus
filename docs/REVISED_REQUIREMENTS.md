# Revised Requirements - Horus VFX Review Application
## Based on User Feedback - 2025-12-15

**Status:** ✅ Requirements Finalized - Ready for Implementation  

---

## 📁 **Storage Location Changes**

### **✅ Store Under Project Root (Not Local ~/.horus/)**

**Why This is Better:**
- ✅ **Faster Performance** - No network latency for metadata access
- ✅ **Centralized Storage** - All users access same data
- ✅ **No Sync Issues** - Single source of truth
- ✅ **Easier Backup** - Part of project backup strategy

### **New Storage Paths:**

#### **Comments:**
```
/mnt/igloo_swa_v/SWA/.horus/comments/{Episode}.json
```
**Examples:**
- `/mnt/igloo_swa_v/SWA/.horus/comments/Ep01.json`
- `/mnt/igloo_swa_v/SWA/.horus/comments/Ep02.json`
- `/mnt/igloo_swa_v/SWA/.horus/comments/Ep03.json`

**Single File Per Episode Benefits:**
- One file read instead of hundreds
- Faster filtering (all episode data in one place)
- Easier to manage and backup

#### **Playlists:**
```
/mnt/igloo_swa_v/SWA/.horus/playlists/{playlist_name}.json
```
**Examples:**
- `/mnt/igloo_swa_v/SWA/.horus/playlists/daily_review_2025-12-15.json`
- `/mnt/igloo_swa_v/SWA/.horus/playlists/weekly_review_ep02.json`
- `/mnt/igloo_swa_v/SWA/.horus/playlists/director_review.json`

---

## 🎯 **Shot Status - 3 States Only**

### **Status Values:**
1. **`"submit"`** - Shot submitted for review (Yellow badge)
2. **`"need fix"`** - Requires changes (Red badge)
3. **`"approved"`** - Approved for final (Green badge)

**No other status values allowed!**

---

## 📊 **Comment Structure with Annotation File Path**

### **Episode Comment File Structure:**
```json
{
  "episode": "Ep02",
  "last_updated": "2025-12-15T14:30:00Z",
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
          "comment_id": "c001",
          "author": "director.smith",
          "text": "Great work! Lighting looks perfect.",
          "frame_number": 1015,
          "timestamp": "2025-12-15T10:30:00Z",
          "priority": "high",
          "replies": [
            {
              "reply_id": "r001",
              "author": "artist.john",
              "text": "Thanks! Will address the shadow issue.",
              "timestamp": "2025-12-15T11:00:00Z"
            }
          ]
        }
      ]
    }
  ]
}
```

**Key Fields:**
- ✅ `annotation_file` - Path to annotation file (for visual annotations)
- ✅ `shot_status` - One of: "submit", "need fix", "approved"
- ✅ `media_file` - Path to movie or image sequence
- ✅ `comments` - Array of comments with replies

---

## 🗂️ **File Navigator - CURRENT DESIGN (DO NOT CHANGE)**

### **Current Design: Dropdown Filters + Table**

**CURRENT TABLE COLUMNS (Keep as-is):**
| Thumbnail | Task Entity | Name | Version | Status | Created |
|-----------|-------------|------|---------|--------|---------|
| 🎬 | SH0010 | Ep02_sq0010_SH0010_comp | v007 | ✓ | 2025-12-15 |
| 🎬 | SH0010 | Ep02_sq0010_SH0010_comp | v006 | ⏳ | 2025-12-14 |
| 🎬 | SH0020 | Ep02_sq0010_SH0020_comp | v004 | ✓ | 2025-12-13 |

**CURRENT FILTER LAYOUT (Keep as-is):**
```
Department: [All ▼]        Episode: [Ep02 ▼]
Sequence: [sq0010 ▼]       Shot: [All ▼]
Status: [All ▼]
```

### **Features (CURRENT - Keep as-is):**

#### **1. Sorting (Already Implemented):**
- ✅ Click table headers to sort
- ✅ `media_table.setSortingEnabled(True)` already in code
- Columns: Thumbnail, Task Entity, Name, Version, Status, Created

#### **2. Refresh Button (Already Implemented):**
- ✅ [Refresh] button already exists
- ✅ Connected to `refresh_horus_btn`

#### **3. Filter Dropdowns (Already Implemented):**
- ✅ **Department:** [All ▼] → animation, lighting, compositing, fx, modeling, rigging
- ✅ **Episode:** [All ▼] → Ep00, Ep01, Ep02
- ✅ **Sequence:** [All ▼] → sq0010, sq0020, sq0030, sq0040, sq0050
- ✅ **Shot:** [All ▼] → (populated dynamically)
- ✅ **Status:** [All ▼] → pending, under_review, approved

**NEED TO UPDATE:**
- Change status values to: "submit", "need fix", "approved"
- Populate Episode dropdown from server scan
- Populate Sequence dropdown from server scan
- Populate Shot dropdown from server scan

#### **4. Scale Control (Already Implemented):**
- ✅ Scale: [Small ▼] [Medium] [Large]
- ✅ Adjusts thumbnail size and row height

#### **5. Search Input (Already Implemented):**
- ✅ Search box with placeholder "Search files..."
- ✅ Connected to filter function

#### **6. Double-Click Behavior (Already Implemented):**
- ✅ `media_table.itemDoubleClicked.connect(on_media_table_double_click)`
- ✅ Loads media in RV

#### **7. Right-Click Context Menu (NEED TO ADD):**
```
┌─────────────────────────────────┐
│ ▶ Open Movie (.mov)             │
│ ▶ Open Image Sequence (.exr)    │
│ ─────────────────────────────── │
│ ➕ Add to Playlist               │
│ 📁 Show in File System           │
│ 📋 Copy Path                     │
└─────────────────────────────────┘
```

**Menu Logic:**
- "Open Movie (.mov)" - Only enabled if .mov file exists
- "Open Image Sequence (.exr)" - Only enabled if .exr sequence exists
- If both exist, show both options
- If only one exists, that option is default on double-click

---

## 🔄 **Cascade Scanning (Not Brute Force)**

### **Principle: Load on Demand**

**Initial Load:**
```
User opens Horus
    ↓
Load Episode list ONLY (Ep01, Ep02, Ep03, Ep04)
    ↓
Display in filter dropdown
```

**User Selects Episode:**
```
User selects "Ep02" from filter
    ↓
Scan sequences for Ep02 ONLY (sq0010, sq0020, etc.)
    ↓
Display in filter dropdown
```

**User Selects Sequence:**
```
User selects "sq0010" from filter
    ↓
Scan shots for Ep02/sq0010 ONLY (SH0010, SH0020, etc.)
    ↓
Display in table
```

**User Selects Shot:**
```
User clicks on SH0010 row
    ↓
Load shot metadata from .json file
    ↓
Scan departments and versions
    ↓
Display in table
```

**Benefits:**
- ✅ Fast initial load (<1 second)
- ✅ No unnecessary file system operations
- ✅ Responsive UI (no lag)
- ✅ Scales to thousands of shots

---

## 🎬 **Opening Media Files**

### **Right-Click Context Menu Options:**

#### **Option 1: Open Movie (.mov)**
```python
def open_movie(media_file):
    """Load .mov file in Open RV."""
    movie_path = media_file["file_path"]
    # Example: /mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0010/comp/output/Ep02_sq0010_SH0010_v007.mov

    rv.commands.addSource(movie_path)
    rv.commands.play()
```

#### **Option 2: Open Image Sequence (.exr)**
```python
def open_image_sequence(media_file):
    """Load .exr image sequence in Open RV."""
    episode = media_file["episode"]
    sequence = media_file["sequence"]
    shot = media_file["shot"]
    department = media_file["department"]
    version = media_file["version"]

    # Build image sequence path
    image_seq_dir = f"/mnt/igloo_swa_w/SWA/all/scene/{episode}/{sequence}/{shot}/{department}/version/{version}/"

    # Find first frame
    # Example: Ep02_sq0010_SH0010.1001.exr
    first_frame = f"{episode}_{sequence}_{shot}.1001.exr"
    image_seq_path = os.path.join(image_seq_dir, first_frame)

    # Load in RV with frame range
    rv.commands.addSource(image_seq_path)
    rv.commands.play()
```

### **Menu Availability Logic:**
```python
def build_context_menu(media_file):
    """Build context menu based on available media."""
    menu_items = []

    # Check if movie exists
    if media_file["has_movie"]:
        menu_items.append({
            "label": "▶ Open Movie (.mov)",
            "action": lambda: open_movie(media_file),
            "enabled": True
        })

    # Check if image sequence exists
    if media_file["has_image_seq"]:
        menu_items.append({
            "label": "▶ Open Image Sequence (.exr)",
            "action": lambda: open_image_sequence(media_file),
            "enabled": True
        })

    # Separator
    menu_items.append({"separator": True})

    # Always available
    menu_items.append({
        "label": "➕ Add to Playlist",
        "action": lambda: add_to_playlist(media_file),
        "enabled": True
    })

    return menu_items
```

---

## 📋 **Playlist Structure with Annotation File Path**

### **Playlist File Structure:**
```json
{
  "playlist_id": "playlist_001",
  "name": "Daily Review - Dec 15, 2025",
  "created_by": "supervisor.jane",
  "created_at": "2025-12-15T09:00:00Z",
  "updated_at": "2025-12-15T14:30:00Z",
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
      "image_seq_path": "/mnt/igloo_swa_w/SWA/all/scene/Ep02/sq0010/SH0010/comp/version/v007/",
      "frame_range": [1001, 1043],
      "comment_count": 3,
      "shot_status": "submit",
      "added_at": "2025-12-15T09:15:00Z"
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
      "image_seq_path": null,
      "frame_range": [1001, 1089],
      "comment_count": 1,
      "shot_status": "approved",
      "added_at": "2025-12-15T09:20:00Z"
    }
  ]
}
```

**Key Fields:**
- ✅ `annotation_file` - Path to annotation file
- ✅ `image_seq_path` - Path to image sequence (null if not available)
- ✅ `shot_status` - One of: "submit", "need fix", "approved"
- ✅ `comment_count` - Number of comments for this shot

---

## ✅ **Summary of Changes**

### **Storage Location:**
- ❌ OLD: `~/.horus/projects/SWA/comments/`
- ✅ NEW: `/mnt/igloo_swa_v/SWA/.horus/comments/`

### **Comment File Structure:**
- ❌ OLD: One file per shot/version
- ✅ NEW: One file per episode (all shots in one file)

### **Shot Status:**
- ❌ OLD: "open", "pending", "resolved", etc.
- ✅ NEW: "submit", "need fix", "approved" (3 states only)

### **File Navigator:**
- ❌ OLD: Tree view
- ✅ NEW: Table view with sorting, pagination, refresh

### **Scanning Strategy:**
- ❌ OLD: Brute force scan entire structure
- ✅ NEW: Cascade scan (load on demand)

### **Context Menu:**
- ✅ NEW: "Open Movie (.mov)" option
- ✅ NEW: "Open Image Sequence (.exr)" option
- ✅ NEW: Smart menu (only show available options)

### **Data Structure:**
- ✅ NEW: `annotation_file` field in all structures
- ✅ NEW: `image_seq_path` field for image sequences
- ✅ NEW: `shot_status` field (3 states)

---

## 🚀 **Ready for Implementation**

All requirements are now finalized and documented. Ready to start Phase 1 implementation!


