"""
Horus Playlist Data Management
=============================

Data loading, saving, and management for timeline playlists.
"""

import json
import os
from horus.utils.globals import timeline_playlist_data


def load_timeline_playlist_data():
    """Load playlist data from JSON database."""
    global timeline_playlist_data
    
    try:
        # Try to load from sample database
        playlist_file = "sample_db/horus_playlists.json"
        
        if os.path.exists(playlist_file):
            with open(playlist_file, 'r') as f:
                data = json.load(f)
                timeline_playlist_data = data.get('playlists', [])
                print(f"✅ Loaded {len(timeline_playlist_data)} playlists from database")
        else:
            # Create default playlist data if file doesn't exist
            timeline_playlist_data = create_default_playlist_data()
            save_timeline_playlist_data()
            print(f"✅ Created default playlist data with {len(timeline_playlist_data)} playlists")
            
    except Exception as e:
        print(f"❌ Error loading playlist data: {e}")
        # Fallback to default data
        timeline_playlist_data = create_default_playlist_data()


def save_timeline_playlist_data():
    """Save playlist data to JSON database."""
    try:
        global timeline_playlist_data
        
        # Ensure directory exists
        os.makedirs("sample_db", exist_ok=True)
        
        # Save to file
        playlist_file = "sample_db/horus_playlists.json"
        data = {
            "playlists": timeline_playlist_data,
            "last_updated": "2025-08-23T10:30:00Z"
        }
        
        with open(playlist_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"✅ Saved {len(timeline_playlist_data)} playlists to database")
        
    except Exception as e:
        print(f"❌ Error saving playlist data: {e}")


def create_default_playlist_data():
    """Create default playlist data for demonstration."""
    return [
        {
            "_id": "playlist_001",
            "name": "Episode 01 - Sequence 010",
            "project_id": "proj_001",
            "created_by": "john.doe",
            "created_at": "2025-08-20T09:00:00Z",
            "updated_at": "2025-08-22T14:30:00Z",
            "description": "Main sequence for Episode 01",
            "type": "sequence",
            "status": "active",
            "settings": {
                "auto_play": True,
                "loop": False,
                "show_timecode": True,
                "default_track_height": 60,
                "timeline_zoom": 1.0,
                "color_coding_enabled": True
            },
            "clips": [
                {
                    "clip_id": "clip_001",
                    "media_id": "media_001",
                    "sequence": "SQ0010",
                    "shot": "SH0010",
                    "version": "v003",
                    "department": "Animation",
                    "start_frame": 1001,
                    "end_frame": 1120,
                    "duration": 120,
                    "file_path": "/path/to/ep01_sq0010_sh0010_animation_v003.mov",
                    "thumbnail_path": "/cache/thumbnails/ep01_sq0010_sh0010_animation_v003.jpg"
                },
                {
                    "clip_id": "clip_002",
                    "media_id": "media_002",
                    "sequence": "SQ0010",
                    "shot": "SH0020",
                    "version": "v002",
                    "department": "Animation",
                    "start_frame": 1001,
                    "end_frame": 1080,
                    "duration": 80,
                    "file_path": "/path/to/ep01_sq0010_sh0020_animation_v002.mov",
                    "thumbnail_path": "/cache/thumbnails/ep01_sq0010_sh0020_animation_v002.jpg"
                },
                {
                    "clip_id": "clip_003",
                    "media_id": "media_003",
                    "sequence": "SQ0010",
                    "shot": "SH0030",
                    "version": "v001",
                    "department": "Animation",
                    "start_frame": 1001,
                    "end_frame": 1150,
                    "duration": 150,
                    "file_path": "/path/to/ep01_sq0010_sh0030_animation_v001.mov",
                    "thumbnail_path": "/cache/thumbnails/ep01_sq0010_sh0030_animation_v001.jpg"
                }
            ],
            "tracks": [
                {
                    "track_id": 1,
                    "name": "Animation Track",
                    "type": "video",
                    "height": 60,
                    "locked": False,
                    "muted": False,
                    "solo": False,
                    "color": "#1f4e79"
                }
            ]
        },
        {
            "_id": "playlist_002",
            "name": "Lighting Review - SQ0020",
            "project_id": "proj_001",
            "created_by": "jane.smith",
            "created_at": "2025-08-21T11:15:00Z",
            "updated_at": "2025-08-22T16:45:00Z",
            "description": "Lighting department review playlist",
            "type": "review",
            "status": "active",
            "settings": {
                "auto_play": False,
                "loop": True,
                "show_timecode": True,
                "default_track_height": 60,
                "timeline_zoom": 1.2,
                "color_coding_enabled": True
            },
            "clips": [
                {
                    "clip_id": "clip_004",
                    "media_id": "media_004",
                    "sequence": "SQ0020",
                    "shot": "SH0010",
                    "version": "v004",
                    "department": "Lighting",
                    "start_frame": 1001,
                    "end_frame": 1100,
                    "duration": 100,
                    "file_path": "/path/to/ep01_sq0020_sh0010_lighting_v004.exr",
                    "thumbnail_path": "/cache/thumbnails/ep01_sq0020_sh0010_lighting_v004.jpg"
                },
                {
                    "clip_id": "clip_005",
                    "media_id": "media_005",
                    "sequence": "SQ0020",
                    "shot": "SH0020",
                    "version": "v003",
                    "department": "Lighting",
                    "start_frame": 1001,
                    "end_frame": 1090,
                    "duration": 90,
                    "file_path": "/path/to/ep01_sq0020_sh0020_lighting_v003.exr",
                    "thumbnail_path": "/cache/thumbnails/ep01_sq0020_sh0020_lighting_v003.jpg"
                }
            ],
            "tracks": [
                {
                    "track_id": 1,
                    "name": "Lighting Track",
                    "type": "video",
                    "height": 60,
                    "locked": False,
                    "muted": False,
                    "solo": False,
                    "color": "#d68910"
                }
            ]
        },
        {
            "_id": "playlist_003",
            "name": "Comp Final - Episode 01",
            "project_id": "proj_001",
            "created_by": "mike.wilson",
            "created_at": "2025-08-22T08:30:00Z",
            "updated_at": "2025-08-22T17:20:00Z",
            "description": "Final compositing shots for client review",
            "type": "final",
            "status": "locked",
            "settings": {
                "auto_play": True,
                "loop": False,
                "show_timecode": True,
                "default_track_height": 60,
                "timeline_zoom": 0.8,
                "color_coding_enabled": True
            },
            "clips": [
                {
                    "clip_id": "clip_006",
                    "media_id": "media_006",
                    "sequence": "SQ0010",
                    "shot": "SH0010",
                    "version": "v005",
                    "department": "Compositing",
                    "start_frame": 1001,
                    "end_frame": 1120,
                    "duration": 120,
                    "file_path": "/path/to/ep01_sq0010_sh0010_comp_v005.mov",
                    "thumbnail_path": "/cache/thumbnails/ep01_sq0010_sh0010_comp_v005.jpg"
                },
                {
                    "clip_id": "clip_007",
                    "media_id": "media_007",
                    "sequence": "SQ0010",
                    "shot": "SH0020",
                    "version": "v004",
                    "department": "Compositing",
                    "start_frame": 1001,
                    "end_frame": 1080,
                    "duration": 80,
                    "file_path": "/path/to/ep01_sq0010_sh0020_comp_v004.mov",
                    "thumbnail_path": "/cache/thumbnails/ep01_sq0010_sh0020_comp_v004.jpg"
                },
                {
                    "clip_id": "clip_008",
                    "media_id": "media_008",
                    "sequence": "SQ0010",
                    "shot": "SH0030",
                    "version": "v003",
                    "department": "Compositing",
                    "start_frame": 1001,
                    "end_frame": 1150,
                    "duration": 150,
                    "file_path": "/path/to/ep01_sq0010_sh0030_comp_v003.mov",
                    "thumbnail_path": "/cache/thumbnails/ep01_sq0010_sh0030_comp_v003.jpg"
                }
            ],
            "tracks": [
                {
                    "track_id": 1,
                    "name": "Compositing Track",
                    "type": "video",
                    "height": 60,
                    "locked": True,
                    "muted": False,
                    "solo": False,
                    "color": "#196f3d"
                }
            ]
        }
    ]
