#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Horus Timeline Playlist Widget
=============================

Professional NLE-style timeline playlist widget following Adobe Premiere Pro patterns.
Implements left panel playlist tree and right panel timeline tracks with full playlist management.

Features:
- Professional NLE interface design
- Playlist creation and management
- Drag-and-drop clip reordering
- Department-based color coding
- Timeline visualization with tracks
- Integration with Horus database
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from PySide2.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTreeWidget, QTreeWidgetItem,
        QScrollArea, QFrame, QLabel, QPushButton, QLineEdit, QComboBox, QSpinBox,
        QCheckBox, QGroupBox, QGridLayout, QListWidget, QListWidgetItem,
        QMenu, QAction, QMessageBox, QInputDialog, QHeaderView, QAbstractItemView
    )
    from PySide2.QtCore import Qt, QTimer, Signal, QMimeData, QPoint
    from PySide2.QtGui import QColor, QPainter, QFont, QPixmap, QDrag
except ImportError:
    print("PySide2 not available - Timeline Playlist Widget will not function")
    sys.exit(1)


class HorusTimelinePlaylistWidget(QWidget):
    """
    Professional timeline playlist widget following Adobe Premiere Pro patterns.
    
    Layout:
    ┌─────────────────────────────────────────────────────────────┐
    │ Timeline Playlist Manager                                    │
    ├─────────────────┬───────────────────────────────────────────┤
    │ Playlist Tree   │ Timeline Tracks                           │
    │ ┌─────────────┐ │ ┌───────────────────────────────────────┐ │
    │ │ ▼ Playlists │ │ │ V1 │████│    │████│    │████│        │ │
    │ │   ├ Review  │ │ │ A1 │▓▓▓▓│    │▓▓▓▓│    │▓▓▓▓│        │ │
    │ │   ├ Daily   │ │ │    └────┴────┴────┴────┴────┴────────┘ │
    │ │   └ Assets  │ │ │ 00:00  01:00  02:00  03:00  04:00     │ │
    │ └─────────────┘ │ └───────────────────────────────────────┘ │
    └─────────────────┴───────────────────────────────────────────┘
    """
    
    # Signals
    playlist_selected = Signal(str)  # playlist_id
    clip_selected = Signal(str)      # clip_id
    playback_requested = Signal(str, int)  # media_path, frame
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_project_id = None
        self.current_playlist_id = None
        self.playlists_data = []
        self.media_records = []
        self.department_colors = {
            "animation": "#1f4e79",
            "lighting": "#d68910", 
            "compositing": "#196f3d",
            "fx": "#6c3483",
            "modeling": "#a93226",
            "texturing": "#8b4513",
            "rigging": "#2e8b57",
            "layout": "#4682b4"
        }
        
        self.setup_ui()
        self.setup_connections()
        self.load_data()
        
    def setup_ui(self):
        """Setup the main UI layout following Adobe Premiere Pro patterns."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header with title and controls
        header = self.create_header()
        layout.addWidget(header)
        
        # Main splitter: Playlist Tree (left) | Timeline (right)
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        
        # Left panel: Playlist tree and controls
        left_panel = self.create_playlist_panel()
        main_splitter.addWidget(left_panel)
        
        # Right panel: Timeline tracks
        right_panel = self.create_timeline_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions (30% left, 70% right)
        main_splitter.setSizes([300, 700])
        layout.addWidget(main_splitter)
        
        # Store references
        self.main_splitter = main_splitter
        
    def create_header(self) -> QWidget:
        """Create header with title and main controls."""
        header = QFrame()
        header.setFixedHeight(40)
        header.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-bottom: 1px solid #555555;
            }
            QLabel {
                color: #e0e0e0;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton {
                background-color: #404040;
                color: #e0e0e0;
                border: 1px solid #555555;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #0078d4;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Title
        title = QLabel("Timeline Playlist Manager")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Main controls
        new_playlist_btn = QPushButton("New Playlist")
        new_playlist_btn.clicked.connect(self.create_new_playlist)
        layout.addWidget(new_playlist_btn)
        
        import_btn = QPushButton("Import")
        layout.addWidget(import_btn)
        
        export_btn = QPushButton("Export")
        layout.addWidget(export_btn)
        
        # Store references
        self.new_playlist_btn = new_playlist_btn
        self.import_btn = import_btn
        self.export_btn = export_btn
        
        return header
        
    def create_playlist_panel(self) -> QWidget:
        """Create left panel with playlist tree and controls."""
        panel = QWidget()
        panel.setMinimumWidth(250)
        panel.setMaximumWidth(400)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Playlist tree header
        tree_header = QLabel("Playlists")
        tree_header.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 12px;")
        layout.addWidget(tree_header)
        
        # Playlist tree widget
        self.playlist_tree = QTreeWidget()
        self.playlist_tree.setHeaderHidden(True)
        self.playlist_tree.setRootIsDecorated(True)
        self.playlist_tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.playlist_tree.setDragDropMode(QAbstractItemView.InternalMove)
        self.setup_playlist_tree_styling()
        layout.addWidget(self.playlist_tree)
        
        # Playlist controls
        controls = self.create_playlist_controls()
        layout.addWidget(controls)
        
        return panel
        
    def create_timeline_panel(self) -> QWidget:
        """Create right panel with timeline tracks."""
        panel = QWidget()
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Timeline header with controls
        timeline_header = self.create_timeline_header()
        layout.addWidget(timeline_header)
        
        # Timeline scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Timeline content widget
        self.timeline_content = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_content)
        self.timeline_layout.setContentsMargins(0, 0, 0, 0)
        self.timeline_layout.setSpacing(2)
        
        scroll_area.setWidget(self.timeline_content)
        layout.addWidget(scroll_area)
        
        # Store references
        self.timeline_scroll = scroll_area
        
        return panel
        
    def setup_playlist_tree_styling(self):
        """Setup playlist tree styling following professional NLE patterns."""
        self.playlist_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #555555;
                selection-background-color: #0078d4;
                outline: none;
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #3a3a3a;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #404040;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
        """)

    def create_playlist_controls(self) -> QWidget:
        """Create playlist management controls."""
        controls = QFrame()
        controls.setFixedHeight(80)
        controls.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #404040;
                color: #e0e0e0;
                border: 1px solid #555555;
                padding: 4px 8px;
                border-radius: 2px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #0078d4;
            }
        """)

        layout = QGridLayout(controls)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)

        # Playlist controls
        duplicate_btn = QPushButton("Duplicate")
        duplicate_btn.clicked.connect(self.duplicate_playlist)
        layout.addWidget(duplicate_btn, 0, 0)

        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(self.rename_playlist)
        layout.addWidget(rename_btn, 0, 1)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_playlist)
        layout.addWidget(delete_btn, 1, 0)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_playlists)
        layout.addWidget(refresh_btn, 1, 1)

        # Store references
        self.duplicate_btn = duplicate_btn
        self.rename_btn = rename_btn
        self.delete_btn = delete_btn
        self.refresh_btn = refresh_btn

        return controls

    def create_timeline_header(self) -> QWidget:
        """Create timeline header with playback and view controls."""
        header = QFrame()
        header.setFixedHeight(35)
        header.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-bottom: 1px solid #555555;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 11px;
            }
            QPushButton {
                background-color: #404040;
                color: #e0e0e0;
                border: 1px solid #555555;
                padding: 3px 8px;
                border-radius: 2px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #0078d4;
            }
            QComboBox {
                background-color: #404040;
                color: #e0e0e0;
                border: 1px solid #555555;
                padding: 2px 5px;
                border-radius: 2px;
                font-size: 10px;
            }
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 5, 10, 5)

        # Current playlist name
        self.current_playlist_label = QLabel("No playlist selected")
        self.current_playlist_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.current_playlist_label)

        layout.addStretch()

        # Timeline controls
        play_btn = QPushButton("▶ Play")
        play_btn.clicked.connect(self.play_timeline)
        layout.addWidget(play_btn)

        stop_btn = QPushButton("⏹ Stop")
        stop_btn.clicked.connect(self.stop_timeline)
        layout.addWidget(stop_btn)

        # Zoom controls
        zoom_label = QLabel("Zoom:")
        layout.addWidget(zoom_label)

        zoom_combo = QComboBox()
        zoom_combo.addItems(["25%", "50%", "75%", "100%", "150%", "200%", "Fit"])
        zoom_combo.setCurrentText("100%")
        zoom_combo.currentTextChanged.connect(self.on_zoom_changed)
        layout.addWidget(zoom_combo)

        # Store references
        self.play_btn = play_btn
        self.stop_btn = stop_btn
        self.zoom_combo = zoom_combo

        return header

    def setup_connections(self):
        """Setup signal connections."""
        self.playlist_tree.itemSelectionChanged.connect(self.on_playlist_selection_changed)
        self.playlist_tree.itemDoubleClicked.connect(self.on_playlist_double_clicked)

    def load_data(self):
        """Load playlist and media data from JSON database."""
        try:
            # Load playlists
            playlist_file = os.path.join("sample_db", "horus_playlists.json")
            if os.path.exists(playlist_file):
                with open(playlist_file, 'r') as f:
                    self.playlists_data = json.load(f)

            # Load media records
            media_file = os.path.join("sample_db", "media_records.json")
            if os.path.exists(media_file):
                with open(media_file, 'r') as f:
                    self.media_records = json.load(f)

            self.populate_playlist_tree()

        except Exception as e:
            print(f"Error loading data: {e}")

    def populate_playlist_tree(self):
        """Populate the playlist tree with data."""
        self.playlist_tree.clear()

        if not self.playlists_data:
            return

        # Group playlists by project
        projects = {}
        for playlist in self.playlists_data:
            project_id = playlist.get("project_id", "unknown")
            if project_id not in projects:
                projects[project_id] = []
            projects[project_id].append(playlist)

        # Create tree structure
        for project_id, playlists in projects.items():
            project_item = QTreeWidgetItem(self.playlist_tree)
            project_item.setText(0, f"Project: {project_id}")
            project_item.setData(0, Qt.UserRole, {"type": "project", "id": project_id})

            # Add playlists under project
            for playlist in playlists:
                playlist_item = QTreeWidgetItem(project_item)
                playlist_name = playlist.get("name", "Unnamed Playlist")
                clip_count = len(playlist.get("clips", []))
                playlist_item.setText(0, f"{playlist_name} ({clip_count} clips)")
                playlist_item.setData(0, Qt.UserRole, {
                    "type": "playlist",
                    "id": playlist["_id"],
                    "data": playlist
                })

                # Set playlist status color
                status = playlist.get("status", "draft")
                if status == "active":
                    playlist_item.setForeground(0, QColor("#4CAF50"))
                elif status == "draft":
                    playlist_item.setForeground(0, QColor("#FFC107"))

        # Expand all items
        self.playlist_tree.expandAll()

    def on_playlist_selection_changed(self):
        """Handle playlist selection change."""
        selected_items = self.playlist_tree.selectedItems()
        if not selected_items:
            self.current_playlist_id = None
            self.current_playlist_label.setText("No playlist selected")
            self.clear_timeline()
            return

        item = selected_items[0]
        item_data = item.data(0, Qt.UserRole)

        if item_data and item_data.get("type") == "playlist":
            playlist_id = item_data["id"]
            playlist_data = item_data["data"]

            self.current_playlist_id = playlist_id
            self.current_playlist_label.setText(f"Playlist: {playlist_data.get('name', 'Unnamed')}")

            # Load timeline for this playlist
            self.load_timeline(playlist_data)

            # Emit signal
            self.playlist_selected.emit(playlist_id)

    def on_playlist_double_clicked(self, item, column):
        """Handle playlist double-click to start playback."""
        item_data = item.data(0, Qt.UserRole)
        if item_data and item_data.get("type") == "playlist":
            self.play_timeline()

    def create_new_playlist(self):
        """Create a new playlist."""
        name, ok = QInputDialog.getText(self, "New Playlist", "Enter playlist name:")
        if ok and name:
            # Generate new playlist ID
            playlist_id = f"playlist_{len(self.playlists_data) + 1:03d}"

            # Create new playlist data
            new_playlist = {
                "_id": playlist_id,
                "name": name,
                "project_id": "proj_001",  # Default project
                "created_by": "user",
                "created_at": datetime.now().isoformat() + "Z",
                "updated_at": datetime.now().isoformat() + "Z",
                "description": f"User created playlist: {name}",
                "type": "user_created",
                "status": "draft",
                "settings": {
                    "auto_play": True,
                    "loop": False,
                    "show_timecode": True,
                    "default_track_height": 60,
                    "timeline_zoom": 1.0,
                    "color_coding_enabled": True
                },
                "clips": [],
                "tracks": [
                    {
                        "track_id": 1,
                        "name": "Video Track 1",
                        "type": "video",
                        "height": 60,
                        "locked": False,
                        "muted": False,
                        "solo": False,
                        "color": "#2d2d2d"
                    }
                ],
                "metadata": {
                    "total_duration": 0,
                    "clip_count": 0,
                    "departments": [],
                    "sequences": [],
                    "last_played_position": 0,
                    "playback_settings": {
                        "frame_rate": 24,
                        "resolution": "1920x1080",
                        "color_space": "Rec709"
                    }
                }
            }

            # Add to data and save
            self.playlists_data.append(new_playlist)
            self.save_playlists()
            self.populate_playlist_tree()

            print(f"Created new playlist: {name}")

    def duplicate_playlist(self):
        """Duplicate the selected playlist."""
        if not self.current_playlist_id:
            QMessageBox.warning(self, "Warning", "Please select a playlist to duplicate.")
            return

        # Find current playlist
        current_playlist = None
        for playlist in self.playlists_data:
            if playlist["_id"] == self.current_playlist_id:
                current_playlist = playlist
                break

        if not current_playlist:
            return

        # Create duplicate
        name, ok = QInputDialog.getText(
            self, "Duplicate Playlist",
            f"Enter name for duplicate of '{current_playlist['name']}':",
            text=f"{current_playlist['name']} Copy"
        )

        if ok and name:
            # Generate new ID
            new_id = f"playlist_{len(self.playlists_data) + 1:03d}"

            # Create duplicate
            duplicate = current_playlist.copy()
            duplicate["_id"] = new_id
            duplicate["name"] = name
            duplicate["created_at"] = datetime.now().isoformat() + "Z"
            duplicate["updated_at"] = datetime.now().isoformat() + "Z"
            duplicate["status"] = "draft"

            # Add to data and save
            self.playlists_data.append(duplicate)
            self.save_playlists()
            self.populate_playlist_tree()

            print(f"Duplicated playlist: {name}")

    def rename_playlist(self):
        """Rename the selected playlist."""
        if not self.current_playlist_id:
            QMessageBox.warning(self, "Warning", "Please select a playlist to rename.")
            return

        # Find current playlist
        current_playlist = None
        for playlist in self.playlists_data:
            if playlist["_id"] == self.current_playlist_id:
                current_playlist = playlist
                break

        if not current_playlist:
            return

        # Get new name
        name, ok = QInputDialog.getText(
            self, "Rename Playlist",
            "Enter new name:",
            text=current_playlist["name"]
        )

        if ok and name:
            current_playlist["name"] = name
            current_playlist["updated_at"] = datetime.now().isoformat() + "Z"

            self.save_playlists()
            self.populate_playlist_tree()
            self.current_playlist_label.setText(f"Playlist: {name}")

            print(f"Renamed playlist to: {name}")

    def delete_playlist(self):
        """Delete the selected playlist."""
        if not self.current_playlist_id:
            QMessageBox.warning(self, "Warning", "Please select a playlist to delete.")
            return

        # Find current playlist
        current_playlist = None
        for i, playlist in enumerate(self.playlists_data):
            if playlist["_id"] == self.current_playlist_id:
                current_playlist = playlist
                break

        if not current_playlist:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self, "Delete Playlist",
            f"Are you sure you want to delete playlist '{current_playlist['name']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.playlists_data.remove(current_playlist)
            self.save_playlists()
            self.populate_playlist_tree()
            self.clear_timeline()

            print(f"Deleted playlist: {current_playlist['name']}")

    def refresh_playlists(self):
        """Refresh playlist data from database."""
        self.load_data()
        print("Refreshed playlist data")

    def save_playlists(self):
        """Save playlist data to JSON database."""
        try:
            playlist_file = os.path.join("sample_db", "horus_playlists.json")
            with open(playlist_file, 'w') as f:
                json.dump(self.playlists_data, f, indent=2)
        except Exception as e:
            print(f"Error saving playlists: {e}")

    def load_timeline(self, playlist_data):
        """Load timeline visualization for the given playlist."""
        self.clear_timeline()

        clips = playlist_data.get("clips", [])
        tracks = playlist_data.get("tracks", [])

        if not clips:
            # Show empty timeline message
            empty_label = QLabel("No clips in this playlist")
            empty_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 14px;
                    padding: 20px;
                    text-align: center;
                }
            """)
            empty_label.setAlignment(Qt.AlignCenter)
            self.timeline_layout.addWidget(empty_label)
            return

        # Create timeline ruler
        ruler = self.create_timeline_ruler(clips)
        self.timeline_layout.addWidget(ruler)

        # Create tracks
        for track in tracks:
            track_widget = self.create_track_widget(track, clips)
            self.timeline_layout.addWidget(track_widget)

        # Add stretch to push tracks to top
        self.timeline_layout.addStretch()

    def clear_timeline(self):
        """Clear the timeline display."""
        # Remove all widgets from timeline layout
        while self.timeline_layout.count():
            child = self.timeline_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def create_timeline_ruler(self, clips) -> QWidget:
        """Create timeline ruler with timecode markers."""
        ruler = QFrame()
        ruler.setFixedHeight(25)
        ruler.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-bottom: 1px solid #555555;
            }
            QLabel {
                color: #cccccc;
                font-size: 10px;
                font-family: monospace;
            }
        """)

        layout = QHBoxLayout(ruler)
        layout.setContentsMargins(60, 0, 0, 0)  # Offset for track labels
        layout.setSpacing(0)

        # Calculate total duration
        total_duration = 0
        if clips:
            total_duration = max(clip.get("position", 0) + clip.get("duration", 0) for clip in clips)

        # Add timecode markers every 30 frames (assuming 24fps)
        if total_duration > 0:
            for frame in range(0, int(total_duration) + 30, 30):
                seconds = frame / 24
                minutes = int(seconds // 60)
                secs = int(seconds % 60)
                frames = frame % 24

                timecode = f"{minutes:02d}:{secs:02d}:{frames:02d}"
                marker = QLabel(timecode)
                marker.setFixedWidth(60)
                marker.setAlignment(Qt.AlignCenter)
                layout.addWidget(marker)

        layout.addStretch()
        return ruler

    def create_track_widget(self, track_data, clips) -> QWidget:
        """Create a timeline track widget with clips."""
        track = QFrame()
        track.setFixedHeight(track_data.get("height", 60))
        track.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-bottom: 1px solid #555555;
            }
        """)

        layout = QHBoxLayout(track)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Track label
        track_label = QLabel(track_data.get("name", "Track"))
        track_label.setFixedWidth(60)
        track_label.setStyleSheet("""
            QLabel {
                background-color: #3a3a3a;
                color: #e0e0e0;
                padding: 5px;
                border-right: 1px solid #555555;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        track_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(track_label)

        # Clips area
        clips_area = QWidget()
        clips_layout = QHBoxLayout(clips_area)
        clips_layout.setContentsMargins(0, 0, 0, 0)
        clips_layout.setSpacing(1)

        # Filter clips for this track
        track_clips = [clip for clip in clips if clip.get("track") == track_data.get("track_id")]
        track_clips.sort(key=lambda x: x.get("position", 0))

        # Add clips to track
        current_position = 0
        for clip in track_clips:
            clip_position = clip.get("position", 0)
            clip_duration = clip.get("duration", 0)

            # Add gap if needed
            if clip_position > current_position:
                gap_width = max(1, (clip_position - current_position) * 2)  # 2 pixels per frame
                gap = QWidget()
                gap.setFixedWidth(gap_width)
                clips_layout.addWidget(gap)

            # Create clip widget
            clip_widget = self.create_clip_widget(clip)
            clips_layout.addWidget(clip_widget)

            current_position = clip_position + clip_duration

        clips_layout.addStretch()
        layout.addWidget(clips_area)

        return track

    def create_clip_widget(self, clip_data) -> QWidget:
        """Create a timeline clip widget."""
        duration = clip_data.get("duration", 0)
        department = clip_data.get("department", "unknown")

        # Calculate width based on duration (2 pixels per frame)
        width = max(40, duration * 2)

        clip = QPushButton()
        clip.setFixedSize(width, 50)
        clip.setToolTip(f"{clip_data.get('sequence', '')}/{clip_data.get('shot', '')} - {clip_data.get('version', '')}")

        # Get department color
        color = self.department_colors.get(department, "#666666")

        clip.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: 1px solid #555555;
                border-radius: 3px;
                font-size: 9px;
                font-weight: bold;
                text-align: left;
                padding: 2px;
            }}
            QPushButton:hover {{
                border-color: #ffffff;
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}aa;
            }}
        """)

        # Set clip text
        shot_name = f"{clip_data.get('shot', 'shot')}"
        version = clip_data.get('version', 'v001')
        clip.setText(f"{shot_name}\n{version}")

        # Connect click handler
        clip.clicked.connect(lambda: self.on_clip_clicked(clip_data))

        return clip

    def on_clip_clicked(self, clip_data):
        """Handle clip click to load in Open RV."""
        try:
            # Find media record for this clip
            media_id = clip_data.get("media_id")
            media_record = None

            for record in self.media_records:
                if record.get("_id") == media_id:
                    media_record = record
                    break

            if media_record:
                file_path = media_record.get("file_path", "")
                if file_path:
                    # Emit signal for playback
                    self.playback_requested.emit(file_path, 0)
                    print(f"Loading clip: {file_path}")
                else:
                    print(f"No file path for clip: {media_id}")
            else:
                print(f"Media record not found: {media_id}")

        except Exception as e:
            print(f"Error loading clip: {e}")

    def play_timeline(self):
        """Start timeline playback."""
        if self.current_playlist_id:
            print(f"Playing playlist: {self.current_playlist_id}")
            # TODO: Implement sequential playback of all clips
        else:
            print("No playlist selected for playback")

    def stop_timeline(self):
        """Stop timeline playback."""
        print("Stopping timeline playback")
        # TODO: Implement playback stop

    def on_zoom_changed(self, zoom_text):
        """Handle timeline zoom change."""
        print(f"Timeline zoom changed to: {zoom_text}")
        # TODO: Implement timeline zoom functionality

    def add_media_to_playlist(self, media_record):
        """Add a media record to the current playlist."""
        if not self.current_playlist_id:
            QMessageBox.warning(self, "Warning", "Please select a playlist first.")
            return

        # Find current playlist
        current_playlist = None
        for playlist in self.playlists_data:
            if playlist["_id"] == self.current_playlist_id:
                current_playlist = playlist
                break

        if not current_playlist:
            return

        # Create new clip
        clips = current_playlist.get("clips", [])

        # Calculate position (add to end)
        position = 0
        if clips:
            last_clip = max(clips, key=lambda x: x.get("position", 0) + x.get("duration", 0))
            position = last_clip.get("position", 0) + last_clip.get("duration", 0)

        # Extract department from task or filename
        department = "unknown"
        if "linked_task_id" in media_record:
            # TODO: Look up task to get department
            pass

        # Try to extract from filename
        filename = media_record.get("file_name", "")
        for dept in self.department_colors.keys():
            if dept in filename.lower():
                department = dept
                break

        # Create clip data
        new_clip = {
            "clip_id": f"clip_{len(clips) + 1:03d}",
            "media_id": media_record["_id"],
            "position": position,
            "duration": media_record.get("metadata", {}).get("duration", 120),
            "in_point": 0,
            "out_point": media_record.get("metadata", {}).get("duration", 120),
            "track": 1,
            "department": department,
            "sequence": self.extract_sequence_from_filename(filename),
            "shot": self.extract_shot_from_filename(filename),
            "version": media_record.get("version", "v001"),
            "color": self.department_colors.get(department, "#666666"),
            "notes": media_record.get("description", ""),
            "added_at": datetime.now().isoformat() + "Z"
        }

        # Add clip to playlist
        clips.append(new_clip)
        current_playlist["clips"] = clips
        current_playlist["updated_at"] = datetime.now().isoformat() + "Z"

        # Update metadata
        metadata = current_playlist.get("metadata", {})
        metadata["clip_count"] = len(clips)
        metadata["total_duration"] = sum(clip.get("duration", 0) for clip in clips)

        # Update departments list
        departments = set(clip.get("department") for clip in clips)
        metadata["departments"] = list(departments)

        current_playlist["metadata"] = metadata

        # Save and refresh
        self.save_playlists()
        self.load_timeline(current_playlist)

        print(f"Added media to playlist: {media_record.get('file_name')}")

    def remove_clip_from_playlist(self, clip_id):
        """Remove a clip from the current playlist."""
        if not self.current_playlist_id:
            return

        # Find current playlist
        current_playlist = None
        for playlist in self.playlists_data:
            if playlist["_id"] == self.current_playlist_id:
                current_playlist = playlist
                break

        if not current_playlist:
            return

        # Remove clip
        clips = current_playlist.get("clips", [])
        clips = [clip for clip in clips if clip.get("clip_id") != clip_id]

        # Reposition remaining clips
        position = 0
        for clip in clips:
            clip["position"] = position
            position += clip.get("duration", 0)

        current_playlist["clips"] = clips
        current_playlist["updated_at"] = datetime.now().isoformat() + "Z"

        # Update metadata
        metadata = current_playlist.get("metadata", {})
        metadata["clip_count"] = len(clips)
        metadata["total_duration"] = sum(clip.get("duration", 0) for clip in clips)

        current_playlist["metadata"] = metadata

        # Save and refresh
        self.save_playlists()
        self.load_timeline(current_playlist)

        print(f"Removed clip from playlist: {clip_id}")

    def reorder_clips(self, clip_ids):
        """Reorder clips in the current playlist."""
        if not self.current_playlist_id:
            return

        # Find current playlist
        current_playlist = None
        for playlist in self.playlists_data:
            if playlist["_id"] == self.current_playlist_id:
                current_playlist = playlist
                break

        if not current_playlist:
            return

        clips = current_playlist.get("clips", [])

        # Create new clip order
        reordered_clips = []
        for clip_id in clip_ids:
            for clip in clips:
                if clip.get("clip_id") == clip_id:
                    reordered_clips.append(clip)
                    break

        # Update positions
        position = 0
        for clip in reordered_clips:
            clip["position"] = position
            position += clip.get("duration", 0)

        current_playlist["clips"] = reordered_clips
        current_playlist["updated_at"] = datetime.now().isoformat() + "Z"

        # Save and refresh
        self.save_playlists()
        self.load_timeline(current_playlist)

        print("Reordered clips in playlist")

    def extract_sequence_from_filename(self, filename):
        """Extract sequence from filename."""
        import re
        match = re.search(r'(seq\d+)', filename.lower())
        return match.group(1) if match else "unknown"

    def extract_shot_from_filename(self, filename):
        """Extract shot from filename."""
        import re
        match = re.search(r'(shot\d+)', filename.lower())
        return match.group(1) if match else "unknown"

    def get_current_playlist_data(self):
        """Get the current playlist data."""
        if not self.current_playlist_id:
            return None

        for playlist in self.playlists_data:
            if playlist["_id"] == self.current_playlist_id:
                return playlist
        return None
