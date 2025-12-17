# ✅ CORRECTED Requirements - Horus VFX Review Application
## Based on CURRENT UI Design - 2025-12-15

**IMPORTANT:** DO NOT REDESIGN THE UI! Keep current design!

---

## 🎨 **CURRENT UI DESIGN (DO NOT CHANGE)**

### **Three-Panel Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Open RV Main Window                       │
├──────────────────────────┬──────────────────────────────────┤
│  📁 SEARCH & NAVIGATE    │   💬 COMMENTS & ANNOTATIONS      │
│  (Left Dock)             │   (Right Dock)                   │
│                          │                                   │
│  Horus Project: [SWA ▼]  │   Filter: [Ep02 ▼] [Author ▼]   │
│  [Refresh]               │   Sort: [Latest ▼]               │
│                          │                                   │
│  Search: [...]           │   👤 director.smith              │
│                          │      "Great work!"                │
│  ┌─ FILTERS ──────────┐ │      💬 Reply                    │
│  │ Department: [All ▼] │ │                                   │
│  │ Episode: [Ep02 ▼]   │ │   💭 Add comment... [✓]         │
│  │ Sequence: [sq0010▼] │ │                                   │
│  │ Shot: [All ▼]       │ │                                   │
│  │ Status: [All ▼]     │ │                                   │
│  └─────────────────────┘ │                                   │
│                          │                                   │
│  Media Files:            │                                   │
│  ┌────────────────────┐ │                                   │
│  │📷│Task│Name│Ver│✓ │ │                                   │
│  ├────────────────────┤ │                                   │
│  │🎬│SH10│comp│v07│✓│ │                                   │
│  │🎬│SH10│comp│v06│⏳│ │                                   │
│  └────────────────────┘ │                                   │
│                          │                                   │
│  Scale: [Small ▼]        │                                   │
│                          │                                   │
├──────────────────────────┴──────────────────────────────────┤
│  🎬 TIMELINE PLAYLIST MANAGER (Bottom Dock)                 │
│                                                              │
│  Playlists:              Timeline:                          │
│  ▶ Daily Review          ████ SH0010 ████ SH0020           │
│  ▶ Weekly Review         ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│                                                              │
│  [New] [Duplicate] [Rename] [Delete]  [Play] [Stop]        │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ **What to KEEP (Current Design)**

### **1. Left Panel - "Search & Navigate - Horus"**
- ✅ Horus Project dropdown
- ✅ Refresh button
- ✅ Search input box
- ✅ **Dropdown filters** (NOT tree view):
  - Department: [All ▼]
  - Episode: [All ▼]
  - Sequence: [All ▼]
  - Shot: [All ▼]
  - Status: [All ▼]
- ✅ Media table with columns:
  - Thumbnail
  - Task Entity
  - Name
  - Version
  - Status
  - Created
- ✅ Scale control: [Small ▼] [Medium] [Large]
- ✅ Sorting enabled (click headers)
- ✅ Double-click to load in RV

### **2. Right Panel - "Comments & Annotations"**
- ✅ Threaded comments (Facebook/Slack style)
- ✅ Reply functionality
- ✅ User avatars and timestamps
- ✅ Add comment input box

### **3. Bottom Panel - "Timeline Playlist Manager"**
- ✅ Playlist tree on left
- ✅ Timeline visualization on right
- ✅ Buttons: New, Duplicate, Rename, Delete, Play, Stop

---

## 🔧 **What to UPDATE (Backend Only)**

### **1. Storage Location - Move to Project Root**
```
OLD: ~/.horus/projects/SWA/comments/
NEW: /mnt/igloo_swa_v/SWA/.horus/comments/Ep02.json

OLD: ~/.horus/projects/SWA/playlists/
NEW: /mnt/igloo_swa_v/SWA/.horus/playlists/daily_review.json
```

### **2. Status Values - Change to 3 States**
```
OLD: "pending", "under_review", "approved"
NEW: "submit", "need fix", "approved"
```

### **3. Filter Dropdowns - Populate from Server**
```python
# Current (hardcoded):
episode_filter.addItems(["All", "Ep00", "Ep01", "Ep02"])

# New (from server scan):
episodes = scan_episodes()  # Returns ["Ep01", "Ep02", "Ep03", "Ep04"]
episode_filter.addItems(["All"] + episodes)
```

### **4. Media Table - Populate from Server**
```python
# Current (from sample_db JSON):
media_records = load_from_json("sample_db/media_records.json")

# New (from file system scan):
media_files = find_media_files(episode, sequence, shot, department)
populate_media_table(media_files)
```

### **5. Add Right-Click Context Menu**
```python
def show_context_menu(position):
    menu = QMenu()
    
    # Check if movie exists
    if has_movie:
        menu.addAction("▶ Open Movie (.mov)", open_movie)
    
    # Check if image sequence exists
    if has_image_seq:
        menu.addAction("▶ Open Image Sequence (.exr)", open_image_sequence)
    
    menu.addSeparator()
    menu.addAction("➕ Add to Playlist", add_to_playlist)
    menu.addAction("📁 Show in File System", show_in_filesystem)
    
    menu.exec_(media_table.viewport().mapToGlobal(position))

media_table.setContextMenuPolicy(Qt.CustomContextMenu)
media_table.customContextMenuRequested.connect(show_context_menu)
```

### **6. Add Annotation File Path to Data**
```json
{
  "media_file": "/mnt/.../Ep02_sq0010_SH0010_v007.mov",
  "annotation_file": "/mnt/.../Ep02_sq0010_SH0010_comp_v007_annotations.json",
  "shot_status": "submit"
}
```

---

## 🚀 **Implementation Tasks (Backend Only)**

### **Phase 1: File System Scanner**
1. Create `FileSystemScanner` class
2. Implement cascade scanning (episodes → sequences → shots)
3. Update filter dropdowns to use scanned data
4. Update media table to show scanned files
5. Load shot metadata from `.json` files

### **Phase 2: Context Menu**
1. Add right-click handler to media table
2. Check for .mov and .exr availability
3. Implement "Open Movie" action
4. Implement "Open Image Sequence" action
5. Implement "Add to Playlist" action

### **Phase 3: Storage Migration**
1. Create `.horus/comments/` directory on server
2. Create `.horus/playlists/` directory on server
3. Migrate comment structure to single-file-per-episode
4. Update `CommentManager` to read/write to new location
5. Update `PlaylistManager` to read/write to new location

### **Phase 4: Status Update**
1. Change status values in code
2. Update status filter dropdown
3. Update status badges (🟡 submit, 🔴 need fix, 🟢 approved)
4. Update comment structure with new status values

---

## ❌ **What NOT to Do**

- ❌ DO NOT change UI layout
- ❌ DO NOT redesign panels
- ❌ DO NOT change from dropdown filters to tree view
- ❌ DO NOT change table columns
- ❌ DO NOT remove existing features
- ❌ DO NOT change panel positions (left/right/bottom)

---

## ✅ **Summary**

**KEEP:**
- Current three-panel layout
- Dropdown filters (NOT tree view)
- Media table with current columns
- Comments panel with threading
- Timeline Playlist Manager

**UPDATE:**
- Backend data source (file system instead of JSON)
- Storage location (project root instead of local)
- Status values (3 states instead of many)
- Add right-click context menu
- Add annotation file path to data

**DO NOT CHANGE:**
- UI design
- Panel layout
- Widget types
- User workflow


