"""
Horus Timeline Tracks
====================

Timeline tracks visualization and management for the playlist panel.
"""

from horus.utils.globals import timeline_playlist_dock


def create_timeline_tracks_panel():
    """Create right panel with timeline tracks."""
    try:
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QLabel, 
                                       QFrame, QHBoxLayout, QPushButton, QComboBox)
        from PySide2.QtCore import Qt

        # Right panel container
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)

        # Timeline header with controls
        timeline_header = QFrame()
        header_layout = QHBoxLayout(timeline_header)
        header_layout.setContentsMargins(5, 5, 5, 5)
        header_layout.setSpacing(10)

        # Timeline title
        timeline_title = QLabel("Timeline")
        timeline_title.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 12px;
                color: #e0e0e0;
                padding: 4px 0px;
            }
        """)
        header_layout.addWidget(timeline_title)

        header_layout.addStretch()

        # Timeline controls
        zoom_label = QLabel("Zoom:")
        zoom_label.setStyleSheet("color: #e0e0e0; font-size: 10px;")
        header_layout.addWidget(zoom_label)

        zoom_combo = QComboBox()
        zoom_combo.setObjectName("zoom_combo")
        zoom_combo.addItems(["25%", "50%", "75%", "100%", "125%", "150%", "200%"])
        zoom_combo.setCurrentText("100%")
        zoom_combo.setMaximumWidth(80)
        header_layout.addWidget(zoom_combo)

        fit_btn = QPushButton("Fit")
        fit_btn.setObjectName("fit_btn")
        fit_btn.setMaximumWidth(40)
        fit_btn.setToolTip("Fit timeline to window")
        header_layout.addWidget(fit_btn)

        right_layout.addWidget(timeline_header)

        # Timeline scroll area
        timeline_scroll = QScrollArea()
        timeline_scroll.setWidgetResizable(True)
        timeline_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        timeline_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        timeline_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #555555;
                background-color: #1e1e1e;
            }
        """)

        # Timeline content widget
        timeline_content = QWidget()
        timeline_layout = QVBoxLayout(timeline_content)
        timeline_layout.setContentsMargins(10, 10, 10, 10)
        timeline_layout.setSpacing(2)

        # Placeholder message
        placeholder_label = QLabel("Select a playlist to view timeline")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 14px;
                padding: 50px;
                border: 2px dashed #555555;
                border-radius: 8px;
                background-color: #2d2d2d;
            }
        """)
        timeline_layout.addWidget(placeholder_label)

        # Add stretch to push content to top
        timeline_layout.addStretch()

        timeline_scroll.setWidget(timeline_content)
        right_layout.addWidget(timeline_scroll)

        # Store references
        right_panel.timeline_header = timeline_header
        right_panel.timeline_title = timeline_title
        right_panel.zoom_combo = zoom_combo
        right_panel.fit_btn = fit_btn
        right_panel.timeline_scroll = timeline_scroll
        right_panel.timeline_content = timeline_content
        right_panel.timeline_layout = timeline_layout
        right_panel.placeholder_label = placeholder_label

        # Connect signals
        from horus.timeline_playlist.playlist_handlers import on_timeline_zoom_changed
        zoom_combo.currentTextChanged.connect(on_timeline_zoom_changed)

        print("✅ Timeline tracks panel created")
        return right_panel

    except Exception as e:
        print(f"❌ Error creating timeline tracks panel: {e}")
        import traceback
        traceback.print_exc()
        return None


def load_playlist_timeline(playlist_data):
    """Load timeline visualization for the given playlist."""
    global timeline_playlist_dock

    try:
        if not timeline_playlist_dock:
            return

        widget = timeline_playlist_dock.widget()
        if not widget or not hasattr(widget, 'right_panel'):
            return

        right_panel = widget.right_panel
        timeline_layout = right_panel.timeline_layout

        # Clear existing timeline content
        clear_timeline_display()

        # Get playlist clips
        clips = playlist_data.get('clips', [])
        tracks = playlist_data.get('tracks', [])

        if not clips:
            # Show empty message
            empty_label = QLabel("No clips in this playlist")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 12px;
                    padding: 30px;
                    border: 1px dashed #555555;
                    border-radius: 4px;
                    background-color: #2d2d2d;
                }
            """)
            timeline_layout.addWidget(empty_label)
            return

        # Create timeline ruler
        ruler = create_timeline_ruler(clips)
        timeline_layout.addWidget(ruler)

        # Create tracks
        for track in tracks:
            track_widget = create_timeline_track_widget(track, clips)
            timeline_layout.addWidget(track_widget)

        # Add stretch to push tracks to top
        timeline_layout.addStretch()

        print(f"✅ Timeline loaded with {len(clips)} clips")

    except Exception as e:
        print(f"❌ Error loading playlist timeline: {e}")
        import traceback
        traceback.print_exc()


def clear_timeline_display():
    """Clear the timeline display."""
    global timeline_playlist_dock

    try:
        if not timeline_playlist_dock:
            return

        widget = timeline_playlist_dock.widget()
        if not widget or not hasattr(widget, 'right_panel'):
            return

        timeline_layout = widget.right_panel.timeline_layout

        # Remove all widgets except the last stretch
        for i in reversed(range(timeline_layout.count())):
            child = timeline_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

    except Exception as e:
        print(f"❌ Error clearing timeline display: {e}")


def create_timeline_ruler(clips):
    """Create timeline ruler with timecode markers."""
    try:
        from PySide2.QtWidgets import QFrame, QHBoxLayout, QLabel
        from PySide2.QtCore import Qt

        ruler_frame = QFrame()
        ruler_frame.setFixedHeight(30)
        ruler_frame.setStyleSheet("""
            QFrame {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 2px;
            }
        """)

        ruler_layout = QHBoxLayout(ruler_frame)
        ruler_layout.setContentsMargins(5, 2, 5, 2)
        ruler_layout.setSpacing(0)

        # Add timecode markers
        total_duration = sum(clip.get('duration', 0) for clip in clips)
        
        # Create markers every 30 frames (assuming 24fps)
        marker_interval = 30
        for frame in range(0, total_duration + marker_interval, marker_interval):
            timecode = f"{frame:04d}"
            marker_label = QLabel(timecode)
            marker_label.setStyleSheet("""
                QLabel {
                    color: #e0e0e0;
                    font-size: 9px;
                    font-family: monospace;
                    padding: 2px;
                }
            """)
            marker_label.setAlignment(Qt.AlignCenter)
            ruler_layout.addWidget(marker_label)

        ruler_layout.addStretch()
        return ruler_frame

    except Exception as e:
        print(f"❌ Error creating timeline ruler: {e}")
        from PySide2.QtWidgets import QFrame
        return QFrame()


def create_timeline_track_widget(track_data, clips):
    """Create a timeline track widget with clips."""
    try:
        from PySide2.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget, QPushButton
        from PySide2.QtCore import Qt

        track_frame = QFrame()
        track_frame.setFixedHeight(45)  # Matching legacy timeline clip height
        track_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 2px;
                margin: 1px 0px;
            }
        """)

        track_layout = QHBoxLayout(track_frame)
        track_layout.setContentsMargins(5, 2, 5, 2)
        track_layout.setSpacing(2)

        # Track label
        track_name = track_data.get('name', 'Track')
        track_color = track_data.get('color', '#555555')
        
        track_label = QLabel(track_name)
        track_label.setFixedWidth(120)
        track_label.setStyleSheet(f"""
            QLabel {{
                background-color: {track_color};
                color: white;
                font-weight: bold;
                font-size: 10px;
                padding: 4px;
                border-radius: 2px;
            }}
        """)
        track_label.setAlignment(Qt.AlignCenter)
        track_layout.addWidget(track_label)

        # Add clips for this track
        track_clips = [clip for clip in clips if clip.get('department', '').lower() in track_name.lower()]
        
        for clip in track_clips:
            clip_widget = create_timeline_clip_widget(clip)
            track_layout.addWidget(clip_widget)

        track_layout.addStretch()
        return track_frame

    except Exception as e:
        print(f"❌ Error creating track widget: {e}")
        from PySide2.QtWidgets import QFrame
        return QFrame()


def create_timeline_clip_widget(clip_data):
    """Create a timeline clip widget."""
    try:
        from PySide2.QtWidgets import QLabel
        from PySide2.QtCore import Qt

        # Calculate clip width based on duration (simplified)
        duration = clip_data.get('duration', 100)
        clip_width = max(80, min(200, duration))  # Between 80-200px

        clip_label = QLabel()
        clip_label.setFixedSize(clip_width, 35)
        clip_label.setAlignment(Qt.AlignCenter)

        # Clip info
        shot = clip_data.get('shot', 'SH000')
        version = clip_data.get('version', 'v001')
        clip_text = f"{shot}\n{version}"

        clip_label.setText(clip_text)
        clip_label.setStyleSheet("""
            QLabel {
                background-color: #0078d4;
                color: white;
                font-size: 9px;
                font-weight: bold;
                border: 1px solid #005a9e;
                border-radius: 3px;
                padding: 2px;
            }
        """)

        # Add click handler
        clip_label.mousePressEvent = lambda event: on_timeline_clip_clicked(clip_data)

        return clip_label

    except Exception as e:
        print(f"❌ Error creating clip widget: {e}")
        from PySide2.QtWidgets import QLabel
        return QLabel("Error")


def on_timeline_clip_clicked(clip_data):
    """Handle clip click to load in Open RV."""
    try:
        file_path = clip_data.get("file_path", "")
        if file_path:
            import rv.commands as rvc
            rvc.addSource(file_path)
            print(f"✅ Loading clip: {file_path}")
        else:
            print(f"❌ No file path for clip: {clip_data.get('shot', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error loading clip: {e}")
