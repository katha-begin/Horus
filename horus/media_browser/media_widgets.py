"""
Horus Media Widgets
==================

Individual media item widgets for the media grid.
"""


def create_media_widget(media_item):
    """Create widget for media item."""
    try:
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                       QPushButton, QFrame, QMenu, QAction)
        from PySide2.QtCore import Qt, QSize
        from PySide2.QtGui import QPixmap, QPainter, QBrush, QColor

        widget = QWidget()
        widget.setFixedSize(180, 140)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)

        # Thumbnail
        thumbnail_label = QLabel()
        thumbnail_label.setFixedSize(170, 96)
        thumbnail_label.setAlignment(Qt.AlignCenter)
        thumbnail_label.setStyleSheet("""
            QLabel {
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #1e1e1e;
            }
        """)

        # Try to load thumbnail
        thumbnail_path = media_item.get('thumbnail_path', '')
        if thumbnail_path:
            try:
                pixmap = QPixmap(thumbnail_path)
                if not pixmap.isNull():
                    # Scale pixmap to fit label
                    scaled_pixmap = pixmap.scaled(
                        170, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    thumbnail_label.setPixmap(scaled_pixmap)
                else:
                    thumbnail_label.setText("📁\nNo Preview")
            except:
                thumbnail_label.setText("📁\nNo Preview")
        else:
            thumbnail_label.setText("📁\nNo Preview")

        layout.addWidget(thumbnail_label)

        # File info
        file_name = media_item.get('file_name', 'Unknown')
        if len(file_name) > 20:
            file_name = file_name[:17] + "..."

        name_label = QLabel(file_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 10px;
                font-weight: bold;
                padding: 2px;
            }
        """)
        layout.addWidget(name_label)

        # Version and status
        info_layout = QHBoxLayout()
        info_layout.setSpacing(5)

        # Version
        version = media_item.get('version', 'v001')
        version_label = QLabel(version)
        version_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 9px;
                padding: 1px 3px;
                border: 1px solid #555555;
                border-radius: 2px;
                background-color: #2d2d2d;
            }
        """)
        info_layout.addWidget(version_label)

        info_layout.addStretch()

        # Status indicator
        status = media_item.get('status', 'pending')
        status_colors = {
            'approved': '#44ff44',
            'pending': '#ffaa00',
            'rejected': '#ff4444'
        }
        status_color = status_colors.get(status, '#888888')

        status_indicator = QLabel("●")
        status_indicator.setStyleSheet(f"""
            QLabel {{
                color: {status_color};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        status_indicator.setToolTip(f"Status: {status.title()}")
        info_layout.addWidget(status_indicator)

        layout.addLayout(info_layout)

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
                    # Right click - context menu
                    menu = QMenu(widget)
                    
                    load_action = QAction("Load in RV", menu)
                    load_action.triggered.connect(lambda: on_click_load_rv(media_item))
                    menu.addAction(load_action)
                    
                    add_to_playlist_action = QAction("Add to Playlist", menu)
                    add_to_playlist_action.triggered.connect(lambda: on_add_to_playlist(media_item))
                    menu.addAction(add_to_playlist_action)
                    
                    menu.addSeparator()
                    
                    info_action = QAction("Show Info", menu)
                    info_action.triggered.connect(lambda: on_show_info(media_item))
                    menu.addAction(info_action)
                    
                    menu.exec_(event.globalPos())

            except Exception as e:
                print(f"Error handling click: {e}")

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

        def on_add_to_playlist(media_item):
            """Add media item to current playlist."""
            try:
                from horus.timeline_playlist.playlist_handlers import add_media_to_current_playlist
                add_media_to_current_playlist(media_item)
            except Exception as e:
                print(f"Error adding to playlist: {e}")

        def on_show_info(media_item):
            """Show media item information."""
            print(f"Media Info: {media_item}")

        widget.mousePressEvent = on_click
        
        return widget
        
    except Exception as e:
        print(f"Error creating widget: {e}")
        from PySide2.QtWidgets import QWidget
        return QWidget()
