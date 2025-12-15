#!/usr/bin/env python3
"""
Standalone Timeline Playlist Demo - Current Sizing
Shows the current track and clip sizes being used in Horus
"""

import sys
from PySide2.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QTreeWidget, QTreeWidgetItem, QFrame, QLabel, 
    QPushButton, QScrollArea
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor

class TimelinePlaylistDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timeline Playlist Demo - Current Sizing")
        self.setGeometry(100, 100, 1200, 600)
        
        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header = QLabel("Timeline Playlist Manager - Current Sizing")
        header.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                color: #e0e0e0;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #555555;
            }
        """)
        layout.addWidget(header)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Playlist tree
        left_panel = self.create_playlist_tree()
        splitter.addWidget(left_panel)
        
        # Right panel - Timeline
        right_panel = self.create_timeline_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([300, 900])
        layout.addWidget(splitter)
        
    def create_playlist_tree(self):
        """Create playlist tree panel."""
        widget = QWidget()
        widget.setFixedWidth(300)
        layout = QVBoxLayout(widget)
        
        # Tree widget
        tree = QTreeWidget()
        tree.setHeaderLabel("Playlists")
        tree.setStyleSheet("""
            QTreeWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #555555;
                font-size: 12px;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #4a90e2;
            }
        """)
        
        # Add sample playlists
        project_item = QTreeWidgetItem(tree)
        project_item.setText(0, "Project: SWA")
        
        playlist1 = QTreeWidgetItem(project_item)
        playlist1.setText(0, "Animation Dailies (15 clips)")
        
        playlist2 = QTreeWidgetItem(project_item)
        playlist2.setText(0, "Lighting Review (12 clips)")
        
        playlist3 = QTreeWidgetItem(project_item)
        playlist3.setText(0, "Final Comp (18 clips)")
        
        tree.expandAll()
        layout.addWidget(tree)
        
        return widget
        
    def create_timeline_panel(self):
        """Create timeline panel with current sizing."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Timeline header (current: 25px)
        header = QFrame()
        header.setFixedHeight(25)  # Current reduced height
        header.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.addWidget(QLabel("Current Playlist: Animation Dailies"))
        layout.addWidget(header)
        
        # Timeline ruler (current: 18px)
        ruler = self.create_timeline_ruler()
        layout.addWidget(ruler)
        
        # Timeline tracks
        track_widget = self.create_timeline_tracks()
        layout.addWidget(track_widget)
        
        layout.addStretch()
        return widget
        
    def create_timeline_ruler(self):
        """Create timeline ruler with current sizing."""
        ruler = QFrame()
        ruler.setFixedHeight(18)  # Current reduced height
        ruler.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #555555;
            }
            QLabel {
                color: #cccccc;
                font-size: 10px;
                font-family: monospace;
            }
        """)
        
        layout = QHBoxLayout(ruler)
        layout.setContentsMargins(65, 0, 0, 0)  # Offset for track labels
        
        # Add timecode markers
        for i in range(0, 300, 30):
            seconds = i / 24
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            frames = i % 24
            
            timecode = f"{minutes:02d}:{secs:02d}:{frames:02d}"
            marker = QLabel(timecode)
            marker.setFixedWidth(120)  # Current marker width
            marker.setAlignment(Qt.AlignCenter)
            layout.addWidget(marker)
            
        layout.addStretch()
        return ruler
        
    def create_timeline_tracks(self):
        """Create timeline tracks with current sizing."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        tracks_widget = QWidget()
        tracks_layout = QVBoxLayout(tracks_widget)
        tracks_layout.setContentsMargins(0, 0, 0, 0)
        tracks_layout.setSpacing(2)
        
        # Sample track data
        tracks = [
            {"name": "Animation", "color": "#1f4e79", "clips": [
                {"name": "sh0010", "version": "v003", "duration": 120, "position": 0},
                {"name": "sh0020", "version": "v002", "duration": 96, "position": 120},
                {"name": "sh0030", "version": "v001", "duration": 144, "position": 216},
            ]},
            {"name": "Lighting", "color": "#d68910", "clips": [
                {"name": "sh0010", "version": "v002", "duration": 120, "position": 0},
                {"name": "sh0020", "version": "v001", "duration": 96, "position": 120},
            ]},
            {"name": "Compositing", "color": "#196f3d", "clips": [
                {"name": "sh0010", "version": "v005", "duration": 120, "position": 0},
            ]},
        ]
        
        for track_data in tracks:
            track_widget = self.create_track_widget(track_data)
            tracks_layout.addWidget(track_widget)
            
        tracks_layout.addStretch()
        scroll_area.setWidget(tracks_widget)
        return scroll_area
        
    def create_track_widget(self, track_data):
        """Create a single track widget with current sizing."""
        track = QFrame()
        track.setFixedHeight(65)  # Current track height from demo
        track.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
            }
        """)
        
        layout = QHBoxLayout(track)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Track label
        label = QLabel(track_data["name"])
        label.setFixedWidth(60)
        label.setStyleSheet(f"""
            QLabel {{
                background-color: #3a3a3a;
                color: #e0e0e0;
                padding: 5px;
                border-right: 1px solid #555555;
                font-size: 11px;
                font-weight: bold;
            }}
        """)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # Clips area
        clips_widget = QWidget()
        clips_layout = QHBoxLayout(clips_widget)
        clips_layout.setContentsMargins(0, 0, 0, 0)
        clips_layout.setSpacing(1)
        
        # Add clips
        for clip_data in track_data["clips"]:
            clip_widget = self.create_clip_widget(clip_data, track_data["color"])
            clips_layout.addWidget(clip_widget)
            
        clips_layout.addStretch()
        layout.addWidget(clips_widget)
        
        return track
        
    def create_clip_widget(self, clip_data, color):
        """Create a clip widget with current sizing."""
        duration = clip_data["duration"]
        width = max(80, duration * 4)  # Current: 4 pixels per frame
        
        clip = QPushButton()
        clip.setFixedSize(width, 58)  # Current clip height: 58px
        clip.setText(f"{clip_data['name']}\n{clip_data['version']}")
        clip.setToolTip(f"Duration: {duration} frames")
        
        clip.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: 1px solid #555555;
                border-radius: 3px;
                font-size: 11px;  # Current font size
                font-weight: bold;
                text-align: left;
                padding: 2px;
            }}
            QPushButton:hover {{
                border-color: #ffffff;
                background-color: {color}dd;
            }}
        """)
        
        return clip

def main():
    app = QApplication(sys.argv)
    
    # Set dark theme
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
    """)
    
    demo = TimelinePlaylistDemo()
    demo.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
