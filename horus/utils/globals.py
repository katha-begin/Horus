"""
Horus Global Variables
======================

Global references and state management for the Horus application.
"""

# Global references for dock widgets
search_dock = None
comments_dock = None
timeline_dock = None
media_grid_dock = None
timeline_playlist_dock = None  # New Timeline Playlist Widget
annotations_popup_window = None

# Database and project state
horus_connector = None
current_project_id = None

# Feature flags
ENABLE_TIMELINE_PLAYLIST = True   # Enable/disable Timeline Playlist feature
ENABLE_LEGACY_TIMELINE = False    # Disable legacy Timeline Sequence panel

# Timeline Playlist global data
timeline_playlist_data = []
current_playlist_id = None
