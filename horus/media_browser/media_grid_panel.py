"""
Horus Media Grid Panel
=====================

Media grid panel for displaying Horus data with thumbnails.
"""

from horus.utils.globals import media_grid_dock
from horus.media_browser.media_widgets import create_media_widget


def create_media_grid_panel():
    """Create media grid panel for Horus data."""
    try:
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                       QScrollArea, QFrame, QGridLayout)
        from PySide2.QtCore import Qt

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Header
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(5, 5, 5, 5)

        # Path display
        path_label = QLabel("No project selected")
        path_label.setObjectName("path_label")
        path_label.setStyleSheet("font-weight: bold; color: #e0e0e0;")
        header_layout.addWidget(path_label)

        header_layout.addStretch()

        # Status display
        status_label = QLabel("Ready")
        status_label.setObjectName("status_label")
        status_label.setStyleSheet("color: #888888; font-size: 10px;")
        header_layout.addWidget(status_label)

        layout.addWidget(header_frame)

        # Scrollable grid area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Grid container
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(10)
        grid_layout.setContentsMargins(10, 10, 10, 10)

        # Add placeholder message
        placeholder_label = QLabel("Select a project to view media")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 14px;
                padding: 50px;
                border: 2px dashed #555555;
                border-radius: 8px;
                background-color: #1e1e1e;
            }
        """)
        grid_layout.addWidget(placeholder_label, 0, 0, 1, 4)

        scroll_area.setWidget(grid_container)
        layout.addWidget(scroll_area)

        # Store references
        widget.path_label = path_label
        widget.status_label = status_label
        widget.grid_layout = grid_layout
        widget.grid_container = grid_container
        widget.scroll_area = scroll_area
        widget.placeholder_label = placeholder_label

        print("✅ Media grid panel created successfully")
        return widget

    except Exception as e:
        print(f"❌ Error creating media grid panel: {e}")
        import traceback
        traceback.print_exc()
        return None


def populate_media_grid(media_items):
    """Populate media grid with Horus data."""
    global media_grid_dock

    try:
        if not media_grid_dock:
            return

        media_grid_widget = media_grid_dock.widget()
        if not media_grid_widget:
            return

        # Clear existing items
        grid_layout = media_grid_widget.grid_layout
        
        # Remove all widgets from grid
        for i in reversed(range(grid_layout.count())):
            child = grid_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        if not media_items:
            # Show placeholder if no items
            placeholder_label = QLabel("No media found for current filters")
            placeholder_label.setAlignment(Qt.AlignCenter)
            placeholder_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 14px;
                    padding: 50px;
                    border: 2px dashed #555555;
                    border-radius: 8px;
                    background-color: #1e1e1e;
                }
            """)
            grid_layout.addWidget(placeholder_label, 0, 0, 1, 4)
            return

        # Add media items to grid
        columns = 4  # Number of columns in grid
        for index, media_item in enumerate(media_items):
            row = index // columns
            col = index % columns
            
            media_widget = create_media_widget(media_item)
            grid_layout.addWidget(media_widget, row, col)

        # Add stretch to push items to top-left
        grid_layout.setRowStretch(len(media_items) // columns + 1, 1)
        grid_layout.setColumnStretch(columns, 1)

        print(f"✅ Populated media grid with {len(media_items)} items")

    except Exception as e:
        print(f"❌ Error populating media grid: {e}")
        import traceback
        traceback.print_exc()
