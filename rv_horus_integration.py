#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Open RV MediaBrowser with Horus Integration
===========================================

Integrates our modular MediaBrowser dock widgets with Horus's JSON database
to display media data from the Horus application within Open RV.
"""

import sys
import os
import json
from pathlib import Path

print("Loading Open RV MediaBrowser with Horus integration...")

# ============================================================================
# Horus Data Connector - Inline Implementation
# ============================================================================

class HorusDataConnector:
    """
    Connects to Horus JSON database for read-only access.
    Provides data for MediaBrowser widgets.
    """

    def __init__(self, data_dir="sample_db"):
        """Initialize connector with data directory."""
        self.data_dir = Path(data_dir)
        self.current_project_id = None
        print(f"📂 Horus Data Directory: {self.data_dir.absolute()}")

    def _load_json_file(self, filename):
        """Load JSON file from data directory."""
        file_path = self.data_dir / filename
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ Loaded {filename}: {len(data) if isinstance(data, list) else 'OK'}")
                return data
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")
                return [] if filename.endswith('.json') else {}
        else:
            print(f"⚠️  File not found: {file_path}")
            return [] if filename.endswith('.json') else {}

    def is_available(self):
        """Check if data directory and files are available."""
        if not self.data_dir.exists():
            print(f"❌ Data directory not found: {self.data_dir}")
            return False

        # Check for at least one data file
        required_files = ["project_configs.json", "media_records.json"]
        for filename in required_files:
            if (self.data_dir / filename).exists():
                return True

        print(f"⚠️  No data files found in {self.data_dir}")
        return False

    def set_current_project(self, project_id):
        """Set the current project ID."""
        self.current_project_id = project_id
        print(f"📁 Current project set to: {project_id}")

    def get_available_projects(self):
        """Get list of available projects."""
        return self._load_json_file("project_configs.json")

    def get_media_records(self):
        """Get all media records."""
        return self._load_json_file("media_records.json")

    def get_media_for_project(self, project_id):
        """Get media records for specific project."""
        all_media = self.get_media_records()
        return [m for m in all_media if m.get("project_id") == project_id]

    def get_playlists(self):
        """Get all playlists."""
        return self._load_json_file("horus_playlists.json")

    def get_annotations(self):
        """Get all annotations."""
        return self._load_json_file("annotations.json")

    def get_tasks(self):
        """Get all tasks."""
        return self._load_json_file("tasks.json")

def get_horus_connector(data_dir="sample_db"):
    """Factory function to create Horus data connector."""
    return HorusDataConnector(data_dir)

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        import sys
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Global references
search_dock = None
comments_dock = None
timeline_dock = None
media_grid_dock = None
timeline_playlist_dock = None  # New Timeline Playlist Widget
horus_connector = None
current_project_id = None
annotations_popup_window = None

# Feature flags
ENABLE_TIMELINE_PLAYLIST = True   # Enable/disable Timeline Playlist feature
ENABLE_LEGACY_TIMELINE = False    # Disable legacy Timeline Sequence panel

# Timeline Playlist global data
timeline_playlist_data = []
current_playlist_id = None

def create_comments_panel():
    """Create comments and annotations panel."""
    try:
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                                       QLabel, QPushButton, QFrame, QListWidget,
                                       QListWidgetItem, QSplitter, QLineEdit,
                                       QComboBox, QScrollArea, QGroupBox)
        from PySide2.QtCore import Qt, QTimer

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Clean header matching reference design
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(5, 5, 5, 5)

        # Comments title with count
        comments_title = QLabel("Comments (23)")
        comments_title.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 14px;")
        header_layout.addWidget(comments_title)

        header_layout.addStretch()

        # Frame info display (compact)
        frame_info_label = QLabel("Frame: --")
        frame_info_label.setObjectName("frame_info_label")
        frame_info_label.setStyleSheet("color: #888888; font-size: 10px;")
        header_layout.addWidget(frame_info_label)

        # Essential action buttons
        rv_paint_btn = QPushButton("Paint")
        rv_paint_btn.setObjectName("rv_paint_btn")
        rv_paint_btn.setMaximumWidth(50)
        rv_paint_btn.setStyleSheet("font-size: 10px; padding: 2px 4px;")
        header_layout.addWidget(rv_paint_btn)

        annotations_popup_btn = QPushButton("Annotations")
        annotations_popup_btn.setObjectName("annotations_popup_btn")
        annotations_popup_btn.setMaximumWidth(70)
        annotations_popup_btn.setStyleSheet("font-size: 10px; padding: 2px 4px;")
        header_layout.addWidget(annotations_popup_btn)

        layout.addWidget(header_frame)

        # Dynamic comments area - scales with panel height
        comments_scroll = QScrollArea()
        comments_scroll.setWidgetResizable(True)
        comments_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        comments_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        comments_scroll.setFrameStyle(QFrame.NoFrame)  # Clean appearance

        comments_container = QWidget()
        comments_container_layout = QVBoxLayout(comments_container)
        comments_container_layout.setContentsMargins(5, 5, 5, 5)
        comments_container_layout.setSpacing(10)

        # Add sample VFX comments with threading
        sample_comments = create_sample_vfx_comments()
        for comment_data in sample_comments:
            comment_widget = create_comment_widget(comment_data)
            comments_container_layout.addWidget(comment_widget)

        comments_container_layout.addStretch()
        comments_scroll.setWidget(comments_container)

        # Add scroll area to main layout with stretch factor for dynamic scaling
        layout.addWidget(comments_scroll, 1)  # Stretch factor 1 = takes available space

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #555555;")
        layout.addWidget(separator)

        # Fixed comment input area at bottom
        comment_input_frame = QFrame()
        comment_input_layout = QVBoxLayout(comment_input_frame)
        comment_input_layout.setContentsMargins(5, 5, 5, 5)

        comment_text = QTextEdit()
        comment_text.setMaximumHeight(40)
        comment_text.setMinimumHeight(40)  # Fixed height for input
        comment_text.setPlaceholderText("Add a comment...")
        comment_text.setObjectName("comment_text")
        comment_input_layout.addWidget(comment_text)

        comment_buttons_frame = QFrame()
        comment_buttons_layout = QHBoxLayout(comment_buttons_frame)
        comment_buttons_layout.setContentsMargins(0, 0, 0, 0)

        add_comment_btn = QPushButton("Comment")
        add_comment_btn.setObjectName("add_comment_btn")
        comment_buttons_layout.addWidget(add_comment_btn)

        add_frame_comment_btn = QPushButton("Frame Comment")
        add_frame_comment_btn.setObjectName("add_frame_comment_btn")
        comment_buttons_layout.addWidget(add_frame_comment_btn)

        comment_buttons_layout.addStretch()
        comment_input_layout.addWidget(comment_buttons_frame)

        # Add input area to main layout with no stretch (fixed at bottom)
        layout.addWidget(comment_input_frame, 0)  # Stretch factor 0 = fixed size

        # Store references
        widget.frame_info_label = frame_info_label
        widget.comments_title = comments_title
        widget.rv_paint_btn = rv_paint_btn
        widget.annotations_popup_btn = annotations_popup_btn
        widget.comments_scroll = comments_scroll
        widget.comments_container = comments_container
        widget.comment_text = comment_text
        widget.add_comment_btn = add_comment_btn
        widget.add_frame_comment_btn = add_frame_comment_btn

        # Connect signals
        rv_paint_btn.clicked.connect(on_open_rv_paint)
        annotations_popup_btn.clicked.connect(on_open_annotations_popup)
        add_comment_btn.clicked.connect(on_add_comment)
        add_frame_comment_btn.clicked.connect(on_add_frame_comment)

        return widget

    except Exception as e:
        print(f"Error creating comments panel: {e}")
        return None

def create_sample_vfx_comments():
    """Create sample VFX review comments with realistic content."""
    return [
        {
            "id": 1,
            "user": "John Doe",
            "avatar": "JD",
            "time": "2 hours ago",
            "frame": None,
            "text": "The lighting in this shot looks great! Ready for comp.",
            "likes": 5,
            "replies": [
                {
                    "id": 2,
                    "user": "Jane Smith",
                    "avatar": "JS",
                    "time": "1 hour ago",
                    "text": "@john.doe Agreed! Color temp is perfect.",
                    "likes": 2
                },
                {
                    "id": 3,
                    "user": "Mike Wilson",
                    "avatar": "MW",
                    "time": "30 min ago",
                    "text": "Can we get a version without the rim light?",
                    "likes": 1
                }
            ]
        },
        {
            "id": 4,
            "user": "Sarah Chen",
            "avatar": "SC",
            "time": "3 hours ago",
            "frame": 1047,
            "text": "The eye line doesn't match the previous shot",
            "likes": 3,
            "priority": "High",
            "status": "Open",
            "replies": [
                {
                    "id": 5,
                    "user": "Director",
                    "avatar": "DR",
                    "time": "2 hours ago",
                    "text": "Good catch! Please adjust in animation.",
                    "likes": 1
                }
            ]
        },
        {
            "id": 6,
            "user": "Alex Rodriguez",
            "avatar": "AR",
            "time": "4 hours ago",
            "frame": 1089,
            "text": "Shadows are too dark in this area - needs color correction",
            "likes": 1,
            "priority": "Medium",
            "status": "Resolved",
            "replies": []
        },
        {
            "id": 7,
            "user": "Emily Davis",
            "avatar": "ED",
            "time": "5 hours ago",
            "text": "Overall composition looks fantastic! Great work team.",
            "likes": 8,
            "replies": [
                {
                    "id": 8,
                    "user": "Tom Anderson",
                    "avatar": "TA",
                    "time": "4 hours ago",
                    "text": "Thanks! The new camera angle really helps.",
                    "likes": 2
                }
            ]
        }
    ]

def create_comment_widget(comment_data):
    """Create a threaded comment widget following Facebook/Slack patterns."""
    try:
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                       QPushButton, QFrame, QTextEdit)
        from PySide2.QtCore import Qt

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Main comment
        comment_frame = QFrame()
        comment_layout = QHBoxLayout(comment_frame)
        comment_layout.setContentsMargins(5, 5, 5, 5)
        comment_layout.setSpacing(8)

        # Slightly smaller avatar (15% reduction: 32px -> 28px)
        avatar_label = QLabel(comment_data["avatar"])
        avatar_label.setFixedSize(28, 28)  # 15% smaller than original 32x32
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setStyleSheet("""
            QLabel {
                background-color: #0078d7;
                color: white;
                border-radius: 14px;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        comment_layout.addWidget(avatar_label)

        # Comment content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(3)

        # Header with user and time
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        user_label = QLabel(comment_data["user"])
        user_label.setStyleSheet("font-weight: bold; color: #e0e0e0;")
        header_layout.addWidget(user_label)

        time_label = QLabel(comment_data["time"])
        time_label.setStyleSheet("color: #888888; font-size: 10px;")
        header_layout.addWidget(time_label)

        # Frame indicator if present
        if comment_data.get("frame"):
            frame_label = QLabel(f"Frame {comment_data['frame']}")
            frame_label.setStyleSheet("color: #0078d7; font-size: 10px; font-weight: bold;")
            header_layout.addWidget(frame_label)

        # Priority and status if present
        if comment_data.get("priority"):
            priority_label = QLabel(f"Priority: {comment_data['priority']}")
            priority_color = "#ff4444" if comment_data["priority"] == "High" else "#ffaa00"
            priority_label.setStyleSheet(f"color: {priority_color}; font-size: 10px;")
            header_layout.addWidget(priority_label)

        if comment_data.get("status"):
            status_label = QLabel(f"Status: {comment_data['status']}")
            status_color = "#44ff44" if comment_data["status"] == "Resolved" else "#ffaa00"
            status_label.setStyleSheet(f"color: {status_color}; font-size: 10px;")
            header_layout.addWidget(status_label)

        header_layout.addStretch()
        content_layout.addLayout(header_layout)

        # Comment text
        text_label = QLabel(comment_data["text"])
        text_label.setWordWrap(True)
        text_label.setStyleSheet("color: #e0e0e0; padding: 2px 0px;")
        content_layout.addWidget(text_label)

        # Actions (likes, reply)
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)

        like_btn = QPushButton(f"Like {comment_data['likes']}")
        like_btn.setFlat(True)
        like_btn.setStyleSheet("color: #888888; font-size: 10px; border: none; padding: 2px 4px;")
        actions_layout.addWidget(like_btn)

        reply_btn = QPushButton("Reply")
        reply_btn.setFlat(True)
        reply_btn.setStyleSheet("color: #888888; font-size: 10px; border: none; padding: 2px 4px;")
        reply_btn.setObjectName(f"reply_btn_{comment_data['id']}")
        actions_layout.addWidget(reply_btn)

        actions_layout.addStretch()
        content_layout.addLayout(actions_layout)

        # Reply input area (initially hidden)
        reply_input_frame = QFrame()
        reply_input_frame.setObjectName(f"reply_input_{comment_data['id']}")
        reply_input_frame.setVisible(False)  # Hidden by default
        reply_input_layout = QVBoxLayout(reply_input_frame)
        reply_input_layout.setContentsMargins(0, 5, 0, 5)

        reply_text = QTextEdit()
        reply_text.setMaximumHeight(30)
        reply_text.setMinimumHeight(30)
        reply_text.setPlaceholderText("Write a reply...")
        reply_text.setObjectName(f"reply_text_{comment_data['id']}")
        reply_input_layout.addWidget(reply_text)

        reply_buttons_layout = QHBoxLayout()
        reply_buttons_layout.setContentsMargins(0, 0, 0, 0)

        post_reply_btn = QPushButton("Post Reply")
        post_reply_btn.setObjectName(f"post_reply_{comment_data['id']}")
        post_reply_btn.setMaximumWidth(80)
        post_reply_btn.setStyleSheet("font-size: 10px; padding: 2px 4px;")
        reply_buttons_layout.addWidget(post_reply_btn)

        cancel_reply_btn = QPushButton("Cancel")
        cancel_reply_btn.setObjectName(f"cancel_reply_{comment_data['id']}")
        cancel_reply_btn.setMaximumWidth(50)
        cancel_reply_btn.setStyleSheet("font-size: 10px; padding: 2px 4px;")
        reply_buttons_layout.addWidget(cancel_reply_btn)

        reply_buttons_layout.addStretch()
        reply_input_layout.addLayout(reply_buttons_layout)

        content_layout.addWidget(reply_input_frame)

        # Connect reply button signals
        reply_btn.clicked.connect(lambda: show_reply_input(comment_data['id']))
        post_reply_btn.clicked.connect(lambda: post_reply(comment_data['id']))
        cancel_reply_btn.clicked.connect(lambda: hide_reply_input(comment_data['id']))

        comment_layout.addLayout(content_layout)
        main_layout.addWidget(comment_frame)

        # Replies with indentation
        if comment_data.get("replies"):
            for reply in comment_data["replies"]:
                reply_widget = create_reply_widget(reply)
                main_layout.addWidget(reply_widget)

        return main_widget

    except Exception as e:
        print(f"Error creating comment widget: {e}")
        return QWidget()

def create_reply_widget(reply_data):
    """Create a reply widget with indentation."""
    try:
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                       QPushButton, QFrame, QTextEdit)
        from PySide2.QtCore import Qt

        reply_widget = QWidget()
        reply_layout = QHBoxLayout(reply_widget)
        reply_layout.setContentsMargins(35, 0, 0, 0)  # 15% less indentation (40px -> 35px)
        reply_layout.setSpacing(6)  # Slightly reduced spacing

        # Connecting line
        line_frame = QFrame()
        line_frame.setFixedWidth(2)
        line_frame.setStyleSheet("background-color: #555555;")
        reply_layout.addWidget(line_frame)

        # Reply content
        content_frame = QFrame()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(8)

        # Slightly smaller reply avatar (15% reduction: 24px -> 20px)
        avatar_label = QLabel(reply_data["avatar"])
        avatar_label.setFixedSize(20, 20)  # 15% smaller than original 24x24
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setStyleSheet("""
            QLabel {
                background-color: #666666;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 9px;
            }
        """)
        content_layout.addWidget(avatar_label)

        # Reply text content
        text_content_layout = QVBoxLayout()
        text_content_layout.setSpacing(2)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        user_label = QLabel(reply_data["user"])
        user_label.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 11px;")
        header_layout.addWidget(user_label)

        time_label = QLabel(reply_data["time"])
        time_label.setStyleSheet("color: #888888; font-size: 9px;")
        header_layout.addWidget(time_label)

        header_layout.addStretch()
        text_content_layout.addLayout(header_layout)

        # Reply text
        text_label = QLabel(reply_data["text"])
        text_label.setWordWrap(True)
        text_label.setStyleSheet("color: #e0e0e0; font-size: 11px;")
        text_content_layout.addWidget(text_label)

        # Reply actions
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)

        like_btn = QPushButton(f"Like {reply_data['likes']}")
        like_btn.setFlat(True)
        like_btn.setStyleSheet("color: #888888; font-size: 9px; border: none; padding: 1px 2px;")
        actions_layout.addWidget(like_btn)

        reply_btn = QPushButton("Reply")
        reply_btn.setFlat(True)
        reply_btn.setStyleSheet("color: #888888; font-size: 9px; border: none; padding: 1px 2px;")
        reply_btn.setObjectName(f"reply_btn_{reply_data['id']}")
        actions_layout.addWidget(reply_btn)

        actions_layout.addStretch()
        text_content_layout.addLayout(actions_layout)

        # Reply input area for nested replies (initially hidden)
        reply_input_frame = QFrame()
        reply_input_frame.setObjectName(f"reply_input_{reply_data['id']}")
        reply_input_frame.setVisible(False)
        reply_input_layout = QVBoxLayout(reply_input_frame)
        reply_input_layout.setContentsMargins(0, 3, 0, 3)

        reply_text = QTextEdit()
        reply_text.setMaximumHeight(25)
        reply_text.setMinimumHeight(25)
        reply_text.setPlaceholderText("Write a reply...")
        reply_text.setObjectName(f"reply_text_{reply_data['id']}")
        reply_input_layout.addWidget(reply_text)

        reply_buttons_layout = QHBoxLayout()
        reply_buttons_layout.setContentsMargins(0, 0, 0, 0)

        post_reply_btn = QPushButton("Post")
        post_reply_btn.setObjectName(f"post_reply_{reply_data['id']}")
        post_reply_btn.setMaximumWidth(40)
        post_reply_btn.setStyleSheet("font-size: 9px; padding: 1px 2px;")
        reply_buttons_layout.addWidget(post_reply_btn)

        cancel_reply_btn = QPushButton("Cancel")
        cancel_reply_btn.setObjectName(f"cancel_reply_{reply_data['id']}")
        cancel_reply_btn.setMaximumWidth(45)
        cancel_reply_btn.setStyleSheet("font-size: 9px; padding: 1px 2px;")
        reply_buttons_layout.addWidget(cancel_reply_btn)

        reply_buttons_layout.addStretch()
        reply_input_layout.addLayout(reply_buttons_layout)

        text_content_layout.addWidget(reply_input_frame)

        # Connect reply button signals
        reply_btn.clicked.connect(lambda: show_reply_input(reply_data['id']))
        post_reply_btn.clicked.connect(lambda: post_reply(reply_data['id']))
        cancel_reply_btn.clicked.connect(lambda: hide_reply_input(reply_data['id']))

        content_layout.addLayout(text_content_layout)
        reply_layout.addWidget(content_frame)

        return reply_widget

    except Exception as e:
        print(f"Error creating reply widget: {e}")
        return QWidget()

def create_timeline_playlist_panel():
    """Create Playlist Manager panel with tree (top) + shot table (bottom)."""
    try:
        from PySide2.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
            QFrame, QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
            QAbstractItemView, QHeaderView, QCheckBox
        )
        from PySide2.QtCore import Qt
        from PySide2.QtGui import QColor

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # ===== TOP HALF: Playlist Tree =====
        tree_label = QLabel("Playlists:")
        tree_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
            }
        """)
        layout.addWidget(tree_label)

        # Playlist tree widget
        playlist_tree = QTreeWidget()
        playlist_tree.setHeaderHidden(True)
        playlist_tree.setRootIsDecorated(True)
        playlist_tree.setSelectionMode(QAbstractItemView.SingleSelection)
        playlist_tree.setMaximumHeight(200)  # Limit height to make room for shot table
        playlist_tree.setStyleSheet("""
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
        """)
        playlist_tree.itemSelectionChanged.connect(on_playlist_tree_selection_changed)
        playlist_tree.itemDoubleClicked.connect(on_playlist_double_clicked)
        layout.addWidget(playlist_tree)

        # Playlist controls
        playlist_controls = QFrame()
        playlist_controls.setFixedHeight(40)
        playlist_controls.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #404040;
                color: #e0e0e0;
                border: 1px solid #555555;
                padding: 5px 10px;
                border-radius: 2px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #0078d4;
            }
        """)

        playlist_controls_layout = QHBoxLayout(playlist_controls)
        playlist_controls_layout.setContentsMargins(5, 5, 5, 5)
        playlist_controls_layout.setSpacing(5)

        new_playlist_btn = QPushButton("New Playlist")
        new_playlist_btn.clicked.connect(create_new_playlist)
        playlist_controls_layout.addWidget(new_playlist_btn)

        duplicate_btn = QPushButton("Duplicate")
        duplicate_btn.clicked.connect(duplicate_current_playlist)
        playlist_controls_layout.addWidget(duplicate_btn)

        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(rename_current_playlist)
        playlist_controls_layout.addWidget(rename_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(delete_current_playlist)
        playlist_controls_layout.addWidget(delete_btn)

        layout.addWidget(playlist_controls)

        # ===== BOTTOM HALF: Shot Table =====
        shot_label = QLabel("Shots in Playlist: (0)")
        shot_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
                margin-top: 10px;
            }
        """)
        layout.addWidget(shot_label)

        # Shot table widget - Same format as Navigator: Name, Version, Status
        shot_table = QTableWidget()
        shot_table.setColumnCount(3)
        shot_table.setHorizontalHeaderLabels(["Name", "Version", "Status"])
        shot_table.setSelectionBehavior(QTableWidget.SelectRows)
        shot_table.setSelectionMode(QAbstractItemView.MultiSelection)
        shot_table.setSortingEnabled(True)
        shot_table.setAlternatingRowColors(True)
        shot_table.verticalHeader().setVisible(False)

        # Make columns fit content
        from PySide2.QtWidgets import QHeaderView
        header = shot_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name - stretch
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Version
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Status

        # Set row height
        shot_table.verticalHeader().setDefaultSectionSize(25)

        shot_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #555555;
                gridline-color: #3a3a3a;
                selection-background-color: #0078d4;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QHeaderView::section {
                background-color: #3a3a3a;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #555555;
                font-weight: bold;
            }
        """)

        # Connect handlers (placeholder for now)
        shot_table.setContextMenuPolicy(Qt.CustomContextMenu)
        # shot_table.customContextMenuRequested.connect(show_shot_context_menu)
        # shot_table.itemDoubleClicked.connect(load_shot_in_rv)

        layout.addWidget(shot_table)

        # Shot action controls
        shot_controls = QFrame()
        shot_controls.setFixedHeight(40)
        shot_controls.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #404040;
                color: #e0e0e0;
                border: 1px solid #555555;
                padding: 5px 10px;
                border-radius: 2px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #0078d4;
            }
            QComboBox {
                background-color: #404040;
                color: #e0e0e0;
                border: 1px solid #555555;
                padding: 3px 8px;
                border-radius: 2px;
                font-size: 11px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 11px;
            }
        """)

        shot_controls_layout = QHBoxLayout(shot_controls)
        shot_controls_layout.setContentsMargins(5, 5, 5, 5)
        shot_controls_layout.setSpacing(5)

        # Status control
        shot_controls_layout.addWidget(QLabel("Status:"))
        status_combo = QComboBox()
        status_combo.addItems(["submit", "need fix", "approved"])
        shot_controls_layout.addWidget(status_combo)

        set_status_btn = QPushButton("Set Status")
        # set_status_btn.clicked.connect(set_selected_shots_status)
        shot_controls_layout.addWidget(set_status_btn)

        shot_controls_layout.addStretch()

        # Shot management
        remove_btn = QPushButton("Remove Selected")
        # remove_btn.clicked.connect(remove_selected_shots)
        shot_controls_layout.addWidget(remove_btn)

        clear_btn = QPushButton("Clear All")
        # clear_btn.clicked.connect(clear_all_shots)
        shot_controls_layout.addWidget(clear_btn)

        # Playback
        load_rv_btn = QPushButton("Load in RV")
        # load_rv_btn.clicked.connect(load_selected_shots_in_rv)
        shot_controls_layout.addWidget(load_rv_btn)

        export_btn = QPushButton("Export")
        # export_btn.clicked.connect(export_playlist)
        shot_controls_layout.addWidget(export_btn)

        layout.addWidget(shot_controls)

        # Load initial data
        load_timeline_playlist_data()

        # Store references
        widget._playlist_tree = playlist_tree
        widget.playlist_tree = playlist_tree
        widget.shot_table = shot_table
        widget.shot_label = shot_label
        widget.status_combo = status_combo

        print("✅ Playlist Manager panel created successfully (UI only)")
        return widget

    except Exception as e:
        print(f"Error creating Playlist Manager panel: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_timeline_playlist_header():
    """Create header with title and main controls."""
    from PySide2.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

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
    new_playlist_btn.clicked.connect(create_new_playlist)
    layout.addWidget(new_playlist_btn)

    refresh_btn = QPushButton("Refresh")
    refresh_btn.clicked.connect(refresh_timeline_playlists)
    layout.addWidget(refresh_btn)

    # Store references
    header.new_playlist_btn = new_playlist_btn
    header.refresh_btn = refresh_btn

    return header

def create_playlist_tree_panel():
    """Create left panel with playlist tree and controls."""
    from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeWidget, QAbstractItemView, QFrame, QGridLayout, QPushButton

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
    playlist_tree = QTreeWidget()
    playlist_tree.setHeaderHidden(True)
    playlist_tree.setRootIsDecorated(True)
    playlist_tree.setSelectionMode(QAbstractItemView.SingleSelection)
    playlist_tree.setDragDropMode(QAbstractItemView.InternalMove)

    # Setup tree styling
    playlist_tree.setStyleSheet("""
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
    """)

    # Connect selection handler
    playlist_tree.itemSelectionChanged.connect(on_playlist_tree_selection_changed)
    playlist_tree.itemDoubleClicked.connect(on_playlist_double_clicked)

    layout.addWidget(playlist_tree)

    # Playlist controls
    controls = QFrame()
    controls.setFixedHeight(56)  # Reduced by 30% (80 * 0.7 = 56)
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

    controls_layout = QGridLayout(controls)
    controls_layout.setContentsMargins(5, 5, 5, 5)
    controls_layout.setSpacing(3)

    # Playlist controls
    duplicate_btn = QPushButton("Duplicate")
    duplicate_btn.clicked.connect(duplicate_current_playlist)
    controls_layout.addWidget(duplicate_btn, 0, 0)

    rename_btn = QPushButton("Rename")
    rename_btn.clicked.connect(rename_current_playlist)
    controls_layout.addWidget(rename_btn, 0, 1)

    delete_btn = QPushButton("Delete")
    delete_btn.clicked.connect(delete_current_playlist)
    controls_layout.addWidget(delete_btn, 1, 0)

    add_media_btn = QPushButton("Add Media")
    add_media_btn.clicked.connect(show_add_media_dialog)
    controls_layout.addWidget(add_media_btn, 1, 1)

    layout.addWidget(controls)

    # Store references
    panel.playlist_tree = playlist_tree
    panel.controls = controls

    return panel

def create_timeline_tracks_panel():
    """Create right panel with timeline tracks."""
    from PySide2.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QFrame, QHBoxLayout, QPushButton, QComboBox
    from PySide2.QtCore import Qt

    panel = QWidget()

    layout = QVBoxLayout(panel)
    layout.setContentsMargins(5, 5, 5, 5)
    layout.setSpacing(5)

    # Timeline header with controls
    timeline_header = QFrame()
    timeline_header.setFixedHeight(40)  # Original demo size - more spacious
    timeline_header.setStyleSheet("""
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

    header_layout = QHBoxLayout(timeline_header)
    header_layout.setContentsMargins(10, 5, 10, 5)

    # Current playlist name
    current_playlist_label = QLabel("No playlist selected")
    current_playlist_label.setStyleSheet("font-weight: bold;")
    header_layout.addWidget(current_playlist_label)

    header_layout.addStretch()

    # Timeline controls
    play_btn = QPushButton("▶ Play")
    play_btn.clicked.connect(play_current_playlist)
    header_layout.addWidget(play_btn)

    stop_btn = QPushButton("⏹ Stop")
    stop_btn.clicked.connect(stop_playlist_playback)
    header_layout.addWidget(stop_btn)

    # Zoom controls
    zoom_label = QLabel("Zoom:")
    header_layout.addWidget(zoom_label)

    zoom_combo = QComboBox()
    zoom_combo.addItems(["25%", "50%", "75%", "100%", "150%", "200%", "Fit"])
    zoom_combo.setCurrentText("100%")
    zoom_combo.currentTextChanged.connect(on_timeline_zoom_changed)
    header_layout.addWidget(zoom_combo)

    layout.addWidget(timeline_header)

    # Timeline scroll area
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    # Timeline content widget
    timeline_content = QWidget()
    timeline_layout = QVBoxLayout(timeline_content)
    timeline_layout.setContentsMargins(0, 0, 0, 0)
    timeline_layout.setSpacing(2)

    # Add empty message initially
    empty_label = QLabel("Select a playlist to view timeline")
    empty_label.setStyleSheet("""
        QLabel {
            color: #888888;
            font-size: 14px;
            padding: 20px;
            text-align: center;
        }
    """)
    empty_label.setAlignment(Qt.AlignCenter)
    timeline_layout.addWidget(empty_label)

    scroll_area.setWidget(timeline_content)
    layout.addWidget(scroll_area)

    # Store references
    panel.timeline_header = timeline_header
    panel.current_playlist_label = current_playlist_label
    panel.timeline_content = timeline_content
    panel.timeline_layout = timeline_layout
    panel.scroll_area = scroll_area

    return panel

def load_timeline_playlist_data():
    """Load playlist data from JSON database."""
    global timeline_playlist_data

    try:
        import json
        import os

        # Load playlists using resource path for bundled executable
        playlist_file = os.path.join(get_resource_path("sample_db"), "horus_playlists.json")
        print(f"Looking for playlist file at: {playlist_file}")

        if os.path.exists(playlist_file):
            with open(playlist_file, 'r', encoding='utf-8') as f:
                timeline_playlist_data = json.load(f)
                print(f"✅ Loaded {len(timeline_playlist_data)} playlists from bundled resources")

                # Print playlist names for verification
                for playlist in timeline_playlist_data:
                    clip_count = len(playlist.get('clips', []))
                    metadata_count = playlist.get('metadata', {}).get('clip_count', 0)
                    print(f"   - {playlist.get('name', 'Unnamed')} ({clip_count} clips, metadata: {metadata_count})")
        else:
            # Fallback to local file for development
            local_playlist_file = os.path.join("sample_db", "horus_playlists.json")
            if os.path.exists(local_playlist_file):
                with open(local_playlist_file, 'r', encoding='utf-8') as f:
                    timeline_playlist_data = json.load(f)
                    print(f"✅ Loaded {len(timeline_playlist_data)} playlists from local file")
            else:
                timeline_playlist_data = []
                print("⚠️  No playlist file found, starting with empty playlists")

    except Exception as e:
        print(f"❌ Error loading playlist data: {e}")
        import traceback
        traceback.print_exc()
        timeline_playlist_data = []

def save_timeline_playlist_data():
    """Save playlist data to JSON database."""
    try:
        import json
        import os

        # Try to save to bundled resource path first, fallback to local
        try:
            playlist_file = os.path.join(get_resource_path("sample_db"), "horus_playlists.json")
            with open(playlist_file, 'w', encoding='utf-8') as f:
                json.dump(timeline_playlist_data, f, indent=2)
            print("✅ Playlist data saved to bundled resources")
        except (OSError, PermissionError):
            # Fallback to local file (bundled resources are read-only)
            local_playlist_file = os.path.join("sample_db", "horus_playlists.json")
            with open(local_playlist_file, 'w', encoding='utf-8') as f:
                json.dump(timeline_playlist_data, f, indent=2)
            print("✅ Playlist data saved to local file")

    except Exception as e:
        print(f"❌ Error saving playlist data: {e}")

def populate_playlist_tree():
    """Populate the playlist tree with data."""
    global timeline_playlist_dock

    print(f"🌳 Populating playlist tree...")
    print(f"   timeline_playlist_dock: {timeline_playlist_dock is not None}")
    print(f"   timeline_playlist_data: {len(timeline_playlist_data) if timeline_playlist_data else 0} playlists")

    if not timeline_playlist_dock or not timeline_playlist_dock.widget():
        print("❌ Timeline playlist dock not available for tree population")
        return

    try:
        from PySide2.QtWidgets import QTreeWidgetItem
        from PySide2.QtCore import Qt
        from PySide2.QtGui import QColor

        widget = timeline_playlist_dock.widget()
        playlist_tree = widget.left_panel.playlist_tree
        playlist_tree.clear()

        if not timeline_playlist_data:
            print("❌ No playlist data available")
            return

        # Group playlists by project
        projects = {}
        for playlist in timeline_playlist_data:
            project_id = playlist.get("project_id", "unknown")
            if project_id not in projects:
                projects[project_id] = []
            projects[project_id].append(playlist)

        # Create tree structure
        for project_id, playlists in projects.items():
            project_item = QTreeWidgetItem(playlist_tree)
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
        playlist_tree.expandAll()

        print(f"✅ Playlist tree populated with {len(timeline_playlist_data)} playlists across {len(projects)} projects")

    except Exception as e:
        print(f"❌ Error populating playlist tree: {e}")
        import traceback
        traceback.print_exc()

def on_playlist_tree_selection_changed():
    """Handle playlist selection change."""
    global timeline_playlist_dock, current_playlist_id

    if not timeline_playlist_dock or not timeline_playlist_dock.widget():
        return

    try:
        from PySide2.QtCore import Qt
        widget = timeline_playlist_dock.widget()
        playlist_tree = widget.left_panel.playlist_tree
        selected_items = playlist_tree.selectedItems()

        if not selected_items:
            current_playlist_id = None
            widget.right_panel.current_playlist_label.setText("No playlist selected")
            clear_timeline_display()
            return

        item = selected_items[0]
        item_data = item.data(0, Qt.UserRole)

        if item_data and item_data.get("type") == "playlist":
            playlist_id = item_data["id"]
            playlist_data = item_data["data"]

            current_playlist_id = playlist_id
            widget.right_panel.current_playlist_label.setText(f"Playlist: {playlist_data.get('name', 'Unnamed')}")

            # Load timeline for this playlist
            load_playlist_timeline(playlist_data)

            print(f"Selected playlist: {playlist_id}")

    except Exception as e:
        print(f"Error handling playlist selection: {e}")

def on_playlist_double_clicked(item, column):
    """Handle playlist double-click to start playback."""
    try:
        from PySide2.QtCore import Qt
        item_data = item.data(0, Qt.UserRole)
        if item_data and item_data.get("type") == "playlist":
            play_current_playlist()
    except Exception as e:
        print(f"Error handling playlist double-click: {e}")

def load_playlist_timeline(playlist_data):
    """Load timeline visualization for the given playlist."""
    global timeline_playlist_dock

    if not timeline_playlist_dock or not timeline_playlist_dock.widget():
        print("❌ Timeline playlist dock not available")
        return

    try:
        widget = timeline_playlist_dock.widget()
        clear_timeline_display()

        clips = playlist_data.get("clips", [])
        tracks = playlist_data.get("tracks", [])

        print(f"🎬 Loading timeline for playlist: {playlist_data.get('name', 'Unknown')}")
        print(f"   Clips: {len(clips)}, Tracks: {len(tracks)}")

        if not clips:
            # Show empty timeline message
            from PySide2.QtWidgets import QLabel
            from PySide2.QtCore import Qt

            empty_label = QLabel("No clips in this playlist\nRight-click media items to add them")
            empty_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 14px;
                    padding: 20px;
                    text-align: center;
                }
            """)
            empty_label.setAlignment(Qt.AlignCenter)
            widget.right_panel.timeline_layout.addWidget(empty_label)
            print("   Empty playlist - showing message")
            return

        # Create timeline ruler
        ruler = create_timeline_ruler(clips)
        widget.right_panel.timeline_layout.addWidget(ruler)
        print("   ✅ Timeline ruler created")

        # Create tracks
        for track in tracks:
            track_widget = create_timeline_track_widget(track, clips)
            widget.right_panel.timeline_layout.addWidget(track_widget)
            print(f"   ✅ Track created: {track.get('name', 'Unknown')}")

        # Add stretch to push tracks to top
        widget.right_panel.timeline_layout.addStretch()

        print(f"   ✅ Timeline loaded successfully")

    except Exception as e:
        print(f"❌ Error loading playlist timeline: {e}")
        import traceback
        traceback.print_exc()

def clear_timeline_display():
    """Clear the timeline display."""
    global timeline_playlist_dock

    if not timeline_playlist_dock or not timeline_playlist_dock.widget():
        return

    try:
        widget = timeline_playlist_dock.widget()
        timeline_layout = widget.right_panel.timeline_layout

        # Remove all widgets from timeline layout
        while timeline_layout.count():
            child = timeline_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    except Exception as e:
        print(f"Error clearing timeline display: {e}")

def create_timeline_ruler(clips):
    """Create timeline ruler with timecode markers."""
    from PySide2.QtWidgets import QFrame, QHBoxLayout, QLabel
    from PySide2.QtCore import Qt

    ruler = QFrame()
    ruler.setFixedHeight(25)  # Legacy timeline size - compact proportions
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
    layout.setContentsMargins(80, 0, 0, 0)  # Offset for track labels (matches professional label width)
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
            marker.setFixedWidth(150)  # Original demo size - better proportions
            marker.setAlignment(Qt.AlignCenter)
            layout.addWidget(marker)

    layout.addStretch()
    return ruler

def create_timeline_track_widget(track_data, clips):
    """Create a timeline track widget with clips."""
    from PySide2.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget, QPushButton
    from PySide2.QtCore import Qt

    track = QFrame()
    track_height = track_data.get("height", 45)  # Legacy timeline size - compact and professional
    track.setFixedHeight(track_height)
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
    track_label.setFixedSize(80, 45)  # Legacy timeline proportions - match track height
    track_label.setStyleSheet("""
        QLabel {
            background-color: #3a3a3a;
            color: #e0e0e0;
            padding: 0px;
            border-right: 1px solid #555555;
            font-size: 11px;
            font-weight: bold;
        }
    """)
    track_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(track_label)

    # Clips area
    clips_area = QWidget()
    clips_area.setFixedHeight(track_height)  # Force clips area to match track height
    clips_layout = QHBoxLayout(clips_area)
    clips_layout.setContentsMargins(0, 0, 0, 0)  # No margins - let clips fill full track height
    clips_layout.setSpacing(0)  # Legacy timeline spacing - no gaps
    clips_layout.setAlignment(Qt.AlignVCenter)  # Center clips vertically in the track
    print(f"🔧 DEBUG: Clips area height set to {track_height}px with vertical centering")

    # Filter clips for this track
    track_clips = [clip for clip in clips if clip.get("track") == track_data.get("track_id")]
    track_clips.sort(key=lambda x: x.get("position", 0))

    # Department colors
    department_colors = {
        "animation": "#1f4e79",
        "lighting": "#d68910",
        "compositing": "#196f3d",
        "fx": "#6c3483",
        "modeling": "#a93226",
        "texturing": "#8b4513",
        "rigging": "#2e8b57",
        "layout": "#4682b4"
    }

    # Add clips to track
    current_position = 0
    for clip in track_clips:
        clip_position = clip.get("position", 0)
        clip_duration = clip.get("duration", 0)

        # Add gap if needed
        if clip_position > current_position:
            gap_width = max(1, (clip_position - current_position) * 1)  # Minimal gaps like legacy timeline
            gap = QWidget()
            gap.setFixedWidth(gap_width)
            clips_layout.addWidget(gap)

        # Create clip widget
        clip_widget = create_timeline_clip_widget(clip, department_colors, track_height)
        clips_layout.addWidget(clip_widget)

        current_position = clip_position + clip_duration

    clips_layout.addStretch()
    layout.addWidget(clips_area)

    return track

def create_timeline_clip_widget(clip_data, department_colors, track_height=45):
    """Create a timeline clip widget using exact legacy timeline approach."""
    from PySide2.QtWidgets import QLabel
    from PySide2.QtCore import Qt

    print(f"🔧 DEBUG: create_timeline_clip_widget called with track_height={track_height}")

    duration = clip_data.get("duration", 0)
    department = clip_data.get("department", "unknown")

    # Use full track height to fill entire area
    width = 120
    clip_height = track_height  # Fill entire track height (45px)

    # Get shot info like legacy timeline
    shot_name = clip_data.get("shot", "")
    version = clip_data.get("version", "v001")

    # Create QLabel like legacy timeline (not QPushButton)
    clip = QLabel(f"{shot_name}\n{version}")
    clip.setFixedSize(width, clip_height)  # Exact legacy timeline sizing
    print(f"🔧 DEBUG: Created clip {shot_name} with size {width}x{clip_height}px")

    # Get department color
    color = department_colors.get(department, "#666666")

    # Use exact legacy timeline styling
    clip.setStyleSheet(f"""
        QLabel {{
            background-color: {color};
            color: #ffffff;
            font-size: 9px;
            font-weight: bold;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 2px;
            margin: 0px;
        }}
    """)
    clip.setAlignment(Qt.AlignCenter)
    clip.setToolTip(f"{clip_data.get('sequence', '')}/{clip_data.get('shot', '')} - {clip_data.get('version', '')}")

    # Add click handler (QLabel needs mouse events)
    clip.mousePressEvent = lambda event: on_timeline_clip_clicked(clip_data)

    return clip

def on_timeline_clip_clicked(clip_data):
    """Handle clip click to load in Open RV."""
    try:
        # Try to get file path directly from clip data first
        file_path = clip_data.get("file_path", "")

        if file_path:
            # Load in RV
            import rv.commands as rvc
            rvc.addSource(file_path)
            print(f"✅ Loading clip from playlist: {file_path}")
            print(f"   Shot: {clip_data.get('sequence', '')}/{clip_data.get('shot', '')} {clip_data.get('version', '')}")
            return

        # Fallback: Find media record for this clip
        media_id = clip_data.get("media_id")
        print(f"🔍 Looking for media record: {media_id}")

        # Get media records from Horus connector
        if horus_connector:
            media_records = horus_connector.get_media_records()
            media_record = None

            for record in media_records:
                if record.get("_id") == media_id:
                    media_record = record
                    break

            if media_record:
                file_path = media_record.get("file_path", "")
                if file_path:
                    # Load in RV
                    import rv.commands as rvc
                    rvc.addSource(file_path)
                    print(f"✅ Loading clip from media record: {file_path}")
                else:
                    print(f"❌ No file path for clip: {media_id}")
            else:
                print(f"❌ Media record not found: {media_id}")
        else:
            print("Horus connector not available")

    except Exception as e:
        print(f"Error loading clip from playlist: {e}")

# Playlist management functions
def create_new_playlist():
    """Create a new playlist."""
    try:
        from PySide2.QtWidgets import QInputDialog
        from datetime import datetime

        name, ok = QInputDialog.getText(None, "New Playlist", "Enter playlist name:")
        if ok and name:
            # Generate new playlist ID
            playlist_id = f"playlist_{len(timeline_playlist_data) + 1:03d}"

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
            timeline_playlist_data.append(new_playlist)
            save_timeline_playlist_data()
            populate_playlist_tree()

            print(f"Created new playlist: {name}")

    except Exception as e:
        print(f"Error creating new playlist: {e}")

def duplicate_current_playlist():
    """Duplicate the selected playlist."""
    try:
        if not current_playlist_id:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, "Warning", "Please select a playlist to duplicate.")
            return

        # Find current playlist
        current_playlist = None
        for playlist in timeline_playlist_data:
            if playlist["_id"] == current_playlist_id:
                current_playlist = playlist
                break

        if not current_playlist:
            return

        # Create duplicate
        from PySide2.QtWidgets import QInputDialog
        from datetime import datetime

        name, ok = QInputDialog.getText(
            None, "Duplicate Playlist",
            f"Enter name for duplicate of '{current_playlist['name']}':",
            text=f"{current_playlist['name']} Copy"
        )

        if ok and name:
            # Generate new ID
            new_id = f"playlist_{len(timeline_playlist_data) + 1:03d}"

            # Create duplicate
            duplicate = current_playlist.copy()
            duplicate["_id"] = new_id
            duplicate["name"] = name
            duplicate["created_at"] = datetime.now().isoformat() + "Z"
            duplicate["updated_at"] = datetime.now().isoformat() + "Z"
            duplicate["status"] = "draft"

            # Add to data and save
            timeline_playlist_data.append(duplicate)
            save_timeline_playlist_data()
            populate_playlist_tree()

            print(f"Duplicated playlist: {name}")

    except Exception as e:
        print(f"Error duplicating playlist: {e}")

def rename_current_playlist():
    """Rename the selected playlist."""
    try:
        if not current_playlist_id:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, "Warning", "Please select a playlist to rename.")
            return

        # Find current playlist
        current_playlist = None
        for playlist in timeline_playlist_data:
            if playlist["_id"] == current_playlist_id:
                current_playlist = playlist
                break

        if not current_playlist:
            return

        # Get new name
        from PySide2.QtWidgets import QInputDialog
        from datetime import datetime

        name, ok = QInputDialog.getText(
            None, "Rename Playlist",
            "Enter new name:",
            text=current_playlist["name"]
        )

        if ok and name:
            current_playlist["name"] = name
            current_playlist["updated_at"] = datetime.now().isoformat() + "Z"

            save_timeline_playlist_data()
            populate_playlist_tree()

            # Update current playlist label
            if timeline_playlist_dock and timeline_playlist_dock.widget():
                widget = timeline_playlist_dock.widget()
                widget.right_panel.current_playlist_label.setText(f"Playlist: {name}")

            print(f"Renamed playlist to: {name}")

    except Exception as e:
        print(f"Error renaming playlist: {e}")

def delete_current_playlist():
    """Delete the selected playlist."""
    try:
        if not current_playlist_id:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, "Warning", "Please select a playlist to delete.")
            return

        # Find current playlist
        current_playlist = None
        for i, playlist in enumerate(timeline_playlist_data):
            if playlist["_id"] == current_playlist_id:
                current_playlist = playlist
                break

        if not current_playlist:
            return

        # Confirm deletion
        from PySide2.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            None, "Delete Playlist",
            f"Are you sure you want to delete playlist '{current_playlist['name']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            timeline_playlist_data.remove(current_playlist)
            save_timeline_playlist_data()
            populate_playlist_tree()
            clear_timeline_display()

            print(f"Deleted playlist: {current_playlist['name']}")

    except Exception as e:
        print(f"Error deleting playlist: {e}")

def show_add_media_dialog():
    """Show dialog to add media to current playlist."""
    try:
        if not current_playlist_id:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, "Warning", "Please select a playlist first.")
            return

        from PySide2.QtWidgets import QMessageBox
        QMessageBox.information(
            None, "Add Media",
            "Right-click media items in the Media Grid to add them to the current playlist."
        )

    except Exception as e:
        print(f"Error showing add media dialog: {e}")

def refresh_timeline_playlists():
    """Refresh playlist data from database."""
    try:
        load_timeline_playlist_data()
        populate_playlist_tree()
        print("Refreshed playlist data")
    except Exception as e:
        print(f"Error refreshing playlists: {e}")

def play_current_playlist():
    """Start timeline playback."""
    try:
        if current_playlist_id:
            print(f"Playing playlist: {current_playlist_id}")
            # TODO: Implement sequential playback of all clips
        else:
            print("No playlist selected for playback")
    except Exception as e:
        print(f"Error playing playlist: {e}")

def stop_playlist_playback():
    """Stop timeline playback."""
    try:
        print("Stopping playlist playback")
        # TODO: Implement playback stop
    except Exception as e:
        print(f"Error stopping playback: {e}")

def on_timeline_zoom_changed(zoom_text):
    """Handle timeline zoom change."""
    try:
        print(f"Timeline zoom changed to: {zoom_text}")
        # TODO: Implement timeline zoom functionality
    except Exception as e:
        print(f"Error changing zoom: {e}")

def add_media_to_current_playlist(media_record):
    """Add a media record to the current playlist."""
    try:
        if not current_playlist_id:
            from PySide2.QtWidgets import QMessageBox
            QMessageBox.warning(None, "Warning", "Please select a playlist first.")
            return

        # Find current playlist
        current_playlist = None
        for playlist in timeline_playlist_data:
            if playlist["_id"] == current_playlist_id:
                current_playlist = playlist
                break

        if not current_playlist:
            return

        # Create new clip
        from datetime import datetime

        clips = current_playlist.get("clips", [])

        # Calculate position (add to end)
        position = 0
        if clips:
            last_clip = max(clips, key=lambda x: x.get("position", 0) + x.get("duration", 0))
            position = last_clip.get("position", 0) + last_clip.get("duration", 0)

        # Extract department from filename or task
        department = "unknown"
        filename = media_record.get("file_name", "")
        department_colors = {
            "animation": "#1f4e79",
            "lighting": "#d68910",
            "compositing": "#196f3d",
            "fx": "#6c3483",
            "modeling": "#a93226",
            "texturing": "#8b4513",
            "rigging": "#2e8b57",
            "layout": "#4682b4"
        }

        # Try to extract from filename
        for dept in department_colors.keys():
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
            "sequence": extract_sequence_from_filename(filename),
            "shot": extract_shot_from_filename(filename),
            "version": media_record.get("version", "v001"),
            "color": department_colors.get(department, "#666666"),
            "notes": media_record.get("description", ""),
            "added_at": datetime.now().isoformat() + "Z",
            "file_path": media_record.get("file_path", "")
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
        save_timeline_playlist_data()

        # Reload timeline if this playlist is currently selected
        if current_playlist_id == current_playlist["_id"]:
            load_playlist_timeline(current_playlist)

        # Update tree to show new clip count
        populate_playlist_tree()

        from PySide2.QtWidgets import QMessageBox
        QMessageBox.information(
            None, "Added to Playlist",
            f"Added '{media_record.get('file_name', 'Unknown')}' to playlist '{current_playlist.get('name', 'Unknown')}'"
        )

        print(f"✅ Added media to playlist: {media_record.get('file_name')}")
        print(f"   Playlist: {current_playlist.get('name')}")
        print(f"   Department: {department}")
        print(f"   Sequence/Shot: {extract_sequence_from_filename(filename)}/{extract_shot_from_filename(filename)}")

    except Exception as e:
        print(f"❌ Error adding media to playlist: {e}")
        import traceback
        traceback.print_exc()

def extract_sequence_from_filename(filename):
    """Extract sequence from filename."""
    import re
    # Look for sq0010, seq010, sequence010 patterns
    match = re.search(r'(sq\d+|seq\d+|sequence\d+)', filename.lower())
    if match:
        seq = match.group(1)
        # Normalize to sq#### format
        if seq.startswith('seq'):
            seq = 'sq' + seq[3:]
        elif seq.startswith('sequence'):
            seq = 'sq' + seq[8:]
        return seq
    return "sq0000"

def extract_shot_from_filename(filename):
    """Extract shot from filename."""
    import re
    # Look for sh0010, shot010, shot0010 patterns
    match = re.search(r'(sh\d+|shot\d+)', filename.lower())
    if match:
        shot = match.group(1)
        # Normalize to sh#### format
        if shot.startswith('shot'):
            shot = 'sh' + shot[4:]
        return shot
    return "sh0000"

def create_timeline_panel():
    """Create timeline panel with shot sequence and department management."""
    try:
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                       QComboBox, QPushButton, QFrame, QScrollArea,
                                       QListWidget, QListWidgetItem, QSplitter, QGridLayout)
        from PySide2.QtCore import Qt
        from PySide2.QtGui import QColor

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header with episode, sequence, and department filters
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(5, 5, 5, 5)

        # Timeline title
        timeline_title = QLabel("Timeline Sequence")
        timeline_title.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 14px;")
        header_layout.addWidget(timeline_title)

        header_layout.addStretch()

        # Episode filter
        episode_label = QLabel("Episode:")
        episode_label.setStyleSheet("color: #888888; font-size: 10px;")
        header_layout.addWidget(episode_label)

        episode_combo = QComboBox()
        episode_combo.addItems(["All", "Ep00", "Ep01", "Ep02"])
        episode_combo.setCurrentText("Ep01")
        episode_combo.setObjectName("timeline_episode_combo")
        episode_combo.setMaximumWidth(60)
        header_layout.addWidget(episode_combo)

        # Sequence filter
        sequence_label = QLabel("Sequence:")
        sequence_label.setStyleSheet("color: #888888; font-size: 10px;")
        header_layout.addWidget(sequence_label)

        sequence_combo = QComboBox()
        sequence_combo.addItems(["All", "sq0010", "sq0020", "sq0030", "sq0040", "sq0050"])
        sequence_combo.setCurrentText("sq0010")
        sequence_combo.setObjectName("timeline_sequence_combo")
        sequence_combo.setMaximumWidth(70)
        header_layout.addWidget(sequence_combo)

        # Department filter
        department_label = QLabel("Department:")
        department_label.setStyleSheet("color: #888888; font-size: 10px;")
        header_layout.addWidget(department_label)

        department_combo = QComboBox()
        department_combo.addItems(["All", "animation", "lighting", "compositing", "fx", "modeling"])
        department_combo.setCurrentText("All")
        department_combo.setObjectName("timeline_department_combo")
        department_combo.setMaximumWidth(90)
        header_layout.addWidget(department_combo)

        # Track height control
        height_label = QLabel("Track Height:")
        height_label.setStyleSheet("color: #888888; font-size: 10px;")
        header_layout.addWidget(height_label)

        height_combo = QComboBox()
        height_combo.addItems(["Small", "Medium", "Large"])
        height_combo.setCurrentText("Small")
        height_combo.setObjectName("timeline_height_combo")
        height_combo.setMaximumWidth(70)
        header_layout.addWidget(height_combo)

        # Zoom control
        zoom_label = QLabel("Zoom:")
        zoom_label.setStyleSheet("color: #888888; font-size: 10px;")
        header_layout.addWidget(zoom_label)

        zoom_combo = QComboBox()
        zoom_combo.addItems(["50%", "75%", "100%", "125%", "150%"])
        zoom_combo.setCurrentText("100%")
        zoom_combo.setObjectName("timeline_zoom_combo")
        zoom_combo.setMaximumWidth(60)
        header_layout.addWidget(zoom_combo)

        layout.addWidget(header_frame)

        # Timeline grid container - no left panel needed
        timeline_grid_scroll = QScrollArea()
        timeline_grid_scroll.setWidgetResizable(True)
        timeline_grid_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        timeline_grid_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        timeline_grid_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #2d2d2d;
                border: 1px solid #555555;
            }
        """)

        timeline_grid_widget = QWidget()
        timeline_grid_layout = QGridLayout(timeline_grid_widget)
        timeline_grid_layout.setObjectName("timeline_grid_layout")
        timeline_grid_layout.setContentsMargins(2, 2, 2, 2)
        timeline_grid_layout.setSpacing(0)  # No spacing - shots right next to each other

        timeline_grid_scroll.setWidget(timeline_grid_widget)
        layout.addWidget(timeline_grid_scroll)

        # Store references
        widget.timeline_title = timeline_title
        widget.episode_combo = episode_combo
        widget.sequence_combo = sequence_combo
        widget.department_combo = department_combo
        widget.height_combo = height_combo
        widget.zoom_combo = zoom_combo
        widget.timeline_grid_layout = timeline_grid_layout
        widget.timeline_grid_scroll = timeline_grid_scroll

        # Connect signals
        episode_combo.currentTextChanged.connect(on_timeline_filter_changed)
        sequence_combo.currentTextChanged.connect(on_timeline_filter_changed)
        department_combo.currentTextChanged.connect(on_timeline_filter_changed)
        height_combo.currentTextChanged.connect(on_timeline_height_changed)
        zoom_combo.currentTextChanged.connect(on_timeline_zoom_changed)

        # Initial population
        populate_timeline_shots(widget)

        return widget

    except Exception as e:
        print(f"Error creating timeline panel: {e}")
        return QWidget()

def create_search_panel():
    """Create search panel with Horus project selection."""
    try:
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                                       QCheckBox, QLabel, QComboBox, QPushButton,
                                       QFrame, QTableWidget, QGridLayout,
                                       QTableWidgetItem, QHeaderView)
        from PySide2.QtCore import Qt

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Header
        header = QLabel("Search & Navigate - Horus")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: #0078d7;")
        layout.addWidget(header)

        # Horus project selection row
        project_row = QHBoxLayout()
        project_row.addWidget(QLabel("Project:"))
        project_selector = QComboBox()
        project_selector.setObjectName("project_selector")
        project_row.addWidget(project_selector, 1)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("refresh_horus_btn")
        refresh_btn.setFixedWidth(60)
        project_row.addWidget(refresh_btn)
        layout.addLayout(project_row)

        # Search input
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search files...")
        layout.addWidget(search_input)

        # Filter section - Order: Episode > Sequence > Department > Shot
        filter_frame = QFrame()
        filter_layout = QGridLayout(filter_frame)
        filter_layout.setContentsMargins(0, 5, 0, 5)
        filter_layout.setSpacing(4)

        # Row 0: Episode filter
        filter_layout.addWidget(QLabel("Episode:"), 0, 0)
        episode_filter = QComboBox()
        episode_filter.addItems(["All"])  # Will be populated dynamically
        episode_filter.setObjectName("episode_filter")
        filter_layout.addWidget(episode_filter, 0, 1)

        # Row 1: Sequence filter
        filter_layout.addWidget(QLabel("Sequence:"), 1, 0)
        sequence_filter = QComboBox()
        sequence_filter.addItems(["All"])  # Will be populated dynamically
        sequence_filter.setObjectName("sequence_filter")
        filter_layout.addWidget(sequence_filter, 1, 1)

        # Row 2: Department filter
        filter_layout.addWidget(QLabel("Department:"), 2, 0)
        department_filter = QComboBox()
        department_filter.addItems(["All", "anim", "comp", "lighting", "layout", "hero"])
        department_filter.setObjectName("department_filter")
        filter_layout.addWidget(department_filter, 2, 1)

        # Row 3: Shot filter
        filter_layout.addWidget(QLabel("Shot:"), 3, 0)
        shot_filter = QComboBox()
        shot_filter.addItems(["All"])  # Will be populated dynamically
        shot_filter.setObjectName("shot_filter")
        filter_layout.addWidget(shot_filter, 3, 1)

        # Row 4: Status filter
        filter_layout.addWidget(QLabel("Status:"), 4, 0)
        status_filter = QComboBox()
        status_filter.addItems(["All", "submit", "need fix", "approved"])
        status_filter.setObjectName("status_filter")
        filter_layout.addWidget(status_filter, 4, 1)

        layout.addWidget(filter_frame)

        # Version toggle row
        version_row = QHBoxLayout()
        version_toggle = QCheckBox("Latest version only")
        version_toggle.setObjectName("version_toggle")
        version_toggle.setChecked(True)  # Default to latest only
        version_toggle.setStyleSheet("QCheckBox { color: #e0e0e0; }")
        version_row.addWidget(version_toggle)
        version_row.addStretch()
        layout.addLayout(version_row)

        # Media table header
        layout.addWidget(QLabel("Media Files:"))

        # Media table - Columns: Name ({ep}_{shot}), Version, Status
        media_table = QTableWidget()
        media_table.setColumnCount(3)
        media_table.setHorizontalHeaderLabels(["Name", "Version", "Status"])
        media_table.setObjectName("media_table")
        media_table.setSelectionBehavior(QTableWidget.SelectRows)
        media_table.setAlternatingRowColors(True)
        media_table.verticalHeader().setVisible(False)
        media_table.setSortingEnabled(True)

        # Make columns fit content
        header = media_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name - stretch
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Version
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Status

        # Set row height
        media_table.verticalHeader().setDefaultSectionSize(25)

        # Connect double-click signal
        media_table.itemDoubleClicked.connect(on_media_table_double_click)

        layout.addWidget(media_table, 1)  # Stretch factor 1 to fill space

        # Connect filter signals
        episode_filter.currentTextChanged.connect(apply_filters)
        sequence_filter.currentTextChanged.connect(apply_filters)
        department_filter.currentTextChanged.connect(apply_filters)
        shot_filter.currentTextChanged.connect(apply_filters)
        status_filter.currentTextChanged.connect(apply_filters)
        search_input.textChanged.connect(apply_filters)
        version_toggle.stateChanged.connect(apply_filters)

        # Store references
        widget.project_selector = project_selector
        widget.refresh_horus_btn = refresh_btn
        widget.media_table = media_table
        widget.episode_filter = episode_filter
        widget.sequence_filter = sequence_filter
        widget.department_filter = department_filter
        widget.shot_filter = shot_filter
        widget.status_filter = status_filter
        widget.search_input = search_input
        widget.version_toggle = version_toggle

        print("Search panel created (new layout)")
        return widget

    except Exception as e:
        print(f"Error creating search panel: {e}")
        return None

def create_media_grid_panel():
    """Create media grid panel for Horus data."""
    try:
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QGridLayout, 
                                       QLabel)
        from PySide2.QtCore import Qt
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("Media Grid - Horus")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: #0078d7;")
        layout.addWidget(header)

        # Path display
        path_label = QLabel("Select Horus project to load media")
        path_label.setStyleSheet("font-size: 10px; color: #666666;")
        path_label.setObjectName("path_label")
        layout.addWidget(path_label)
        
        # Grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(4)
        
        scroll_area.setWidget(grid_container)
        layout.addWidget(scroll_area, 1)
        
        # Status
        status_label = QLabel("Ready - Connect to Horus")
        status_label.setStyleSheet("font-size: 10px; color: #888888;")
        status_label.setObjectName("status_label")
        layout.addWidget(status_label)
        
        # Store references
        widget.path_label = path_label
        widget.status_label = status_label
        widget.grid_layout = grid_layout
        widget.grid_container = grid_container
        
        print("Media grid panel created")
        return widget
        
    except Exception as e:
        print(f"Error creating media grid panel: {e}")
        return None

def setup_horus_integration():
    """Set up Horus data integration."""
    global horus_connector, search_dock, media_grid_dock

    try:
        # Initialize Horus connector with resource path
        data_dir = get_resource_path("sample_db")
        print(f"🔍 Looking for Horus database at: {data_dir}")
        horus_connector = get_horus_connector(data_dir)

        if not horus_connector.is_available():
            print("⚠️  Horus data not available - using sample data")
            # Try fallback to local sample_db
            horus_connector = get_horus_connector("sample_db")
            if not horus_connector.is_available():
                print("❌ No Horus database found")
                return False
        
        # Get widgets
        search_widget = search_dock.widget() if search_dock else None
        if not search_widget:
            print("Could not find search widget")
            return False
        
        # Load projects
        projects = horus_connector.get_available_projects()
        project_selector = search_widget.project_selector

        project_selector.clear()
        project_selector.addItem("Select Project...", "")

        for project in projects:
            project_id = project.get('_id', project.get('id', ''))  # Support both _id and id
            project_name = project.get('name', 'Unknown')
            project_selector.addItem(f"{project_name} ({project_id})", project_id)
        
        # Connect signals
        project_selector.currentTextChanged.connect(on_project_changed)
        search_widget.refresh_horus_btn.clicked.connect(refresh_horus_data)

        print(f"Horus integration setup - {len(projects)} projects")
        return True

    except Exception as e:
        print(f"Error setting up Horus integration: {e}")
        return False

def on_project_changed():
    """Handle project selection change."""
    global current_project_id, horus_connector, search_dock, media_grid_dock
    
    try:
        search_widget = search_dock.widget() if search_dock else None
        if not search_widget:
            return
        
        project_id = search_widget.project_selector.currentData()
        if not project_id or project_id == current_project_id:
            return
        
        current_project_id = project_id
        horus_connector.set_current_project(project_id)

        print(f"Loading project: {project_id}")

        # Load media
        media_items = horus_connector.get_media_for_project(project_id)
        
        # Update grid
        populate_media_grid(media_items)
        
        # Update media table
        update_media_table(project_id, media_items)

        # Update shot filter options
        update_shot_filter(media_items)
        
        # Update status
        media_grid_widget = media_grid_dock.widget() if media_grid_dock else None
        if media_grid_widget:
            media_grid_widget.path_label.setText(f"Project: {project_id}")
            media_grid_widget.status_label.setText(f"Loaded {len(media_items)} items")
        
        print(f"Loaded {len(media_items)} media items")
        
    except Exception as e:
        print(f"Error loading project: {e}")

def populate_media_grid(media_items):
    """Populate media grid with Horus data."""
    global media_grid_dock
    
    try:
        media_grid_widget = media_grid_dock.widget() if media_grid_dock else None
        if not media_grid_widget:
            return
        
        # Clear grid
        grid_layout = media_grid_widget.grid_layout
        for i in reversed(range(grid_layout.count())):
            child = grid_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add items
        for i, media_item in enumerate(media_items):
            media_widget = create_media_widget(media_item)
            row = i // 4
            col = i % 4
            grid_layout.addWidget(media_widget, row, col)
        
    except Exception as e:
        print(f"Error populating grid: {e}")

def create_media_widget(media_item):
    """Create widget for media item."""
    try:
        from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel
        from PySide2.QtCore import Qt
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        # File name
        file_name = media_item.get('file_name', 'Unknown')
        name_label = QLabel(file_name)
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # Task
        task_id = media_item.get('task_id', '')
        task_label = QLabel(f"Task: {task_id}")
        task_label.setAlignment(Qt.AlignCenter)
        task_label.setStyleSheet("font-size: 9px; color: #888888;")
        layout.addWidget(task_label)
        
        # Version
        version = media_item.get('version', '')
        version_label = QLabel(f"Version: {version}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("font-size: 9px; color: #888888;")
        layout.addWidget(version_label)
        
        # Status
        status = media_item.get('approval_status', 'pending')
        status_label = QLabel(f"Status: {status}")
        status_label.setAlignment(Qt.AlignCenter)
        status_color = "#00aa00" if status == "approved" else "#aa0000" if status == "rejected" else "#aaaa00"
        status_label.setStyleSheet(f"font-size: 9px; color: {status_color};")
        layout.addWidget(status_label)
        
        # Style with dark theme
        widget.setStyleSheet("""
            QWidget {
                border: 1px solid #555555;
                background-color: #3a3a3a;
                border-radius: 4px;
                min-height: 100px;
                min-width: 140px;
            }
            QWidget:hover {
                border-color: #0078d4;
                background-color: #4a4a4a;
            }
            QLabel {
                background-color: transparent;
                color: #e0e0e0;
            }
        """)
        
        # Store data
        widget.horus_data = media_item
        
        # Click handler with right-click context menu
        def on_click(event):
            try:
                from PySide2.QtCore import Qt
                from PySide2.QtWidgets import QMenu, QAction

                if event.button() == Qt.LeftButton:
                    # Left click - load in RV
                    file_path = media_item.get('file_path', '')
                    if file_path:
                        try:
                            import rv.commands as rvc
                            rvc.addSource(file_path)
                            print(f"Loaded in RV: {file_name}")
                        except:
                            print(f"Selected: {file_name}")
                    else:
                        print(f"No path for: {file_name}")

                elif event.button() == Qt.RightButton:
                    # Right click - show context menu
                    if ENABLE_TIMELINE_PLAYLIST and timeline_playlist_dock:
                        menu = QMenu(widget)

                        # Add to playlist action
                        add_to_playlist_action = QAction("Add to Current Playlist", menu)
                        add_to_playlist_action.triggered.connect(
                            lambda: add_media_to_current_playlist(media_item)
                        )
                        menu.addAction(add_to_playlist_action)

                        # Load in RV action
                        load_action = QAction("Load in RV", menu)
                        load_action.triggered.connect(
                            lambda: on_click_load_rv(media_item)
                        )
                        menu.addAction(load_action)

                        # Show menu at cursor position
                        menu.exec_(event.globalPos())

            except Exception as e:
                print(f"Error: {e}")

        def on_click_load_rv(media_item):
            """Load media item in RV."""
            file_path = media_item.get('file_path', '')
            if file_path:
                try:
                    import rv.commands as rvc
                    rvc.addSource(file_path)
                    print(f"Loaded in RV: {media_item.get('file_name', 'Unknown')}")
                except:
                    print(f"Selected: {media_item.get('file_name', 'Unknown')}")

        widget.mousePressEvent = on_click
        
        return widget
        
    except Exception as e:
        print(f"Error creating widget: {e}")
        return QWidget()

def update_media_table(project_id, media_items):
    """Update media table with thumbnails."""
    global search_dock

    try:
        print(f"Updating media table for project {project_id} with {len(media_items)} items")

        search_widget = search_dock.widget() if search_dock else None
        if not search_widget:
            print("No search widget found")
            return

        media_table = search_widget.media_table
        if not media_table:
            print("No media table found")
            return

        # Clear existing rows
        media_table.setRowCount(0)

        # Populate table with media items
        from PySide2.QtWidgets import QLabel, QTableWidgetItem
        from PySide2.QtCore import Qt
        from PySide2.QtGui import QPixmap

        for row, media_item in enumerate(media_items):
            media_table.insertRow(row)

            # Extract data from media item
            file_name = media_item.get('file_name', 'Unknown')
            version = media_item.get('version', media_item.get('linked_version', 'v001'))
            task_id = media_item.get('task_id') or media_item.get('linked_task_id', 'Unknown')
            created_at = media_item.get('created_at', media_item.get('_created_at', ''))
            approval_status = media_item.get('approval_status', 'pending')

            # Parse task entity (department from task_id)
            task_entity = "unknown"
            if "_" in task_id:
                parts = task_id.split("_")
                if len(parts) >= 4:
                    task_entity = parts[-1]  # Last part is usually the department

            # Use the actual file name or create a proper shot name
            if file_name and file_name != 'Unknown':
                display_name = file_name
            else:
                # Parse shot name from task_id as fallback
                if "_" in task_id:
                    parts = task_id.split("_")
                    if len(parts) >= 3:
                        # Format: ep00_sq0010_sh0020_lighting -> ep01_sq0010_sh0010
                        episode = parts[0] if parts[0].startswith('ep') else 'ep01'
                        sequence = parts[1] if parts[1].startswith('sq') else 'sq0010'
                        shot = parts[2] if parts[2].startswith('sh') else 'sh0010'
                        display_name = f"{episode}_{sequence}_{shot}"
                    else:
                        display_name = task_id
                else:
                    display_name = task_id

            # Format created date
            created_display = ""
            if created_at:
                try:
                    # Try to parse and format the date
                    if 'T' in created_at:
                        date_part = created_at.split('T')[0]
                        created_display = date_part
                    else:
                        created_display = created_at[:10] if len(created_at) >= 10 else created_at
                except:
                    created_display = created_at

            # Thumbnail column (placeholder for now)
            thumbnail_label = QLabel("[IMG]")
            thumbnail_label.setAlignment(Qt.AlignCenter)
            thumbnail_label.setStyleSheet("background-color: #2d2d2d; color: #ffffff; border: 1px solid #555;")
            media_table.setCellWidget(row, 0, thumbnail_label)

            # Task Entity column
            task_item = QTableWidgetItem(task_entity)
            task_item.setData(Qt.UserRole, media_item)
            media_table.setItem(row, 1, task_item)

            # Name column
            name_item = QTableWidgetItem(display_name)
            media_table.setItem(row, 2, name_item)

            # Version column
            version_item = QTableWidgetItem(version)
            media_table.setItem(row, 3, version_item)

            # Status column
            status_item = QTableWidgetItem(approval_status)
            media_table.setItem(row, 4, status_item)

            # Created column
            created_item = QTableWidgetItem(created_display)
            media_table.setItem(row, 5, created_item)

        print(f"Populated media table with {len(media_items)} items")

    except Exception as e:
        print(f"Error updating media table: {e}")

def apply_filters():
    """Apply filters to the media table."""
    global search_dock, current_project_id, horus_connector

    try:
        if not current_project_id or not horus_connector:
            return

        search_widget = search_dock.widget() if search_dock else None
        if not search_widget:
            return

        # Get filter values
        department = search_widget.department_filter.currentText()
        episode = search_widget.episode_filter.currentText()
        sequence = search_widget.sequence_filter.currentText()
        shot = search_widget.shot_filter.currentText()
        status = search_widget.status_filter.currentText()
        search_text = search_widget.search_input.text().lower()

        # Get all media items for current project
        all_media_items = horus_connector.get_media_for_project(current_project_id)

        # Apply filters
        filtered_items = []
        for item in all_media_items:
            # Apply department filter
            if department != "All":
                task_id = item.get('task_id') or item.get('linked_task_id', '')
                if not task_id.endswith(department.lower()):
                    continue

            # Apply episode filter
            if episode != "All":
                task_id = item.get('task_id') or item.get('linked_task_id', '')
                if not task_id.startswith(episode.lower()):
                    continue

            # Apply sequence filter
            if sequence != "All":
                task_id = item.get('task_id') or item.get('linked_task_id', '')
                if sequence.lower() not in task_id:
                    continue

            # Apply shot filter
            if shot != "All":
                task_id = item.get('task_id') or item.get('linked_task_id', '')
                if shot.lower() not in task_id:
                    continue

            # Apply status filter
            if status != "All":
                item_status = item.get('approval_status', 'pending')
                if item_status != status:
                    continue

            # Apply search text filter
            if search_text:
                file_name = item.get('file_name', '').lower()
                task_id = item.get('task_id') or item.get('linked_task_id', '')
                if search_text not in file_name and search_text not in task_id.lower():
                    continue

            filtered_items.append(item)

        # Update table with filtered items
        update_media_table(current_project_id, filtered_items)

    except Exception as e:
        print(f"Error applying filters: {e}")

def update_shot_filter(media_items):
    """Update shot filter dropdown with available shots."""
    global search_dock

    try:
        search_widget = search_dock.widget() if search_dock else None
        if not search_widget:
            return

        shot_filter = search_widget.shot_filter

        # Extract unique shots from media items
        shots = set()
        for item in media_items:
            task_id = item.get('task_id') or item.get('linked_task_id', '')
            if "_" in task_id:
                parts = task_id.split("_")
                if len(parts) >= 3:
                    shot = parts[2]  # Usually the shot part
                    if shot.startswith('sh'):
                        shots.add(shot)

        # Update shot filter
        shot_filter.clear()
        shot_filter.addItem("All")
        for shot in sorted(shots):
            shot_filter.addItem(shot)

    except Exception as e:
        print(f"Error updating shot filter: {e}")

def on_media_table_double_click(item):
    """Handle double-click on media table item."""
    try:
        from PySide2.QtCore import Qt

        if not item:
            return

        # Get the media item data from the task entity column (column 1)
        row = item.row()
        search_widget = search_dock.widget() if search_dock else None
        if not search_widget:
            return

        media_table = search_widget.media_table
        task_item = media_table.item(row, 1)  # Task Entity column

        if task_item:
            media_item = task_item.data(Qt.UserRole)
            if media_item:
                file_path = media_item.get('file_path') or media_item.get('storage_url', '')
                if file_path:
                    print(f"Loading media file: {file_path}")
                    # Load the media file in Open RV
                    load_media_in_rv(file_path)
                else:
                    print("No file path found for media item")
            else:
                print("No media item data found")

    except Exception as e:
        print(f"Error handling media table double-click: {e}")

def on_scale_changed():
    """Handle scale change for table size."""
    global search_dock

    try:
        search_widget = search_dock.widget() if search_dock else None
        if not search_widget:
            return

        scale = search_widget.scale_combo.currentText()
        media_table = search_widget.media_table

        if scale == "Small":
            # Small scale
            media_table.setColumnWidth(0, 40)   # Thumbnail
            media_table.setColumnWidth(1, 60)   # Task Entity
            media_table.setColumnWidth(2, 100)  # Name
            media_table.setColumnWidth(3, 40)   # Version
            media_table.setColumnWidth(4, 60)   # Status
            media_table.setColumnWidth(5, 80)   # Created
            media_table.verticalHeader().setDefaultSectionSize(30)
        elif scale == "Medium":
            # Medium scale
            media_table.setColumnWidth(0, 60)   # Thumbnail
            media_table.setColumnWidth(1, 90)   # Task Entity
            media_table.setColumnWidth(2, 150)  # Name
            media_table.setColumnWidth(3, 60)   # Version
            media_table.setColumnWidth(4, 90)   # Status
            media_table.setColumnWidth(5, 120)  # Created
            media_table.verticalHeader().setDefaultSectionSize(45)
        elif scale == "Large":
            # Large scale
            media_table.setColumnWidth(0, 80)   # Thumbnail
            media_table.setColumnWidth(1, 120)  # Task Entity
            media_table.setColumnWidth(2, 200)  # Name
            media_table.setColumnWidth(3, 80)   # Version
            media_table.setColumnWidth(4, 120)  # Status
            media_table.setColumnWidth(5, 160)  # Created
            media_table.verticalHeader().setDefaultSectionSize(60)

        print(f"Table scale changed to: {scale}")

    except Exception as e:
        print(f"Error changing table scale: {e}")

# Comments and Annotations Functions
def on_add_comment():
    """Handle adding a general comment."""
    global comments_dock

    try:
        comments_widget = comments_dock.widget() if comments_dock else None
        if not comments_widget:
            return

        comment_text = comments_widget.comment_text.toPlainText().strip()
        if not comment_text:
            return

        # Create new comment data
        new_comment = {
            "id": 999,  # Would be generated by database
            "user": "Current User",
            "avatar": "CU",
            "time": "Just now",
            "frame": None,
            "text": comment_text,
            "likes": 0,
            "replies": []
        }

        # Create and add comment widget
        comment_widget = create_comment_widget(new_comment)
        comments_widget.comments_container.layout().insertWidget(
            comments_widget.comments_container.layout().count() - 1, comment_widget)

        comments_widget.comment_text.clear()

        print(f"Added general comment: {comment_text}")

    except Exception as e:
        print(f"Error adding comment: {e}")

def on_add_frame_comment():
    """Handle adding a frame-specific comment."""
    global comments_dock

    try:
        comments_widget = comments_dock.widget() if comments_dock else None
        if not comments_widget:
            return

        comment_text = comments_widget.comment_text.toPlainText().strip()
        if not comment_text:
            return

        # Get current frame from Open RV
        current_frame = get_current_frame()

        # Create new frame-specific comment data
        new_comment = {
            "id": 998,  # Would be generated by database
            "user": "Current User",
            "avatar": "CU",
            "time": "Just now",
            "frame": current_frame,
            "text": comment_text,
            "likes": 0,
            "priority": "Medium",
            "status": "Open",
            "replies": []
        }

        # Create and add comment widget
        comment_widget = create_comment_widget(new_comment)
        comments_widget.comments_container.layout().insertWidget(
            comments_widget.comments_container.layout().count() - 1, comment_widget)

        comments_widget.comment_text.clear()

        print(f"Added frame comment at frame {current_frame}: {comment_text}")

    except Exception as e:
        print(f"Error adding frame comment: {e}")

def create_annotations_popup():
    """Create the annotations popup window."""
    try:
        from PySide2.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                                       QPushButton, QLabel, QFrame)
        from PySide2.QtCore import Qt

        popup = QDialog()
        popup.setWindowTitle("Annotations")
        popup.setModal(False)  # Non-modal so it can float
        popup.resize(400, 300)
        popup.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint)

        layout = QVBoxLayout(popup)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header
        header_label = QLabel("Annotations")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #e0e0e0;")
        layout.addWidget(header_label)

        # Annotations list
        annotations_list = QListWidget()
        annotations_list.setObjectName("annotations_list")
        layout.addWidget(annotations_list)

        # Add some sample annotations
        annotations_list.addItem("Frame 1047: Eye line annotation")
        annotations_list.addItem("Frame 1089: Color correction note")
        annotations_list.addItem("Frame 1120: Lighting adjustment")

        # Controls
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)

        clear_btn = QPushButton("Clear All")
        clear_btn.setObjectName("clear_annotations_btn")
        controls_layout.addWidget(clear_btn)

        save_btn = QPushButton("Save Annotations")
        save_btn.setObjectName("save_annotations_btn")
        controls_layout.addWidget(save_btn)

        export_btn = QPushButton("Export from RV")
        export_btn.setObjectName("export_annotations_btn")
        controls_layout.addWidget(export_btn)

        controls_layout.addStretch()
        layout.addWidget(controls_frame)

        # Store references
        popup.annotations_list = annotations_list
        popup.clear_btn = clear_btn
        popup.save_btn = save_btn
        popup.export_btn = export_btn

        # Connect signals
        clear_btn.clicked.connect(lambda: on_clear_annotations(popup))
        save_btn.clicked.connect(lambda: on_save_annotations(popup))
        export_btn.clicked.connect(on_export_rv_annotations)

        # Apply dark theme styling
        apply_rv_styling(popup)

        return popup

    except Exception as e:
        print(f"Error creating annotations popup: {e}")
        return None

def show_reply_input(comment_id):
    """Show the reply input for a specific comment."""
    global comments_dock

    try:
        from PySide2.QtWidgets import QFrame, QTextEdit

        comments_widget = comments_dock.widget() if comments_dock else None
        if not comments_widget:
            return

        # Find and show the reply input frame for this comment
        reply_input_frame = comments_widget.findChild(QFrame, f"reply_input_{comment_id}")
        if reply_input_frame:
            reply_input_frame.setVisible(True)

            # Focus on the text input
            reply_text = comments_widget.findChild(QTextEdit, f"reply_text_{comment_id}")
            if reply_text:
                reply_text.setFocus()

            print(f"Showing reply input for comment {comment_id}")

    except Exception as e:
        print(f"Error showing reply input: {e}")

def hide_reply_input(comment_id):
    """Hide the reply input for a specific comment."""
    global comments_dock

    try:
        from PySide2.QtWidgets import QFrame, QTextEdit

        comments_widget = comments_dock.widget() if comments_dock else None
        if not comments_widget:
            return

        # Find and hide the reply input frame for this comment
        reply_input_frame = comments_widget.findChild(QFrame, f"reply_input_{comment_id}")
        if reply_input_frame:
            reply_input_frame.setVisible(False)

            # Clear the text input
            reply_text = comments_widget.findChild(QTextEdit, f"reply_text_{comment_id}")
            if reply_text:
                reply_text.clear()

            print(f"Hiding reply input for comment {comment_id}")

    except Exception as e:
        print(f"Error hiding reply input: {e}")

def post_reply(comment_id):
    """Post a reply to a specific comment."""
    global comments_dock

    try:
        from PySide2.QtWidgets import QTextEdit

        comments_widget = comments_dock.widget() if comments_dock else None
        if not comments_widget:
            return

        # Get the reply text
        reply_text = comments_widget.findChild(QTextEdit, f"reply_text_{comment_id}")
        if not reply_text:
            return

        reply_content = reply_text.toPlainText().strip()
        if not reply_content:
            print("Reply text is empty")
            return

        # Create new reply data
        new_reply = {
            "id": 9999,  # Would be generated by database
            "user": "Current User",
            "avatar": "CU",
            "time": "Just now",
            "text": reply_content,
            "likes": 0
        }

        print(f"Posted reply to comment {comment_id}: {reply_content}")

        # TODO: Add the reply to the comment thread in the UI
        # For now, just hide the input and clear it
        hide_reply_input(comment_id)

        # TODO: In a real implementation, you would:
        # 1. Add the reply to the database
        # 2. Refresh the comment thread to show the new reply
        # 3. Update the reply count

    except Exception as e:
        print(f"Error posting reply: {e}")

def on_open_annotations_popup():
    """Open the annotations popup window."""
    global annotations_popup_window

    try:
        # Create popup if it doesn't exist
        if 'annotations_popup_window' not in globals() or annotations_popup_window is None:
            annotations_popup_window = create_annotations_popup()

        if annotations_popup_window:
            annotations_popup_window.show()
            annotations_popup_window.raise_()
            annotations_popup_window.activateWindow()
            print("Opened annotations popup window")

    except Exception as e:
        print(f"Error opening annotations popup: {e}")

def generate_comprehensive_mockup_data():
    """Generate comprehensive mockup shot data for timeline demonstration."""
    try:
        import random

        mockup_data = {}

        # Define episodes, sequences, and shots
        episodes = ["ep01", "ep02"]
        sequences = {
            "ep01": ["sq0010", "sq0020", "sq0030"],
            "ep02": ["sq0040", "sq0050"]
        }
        shots_per_sequence = {
            "sq0010": ["sh0010", "sh0020", "sh0030", "sh0040", "sh0050"],
            "sq0020": ["sh0010", "sh0020", "sh0030"],
            "sq0030": ["sh0010", "sh0020", "sh0030", "sh0040"],
            "sq0040": ["sh0010", "sh0020", "sh0030", "sh0040", "sh0050", "sh0060"],
            "sq0050": ["sh0010", "sh0020"]
        }
        departments = ["animation", "lighting", "compositing", "fx", "modeling"]

        # Generate data for each combination
        for episode in episodes:
            for sequence in sequences[episode]:
                for shot in shots_per_sequence[sequence]:
                    shot_key = f"{episode}_{sequence}_{shot}"
                    mockup_data[shot_key] = {}

                    for dept in departments:
                        # Randomly decide if this department has data for this shot
                        # 80% chance of having data, 20% chance of being empty
                        if random.random() < 0.8:
                            # Generate 1-4 versions for this department/shot
                            num_versions = random.randint(1, 4)
                            versions = []

                            for v in range(1, num_versions + 1):
                                version_data = {
                                    "id": f"{shot_key}_{dept}_v{v:03d}",
                                    "task_id": f"{episode}_{sequence}_{shot}_{dept}",
                                    "version": f"v{v:03d}",
                                    "linked_version": f"v{v:03d}",
                                    "name": f"{shot}_{dept}_v{v:03d}",
                                    "department": dept,
                                    "episode": episode,
                                    "sequence": sequence,
                                    "shot": shot,
                                    "status": random.choice(["approved", "pending", "in_progress", "rejected"]),
                                    "file_path": f"/projects/{episode}/{sequence}/{shot}/{dept}/{shot}_{dept}_v{v:03d}.mov"
                                }
                                versions.append(version_data)

                            mockup_data[shot_key][dept] = versions

        print(f"Generated mockup data for {len(mockup_data)} shots across {len(departments)} departments")
        return mockup_data

    except Exception as e:
        print(f"Error generating mockup data: {e}")
        return {}

def populate_timeline_shots(timeline_widget):
    """Populate timeline with shots based on current filters."""
    try:
        global horus_connector, current_project_id

        # Get filter values
        episode = timeline_widget.episode_combo.currentText()
        sequence = timeline_widget.sequence_combo.currentText()
        department = timeline_widget.department_combo.currentText()

        print(f"Populating timeline for Episode: {episode}, Sequence: {sequence}, Department: {department}")

        # Use comprehensive mockup data for demonstration
        all_shots_data = generate_comprehensive_mockup_data()

        # Filter shots based on episode and sequence
        filtered_shots = {}

        for shot_key, shot_data in all_shots_data.items():
            parts = shot_key.split('_')
            if len(parts) >= 3:
                item_episode = parts[0]
                item_sequence = parts[1]
                item_shot = parts[2]

                # Apply episode filter
                if episode != "All" and item_episode.lower() != episode.lower():
                    continue

                # Apply sequence filter
                if sequence != "All" and item_sequence.lower() != sequence.lower():
                    continue

                # Apply department filter
                if department != "All":
                    # Filter to only show selected department
                    filtered_shot_data = {}
                    if department.lower() in shot_data:
                        filtered_shot_data[department.lower()] = shot_data[department.lower()]
                    filtered_shots[shot_key] = filtered_shot_data
                else:
                    # Show all departments
                    filtered_shots[shot_key] = shot_data

        # Update timeline display
        update_timeline_display(timeline_widget, filtered_shots)

        print(f"Filtered to {len(filtered_shots)} shots for display")

    except Exception as e:
        print(f"Error populating timeline shots: {e}")

def update_timeline_display(timeline_widget, shots_data):
    """Update timeline display to match professional NLE layout like Adobe Premiere Pro."""
    try:
        from PySide2.QtWidgets import QLabel, QPushButton, QFrame, QHBoxLayout, QVBoxLayout
        from PySide2.QtCore import Qt

        # Clear existing timeline
        clear_timeline_display(timeline_widget)

        # Get sorted shot list
        shot_keys = sorted(shots_data.keys())
        if not shot_keys:
            print("No shots to display")
            return

        # Professional NLE dimensions - uniform track height
        TRACK_HEIGHT = 45  # Uniform height for all tracks
        TRACK_LABEL_WIDTH = 80  # Width for track labels (V1, V2, etc.)

        # Fixed department order
        departments = ["animation", "lighting", "compositing", "fx", "modeling"]

        grid_layout = timeline_widget.timeline_grid_layout
        grid_layout.setSpacing(0)  # No spacing
        grid_layout.setContentsMargins(0, 0, 0, 0)

        # Add timeline ruler at top (like NLE)
        ruler_frame = create_legacy_timeline_ruler(shot_keys, TRACK_LABEL_WIDTH)
        grid_layout.addWidget(ruler_frame, 0, 0)

        # Create timeline tracks like NLE
        for row, dept in enumerate(departments):
            # Get department data for all shots
            dept_data = {}
            for shot_key in shot_keys:
                shot_data = shots_data.get(shot_key, {})
                if dept in shot_data:
                    dept_data[shot_key] = shot_data[dept][0] if shot_data[dept] else {}

            # Create track row
            track_frame = create_nle_track_row(dept, shot_keys, dept_data, TRACK_HEIGHT, TRACK_LABEL_WIDTH)
            grid_layout.addWidget(track_frame, row + 1, 0)  # +1 to account for ruler

        print(f"Updated NLE-style timeline with {len(shot_keys)} shots and {len(departments)} departments")

    except Exception as e:
        print(f"Error updating timeline display: {e}")

def create_nle_track_row(department, shot_keys, dept_shots_data, track_height, label_width):
    """Create a single track row like Adobe Premiere Pro."""
    try:
        from PySide2.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
        from PySide2.QtCore import Qt

        # Department colors
        dept_colors = {
            "animation": "#4472C4",    # Blue like V1
            "lighting": "#70AD47",     # Green like V2
            "compositing": "#FFC000",  # Yellow like A1
            "fx": "#C55A5A",          # Red like A2
            "modeling": "#7030A0"      # Purple
        }

        track_frame = QFrame()
        track_frame.setFixedHeight(track_height)
        track_frame.setStyleSheet("QFrame { background-color: #2d2d2d; border: none; }")

        track_layout = QHBoxLayout(track_frame)
        track_layout.setContentsMargins(0, 0, 0, 0)
        track_layout.setSpacing(0)

        # Track label (like V1, V2, A1, A2)
        track_names = {
            "animation": "V1",
            "lighting": "V2",
            "compositing": "A1",
            "fx": "A2",
            "modeling": "V3"
        }
        track_label = QLabel(track_names.get(department, "V1"))
        track_label.setFixedSize(label_width, track_height)
        track_label.setStyleSheet(f"""
            QLabel {{
                background-color: #404040;
                color: #ffffff;
                font-weight: bold;
                font-size: 11px;
                border: 1px solid #555555;
                padding: 0px;
                margin: 0px;
            }}
        """)
        track_label.setAlignment(Qt.AlignCenter)
        track_layout.addWidget(track_label)

        # Timeline clips area - continuous like NLE
        clips_container = QFrame()
        clips_container.setStyleSheet(f"""
            QFrame {{
                background-color: {dept_colors.get(department, '#404040')};
                border: 1px solid #333333;
                margin: 0px;
            }}
        """)
        clips_container.setFixedHeight(track_height - 2)  # Account for border

        clips_layout = QHBoxLayout(clips_container)
        clips_layout.setContentsMargins(0, 0, 0, 0)
        clips_layout.setSpacing(0)

        # Add shot clips as continuous blocks
        total_width = 0
        for shot_key in shot_keys:
            shot_data = dept_shots_data.get(shot_key, {})
            if shot_data:
                # Shot has data - create clip
                shot_name = shot_key.split('_')[-1]
                version = shot_data.get('version', 'v001')

                clip_label = QLabel(f"{shot_name}\n{version}")
                clip_label.setFixedSize(120, track_height - 4)  # Fixed width for each shot
                clip_label.setStyleSheet("""
                    QLabel {
                        background-color: rgba(255, 255, 255, 0.1);
                        color: #ffffff;
                        font-size: 9px;
                        font-weight: bold;
                        border: 1px solid rgba(255, 255, 255, 0.2);
                        padding: 2px;
                        margin: 0px;
                    }
                """)
                clip_label.setAlignment(Qt.AlignCenter)
                clips_layout.addWidget(clip_label)
                total_width += 120

        # Fill remaining space
        clips_layout.addStretch()
        track_layout.addWidget(clips_container)

        return track_frame

    except Exception as e:
        print(f"Error creating NLE track row: {e}")
        return QFrame()

def create_legacy_timeline_ruler(shot_keys, label_width):
    """Create timeline ruler like NLE applications (legacy)."""
    try:
        from PySide2.QtWidgets import QFrame, QHBoxLayout, QLabel
        from PySide2.QtCore import Qt

        ruler_frame = QFrame()
        ruler_frame.setFixedHeight(25)
        ruler_frame.setStyleSheet("QFrame { background-color: #1e1e1e; border-bottom: 1px solid #555555; }")

        ruler_layout = QHBoxLayout(ruler_frame)
        ruler_layout.setContentsMargins(0, 0, 0, 0)
        ruler_layout.setSpacing(0)

        # Empty space for track labels
        spacer_label = QLabel("")
        spacer_label.setFixedSize(label_width, 25)
        spacer_label.setStyleSheet("QLabel { background-color: #1e1e1e; border-right: 1px solid #555555; }")
        ruler_layout.addWidget(spacer_label)

        # Timeline markers for each shot
        for i, shot_key in enumerate(shot_keys):
            shot_name = shot_key.split('_')[-1]
            marker_label = QLabel(shot_name)
            marker_label.setFixedSize(120, 25)  # Match clip width
            marker_label.setStyleSheet("""
                QLabel {
                    background-color: #1e1e1e;
                    color: #cccccc;
                    font-size: 9px;
                    border-right: 1px solid #555555;
                    padding: 2px;
                }
            """)
            marker_label.setAlignment(Qt.AlignCenter)
            ruler_layout.addWidget(marker_label)

        # Fill remaining space
        ruler_layout.addStretch()

        return ruler_frame

    except Exception as e:
        print(f"Error creating timeline ruler: {e}")
        return QFrame()

def create_department_track(department, shot_keys, shots_data):
    """Create a timeline track for a specific department with enhanced visual design."""
    try:
        from PySide2.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
        from PySide2.QtCore import Qt

        # Department color scheme
        dept_colors = {
            "animation": {"bg": "#1f4e79", "text": "#ffffff"},
            "lighting": {"bg": "#d68910", "text": "#000000"},
            "compositing": {"bg": "#196f3d", "text": "#ffffff"},
            "fx": {"bg": "#6c3483", "text": "#ffffff"},
            "modeling": {"bg": "#a93226", "text": "#ffffff"}
        }

        # Get colors for this department
        colors = dept_colors.get(department.lower(), {"bg": "#2d2d2d", "text": "#e0e0e0"})

        track_frame = QFrame()
        track_frame.setFixedHeight(70)  # Increased from 40px to 70px
        track_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid #555555;
                background-color: {colors['bg']};
                border-radius: 3px;
                margin: 1px;
            }}
        """)

        track_layout = QHBoxLayout(track_frame)
        track_layout.setContentsMargins(5, 5, 5, 5)  # Increased margins for better spacing
        track_layout.setSpacing(3)

        # Department label with enhanced styling
        dept_label = QLabel(department.capitalize())
        dept_label.setStyleSheet(f"""
            color: {colors['text']};
            font-weight: bold;
            font-size: 12px;
            background-color: rgba(0, 0, 0, 0.2);
            padding: 4px 8px;
            border-radius: 2px;
        """)
        dept_label.setFixedWidth(100)  # Increased width for better readability
        dept_label.setAlignment(Qt.AlignCenter)
        track_layout.addWidget(dept_label)

        # Shot clips
        for shot_key in shot_keys:
            shot_clip = create_shot_clip(shot_key, department, shots_data.get(shot_key, {}))
            track_layout.addWidget(shot_clip)

        track_layout.addStretch()

        return track_frame

    except Exception as e:
        print(f"Error creating department track: {e}")
        return QFrame()

def create_aligned_department_track(department, shot_keys, shots_data, clip_width, clip_height, label_width):
    """Create a perfectly aligned department track with standardized sizing."""
    try:
        from PySide2.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
        from PySide2.QtCore import Qt

        # Department color scheme
        dept_colors = {
            "animation": {"bg": "#1f4e79", "text": "#ffffff"},
            "lighting": {"bg": "#d68910", "text": "#000000"},
            "compositing": {"bg": "#196f3d", "text": "#ffffff"},
            "fx": {"bg": "#6c3483", "text": "#ffffff"},
            "modeling": {"bg": "#a93226", "text": "#ffffff"}
        }

        # Get colors for this department
        colors = dept_colors.get(department.lower(), {"bg": "#2d2d2d", "text": "#e0e0e0"})

        track_frame = QFrame()
        track_frame.setFixedHeight(70)  # Standardized height
        track_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid #555555;
                background-color: {colors['bg']};
                border-radius: 3px;
                margin: 1px;
            }}
        """)

        track_layout = QHBoxLayout(track_frame)
        track_layout.setContentsMargins(5, 5, 5, 5)
        track_layout.setSpacing(5)  # Consistent spacing

        # Department label with standardized sizing
        dept_label = QLabel(department.capitalize())
        dept_label.setStyleSheet(f"""
            color: {colors['text']};
            font-weight: bold;
            font-size: 12px;
            background-color: rgba(0, 0, 0, 0.2);
            padding: 4px 8px;
            border-radius: 2px;
        """)
        dept_label.setFixedWidth(label_width)  # Standardized width
        dept_label.setAlignment(Qt.AlignCenter)
        track_layout.addWidget(dept_label)

        # Shot clips with perfect alignment
        for shot_key in shot_keys:
            shot_clip = create_aligned_shot_clip(shot_key, department, shots_data.get(shot_key, {}), clip_width, clip_height)
            track_layout.addWidget(shot_clip)

        track_layout.addStretch()

        return track_frame

    except Exception as e:
        print(f"Error creating aligned department track: {e}")
        return QFrame()

def create_grid_department_label(department, label_width, label_height):
    """Create a department label for the grid layout."""
    try:
        from PySide2.QtWidgets import QLabel
        from PySide2.QtCore import Qt

        # Department color scheme
        dept_colors = {
            "animation": {"bg": "#1f4e79", "text": "#ffffff"},
            "lighting": {"bg": "#d68910", "text": "#000000"},
            "compositing": {"bg": "#196f3d", "text": "#ffffff"},
            "fx": {"bg": "#6c3483", "text": "#ffffff"},
            "modeling": {"bg": "#a93226", "text": "#ffffff"}
        }

        # Get colors for this department
        colors = dept_colors.get(department.lower(), {"bg": "#2d2d2d", "text": "#e0e0e0"})

        dept_label = QLabel(department.capitalize())
        dept_label.setStyleSheet(f"""
            color: {colors['text']};
            font-weight: bold;
            font-size: 13px;
            background-color: {colors['bg']};
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #555555;
        """)
        dept_label.setFixedSize(label_width, label_height)
        dept_label.setAlignment(Qt.AlignCenter)

        return dept_label

    except Exception as e:
        print(f"Error creating grid department label: {e}")
        return QLabel("Error")

def create_shot_clip(shot_key, department, shot_data):
    """Create a shot clip widget for the timeline with enhanced styling."""
    try:
        from PySide2.QtWidgets import QPushButton, QMenu
        from PySide2.QtCore import Qt

        # Get versions for this department
        dept_items = shot_data.get(department, [])

        if not dept_items:
            # Empty clip with better styling
            clip = QPushButton("---")
            clip.setFixedSize(85, 50)  # Increased size to match track height
            clip.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.3);
                    color: #666666;
                    border: 1px dashed #444444;
                    font-size: 10px;
                    border-radius: 3px;
                }
            """)
            clip.setEnabled(False)
            return clip

        # Get latest version or first available
        latest_item = dept_items[0]  # Could sort by version here
        version = latest_item.get('version', latest_item.get('linked_version', 'v001'))

        # Create clip button with enhanced styling
        clip = QPushButton(version)
        clip.setFixedSize(85, 50)  # Increased size for better visibility
        clip.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.9);
                color: #000000;
                border: 2px solid #ffffff;
                font-size: 11px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #ffffff;
                border: 2px solid #ffff00;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)

        # Store data for version switching
        clip.setProperty("shot_key", shot_key)
        clip.setProperty("department", department)
        clip.setProperty("versions", [item.get('version', 'v001') for item in dept_items])

        # Connect to version change handler
        clip.clicked.connect(lambda checked=False: on_shot_clip_clicked(clip))

        return clip

    except Exception as e:
        print(f"Error creating shot clip: {e}")
        return QPushButton("Error")

def create_aligned_shot_clip(shot_key, department, shot_data, clip_width, clip_height):
    """Create a shot clip widget with standardized sizing for perfect grid alignment."""
    try:
        from PySide2.QtWidgets import QPushButton, QMenu
        from PySide2.QtCore import Qt

        # Get versions for this department
        dept_items = shot_data.get(department, [])

        if not dept_items:
            # Empty clip with standardized sizing
            clip = QPushButton("---")
            clip.setFixedSize(clip_width, clip_height)
            clip.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.3);
                    color: #666666;
                    border: 1px dashed #444444;
                    font-size: 10px;
                    border-radius: 3px;
                }
            """)
            clip.setEnabled(False)
            return clip

        # Get latest version or first available
        latest_item = dept_items[0]  # Could sort by version here
        version = latest_item.get('version', latest_item.get('linked_version', 'v001'))

        # Create clip button with standardized sizing
        clip = QPushButton(version)
        clip.setFixedSize(clip_width, clip_height)  # Standardized size for perfect alignment
        clip.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.9);
                color: #000000;
                border: 2px solid #ffffff;
                font-size: 11px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #ffffff;
                border: 2px solid #ffff00;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)

        # Store data for version switching
        clip.setProperty("shot_key", shot_key)
        clip.setProperty("department", department)
        clip.setProperty("versions", [item.get('version', 'v001') for item in dept_items])

        # Connect to version change handler
        clip.clicked.connect(lambda checked=False: on_shot_clip_clicked(clip))

        return clip

    except Exception as e:
        print(f"Error creating aligned shot clip: {e}")
        return QPushButton("Error")

def create_grid_department_label(department, label_width, label_height):
    """Create a department label for the grid layout."""
    try:
        from PySide2.QtWidgets import QLabel
        from PySide2.QtCore import Qt

        # Department color scheme
        dept_colors = {
            "animation": {"bg": "#1f4e79", "text": "#ffffff"},
            "lighting": {"bg": "#d68910", "text": "#000000"},
            "compositing": {"bg": "#196f3d", "text": "#ffffff"},
            "fx": {"bg": "#6c3483", "text": "#ffffff"},
            "modeling": {"bg": "#a93226", "text": "#ffffff"}
        }

        # Get colors for this department
        colors = dept_colors.get(department.lower(), {"bg": "#2d2d2d", "text": "#e0e0e0"})

        dept_label = QLabel(department.capitalize())
        dept_label.setStyleSheet(f"""
            color: {colors['text']};
            font-weight: bold;
            font-size: 13px;
            background-color: {colors['bg']};
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #555555;
        """)
        dept_label.setFixedSize(label_width, label_height)
        dept_label.setAlignment(Qt.AlignCenter)

        return dept_label

    except Exception as e:
        print(f"Error creating grid department label: {e}")
        return QLabel("Error")

def create_professional_department_label(department, label_width, label_height):
    """Create a professional department label matching NLE standards."""
    try:
        from PySide2.QtWidgets import QLabel
        from PySide2.QtCore import Qt

        # Professional NLE color scheme - more subtle and industry-standard
        dept_colors = {
            "animation": {"bg": "#2c5aa0", "text": "#ffffff"},      # Professional blue
            "lighting": {"bg": "#b8860b", "text": "#ffffff"},       # Professional gold
            "compositing": {"bg": "#228b22", "text": "#ffffff"},    # Professional green
            "fx": {"bg": "#8b008b", "text": "#ffffff"},             # Professional magenta
            "modeling": {"bg": "#b22222", "text": "#ffffff"}        # Professional red
        }

        # Get colors for this department
        colors = dept_colors.get(department.lower(), {"bg": "#404040", "text": "#ffffff"})

        dept_label = QLabel(department.upper())  # Uppercase for professional look
        dept_label.setStyleSheet(f"""
            QLabel {{
                color: {colors['text']};
                font-weight: bold;
                font-size: 10px;
                background-color: {colors['bg']};
                padding: 0px;
                border: none;
                margin: 0px;
            }}
        """)
        dept_label.setFixedSize(label_width, label_height)
        dept_label.setAlignment(Qt.AlignCenter)

        return dept_label

    except Exception as e:
        print(f"Error creating professional department label: {e}")
        return QLabel("Error")

def create_professional_shot_clip(shot_key, department, shot_data, clip_width, clip_height):
    """Create a professional shot clip matching NLE standards."""
    try:
        from PySide2.QtWidgets import QPushButton, QMenu
        from PySide2.QtCore import Qt

        # Get versions for this department
        dept_items = shot_data.get(department, [])

        # Extract shot name from shot_key
        shot_name = shot_key.split('_')[-1] if '_' in shot_key else shot_key

        if not dept_items:
            # Empty clip with no spacing
            clip = QPushButton(f"{shot_name}\n---")
            clip.setFixedSize(clip_width, clip_height)
            clip.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a1a;
                    color: #666666;
                    border: none;
                    font-size: 9px;
                    margin: 0px;
                    padding: 0px;
                }
            """)
            clip.setEnabled(False)
            return clip

        # Get latest version
        latest_item = dept_items[0]
        version = latest_item.get('version', latest_item.get('linked_version', 'v001'))

        # Create professional clip button with no spacing
        clip = QPushButton(f"{shot_name}\n{version}")
        clip.setFixedSize(clip_width, clip_height)
        clip.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: none;
                font-size: 9px;
                font-weight: bold;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)

        # Store data for version switching
        clip.setProperty("shot_key", shot_key)
        clip.setProperty("shot_name", shot_name)
        clip.setProperty("department", department)
        clip.setProperty("versions", [item.get('version', 'v001') for item in dept_items])

        # Connect to version change handler
        clip.clicked.connect(lambda checked=False: on_shot_clip_clicked(clip))

        return clip

    except Exception as e:
        print(f"Error creating professional shot clip: {e}")
        return QPushButton("Error")

def create_shot_clip_with_name(shot_key, department, shot_data, clip_width, clip_height):
    """Create a shot clip widget with shot name and version displayed."""
    try:
        from PySide2.QtWidgets import QPushButton, QMenu
        from PySide2.QtCore import Qt

        # Get versions for this department
        dept_items = shot_data.get(department, [])

        # Extract shot name from shot_key (e.g., "ep01_sq0010_sh0020" -> "sh0020")
        shot_name = shot_key.split('_')[-1] if '_' in shot_key else shot_key

        if not dept_items:
            # Empty clip with shot name
            clip = QPushButton(f"{shot_name}\n---")
            clip.setFixedSize(clip_width, clip_height)
            clip.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.3);
                    color: #666666;
                    border: 1px dashed #444444;
                    font-size: 10px;
                    border-radius: 3px;
                }
            """)
            clip.setEnabled(False)
            return clip

        # Get latest version or first available
        latest_item = dept_items[0]  # Could sort by version here
        version = latest_item.get('version', latest_item.get('linked_version', 'v001'))

        # Create clip button with shot name and version
        clip = QPushButton(f"{shot_name}\n{version}")
        clip.setFixedSize(clip_width, clip_height)
        clip.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.9);
                color: #000000;
                border: 2px solid #ffffff;
                font-size: 10px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #ffffff;
                border: 2px solid #ffff00;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)

        # Store data for version switching
        clip.setProperty("shot_key", shot_key)
        clip.setProperty("shot_name", shot_name)
        clip.setProperty("department", department)
        clip.setProperty("versions", [item.get('version', 'v001') for item in dept_items])

        # Connect to version change handler
        clip.clicked.connect(lambda checked=False: on_shot_clip_clicked(clip))

        return clip

    except Exception as e:
        print(f"Error creating shot clip with name: {e}")
        return QPushButton("Error")

# Legacy timeline function removed - using playlist timeline version

def on_timeline_filter_changed():
    """Handle timeline filter changes."""
    global timeline_dock

    try:
        timeline_widget = timeline_dock.widget() if timeline_dock else None
        if not timeline_widget:
            return

        # Repopulate timeline with new filters
        populate_timeline_shots(timeline_widget)

    except Exception as e:
        print(f"Error handling timeline filter change: {e}")

# Department order change handler removed - using fixed order now

def on_timeline_height_changed():
    """Handle timeline track height changes."""
    global timeline_dock

    try:
        timeline_widget = timeline_dock.widget() if timeline_dock else None
        if not timeline_widget:
            return

        height_setting = timeline_widget.height_combo.currentText()
        print(f"Changing timeline track height to: {height_setting}")

        # Repopulate timeline with new height settings
        populate_timeline_shots(timeline_widget)

    except Exception as e:
        print(f"Error changing timeline height: {e}")

def on_timeline_zoom_changed():
    """Handle timeline zoom changes."""
    global timeline_dock

    try:
        timeline_widget = timeline_dock.widget() if timeline_dock else None
        if not timeline_widget:
            return

        zoom_setting = timeline_widget.zoom_combo.currentText()
        print(f"Changing timeline zoom to: {zoom_setting}")

        # Apply zoom to timeline grid
        zoom_factor = float(zoom_setting.replace('%', '')) / 100.0
        timeline_widget.timeline_grid_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: #2d2d2d;
            }}
            QWidget {{
                font-size: {int(10 * zoom_factor)}px;
            }}
        """)

        print(f"Applied {zoom_setting} zoom to timeline")

    except Exception as e:
        print(f"Error changing timeline zoom: {e}")

def on_shot_clip_clicked(clip_button):
    """Handle shot clip clicks for version changing."""
    try:
        from PySide2.QtWidgets import QMenu

        shot_key = clip_button.property("shot_key")
        department = clip_button.property("department")
        versions = clip_button.property("versions")

        if not versions:
            print(f"No versions available for {shot_key} {department}")
            return

        # Create context menu for version selection
        menu = QMenu()

        for version in versions:
            action = menu.addAction(version)
            action.triggered.connect(lambda checked, v=version: change_shot_version(clip_button, v))

        # Show menu at button position
        menu.exec_(clip_button.mapToGlobal(clip_button.rect().bottomLeft()))

    except Exception as e:
        print(f"Error handling shot clip click: {e}")

def change_shot_version(clip_button, new_version):
    """Change the version for a specific shot clip."""
    try:
        shot_key = clip_button.property("shot_key")
        shot_name = clip_button.property("shot_name")
        department = clip_button.property("department")

        # Update button text with shot name and new version
        clip_button.setText(f"{shot_name}\n{new_version}")

        print(f"Changed {shot_key} {department} to {new_version}")

        # TODO: Update database or load new version in RV

    except Exception as e:
        print(f"Error changing shot version: {e}")

def on_open_rv_paint():
    """Open Open RV's built-in paint/annotation tools."""
    try:
        # Simulate F10 key press to open Open RV paint tools
        import rv.commands as rvc

        # Try to activate paint mode in Open RV
        # This is equivalent to pressing F10 in Open RV
        try:
            # Method 1: Try to call paint mode directly
            rvc.setStringProperty("#RVPaint.mode.active", ["paint"], True)
            print("Activated Open RV Paint mode")
        except:
            try:
                # Method 2: Try to send F10 key event
                from PySide2.QtWidgets import QApplication
                from PySide2.QtCore import Qt
                from PySide2.QtGui import QKeyEvent

                app = QApplication.instance()
                if app:
                    # Send F10 key event to activate paint mode
                    key_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_F10, Qt.NoModifier)
                    app.sendEvent(app.focusWidget(), key_event)
                    print("Sent F10 key to activate Open RV Paint mode")
                else:
                    print("Could not access QApplication to send F10 key")
            except Exception as e2:
                print(f"Could not activate paint mode: {e2}")
                print("Please press F10 manually to activate Open RV Paint tools")

    except Exception as e:
        print(f"Error opening RV paint tools: {e}")
        print("Please press F10 manually to activate Open RV Paint tools")

def on_export_rv_annotations():
    """Export annotations from Open RV's annotation system."""
    try:
        import rv.commands as rvc

        # Try to get annotation data from Open RV
        try:
            # Get current source
            sources = rvc.sources()
            if not sources:
                print("No sources loaded in Open RV")
                return

            current_source = sources[0]

            # Try to get paint/annotation data
            # This is a placeholder - actual implementation would depend on Open RV's API
            annotations = []

            # Check for paint strokes or annotations
            try:
                # Get paint node properties (if available)
                paint_nodes = rvc.nodesOfType("RVPaint")
                for node in paint_nodes:
                    # Get paint data from node
                    # This would need to be implemented based on Open RV's actual API
                    print(f"Found paint node: {node}")

            except Exception as e:
                print(f"Could not access paint nodes: {e}")

            # Add to annotations popup list as placeholder
            global annotations_popup_window
            if 'annotations_popup_window' in globals() and annotations_popup_window:
                current_frame = get_current_frame()
                annotation_text = f"Exported annotation from frame {current_frame}"
                annotations_popup_window.annotations_list.addItem(annotation_text)

            print("Exported annotations from Open RV (placeholder implementation)")

        except Exception as e:
            print(f"Error accessing Open RV annotation data: {e}")

    except Exception as e:
        print(f"Error exporting RV annotations: {e}")

def on_clear_annotations(popup=None):
    """Handle clearing all annotations."""
    try:
        if popup and hasattr(popup, 'annotations_list'):
            popup.annotations_list.clear()
            print("Cleared all annotations from popup")
        else:
            # Fallback to global popup
            global annotations_popup_window
            if 'annotations_popup_window' in globals() and annotations_popup_window:
                annotations_popup_window.annotations_list.clear()
                print("Cleared all annotations")

    except Exception as e:
        print(f"Error clearing annotations: {e}")

def on_save_annotations(popup=None):
    """Handle saving annotations to database."""
    try:
        if popup and hasattr(popup, 'annotations_list'):
            # Get annotations from popup
            annotations = []
            for i in range(popup.annotations_list.count()):
                item = popup.annotations_list.item(i)
                annotations.append(item.text())
            print(f"Saving {len(annotations)} annotations to database...")
        else:
            # Fallback to global popup
            global annotations_popup_window
            if 'annotations_popup_window' in globals() and annotations_popup_window:
                annotations = []
                for i in range(annotations_popup_window.annotations_list.count()):
                    item = annotations_popup_window.annotations_list.item(i)
                    annotations.append(item.text())
                print(f"Saving {len(annotations)} annotations to database...")

        # TODO: Implement actual saving to Horus database

    except Exception as e:
        print(f"Error saving annotations: {e}")

def get_current_frame():
    """Get current frame from Open RV."""
    try:
        # TODO: Implement actual Open RV frame retrieval
        # For now, return a placeholder
        return 1001
    except Exception as e:
        print(f"Error getting current frame: {e}")
        return 1001

def update_frame_info():
    """Update frame information display."""
    global comments_dock

    try:
        comments_widget = comments_dock.widget() if comments_dock else None
        if not comments_widget:
            return

        current_frame = get_current_frame()
        # TODO: Get actual timecode from Open RV
        timecode = "00:43:15"

        frame_info_text = f"Frame: {current_frame} | Time: {timecode}"
        comments_widget.frame_info_label.setText(frame_info_text)

    except Exception as e:
        print(f"Error updating frame info: {e}")

def load_media_in_rv(file_path):
    """Load media file in Open RV."""
    try:
        import rv.commands as rvc
        rvc.addSource(file_path)
        print(f"Loaded in RV: {file_path}")
    except Exception as e:
        print(f"Error loading in RV: {e}")

def refresh_horus_data():
    """Refresh Horus data."""
    try:
        print("Refreshing Horus data...")
        setup_horus_integration()
        if current_project_id:
            on_project_changed()
        print("Refreshed")
    except Exception as e:
        print(f"Error refreshing: {e}")

def apply_rv_styling(widget):
    """Apply RV dark theme styling."""
    try:
        # Use RV's default dark theme colors
        bg_color = "#3a3a3a"          # Dark gray background
        text_color = "#e0e0e0"        # Light gray text
        highlight_color = "#0078d7"   # Blue highlight
        button_color = "#4a4a4a"      # Slightly lighter gray for buttons
        border_color = "#555555"      # Medium gray borders
        dark_bg = "#2a2a2a"          # Darker background for inputs

        style = f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
                font-family: Arial, sans-serif;
                font-size: 11px;
            }}
            QLabel {{
                background-color: transparent;
                color: {text_color};
            }}
            QLineEdit {{
                background-color: {dark_bg};
                border: 1px solid {border_color};
                border-radius: 3px;
                padding: 4px;
                color: {text_color};
            }}
            QLineEdit:focus {{
                border-color: {highlight_color};
            }}
            QPushButton {{
                background-color: {button_color};
                border: 1px solid {border_color};
                border-radius: 3px;
                padding: 6px 12px;
                color: {text_color};
            }}
            QPushButton:hover {{
                background-color: #5a5a5a;
                border-color: {highlight_color};
            }}
            QPushButton:pressed {{
                background-color: {dark_bg};
            }}
            QComboBox {{
                background-color: {button_color};
                border: 1px solid {border_color};
                border-radius: 3px;
                padding: 4px 6px;
                color: {text_color};
                min-height: 20px;
            }}
            QComboBox:hover {{
                border-color: {highlight_color};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {text_color};
            }}
            QTreeWidget, QListWidget {{
                background-color: {dark_bg};
                border: 1px solid {border_color};
                selection-background-color: {highlight_color};
                alternate-background-color: #333333;
                color: {text_color};
            }}
            QTreeWidget::item {{
                padding: 3px;
                border: none;
            }}
            QTreeWidget::item:selected {{
                background-color: {highlight_color};
                color: white;
            }}
            QScrollArea {{
                background-color: {dark_bg};
                border: 1px solid {border_color};
            }}
            QCheckBox {{
                color: {text_color};
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid {border_color};
                border-radius: 2px;
                background-color: {button_color};
            }}
            QCheckBox::indicator:checked {{
                background-color: {highlight_color};
                border-color: {highlight_color};
            }}
            QFrame {{
                background-color: {bg_color};
                border: none;
            }}
        """

        widget.setStyleSheet(style)

    except Exception as e:
        print(f"Error applying styling: {e}")

def create_modular_media_browser():
    """Create modular dock widgets with Horus integration."""
    global search_dock, comments_dock, timeline_dock, media_grid_dock

    try:
        from PySide2.QtWidgets import QApplication, QMainWindow, QDockWidget, QWidget, QLabel
        from PySide2.QtCore import Qt

        print("Creating modular MediaBrowser with Horus integration...")
        
        # Get RV main window
        app = QApplication.instance()
        if not app:
            print("No QApplication found")
            return False
        
        rv_main_window = None
        for widget in app.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                rv_main_window = widget
                break
        
        if not rv_main_window:
            print("Could not find RV main window")
            return False
        
        print(f"Found RV main window")
        
        # Create panels
        search_panel = create_search_panel()
        media_grid_panel = create_media_grid_panel()
        comments_panel = create_comments_panel()

        # Create timeline panels based on feature flags
        timeline_panel = None
        timeline_playlist_panel = None

        if ENABLE_TIMELINE_PLAYLIST:
            # Create new Timeline Playlist Manager as primary timeline interface
            timeline_playlist_panel = create_timeline_playlist_panel()
            if timeline_playlist_panel:
                print("✅ Timeline Playlist Manager enabled (primary timeline interface)")
            else:
                print("❌ Timeline Playlist Manager creation failed")
                # Fallback to legacy timeline if playlist creation fails
                if ENABLE_LEGACY_TIMELINE:
                    timeline_panel = create_timeline_panel()
                    print("⚠️  Fallback to legacy Timeline Sequence panel")
        elif ENABLE_LEGACY_TIMELINE:
            # Create legacy timeline panel only if explicitly enabled
            timeline_panel = create_timeline_panel()
            print("✅ Legacy Timeline Sequence panel enabled")
        else:
            print("⚠️  No timeline interface enabled")

        # Validate required panels (timeline panels are optional based on feature flags)
        required_panels = [search_panel, media_grid_panel, comments_panel]
        if not all(required_panels):
            print("❌ Failed to create required panels")
            return False

        # Apply styling to all created panels
        panels_to_style = [search_panel, media_grid_panel, comments_panel]
        if timeline_panel:
            panels_to_style.append(timeline_panel)
        if timeline_playlist_panel:
            panels_to_style.append(timeline_playlist_panel)

        for panel in panels_to_style:
            apply_rv_styling(panel)
        
        # ===== NEW 3-SECTION LAYOUT (RV Standard Tabbed Docks) =====
        # LEFT SECTION: Navigator dock + Playlist dock (tabified together)
        # CENTER SECTION: RV Viewer (native)
        # RIGHT SECTION: Comments & Annotations

        # Create Search & Navigate dock (left side) - Narrow, resizable
        search_dock = QDockWidget("Search & Navigate - Horus", rv_main_window)
        search_dock.setWidget(search_panel)
        search_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        search_dock.setMinimumWidth(180)  # Minimum usable width
        # No max width - fully resizable

        # Create Playlist Manager dock (left side) - Resizable
        playlist_dock = None
        if timeline_playlist_panel:
            playlist_dock = QDockWidget("Playlist Manager", rv_main_window)
            playlist_dock.setWidget(timeline_playlist_panel)
            playlist_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
            playlist_dock.setMinimumWidth(180)  # Minimum usable width
            # No max width - fully resizable

        # Create comments dock (right side)
        comments_dock = QDockWidget("Comments & Annotations", rv_main_window)
        comments_dock.setWidget(comments_panel)
        comments_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        comments_dock.setMinimumWidth(200)
        comments_dock.setMaximumWidth(16777215)
        comments_dock.resize(340, 600)

        # Media grid dock (hidden by default, can be shown if needed)
        media_grid_dock = QDockWidget("Media Grid - Horus", rv_main_window)
        media_grid_dock.setWidget(media_grid_panel)
        media_grid_dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        media_grid_dock.hide()  # Hidden by default in new layout

        # Add dock widgets to RV main window
        rv_main_window.addDockWidget(Qt.LeftDockWidgetArea, search_dock)

        # Add playlist dock and tabify with search dock (RV standard)
        if playlist_dock:
            rv_main_window.addDockWidget(Qt.LeftDockWidgetArea, playlist_dock)
            rv_main_window.tabifyDockWidget(search_dock, playlist_dock)
            # Make search dock the active tab by default
            search_dock.raise_()
            print("✅ Navigator and Playlist docks tabified together (RV standard)")

            # Populate playlist tree
            populate_playlist_tree()
            print("✅ Playlist tree populated with existing playlists")

        rv_main_window.addDockWidget(Qt.RightDockWidgetArea, comments_dock)
        rv_main_window.addDockWidget(Qt.RightDockWidgetArea, media_grid_dock)

        # Store global references for access from other functions
        globals()['search_dock'] = search_dock
        globals()['comments_dock'] = comments_dock
        globals()['media_grid_dock'] = media_grid_dock

        if playlist_dock:
            globals()['playlist_dock'] = playlist_dock
            globals()['timeline_playlist_dock'] = playlist_dock  # For backward compatibility

        # Show core panels
        search_dock.show()
        comments_dock.show()
        if playlist_dock:
            playlist_dock.show()

        # New 3-section layout is now active
        print("✅ 3-Section Layout Active (RV Standard):")
        print("   LEFT: Navigator + Playlist (Tabbed, width reduced by 50%)")
        print("   CENTER: RV Viewer")
        print("   RIGHT: Comments & Annotations")
        
        # Setup Horus integration
        setup_horus_integration()

        print("SUCCESS: Modular MediaBrowser with Horus integration created!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# Create the modular browser
success = create_modular_media_browser()

if success:
    print("🎉 SUCCESS: Open RV MediaBrowser with Horus integration!")
    print("📋 Core Features:")
    print("  ✅ Project selection in Search panel")
    print("  ✅ Media grid with Horus metadata")
    print("  ✅ Click media items to load in RV")
    print("  ✅ Real-time data from Horus database")
    print("  ✅ Professional comment threading system")

    # Timeline interface status
    if ENABLE_TIMELINE_PLAYLIST and 'timeline_playlist_dock' in globals() and timeline_playlist_dock:
        print("🎬 PRIMARY TIMELINE INTERFACE:")
        print("  ✅ Timeline Playlist Manager (NLE-Style)")
        print("    * Professional left/right panel layout")
        print("    * Playlist creation, duplication, rename, deletion")
        print("    * Department-based color coding")
        print("    * Timeline visualization with tracks and rulers")
        print("    * Click timeline clips to load in Open RV")
        print("    * Integrated with Horus three-panel system")

        if ENABLE_LEGACY_TIMELINE and 'timeline_dock' in globals() and timeline_dock:
            print("  📝 Legacy Timeline Sequence (Secondary Tab)")
        else:
            print("  📝 Legacy Timeline Sequence (Disabled)")

    elif ENABLE_LEGACY_TIMELINE and 'timeline_dock' in globals() and timeline_dock:
        print("🎬 TIMELINE INTERFACE:")
        print("  ✅ Legacy Timeline Sequence (Primary)")
        print("  📝 Timeline Playlist Manager (Disabled)")
    else:
        print("⚠️  No timeline interface enabled")

    print("\n🚀 Timeline Playlist Manager is now the primary timeline interface!")
else:
    print("❌ Failed to create MediaBrowser")
