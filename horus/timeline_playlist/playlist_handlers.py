"""
Horus Playlist Handlers
======================

Event handlers for playlist interactions and management.
"""

from horus.utils.globals import timeline_playlist_dock, current_playlist_id, timeline_playlist_data
from horus.timeline_playlist.playlist_data import save_timeline_playlist_data, load_timeline_playlist_data
from horus.timeline_playlist.playlist_tree import populate_playlist_tree
from horus.timeline_playlist.timeline_tracks import load_playlist_timeline


def on_playlist_tree_selection_changed():
    """Handle playlist selection change."""
    global timeline_playlist_dock, current_playlist_id

    try:
        if not timeline_playlist_dock:
            return

        widget = timeline_playlist_dock.widget()
        if not widget or not hasattr(widget, 'left_panel'):
            return

        playlist_tree = widget.left_panel.playlist_tree
        selected_items = playlist_tree.selectedItems()

        if not selected_items:
            current_playlist_id = None
            return

        selected_item = selected_items[0]
        playlist_data = selected_item.data(0, Qt.UserRole)

        if playlist_data:
            current_playlist_id = playlist_data.get('_id')
            print(f"Selected playlist: {playlist_data.get('name', 'Unknown')}")
            
            # Load timeline for selected playlist
            load_playlist_timeline(playlist_data)
        else:
            current_playlist_id = None

    except Exception as e:
        print(f"❌ Error handling playlist selection: {e}")


def on_playlist_double_clicked(item, column):
    """Handle playlist double-click to start playback."""
    try:
        playlist_data = item.data(0, Qt.UserRole)
        if playlist_data:
            playlist_name = playlist_data.get('name', 'Unknown')
            print(f"Double-clicked playlist: {playlist_name}")
            # TODO: Implement playlist playback
    except Exception as e:
        print(f"❌ Error handling playlist double-click: {e}")


def create_new_playlist():
    """Create a new playlist."""
    try:
        from PySide2.QtWidgets import QInputDialog
        from datetime import datetime
        import uuid

        # Get playlist name from user
        name, ok = QInputDialog.getText(None, "New Playlist", "Enter playlist name:")
        if not ok or not name.strip():
            return

        # Generate unique ID
        playlist_id = f"playlist_{uuid.uuid4().hex[:8]}"

        # Create new playlist data
        new_playlist = {
            "_id": playlist_id,
            "name": name.strip(),
            "project_id": "proj_001",  # Default project
            "created_by": "user",
            "created_at": datetime.now().isoformat() + "Z",
            "updated_at": datetime.now().isoformat() + "Z",
            "description": f"User created playlist: {name}",
            "type": "user_created",
            "status": "draft",
            "settings": {
                "auto_play": True,
                "loop": False,
                "show_timecode": True,
                "default_track_height": 60,
                "timeline_zoom": 1.0,
                "color_coding_enabled": True
            },
            "clips": [],
            "tracks": [
                {
                    "track_id": 1,
                    "name": "Video Track 1",
                    "type": "video",
                    "height": 60,
                    "locked": False,
                    "muted": False,
                    "solo": False,
                    "color": "#2d2d2d"
                }
            ]
        }

        # Add to playlist data
        timeline_playlist_data.append(new_playlist)
        save_timeline_playlist_data()
        populate_playlist_tree()

        print(f"✅ Created new playlist: {name}")

    except Exception as e:
        print(f"❌ Error creating new playlist: {e}")


def duplicate_current_playlist():
    """Duplicate the selected playlist."""
    try:
        if not current_playlist_id:
            print("No playlist selected for duplication")
            return

        # Find current playlist
        current_playlist = None
        for playlist in timeline_playlist_data:
            if playlist.get('_id') == current_playlist_id:
                current_playlist = playlist
                break

        if not current_playlist:
            print("Selected playlist not found")
            return

        from PySide2.QtWidgets import QInputDialog
        from datetime import datetime
        import uuid
        import copy

        # Get new name
        original_name = current_playlist.get('name', 'Unknown')
        new_name, ok = QInputDialog.getText(None, "Duplicate Playlist", 
                                          f"Enter name for duplicate:", text=f"{original_name} Copy")
        if not ok or not new_name.strip():
            return

        # Create duplicate
        duplicate_playlist = copy.deepcopy(current_playlist)
        duplicate_playlist['_id'] = f"playlist_{uuid.uuid4().hex[:8]}"
        duplicate_playlist['name'] = new_name.strip()
        duplicate_playlist['created_at'] = datetime.now().isoformat() + "Z"
        duplicate_playlist['updated_at'] = datetime.now().isoformat() + "Z"
        duplicate_playlist['status'] = "draft"

        # Add to playlist data
        timeline_playlist_data.append(duplicate_playlist)
        save_timeline_playlist_data()
        populate_playlist_tree()

        print(f"✅ Duplicated playlist: {original_name} -> {new_name}")

    except Exception as e:
        print(f"❌ Error duplicating playlist: {e}")


def rename_current_playlist():
    """Rename the selected playlist."""
    try:
        if not current_playlist_id:
            print("No playlist selected for renaming")
            return

        # Find current playlist
        current_playlist = None
        for playlist in timeline_playlist_data:
            if playlist.get('_id') == current_playlist_id:
                current_playlist = playlist
                break

        if not current_playlist:
            print("Selected playlist not found")
            return

        from PySide2.QtWidgets import QInputDialog
        from datetime import datetime

        # Get new name
        current_name = current_playlist.get('name', 'Unknown')
        new_name, ok = QInputDialog.getText(None, "Rename Playlist", 
                                          "Enter new name:", text=current_name)
        if not ok or not new_name.strip():
            return

        # Update playlist
        current_playlist['name'] = new_name.strip()
        current_playlist['updated_at'] = datetime.now().isoformat() + "Z"

        save_timeline_playlist_data()
        populate_playlist_tree()

        print(f"✅ Renamed playlist: {current_name} -> {new_name}")

    except Exception as e:
        print(f"❌ Error renaming playlist: {e}")


def delete_current_playlist():
    """Delete the selected playlist."""
    try:
        if not current_playlist_id:
            print("No playlist selected for deletion")
            return

        # Find current playlist
        current_playlist = None
        playlist_index = -1
        for i, playlist in enumerate(timeline_playlist_data):
            if playlist.get('_id') == current_playlist_id:
                current_playlist = playlist
                playlist_index = i
                break

        if not current_playlist:
            print("Selected playlist not found")
            return

        from PySide2.QtWidgets import QMessageBox

        # Confirm deletion
        playlist_name = current_playlist.get('name', 'Unknown')
        reply = QMessageBox.question(None, "Delete Playlist", 
                                   f"Are you sure you want to delete '{playlist_name}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return

        # Remove playlist
        timeline_playlist_data.pop(playlist_index)
        save_timeline_playlist_data()
        populate_playlist_tree()

        print(f"✅ Deleted playlist: {playlist_name}")

    except Exception as e:
        print(f"❌ Error deleting playlist: {e}")


def show_add_media_dialog():
    """Show dialog to add media to current playlist."""
    try:
        if not current_playlist_id:
            print("No playlist selected for adding media")
            return

        print("Add media dialog - TODO: Implement media selection")
        # TODO: Implement media selection dialog

    except Exception as e:
        print(f"❌ Error showing add media dialog: {e}")


def refresh_timeline_playlists():
    """Refresh playlist data from database."""
    try:
        load_timeline_playlist_data()
        populate_playlist_tree()
        print("Refreshed playlist data")
    except Exception as e:
        print(f"❌ Error refreshing playlists: {e}")


def play_current_playlist():
    """Start timeline playback."""
    try:
        if current_playlist_id:
            print(f"Playing playlist: {current_playlist_id}")
            # TODO: Implement sequential playback of all clips
        else:
            print("No playlist selected for playback")
    except Exception as e:
        print(f"❌ Error playing playlist: {e}")


def stop_playlist_playback():
    """Stop timeline playback."""
    try:
        print("Stopping playlist playback")
        # TODO: Implement playback stop
    except Exception as e:
        print(f"❌ Error stopping playback: {e}")


def on_timeline_zoom_changed(zoom_text):
    """Handle timeline zoom change."""
    try:
        print(f"Timeline zoom changed to: {zoom_text}")
        # TODO: Implement timeline zoom functionality
    except Exception as e:
        print(f"❌ Error changing timeline zoom: {e}")


def add_media_to_current_playlist(media_record):
    """Add a media record to the current playlist."""
    try:
        if not current_playlist_id:
            print("No playlist selected for adding media")
            return

        # Find current playlist
        current_playlist = None
        for playlist in timeline_playlist_data:
            if playlist.get('_id') == current_playlist_id:
                current_playlist = playlist
                break

        if not current_playlist:
            print("Selected playlist not found")
            return

        # Create clip data from media record
        from datetime import datetime
        import uuid

        new_clip = {
            "clip_id": f"clip_{uuid.uuid4().hex[:8]}",
            "media_id": media_record.get('_id', ''),
            "sequence": media_record.get('sequence', ''),
            "shot": media_record.get('shot', ''),
            "version": media_record.get('version', 'v001'),
            "department": media_record.get('department', ''),
            "start_frame": 1001,
            "end_frame": 1100,  # Default duration
            "duration": 100,
            "file_path": media_record.get('file_path', ''),
            "thumbnail_path": media_record.get('thumbnail_path', '')
        }

        # Add clip to playlist
        current_playlist['clips'].append(new_clip)
        current_playlist['updated_at'] = datetime.now().isoformat() + "Z"

        save_timeline_playlist_data()

        # Refresh timeline display
        load_playlist_timeline(current_playlist)

        print(f"✅ Added media to playlist: {media_record.get('file_name', 'Unknown')}")

    except Exception as e:
        print(f"❌ Error adding media to playlist: {e}")


# Import required Qt classes at module level
try:
    from PySide2.QtCore import Qt
except ImportError:
    print("Warning: PySide2 not available for playlist handlers")
