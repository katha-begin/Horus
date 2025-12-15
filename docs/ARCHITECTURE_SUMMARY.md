# Horus Architecture Summary
## Simplified File System-Based Approach

**Date:** 2025-12-15  
**Status:** Planning Complete - Ready for Implementation  

---

## 🎯 **Key Decisions**

### ✅ **What We're Using:**
1. **PySide2** - Keep current UI framework (Qt 5)
2. **File System Scanning** - Direct access to network mounts
3. **JSON Files** - Separate files for comments and playlists
4. **Existing Shot Metadata** - Use `.{Episode}_{Sequence}_{Shot}.json` files
5. **Current UI Design** - Keep three-widget layout

### ❌ **What We're NOT Using (For POC):**
1. ~~Database (PostgreSQL/SQLite)~~ - Too complex for POC
2. ~~PySide6~~ - Open RV uses Qt 5/PySide2
3. ~~Timeline Widget~~ - Not needed for POC
4. ~~Complex search~~ - Simple filtering is sufficient

---

## 📁 **Data Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Remote Server (10.100.128.193)           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /mnt/igloo_swa_v/SWA/all/scene/  (Project Root - Movies)   │
│  ├── Ep01/                                                   │
│  ├── Ep02/                                                   │
│  │   ├── sq0010/                                             │
│  │   │   ├── SH0010/                                         │
│  │   │   │   ├── .Ep02_sq0010_SH0010.json  ← Shot Metadata  │
│  │   │   │   ├── comp/                                       │
│  │   │   │   │   └── output/                                 │
│  │   │   │   │       ├── Ep02_sq0010_SH0010_v006.mov        │
│  │   │   │   │       └── Ep02_sq0010_SH0010_v007.mov        │
│  │   │   │   ├── anim/                                       │
│  │   │   │   └── lighting/                                   │
│  │   │   ├── SH0020/                                         │
│  │   │   └── SH0030/                                         │
│  │   └── sq0020/                                             │
│  ├── Ep03/                                                   │
│  └── Ep04/                                                   │
│                                                              │
│  /mnt/igloo_swa_w/SWA/all/scene/  (Image Root - Sequences)  │
│  └── Ep02/                                                   │
│      └── sq0010/                                             │
│          └── SH0010/                                         │
│              └── comp/                                       │
│                  └── version/                                │
│                      ├── v001/                               │
│                      │   ├── Ep02_sq0010_SH0010.1001.exr    │
│                      │   ├── Ep02_sq0010_SH0010.1002.exr    │
│                      │   └── ...                             │
│                      └── v007/                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Local Storage (~/.horus/)                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ~/.horus/projects/SWA/                                      │
│  ├── comments/                                               │
│  │   ├── Ep02_sq0010_SH0010_comp_v007.json  ← Comments      │
│  │   ├── Ep02_sq0010_SH0020_comp_v004.json                  │
│  │   └── ...                                                 │
│  └── playlists/                                              │
│      ├── daily_review_2025-12-15.json  ← Playlists          │
│      ├── weekly_review.json                                  │
│      └── ...                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 **UI Layout (CURRENT DESIGN - DO NOT CHANGE)**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Open RV Main Window                                 │
├────────────────────────────────────┬────────────────────────────────────────┤
│                                    │                                        │
│  📁 SEARCH & NAVIGATE - HORUS      │   💬 COMMENTS & ANNOTATIONS           │
│  (Left Dock)                       │   (Right Dock)                        │
│                                    │                                        │
│  Horus Project: [SWA ▼]            │   Filter: [Ep02 ▼] [All Authors ▼]   │
│  [Refresh]                         │   Sort: [Latest First ▼]             │
│                                    │                                        │
│  Search: [Search files...]         │   👤 director.smith • Frame 1015     │
│                                    │      "Great work!"                    │
│  ┌─ FILTERS ─────────────────┐    │      👍 3  💬 Reply                   │
│  │ Department: [All ▼]        │    │      └─ 👤 artist.john               │
│  │ Episode: [Ep02 ▼]          │    │         "Thanks!"                     │
│  │ Sequence: [sq0010 ▼]       │    │                                        │
│  │ Shot: [All ▼]              │    │   👤 supervisor.jane • Frame 1028    │
│  │ Status: [All ▼]            │    │      "Eye line needs adjustment"      │
│  └────────────────────────────┘    │      👍 1  💬 Reply                   │
│                                    │                                        │
│  Media Files:                      │   💭 Add a comment... [✓]            │
│  ┌──────────────────────────────┐ │                                        │
│  │ 📷 | Task | Name | Ver | ✓ │ │                                        │
│  ├──────────────────────────────┤ │                                        │
│  │ 🎬 | SH10 | comp | v07 | ✓ │ │                                        │
│  │ 🎬 | SH10 | comp | v06 | ⏳│ │                                        │
│  │ 🎬 | SH20 | comp | v04 | ✓ │ │                                        │
│  │ 🎬 | SH20 | anim | v03 | ⏳│ │                                        │
│  └──────────────────────────────┘ │                                        │
│                                    │                                        │
│  Scale: [Small ▼]                  │                                        │
│                                    │                                        │
├────────────────────────────────────┴────────────────────────────────────────┤
│                                                                             │
│  🎬 TIMELINE PLAYLIST MANAGER (Bottom Dock)                                │
│                                                                             │
│  Playlists:                        Timeline:                               │
│  ┌─────────────────────┐          ┌──────────────────────────────────────┐│
│  │ ▶ Daily Review      │          │ ████ SH0010_v007 ████ SH0020_v004   ││
│  │ ▶ Weekly Review     │          │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ││
│  │ ▶ Director Review   │          │ 00:00        01:00        02:00      ││
│  └─────────────────────┘          └──────────────────────────────────────┘│
│                                                                             │
│  [New] [Duplicate] [Rename] [Delete]    [Play] [Stop] [Export]            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**CURRENT DESIGN FEATURES (DO NOT CHANGE):**
- ✅ **Left Panel:** Dropdown filters (NOT tree view)
- ✅ **Media Table:** Thumbnail | Task Entity | Name | Version | Status | Created
- ✅ **Right Panel:** Comments with threading
- ✅ **Bottom Panel:** Timeline Playlist Manager
- ✅ **Sorting:** Click table headers
- ✅ **Scale:** Small/Medium/Large thumbnails

---

## 🔄 **Data Flow**

### **1. Loading Media Files:**
```
User Action: Browse File Navigator
    ↓
FileSystemScanner.scan_shots("Ep02", "sq0010")
    ↓
Find media files in output/ directory
    ↓
Load shot metadata from .json file
    ↓
Display in File Navigator tree
    ↓
User Action: Double-click file
    ↓
Load in Open RV viewer
```

### **2. Adding to Playlist:**
```
User Action: Right-click file → "Add to Playlist"
    ↓
PlaylistManager.add_clip(playlist_id, clip_data)
    ↓
Update playlist JSON file
    ↓
Refresh Playlist Manager widget
    ↓
Show clip in playlist with metadata
```

### **3. Adding Comments:**
```
User Action: Type comment and press Enter
    ↓
Get current frame number from Open RV
    ↓
CommentManager.add_comment(media_file, author, text, frame)
    ↓
Save to comment JSON file
    ↓
Refresh Comments widget
    ↓
Show new comment in threaded view
```

### **4. Filtering Comments:**
```
User Action: Select "Ep02" from filter dropdown
    ↓
CommentManager.filter_comments(episode="Ep02")
    ↓
Load all comment files starting with "Ep02"
    ↓
Aggregate comments from all files
    ↓
Sort by selected criteria (timestamp, frame, etc.)
    ↓
Display filtered comments in widget
```

---

## 🛠️ **Technology Stack**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **UI Framework** | PySide2 (Qt 5) | Widget system |
| **Media Player** | Open RV 3.0+ | Video playback |
| **Data Storage** | JSON files | Comments & playlists |
| **File System** | Network mounts | Media files |
| **Metadata** | Existing .json files | Shot information |
| **Language** | Python 3.7+ | Core logic |


