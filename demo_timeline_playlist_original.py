#!/usr/bin/env python3
"""
Standalone Timeline Playlist Demo - Original Good Sizing
Shows the original track and clip sizes that were working well
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
        self.setWindowTitle("Timeline Playlist Demo - Original Good Sizing")
        self.setGeometry(100, 100, 1200, 700)  # Taller for original sizing
        
        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header = QLabel("Timeline Playlist Manager - Original Good Sizing")
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
        """Create timeline panel with original good sizing."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Timeline header (original: 40px)
        header = QFrame()
        header.setFixedHeight(40)  # Original height
        header.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.addWidget(QLabel("Current Playlist: Animation Dailies"))
        layout.addWidget(header)
        
        # Timeline ruler (original: 30px)
        ruler = self.create_timeline_ruler()
        layout.addWidget(ruler)
        
        # Timeline tracks
        track_widget = self.create_timeline_tracks()
        layout.addWidget(track_widget)
        
        layout.addStretch()
        return widget
        
    def create_timeline_ruler(self):
        """Create timeline ruler with original sizing."""
        ruler = QFrame()
        ruler.setFixedHeight(30)  # Original height
        ruler.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #555555;
            }
            QLabel {
                color: #cccccc;
                font-size: 11px;
                font-family: monospace;
            }
        """)
        
        layout = QHBoxLayout(ruler)
        layout.setContentsMargins(80, 0, 0, 0)  # Offset for track labels
        
        # Add timecode markers
        for i in range(0, 300, 30):
            seconds = i / 24
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            frames = i % 24
            
            timecode = f"{minutes:02d}:{secs:02d}:{frames:02d}"
            marker = QLabel(timecode)
            marker.setFixedWidth(150)  # Original marker width
            marker.setAlignment(Qt.AlignCenter)
            layout.addWidget(marker)
            
        layout.addStretch()
        return ruler
        
    def create_timeline_tracks(self):
        """Create timeline tracks with original good sizing."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        tracks_widget = QWidget()
        tracks_layout = QVBoxLayout(tracks_widget)
        tracks_layout.setContentsMargins(0, 0, 0, 0)
        tracks_layout.setSpacing(3)  # Original spacing
        
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
        """Create a single track widget with original good sizing."""
        track = QFrame()
        track.setFixedHeight(80)  # Original good track height
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
        label.setFixedWidth(75)  # Original label width
        label.setStyleSheet(f"""
            QLabel {{
                background-color: #3a3a3a;
                color: #e0e0e0;
                padding: 8px;
                border-right: 1px solid #555555;
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # Clips area
        clips_widget = QWidget()
        clips_layout = QHBoxLayout(clips_widget)
        clips_layout.setContentsMargins(5, 5, 5, 5)  # Original margins
        clips_layout.setSpacing(2)  # Original spacing
        
        # Add clips
        for clip_data in track_data["clips"]:
            clip_widget = self.create_clip_widget(clip_data, track_data["color"])
            clips_layout.addWidget(clip_widget)
            
        clips_layout.addStretch()
        layout.addWidget(clips_widget)
        
        return track
        
    def create_clip_widget(self, clip_data, color):
        """Create a clip widget with original good sizing."""
        duration = clip_data["duration"]
        width = max(100, duration * 3)  # Original: 3 pixels per frame
        
        clip = QPushButton()
        clip.setFixedSize(width, 70)  # Original clip height: 70px
        clip.setText(f"{clip_data['name']}\n{clip_data['version']}")
        clip.setToolTip(f"Duration: {duration} frames")
        
        clip.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: 2px solid #555555;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                text-align: center;
                padding: 4px;
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
