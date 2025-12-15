# Final 3-Section Layout Design
## Navigator + Playlist (Left Tabs) | Viewer (Center) | Comments (Right)

**Date:** 2025-12-15  
**Status:** Final Design Specification  

---

## 🎨 **3-Section Layout**

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Open RV Main Window                         │
├──────────────────────┬──────────────────┬──────────────────────────┤
│  LEFT (Tabs)         │  CENTER          │  RIGHT                   │
│                      │                  │                          │
│  ┌─ Tab 1: Search ─┐│                  │  💬 Comments             │
│  │ Episode: [Ep02▼]││                  │  ┌────────────────────┐ │
│  │ Sequence:[sq10▼]││                  │  │👤 director.smith   │ │
│  │ Shot: [All ▼]   ││   🎬 RV VIEWER  │  │  "Great work!"     │ │
│  │                 ││                  │  │  💬 Reply          │ │
│  │ Media Files:    ││   (Playback)     │  └────────────────────┘ │
│  │ ┌─────────────┐ ││                  │  💭 Add comment...     │
│  │ │🎬│SH10│v07│✓││                  │                          │
│  │ │🎬│SH20│v04│✓││                  │                          │
│  │ └─────────────┘ ││                  │                          │
│  └─────────────────┘│                  │                          │
│                      │                  │                          │
│  ┌─ Tab 2: Playlist┐│                  │                          │
│  │ Playlists:      ││                  │                          │
│  │ ▶ Daily Review  ││                  │                          │
│  │ [Duplicate]     ││                  │                          │
│  │                 ││                  │                          │
│  │ Shots (3):      ││                  │                          │
│  │ ┌─────────────┐ ││                  │                          │
│  │ │SH10│v07│🟡│✓││                  │                          │
│  │ │SH20│v04│🟢│✓││                  │                          │
│  │ └─────────────┘ ││                  │                          │
│  │ [Remove] [Load] ││                  │                          │
│  └─────────────────┘│                  │                          │
└──────────────────────┴──────────────────┴──────────────────────────┘
```

---

## 📐 **Section Specifications**

### **LEFT SECTION - Tabbed Dock (Qt.LeftDockWidgetArea)**

#### **Tab 1: "Search & Navigate - Horus"**
**Content:** (Keep current design)
- Horus Project dropdown
- Refresh button
- Search input
- Filter dropdowns (Episode, Sequence, Shot, Department, Status)
- Media table (Thumbnail | Task | Name | Version | Status | Created)
- Scale control

#### **Tab 2: "Playlist Manager"**
**Content:** (New design)

**Top Half - Playlist Tree:**
```
Playlists:
┌────────────────────┐
│ ▶ Daily Review     │
│ ▶ Weekly Review    │
│ ▶ Director Review  │
└────────────────────┘

[New Playlist] [Duplicate] [Rename] [Delete]
```

**Bottom Half - Shot Table:**
```
Playlist: Daily Review (3 shots)
┌──────────────────────────────────────┐
│ Shot │ Seq │ Dept │ Ver │ Status │ ✓ │
├──────────────────────────────────────┤
│ SH10 │sq10 │ comp │ v07 │  🟡   │ ☑ │
│ SH20 │sq10 │ comp │ v04 │  🟢   │ ☐ │
│ SH30 │sq20 │ anim │ v03 │  🔴   │ ☐ │
└──────────────────────────────────────┘

Status: [submit ▼] [Set Status]
[Remove Selected] [Clear All] [Load in RV] [Export]
```

---

### **CENTER SECTION - RV Viewer (Native)**
- Open RV's native viewport
- Media playback area
- No custom widgets needed

---

### **RIGHT SECTION - Comments Dock (Qt.RightDockWidgetArea)**
**Content:** (Keep current design)
- Filter dropdowns (Episode, Author, Status)
- Sort dropdown (Latest, Frame, Priority)
- Threaded comments with replies
- Add comment input

---

## 🔧 **Implementation Changes**

### **File:** `rv_horus_integration.py`

### **Change 1: Create Tabbed Left Dock**

**Current Code (Lines 4200-4242):**
```python
# Separate docks
rv_main_window.addDockWidget(Qt.LeftDockWidgetArea, search_dock)
rv_main_window.addDockWidget(Qt.RightDockWidgetArea, comments_dock)
rv_main_window.addDockWidget(Qt.BottomDockWidgetArea, timeline_playlist_dock)
```

**New Code:**
```python
# Create tabbed left dock
left_dock = QDockWidget("Navigator & Playlists", rv_main_window)
left_dock.setAllowedAreas(Qt.LeftDockWidgetArea)

# Create tab widget
left_tabs = QTabWidget()
left_tabs.addTab(search_panel, "📁 Search & Navigate")
left_tabs.addTab(playlist_panel, "📋 Playlist Manager")

left_dock.setWidget(left_tabs)

# Add docks
rv_main_window.addDockWidget(Qt.LeftDockWidgetArea, left_dock)
rv_main_window.addDockWidget(Qt.RightDockWidgetArea, comments_dock)

# Store references
globals()['left_dock'] = left_dock
globals()['left_tabs'] = left_tabs
globals()['comments_dock'] = comments_dock
```

---

### **Change 2: Redesign Playlist Panel**

**Replace:** `create_timeline_playlist_panel()`

**With:** `create_playlist_manager_panel()`

```python
def create_playlist_manager_panel():
    """Create playlist manager with tree + shot table."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(5, 5, 5, 5)
    layout.setSpacing(5)
    
    # ===== TOP HALF: Playlist Tree =====
    tree_label = QLabel("Playlists:")
    tree_label.setStyleSheet("font-weight: bold; color: #e0e0e0;")
    layout.addWidget(tree_label)
    
    playlist_tree = QTreeWidget()
    playlist_tree.setHeaderHidden(True)
    playlist_tree.setMaximumHeight(200)  # Limit height
    playlist_tree.itemSelectionChanged.connect(on_playlist_selected)
    layout.addWidget(playlist_tree)
    
    # Playlist controls
    playlist_controls = QFrame()
    playlist_controls_layout = QHBoxLayout(playlist_controls)
    
    new_btn = QPushButton("New Playlist")
    new_btn.clicked.connect(create_new_playlist)
    playlist_controls_layout.addWidget(new_btn)
    
    duplicate_btn = QPushButton("Duplicate")
    duplicate_btn.clicked.connect(duplicate_playlist)
    playlist_controls_layout.addWidget(duplicate_btn)
    
    rename_btn = QPushButton("Rename")
    rename_btn.clicked.connect(rename_playlist)
    playlist_controls_layout.addWidget(rename_btn)
    
    delete_btn = QPushButton("Delete")
    delete_btn.clicked.connect(delete_playlist)
    playlist_controls_layout.addWidget(delete_btn)
    
    layout.addWidget(playlist_controls)
    
    # ===== BOTTOM HALF: Shot Table =====
    shot_label = QLabel("Shots in Playlist: (0)")
    shot_label.setStyleSheet("font-weight: bold; color: #e0e0e0;")
    layout.addWidget(shot_label)
    
    shot_table = QTableWidget()
    shot_table.setColumnCount(6)
    shot_table.setHorizontalHeaderLabels([
        "Shot", "Sequence", "Department", "Version", "Status", "✓"
    ])
    shot_table.setSelectionBehavior(QTableWidget.SelectRows)
    shot_table.setSortingEnabled(True)
    shot_table.setContextMenuPolicy(Qt.CustomContextMenu)
    shot_table.customContextMenuRequested.connect(show_shot_context_menu)
    shot_table.itemDoubleClicked.connect(load_shot_in_rv)
    layout.addWidget(shot_table)
    
    # Shot action controls
    shot_controls = QFrame()
    shot_controls_layout = QHBoxLayout(shot_controls)
    
    shot_controls_layout.addWidget(QLabel("Status:"))
    status_combo = QComboBox()
    status_combo.addItems(["submit", "need fix", "approved"])
    shot_controls_layout.addWidget(status_combo)
    
    set_status_btn = QPushButton("Set Status")
    set_status_btn.clicked.connect(set_selected_shots_status)
    shot_controls_layout.addWidget(set_status_btn)
    
    shot_controls_layout.addStretch()
    
    remove_btn = QPushButton("Remove Selected")
    remove_btn.clicked.connect(remove_selected_shots)
    shot_controls_layout.addWidget(remove_btn)
    
    clear_btn = QPushButton("Clear All")
    clear_btn.clicked.connect(clear_all_shots)
    shot_controls_layout.addWidget(clear_btn)
    
    load_btn = QPushButton("Load in RV")
    load_btn.clicked.connect(load_selected_shots_in_rv)
    shot_controls_layout.addWidget(load_btn)
    
    export_btn = QPushButton("Export")
    export_btn.clicked.connect(export_playlist)
    shot_controls_layout.addWidget(export_btn)
    
    layout.addWidget(shot_controls)
    
    # Store references
    widget.playlist_tree = playlist_tree
    widget.shot_table = shot_table
    widget.shot_label = shot_label
    widget.status_combo = status_combo
    
    return widget
```

---

## ✅ **Implementation Checklist**

### **Phase 1: Layout Restructure**
- [ ] Create tabbed left dock with QTabWidget
- [ ] Add "Search & Navigate" as Tab 1
- [ ] Add "Playlist Manager" as Tab 2
- [ ] Remove bottom timeline dock
- [ ] Keep comments on right

### **Phase 2: Playlist Manager**
- [ ] Create playlist tree (top half)
- [ ] Create shot table (bottom half)
- [ ] Add playlist controls (New, Duplicate, Rename, Delete)
- [ ] Add shot controls (Status, Remove, Load, Export)
- [ ] Connect selection handlers

### **Phase 3: Functionality**
- [ ] Populate shot table from playlist JSON
- [ ] Implement "Set Status" → update comment JSON
- [ ] Implement "Remove Selected" → remove from playlist only
- [ ] Implement "Load in RV" → load all selected shots
- [ ] Add right-click context menu

---

## 📋 **Answers to Your Questions**

1. ✅ **Playlist data:** Populate from JSON structure
2. ✅ **Status update:** Update comment JSON file on server
3. ✅ **Remove shots:** Remove from playlist ONLY (no file deletion)
4. ✅ **Load in RV:** Load ALL selected shots

---

**Ready to implement! Shall I start with Phase 1 (Layout Restructure)?**


