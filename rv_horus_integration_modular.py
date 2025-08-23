#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Open RV MediaBrowser with Horus Integration
===========================================

Integrates our modular MediaBrowser dock widgets with Horus's JSON database
to display media data from the Horus application within Open RV.

This file serves as the main orchestration layer for the modular Horus components.
"""

import sys
import os

# Add path for MediaBrowser package
try:
    project_root = os.getcwd()
    media_browser_path = os.path.join(project_root, 'src', 'packages', 'media_browser', 'python')
    sys.path.insert(0, media_browser_path)

    # Add path for Horus modular components
    horus_path = os.path.join(project_root, 'horus')
    sys.path.insert(0, horus_path)
    print(f"Added paths: {media_browser_path}, {horus_path}")
except Exception as e:
    print(f"Error setting up paths: {e}")

# Import Horus data connector
try:
    from media_browser.horus_data_connector import get_horus_connector
    print("✅ Imported Horus data connector")
except ImportError as e:
    print(f"❌ Failed to import Horus data connector: {e}")
    # Create a dummy connector for testing
    def get_horus_connector():
        return None

# Import modular Horus components with fallbacks
try:
    from horus.utils.globals import *
    from horus.utils.resource_utils import get_resource_path
    print("✅ Imported Horus utilities")
except ImportError as e:
    print(f"❌ Failed to import Horus utilities: {e}")
    # Create fallback globals
    search_dock = None
    comments_dock = None
    timeline_dock = None
    media_grid_dock = None
    timeline_playlist_dock = None
    horus_connector = None
    current_project_id = None
    annotations_popup_window = None
    ENABLE_TIMELINE_PLAYLIST = True
    ENABLE_LEGACY_TIMELINE = False
    timeline_playlist_data = []
    current_playlist_id = None

    def get_resource_path(relative_path):
        return os.path.join(os.path.abspath("."), relative_path)

# Import panel creation functions with fallbacks
try:
    from horus.media_browser.search_panel import create_search_panel
    print("✅ Imported search panel")
except ImportError as e:
    print(f"❌ Failed to import search panel: {e}")
    def create_search_panel():
        from PySide2.QtWidgets import QLabel
        return QLabel("Search Panel - Module not found")

try:
    from horus.media_browser.media_grid_panel import create_media_grid_panel
    print("✅ Imported media grid panel")
except ImportError as e:
    print(f"❌ Failed to import media grid panel: {e}")
    def create_media_grid_panel():
        from PySide2.QtWidgets import QLabel
        return QLabel("Media Grid Panel - Module not found")

try:
    from horus.comments.comments_panel import create_comments_panel
    print("✅ Imported comments panel")
except ImportError as e:
    print(f"❌ Failed to import comments panel: {e}")
    def create_comments_panel():
        from PySide2.QtWidgets import QLabel
        return QLabel("Comments Panel - Module not found")

try:
    from horus.timeline_playlist.timeline_playlist_panel import create_timeline_playlist_panel
    print("✅ Imported timeline playlist panel")
except ImportError as e:
    print(f"❌ Failed to import timeline playlist panel: {e}")
    def create_timeline_playlist_panel():
        from PySide2.QtWidgets import QLabel
        return QLabel("Timeline Playlist Panel - Module not found")

try:
    from horus.database.horus_integration import setup_horus_integration
    print("✅ Imported database integration")
except ImportError as e:
    print(f"❌ Failed to import database integration: {e}")
    def setup_horus_integration():
        print("Database integration not available")

try:
    from horus.ui_components.styling import apply_rv_styling
    print("✅ Imported styling")
except ImportError as e:
    print(f"❌ Failed to import styling: {e}")
    def apply_rv_styling(widget):
        print("Styling not available")

print("Loading Open RV MediaBrowser with Horus integration...")


def create_modular_media_browser():
    """Create modular dock widgets with Horus integration."""
    global search_dock, comments_dock, timeline_dock, media_grid_dock, timeline_playlist_dock

    try:
        # Import Open RV modules
        import rv.rvui
        import rv.commands as rvc
        from PySide2.QtWidgets import QDockWidget
        from PySide2.QtCore import Qt

        # Get main window
        main_window = None
        for widget in rv.rvui.qtutils.sessionWindow().findChildren(rv.rvui.qtutils.sessionWindow().__class__):
            if hasattr(widget, 'menuBar'):
                main_window = widget
                break
        
        if not main_window:
            main_window = rv.rvui.qtutils.sessionWindow()
        
        print(f"Found RV main window")
        
        # Create panels using modular components
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
        else:
            print("⚠️  Timeline Playlist disabled")

        # Create dock widgets
        if search_panel:
            search_dock = QDockWidget("Search & Filters", main_window)
            search_dock.setWidget(search_panel)
            search_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
            main_window.addDockWidget(Qt.LeftDockWidgetArea, search_dock)
            apply_rv_styling(search_dock)

        if media_grid_panel:
            media_grid_dock = QDockWidget("Media Grid", main_window)
            media_grid_dock.setWidget(media_grid_panel)
            media_grid_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
            main_window.addDockWidget(Qt.LeftDockWidgetArea, media_grid_dock)
            apply_rv_styling(media_grid_dock)

        if comments_panel:
            comments_dock = QDockWidget("Comments & Annotations", main_window)
            comments_dock.setWidget(comments_panel)
            comments_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
            main_window.addDockWidget(Qt.RightDockWidgetArea, comments_dock)
            apply_rv_styling(comments_dock)

        # Timeline Playlist dock (primary timeline interface)
        if timeline_playlist_panel:
            timeline_playlist_dock = QDockWidget("Timeline Playlist Manager", main_window)
            timeline_playlist_dock.setWidget(timeline_playlist_panel)
            timeline_playlist_dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
            main_window.addDockWidget(Qt.BottomDockWidgetArea, timeline_playlist_dock)
            apply_rv_styling(timeline_playlist_dock)

        # Organize dock layout
        if search_dock and media_grid_dock:
            main_window.tabifyDockWidget(search_dock, media_grid_dock)
            search_dock.raise_()  # Bring search to front

        # Show dock widgets
        if search_dock:
            search_dock.show()
            search_dock.raise_()
            print("✅ Search panel displayed")

        if media_grid_dock:
            media_grid_dock.show()
            print("✅ Media grid displayed")

        if comments_dock:
            comments_dock.show()
            comments_dock.raise_()
            print("✅ Comments panel displayed")

        if timeline_playlist_dock:
            timeline_playlist_dock.show()
            timeline_playlist_dock.raise_()
            print("✅ Timeline Playlist Manager displayed")
        
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
    print("🎉 Horus modular integration loaded successfully!")
else:
    print("❌ Failed to load Horus modular integration")
