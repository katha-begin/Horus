"""
Horus Playlist Tree
==================

Playlist tree widget and management for the timeline playlist panel.
"""

from horus.utils.globals import timeline_playlist_dock, timeline_playlist_data, current_playlist_id


def create_playlist_tree_panel():
    """Create left panel with playlist tree and controls."""
    try:
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTreeWidget, 
                                       QAbstractItemView, QFrame, QGridLayout, QPushButton)
        from PySide2.QtCore import Qt

        # Left panel container
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)

        # Playlist tree header
        tree_header = QLabel("Playlists")
        tree_header.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 12px;
                color: #e0e0e0;
                padding: 4px 0px;
                border-bottom: 1px solid #555555;
            }
        """)
        left_layout.addWidget(tree_header)

        # Playlist tree widget
        playlist_tree = QTreeWidget()
        playlist_tree.setObjectName("playlist_tree")
        playlist_tree.setHeaderHidden(True)
        playlist_tree.setRootIsDecorated(True)
        playlist_tree.setSelectionMode(QAbstractItemView.SingleSelection)
        playlist_tree.setAlternatingRowColors(True)
        
        # Configure tree appearance
        playlist_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                color: #e0e0e0;
                font-size: 11px;
                outline: none;
            }
            QTreeWidget::item {
                padding: 4px;
                border: none;
            }
            QTreeWidget::item:hover {
                background-color: #3a3a3a;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: none;
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
                image: none;
            }
        """)
        
        left_layout.addWidget(playlist_tree)

        # Playlist controls
        controls_frame = QFrame()
        controls_layout = QGridLayout(controls_frame)
        controls_layout.setContentsMargins(0, 5, 0, 0)
        controls_layout.setSpacing(3)

        # Control buttons
        duplicate_btn = QPushButton("Duplicate")
        duplicate_btn.setObjectName("duplicate_btn")
        duplicate_btn.setToolTip("Duplicate selected playlist")
        controls_layout.addWidget(duplicate_btn, 0, 0)

        rename_btn = QPushButton("Rename")
        rename_btn.setObjectName("rename_btn")
        rename_btn.setToolTip("Rename selected playlist")
        controls_layout.addWidget(rename_btn, 0, 1)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("delete_btn")
        delete_btn.setToolTip("Delete selected playlist")
        controls_layout.addWidget(delete_btn, 1, 0)

        add_media_btn = QPushButton("Add Media")
        add_media_btn.setObjectName("add_media_btn")
        add_media_btn.setToolTip("Add media to selected playlist")
        controls_layout.addWidget(add_media_btn, 1, 1)

        left_layout.addWidget(controls_frame)

        # Store references
        left_panel.playlist_tree = playlist_tree
        left_panel.duplicate_btn = duplicate_btn
        left_panel.rename_btn = rename_btn
        left_panel.delete_btn = delete_btn
        left_panel.add_media_btn = add_media_btn

        # Connect signals (will be connected in handlers module)
        from horus.timeline_playlist.playlist_handlers import (
            on_playlist_tree_selection_changed, on_playlist_double_clicked,
            duplicate_current_playlist, rename_current_playlist,
            delete_current_playlist, show_add_media_dialog
        )
        
        playlist_tree.itemSelectionChanged.connect(on_playlist_tree_selection_changed)
        playlist_tree.itemDoubleClicked.connect(on_playlist_double_clicked)
        duplicate_btn.clicked.connect(duplicate_current_playlist)
        rename_btn.clicked.connect(rename_current_playlist)
        delete_btn.clicked.connect(delete_current_playlist)
        add_media_btn.clicked.connect(show_add_media_dialog)

        print("✅ Playlist tree panel created")
        return left_panel

    except Exception as e:
        print(f"❌ Error creating playlist tree panel: {e}")
        import traceback
        traceback.print_exc()
        return None


def populate_playlist_tree():
    """Populate the playlist tree with data."""
    global timeline_playlist_dock

    try:
        if not timeline_playlist_dock:
            return

        widget = timeline_playlist_dock.widget()
        if not widget or not hasattr(widget, 'left_panel'):
            return

        playlist_tree = widget.left_panel.playlist_tree
        playlist_tree.clear()

        # Group playlists by type
        playlist_groups = {}
        for playlist in timeline_playlist_data:
            playlist_type = playlist.get('type', 'other').title()
            if playlist_type not in playlist_groups:
                playlist_groups[playlist_type] = []
            playlist_groups[playlist_type].append(playlist)

        # Add grouped items to tree
        from PySide2.QtWidgets import QTreeWidgetItem
        
        for group_name, playlists in playlist_groups.items():
            # Create group item
            group_item = QTreeWidgetItem(playlist_tree)
            group_item.setText(0, f"{group_name} ({len(playlists)})")
            group_item.setExpanded(True)
            
            # Style group item
            font = group_item.font(0)
            font.setBold(True)
            group_item.setFont(0, font)

            # Add playlist items
            for playlist in playlists:
                playlist_item = QTreeWidgetItem(group_item)
                playlist_name = playlist.get('name', 'Unknown Playlist')
                playlist_status = playlist.get('status', 'active')
                
                # Add status indicator
                status_icon = "🔒" if playlist_status == "locked" else "📋"
                playlist_item.setText(0, f"{status_icon} {playlist_name}")
                
                # Store playlist data
                playlist_item.setData(0, Qt.UserRole, playlist)

        print(f"✅ Populated playlist tree with {len(timeline_playlist_data)} playlists")

    except Exception as e:
        print(f"❌ Error populating playlist tree: {e}")
        import traceback
        traceback.print_exc()


# Import required Qt classes at module level
try:
    from PySide2.QtCore import Qt
except ImportError:
    print("Warning: PySide2 not available for playlist tree")
