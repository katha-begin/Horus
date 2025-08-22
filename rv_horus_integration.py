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

# Add path for MediaBrowser package
try:
    project_root = os.getcwd()
    media_browser_path = os.path.join(project_root, 'src', 'packages', 'media_browser', 'python')
    sys.path.insert(0, media_browser_path)
except:
    pass

# Import Horus data connector
from media_browser.horus_data_connector import get_horus_connector

print("Loading Open RV MediaBrowser with Horus integration...")

# Global references
search_dock = None
comments_dock = None
timeline_dock = None
media_grid_dock = None
horus_connector = None
current_project_id = None

def create_search_panel():
    """Create search panel with Horus project selection."""
    try:
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, 
                                       QTreeWidget, QCheckBox, QLabel, QTreeWidgetItem,
                                       QComboBox, QPushButton, QFrame)
        from PySide2.QtCore import Qt
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("Search & Navigate - Horus")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: #0078d7;")
        layout.addWidget(header)

        # Horus project selection
        layout.addWidget(QLabel("Horus Project:"))
        project_selector = QComboBox()
        project_selector.setObjectName("project_selector")
        layout.addWidget(project_selector)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("refresh_horus_btn")
        layout.addWidget(refresh_btn)
        
        # Search input
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search files...")
        layout.addWidget(search_input)
        
        # Filters
        layout.addWidget(QLabel("File Type Filters:"))
        
        images_filter = QCheckBox("Images")
        images_filter.setChecked(True)
        layout.addWidget(images_filter)
        
        videos_filter = QCheckBox("Videos")
        videos_filter.setChecked(True)
        layout.addWidget(videos_filter)
        
        # Directory tree
        layout.addWidget(QLabel("Project Structure:"))
        
        directory_tree = QTreeWidget()
        directory_tree.setHeaderLabel("Tasks & Media")
        directory_tree.setObjectName("directory_tree")
        layout.addWidget(directory_tree, 1)
        
        # Store references
        widget.project_selector = project_selector
        widget.refresh_horus_btn = refresh_btn
        widget.directory_tree = directory_tree
        
        print("Search panel created")
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
        # Initialize Horus connector
        horus_connector = get_horus_connector()

        if not horus_connector.is_available():
            print("Horus data not available")
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
            project_id = project.get('id', '')
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
        
        # Update tree
        update_directory_tree(project_id, media_items)
        
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
        
        # Click handler
        def on_click():
            try:
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
            except Exception as e:
                print(f"Error: {e}")
        
        widget.mousePressEvent = lambda event: on_click()
        
        return widget
        
    except Exception as e:
        print(f"Error creating widget: {e}")
        return QWidget()

def update_directory_tree(project_id, media_items):
    """Update directory tree."""
    global search_dock

    try:
        print(f"Updating directory tree for project {project_id} with {len(media_items)} items")

        search_widget = search_dock.widget() if search_dock else None
        if not search_widget:
            print("No search widget found")
            return

        tree_widget = search_widget.directory_tree
        if not tree_widget:
            print("No tree widget found")
            return

        tree_widget.clear()
        
        # Group by task
        tasks_dict = {}
        for item in media_items:
            # Try both task_id and linked_task_id fields
            task_id = item.get('task_id') or item.get('linked_task_id', 'Unknown')
            if task_id not in tasks_dict:
                tasks_dict[task_id] = []
            tasks_dict[task_id].append(item)

        print(f"Found {len(tasks_dict)} tasks: {list(tasks_dict.keys())}")
        
        # Create tree
        from PySide2.QtWidgets import QTreeWidgetItem
        from PySide2.QtCore import Qt
        
        project_item = QTreeWidgetItem(tree_widget)
        project_item.setText(0, f"Project: {project_id}")
        
        for task_id, task_media in tasks_dict.items():
            task_item = QTreeWidgetItem(project_item)
            task_item.setText(0, f"{task_id} ({len(task_media)} files)")
            
            for media_item in task_media:
                file_name = media_item.get('file_name', 'Unknown')
                version = media_item.get('version', '')
                
                media_tree_item = QTreeWidgetItem(task_item)
                media_tree_item.setText(0, f"{file_name} ({version})")
                media_tree_item.setData(0, Qt.UserRole, media_item)
        
        tree_widget.expandAll()
        
    except Exception as e:
        print(f"Error updating tree: {e}")

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
        
        # Simple placeholder panels
        from PySide2.QtWidgets import QVBoxLayout

        comments_panel = QWidget()
        comments_layout = QVBoxLayout(comments_panel)
        comments_layout.addWidget(QLabel("Comments & Annotations"))

        timeline_panel = QWidget()
        timeline_layout = QVBoxLayout(timeline_panel)
        timeline_layout.addWidget(QLabel("Timeline Sequence"))
        
        if not all([search_panel, media_grid_panel, comments_panel, timeline_panel]):
            print("Failed to create panels")
            return False
        
        # Apply styling
        for panel in [search_panel, media_grid_panel, comments_panel, timeline_panel]:
            apply_rv_styling(panel)
        
        # Create dock widgets
        search_dock = QDockWidget("Search & Navigate - Horus", rv_main_window)
        search_dock.setWidget(search_panel)
        search_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        comments_dock = QDockWidget("Comments & Annotations", rv_main_window)
        comments_dock.setWidget(comments_panel)
        comments_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        timeline_dock = QDockWidget("Timeline Sequence", rv_main_window)
        timeline_dock.setWidget(timeline_panel)
        timeline_dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        
        media_grid_dock = QDockWidget("Media Grid - Horus", rv_main_window)
        media_grid_dock.setWidget(media_grid_panel)
        media_grid_dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        
        # Add to RV
        rv_main_window.addDockWidget(Qt.LeftDockWidgetArea, search_dock)
        rv_main_window.addDockWidget(Qt.RightDockWidgetArea, comments_dock)
        rv_main_window.addDockWidget(Qt.BottomDockWidgetArea, timeline_dock)
        rv_main_window.addDockWidget(Qt.RightDockWidgetArea, media_grid_dock)
        
        # Show panels
        search_dock.show()
        comments_dock.show()
        timeline_dock.show()
        media_grid_dock.show()
        
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
    print("SUCCESS: Open RV MediaBrowser with Horus integration!")
    print("Features:")
    print("  - Project selection in Search panel")
    print("  - Media grid with Horus metadata")
    print("  - Click media items to load in RV")
    print("  - Real-time data from Horus database")
else:
    print("Failed to create MediaBrowser")
