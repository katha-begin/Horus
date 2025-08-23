"""
Horus Timeline Playlist Panel
============================

Main Timeline Playlist panel creation and management.
"""

from horus.utils.globals import timeline_playlist_dock, timeline_playlist_data, current_playlist_id
from horus.timeline_playlist.playlist_data import load_timeline_playlist_data, save_timeline_playlist_data
from horus.timeline_playlist.playlist_tree import create_playlist_tree_panel, populate_playlist_tree
from horus.timeline_playlist.timeline_tracks import create_timeline_tracks_panel
from horus.timeline_playlist.playlist_handlers import (
    on_playlist_tree_selection_changed, on_playlist_double_clicked,
    create_new_playlist, duplicate_current_playlist, rename_current_playlist,
    delete_current_playlist, show_add_media_dialog, refresh_timeline_playlists,
    play_current_playlist, stop_playlist_playback, on_timeline_zoom_changed
)


def create_timeline_playlist_panel():
    """Create Timeline Playlist panel integrated into Horus-RV."""
    try:
        from PySide2.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTreeWidget, QTreeWidgetItem,
            QScrollArea, QFrame, QLabel, QPushButton, QLineEdit, QComboBox,
            QMenu, QAction, QMessageBox, QInputDialog, QAbstractItemView, QGridLayout
        )
        from PySide2.QtCore import Qt

        # Main widget
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Header with title and main controls
        header = create_timeline_playlist_header()
        main_layout.addWidget(header)

        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Left panel - Playlist tree and controls
        left_panel = create_playlist_tree_panel()
        left_panel.setMinimumWidth(250)
        left_panel.setMaximumWidth(400)
        splitter.addWidget(left_panel)

        # Right panel - Timeline tracks
        right_panel = create_timeline_tracks_panel()
        right_panel.setMinimumWidth(400)
        splitter.addWidget(right_panel)

        # Set splitter proportions (30% left, 70% right)
        splitter.setSizes([300, 700])
        main_layout.addWidget(splitter)

        # Store references for access
        widget.header = header
        widget.left_panel = left_panel
        widget.right_panel = right_panel
        widget.splitter = splitter

        # Load initial data
        load_timeline_playlist_data()
        populate_playlist_tree()

        print("✅ Timeline Playlist panel created successfully")
        return widget

    except Exception as e:
        print(f"❌ Error creating Timeline Playlist panel: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_timeline_playlist_header():
    """Create header with title and main controls."""
    from PySide2.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
    from PySide2.QtCore import Qt

    header_frame = QFrame()
    header_layout = QHBoxLayout(header_frame)
    header_layout.setContentsMargins(5, 5, 5, 5)
    header_layout.setSpacing(10)

    # Title
    title_label = QLabel("Timeline Playlist Manager")
    title_label.setStyleSheet("""
        QLabel {
            font-weight: bold;
            font-size: 14px;
            color: #e0e0e0;
            padding: 2px 0px;
        }
    """)
    header_layout.addWidget(title_label)

    header_layout.addStretch()

    # Main control buttons
    new_playlist_btn = QPushButton("New Playlist")
    new_playlist_btn.setObjectName("new_playlist_btn")
    new_playlist_btn.clicked.connect(create_new_playlist)
    header_layout.addWidget(new_playlist_btn)

    refresh_btn = QPushButton("Refresh")
    refresh_btn.setObjectName("refresh_btn")
    refresh_btn.clicked.connect(refresh_timeline_playlists)
    header_layout.addWidget(refresh_btn)

    # Playback controls
    play_btn = QPushButton("▶ Play")
    play_btn.setObjectName("play_btn")
    play_btn.clicked.connect(play_current_playlist)
    header_layout.addWidget(play_btn)

    stop_btn = QPushButton("⏹ Stop")
    stop_btn.setObjectName("stop_btn")
    stop_btn.clicked.connect(stop_playlist_playback)
    header_layout.addWidget(stop_btn)

    return header_frame
