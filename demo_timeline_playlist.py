#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo Timeline Playlist Widget
============================

Standalone demo for testing the Timeline Playlist Widget outside of Open RV.
This allows development and testing of the widget functionality.
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    from PySide2.QtCore import Qt
    from horus_timeline_playlist_widget import HorusTimelinePlaylistWidget
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure PySide2 is installed: pip install PySide2")
    sys.exit(1)


class TimelinePlaylistDemo(QMainWindow):
    """Demo window for Timeline Playlist Widget."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Horus Timeline Playlist Widget Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create Timeline Playlist Widget
        self.playlist_widget = HorusTimelinePlaylistWidget()
        layout.addWidget(self.playlist_widget)
        
        # Connect signals
        self.playlist_widget.playback_requested.connect(self.on_playback_requested)
        self.playlist_widget.playlist_selected.connect(self.on_playlist_selected)
        self.playlist_widget.clip_selected.connect(self.on_clip_selected)
        
        print("Timeline Playlist Demo initialized")
        print("Features available:")
        print("- Create new playlists")
        print("- View existing playlists from sample_db/horus_playlists.json")
        print("- Timeline visualization with department color coding")
        print("- Playlist management (duplicate, rename, delete)")
        
    def on_playback_requested(self, media_path, frame):
        """Handle playback request."""
        print(f"Demo: Playback requested - {media_path} at frame {frame}")
        print("(In real integration, this would load the media in Open RV)")
        
    def on_playlist_selected(self, playlist_id):
        """Handle playlist selection."""
        print(f"Demo: Playlist selected - {playlist_id}")
        
    def on_clip_selected(self, clip_id):
        """Handle clip selection."""
        print(f"Demo: Clip selected - {clip_id}")


def main():
    """Run the demo application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Horus Timeline Playlist Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create and show demo window
    demo = TimelinePlaylistDemo()
    demo.show()
    
    print("\n" + "="*60)
    print("🎬 Horus Timeline Playlist Widget Demo")
    print("="*60)
    print("Instructions:")
    print("1. Use 'New Playlist' to create a new playlist")
    print("2. Select playlists from the tree to view timeline")
    print("3. Right-click playlists for management options")
    print("4. Click clips in timeline to simulate playback")
    print("5. Use playlist controls to duplicate/rename/delete")
    print("\nData is loaded from: sample_db/horus_playlists.json")
    print("Media records from: sample_db/media_records.json")
    print("="*60)
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
