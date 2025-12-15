# Playlist UI Redesign - Remove Timeline, Add Shot Table
## Keep Current Layout Structure - Only Change Right Panel

**Date:** 2025-12-15  
**Status:** Design Specification  

---

## 🎯 **Changes Required**

### **KEEP (Left Panel):**
- ✅ Playlist tree widget
- ✅ Buttons: Duplicate, Rename, Delete, Add Media
- ✅ Same styling and layout

### **REMOVE (Right Panel):**
- ❌ Timeline visualization
- ❌ Timeline tracks
- ❌ Zoom controls
- ❌ Play/Stop buttons

### **ADD (Right Panel):**
- ✅ **Shot table** with columns
- ✅ **Remove button** for selected shots
- ✅ **Set Status dropdown** for selected shots
- ✅ **Shot count** display
- ✅ **Right-click context menu**

---

## 🎨 **New Playlist UI Design**

```
┌─────────────────────────────────────────────────────────────────────┐
│  Timeline Playlist Manager                    [New Playlist] [Refresh]│
├──────────────────────────┬──────────────────────────────────────────┤
│                          │                                           │
│  Playlists               │  Playlist: Daily Review (3 shots)        │
│  ┌────────────────────┐  │  ┌─────────────────────────────────────┐│
│  │ ▶ Daily Review     │  │  │Shot│Seq│Dept│Ver│Status│Modified│✓││
│  │   ├─ Ep02_sq0010   │  │  ├─────────────────────────────────────┤│
│  │   │   └─ SH0010    │  │  │SH10│sq10│comp│v07│🟡submit│12/15│ ││
│  │   └─ Ep02_sq0010   │  │  │SH20│sq10│comp│v04│🟢approved│12/14│││
│  │       └─ SH0020    │  │  │SH30│sq20│anim│v03│🔴need fix│12/13│││
│  │                    │  │  └─────────────────────────────────────┘│
│  │ ▶ Weekly Review    │  │                                           │
│  │ ▶ Director Review  │  │  Selected: 1 shot                        │
│  └────────────────────┘  │                                           │
│                          │  Status: [submit ▼] [Set Status]         │
│  [Duplicate] [Rename]    │  [Remove Selected] [Clear All]           │
│  [Delete] [Add Media]    │  [Load in RV] [Export List]              │
│                          │                                           │
└──────────────────────────┴──────────────────────────────────────────┘
```

---

## 📊 **Shot Table Specification**

### **Table Columns:**
| Column | Width | Description |
|--------|-------|-------------|
| **Shot** | 60px | Shot name (SH0010, SH0020) |
| **Sequence** | 60px | Sequence name (sq0010) |
| **Department** | 80px | Department (comp, anim, lighting) |
| **Version** | 50px | Version (v001, v007) |
| **Status** | 80px | Status badge (🟡 submit, 🔴 need fix, 🟢 approved) |
| **Modified** | 80px | Last modified date |
| **✓** | 30px | Checkbox for selection |

### **Table Features:**
- ✅ Multi-select with checkboxes
- ✅ Sorting (click column headers)
- ✅ Drag to reorder rows
- ✅ Double-click to load in RV
- ✅ Right-click context menu
- ✅ Color-coded status badges

---

## 🔧 **Action Buttons**

### **Status Control:**
```
Status: [submit ▼] [Set Status]
```
- Dropdown with 3 options: submit, need fix, approved
- "Set Status" button applies to all selected shots
- Updates status in comment JSON file

### **Shot Management:**
```
[Remove Selected] [Clear All]
```
- "Remove Selected" - Remove checked shots from playlist
- "Clear All" - Remove all shots from playlist (with confirmation)

### **Playback:**
```
[Load in RV] [Export List]
```
- "Load in RV" - Load selected shots in RV viewer
- "Export List" - Export playlist to text file

---

## 🖱️ **Right-Click Context Menu**

```
┌─────────────────────────────────┐
│ ▶ Load in RV                    │
│ ▶ Load Movie (.mov)             │
│ ▶ Load Image Sequence (.exr)    │
│ ─────────────────────────────── │
│ 📝 Set Status                   │
│   ├─ 🟡 Submit                  │
│   ├─ 🔴 Need Fix                │
│   └─ 🟢 Approved                │
│ ─────────────────────────────── │
│ ❌ Remove from Playlist          │
│ 📁 Show in File System           │
│ 💬 View Comments                 │
└─────────────────────────────────┘
```

---

## 💾 **Data Structure (No Changes)**

### **Playlist JSON:**
```json
{
  "playlist_id": "playlist_001",
  "name": "Daily Review",
  "clips": [
    {
      "clip_id": "clip_001",
      "episode": "Ep02",
      "sequence": "sq0010",
      "shot": "SH0010",
      "department": "comp",
      "version": "v007",
      "file_path": "/mnt/.../Ep02_sq0010_SH0010_v007.mov",
      "annotation_file": "/mnt/.../annotations.json",
      "shot_status": "submit",
      "added_at": "2025-12-15T09:15:00Z"
    }
  ]
}
```

---

## 🔄 **Implementation Changes**

### **File:** `rv_horus_integration.py`

### **Function to Modify:** `create_timeline_tracks_panel()`

**OLD (Remove):**
```python
def create_timeline_tracks_panel():
    # Timeline visualization
    # Timeline tracks
    # Zoom controls
    # Play/Stop buttons
```

**NEW (Replace with):**
```python
def create_playlist_shots_table_panel():
    """Create right panel with shot table."""
    panel = QWidget()
    layout = QVBoxLayout(panel)
    
    # Header with playlist name and shot count
    header = QFrame()
    header_layout = QHBoxLayout(header)
    playlist_name_label = QLabel("No playlist selected")
    shot_count_label = QLabel("0 shots")
    header_layout.addWidget(playlist_name_label)
    header_layout.addStretch()
    header_layout.addWidget(shot_count_label)
    layout.addWidget(header)
    
    # Shot table
    shot_table = QTableWidget()
    shot_table.setColumnCount(7)
    shot_table.setHorizontalHeaderLabels([
        "Shot", "Sequence", "Department", "Version", "Status", "Modified", "✓"
    ])
    shot_table.setSelectionBehavior(QTableWidget.SelectRows)
    shot_table.setSortingEnabled(True)
    shot_table.setContextMenuPolicy(Qt.CustomContextMenu)
    shot_table.customContextMenuRequested.connect(show_shot_context_menu)
    shot_table.itemDoubleClicked.connect(load_shot_in_rv)
    layout.addWidget(shot_table)
    
    # Action buttons
    action_frame = QFrame()
    action_layout = QHBoxLayout(action_frame)
    
    # Status control
    action_layout.addWidget(QLabel("Status:"))
    status_combo = QComboBox()
    status_combo.addItems(["submit", "need fix", "approved"])
    action_layout.addWidget(status_combo)
    
    set_status_btn = QPushButton("Set Status")
    set_status_btn.clicked.connect(set_selected_shots_status)
    action_layout.addWidget(set_status_btn)
    
    action_layout.addStretch()
    
    # Shot management
    remove_btn = QPushButton("Remove Selected")
    remove_btn.clicked.connect(remove_selected_shots)
    action_layout.addWidget(remove_btn)
    
    clear_btn = QPushButton("Clear All")
    clear_btn.clicked.connect(clear_all_shots)
    action_layout.addWidget(clear_btn)
    
    # Playback
    load_rv_btn = QPushButton("Load in RV")
    load_rv_btn.clicked.connect(load_selected_in_rv)
    action_layout.addWidget(load_rv_btn)
    
    export_btn = QPushButton("Export List")
    export_btn.clicked.connect(export_playlist)
    action_layout.addWidget(export_btn)
    
    layout.addWidget(action_frame)
    
    # Store references
    panel.shot_table = shot_table
    panel.playlist_name_label = playlist_name_label
    panel.shot_count_label = shot_count_label
    panel.status_combo = status_combo
    
    return panel
```

---

## ✅ **Summary**

**KEEP:**
- Left panel (playlist tree)
- Overall layout structure
- Styling and colors

**REMOVE:**
- Timeline visualization
- Timeline tracks
- Zoom controls
- Play/Stop buttons

**ADD:**
- Shot table with 7 columns
- Status dropdown and "Set Status" button
- Remove/Clear buttons
- Load in RV / Export buttons
- Right-click context menu
- Multi-select with checkboxes

**NO CHANGES:**
- Data structure (playlist JSON)
- Storage location
- Left panel functionality


