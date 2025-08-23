# Timeline Playlist Feature for Horus-RV

## Overview

The Timeline Playlist feature adds professional NLE-style playlist management to Horus-RV, following Adobe Premiere Pro interface patterns. This feature provides a comprehensive timeline editor with playlist management capabilities integrated into the existing Horus three-panel system.

## Features

### 🎬 Professional NLE Interface
- **Left Panel**: Playlist tree with project organization
- **Right Panel**: Timeline tracks with professional visualization
- **Adobe Premiere Pro Patterns**: Industry-standard interface design
- **Department Color Coding**: Visual organization by department
- **Timeline Ruler**: Timecode display and navigation

### 📋 Playlist Management
- **Create Playlists**: Custom named playlists with metadata
- **Duplicate Playlists**: Copy existing playlists with modifications
- **Rename Playlists**: Update playlist names and descriptions
- **Delete Playlists**: Remove unwanted playlists with confirmation
- **Status Tracking**: Active, draft, and archived playlist states

### 🎞️ Clip Management
- **Add Clips**: Right-click media items to add to current playlist
- **Reorder Clips**: Drag-and-drop functionality for clip organization
- **Replace Versions**: Update clip versions while maintaining timeline position
- **Remove Clips**: Delete clips from playlists
- **Timeline Visualization**: Professional track-based display

### 🎨 Visual Design
- **Department Colors**:
  - Animation: Blue (#1f4e79)
  - Lighting: Orange (#d68910)
  - Compositing: Green (#196f3d)
  - FX: Purple (#6c3483)
  - Modeling: Red (#a93226)
  - Texturing: Brown (#8b4513)
  - Rigging: Sea Green (#2e8b57)
  - Layout: Steel Blue (#4682b4)

## Database Schema

### Playlist Structure
```json
{
  "_id": "playlist_001",
  "name": "Episode 01 - Animation Review",
  "project_id": "proj_001",
  "created_by": "user",
  "created_at": "2025-01-23T10:00:00Z",
  "updated_at": "2025-01-23T15:30:00Z",
  "description": "Animation review playlist",
  "type": "review",
  "status": "active",
  "settings": {
    "auto_play": true,
    "loop": false,
    "show_timecode": true,
    "default_track_height": 60,
    "timeline_zoom": 1.0,
    "color_coding_enabled": true
  },
  "clips": [...],
  "tracks": [...],
  "metadata": {...}
}
```

### Clip Structure
```json
{
  "clip_id": "clip_001",
  "media_id": "media_001",
  "position": 0,
  "duration": 120,
  "in_point": 0,
  "out_point": 120,
  "track": 1,
  "department": "animation",
  "sequence": "seq010",
  "shot": "shot010",
  "version": "v003",
  "color": "#1f4e79",
  "notes": "Final animation approved",
  "added_at": "2025-01-23T10:15:00Z"
}
```

## Integration

### Feature Flag
The Timeline Playlist feature can be enabled/disabled using the feature flag:
```python
ENABLE_TIMELINE_PLAYLIST = True  # Set to False to disable
```

### Open RV Integration
- **Dock Widget**: Tabified with existing timeline for space efficiency
- **Media Browser**: Right-click context menu to add clips to playlists
- **Playback Integration**: Seamless loading of clips in Open RV
- **Backward Compatibility**: Existing functionality remains unchanged

### File Structure
```
Horus/
├── horus_timeline_playlist_widget.py    # Main widget implementation
├── rv_horus_integration.py              # Updated integration
├── sample_db/horus_playlists.json       # Playlist database
├── demo_timeline_playlist.py            # Standalone demo
└── TIMELINE_PLAYLIST_FEATURE.md         # This documentation
```

## Usage

### In Open RV
1. Launch Horus-RV: `python rv_horus_integration.py`
2. Look for "Timeline Playlist Manager" dock widget
3. Create new playlists or select existing ones
4. Right-click media items in Media Grid to add to current playlist
5. Click clips in timeline to load in Open RV

### Standalone Demo
```bash
python demo_timeline_playlist.py
```

## Development

### Git Branch
Development is done on the `feature/timeline-playlist` branch following Git Flow strategy.

### Dependencies
- PySide2 (Qt framework)
- Existing Horus database structure
- Open RV integration (optional for standalone demo)

### Testing
- Standalone demo for widget testing
- Integration testing with Open RV
- Database schema validation
- Cross-platform compatibility

## Future Enhancements

### Planned Features
- **Audio Track Support**: Multi-channel audio timeline
- **Transition Effects**: Crossfades and transitions between clips
- **Markers and Notes**: Frame-accurate annotations
- **Export Functionality**: EDL, XML, and AAF export
- **Collaborative Features**: Multi-user playlist editing
- **Version Control**: Playlist versioning and history

### Integration Opportunities
- **ShotGrid Integration**: Automatic playlist creation from ShotGrid data
- **ftrack Integration**: Review session synchronization
- **OpenTimelineIO**: Industry-standard timeline data exchange
- **Color Pipeline**: Shot-based color management integration

## Technical Architecture

### Widget Hierarchy
```
HorusTimelinePlaylistWidget
├── Header (title and main controls)
├── Main Splitter
│   ├── Left Panel (playlist tree and controls)
│   └── Right Panel (timeline tracks and ruler)
└── Integration signals and slots
```

### Signal/Slot Architecture
- `playlist_selected(str)`: Emitted when playlist is selected
- `clip_selected(str)`: Emitted when clip is clicked
- `playback_requested(str, int)`: Emitted for media loading

### Performance Considerations
- Lazy loading of timeline visualization
- Efficient clip widget creation and management
- Optimized database operations
- Memory management for large playlists

This Timeline Playlist feature represents a significant enhancement to Horus-RV, bringing professional NLE capabilities to the VFX review workflow while maintaining the existing three-panel architecture and ensuring backward compatibility.
