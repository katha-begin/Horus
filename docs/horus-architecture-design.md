# Horus: Three-Widget Modular Architecture Design
## Advanced Open RV Studio Pipeline Integration

**Project:** Horus (formerly Monto-openRv)  
**Version:** 2.0  
**Date:** 2025-08-22  
**Status:** Architecture Design Phase  

---

## 1. Executive Summary

### 1.1 Project Vision
Horus represents a complete architectural redesign of the Open RV application, transforming it from a single MediaBrowser widget into a comprehensive three-widget modular system. Named after the Egyptian god of sky, vision, watchfulness, and foresight, Horus embodies the qualities essential for professional media review and pipeline management.

### 1.2 Core Architecture Principles
- **Modular Independence**: Three independently dockable panels with clean separation of concerns
- **Adobe Premiere-Inspired UX**: Familiar interface patterns for VFX professionals
- **Facebook-Style Collaboration**: Modern threaded comment system with real-time features
- **OTIO Integration**: Professional timeline management with industry-standard interchange
- **Extension-Ready Design**: Future-proof architecture for ShotGrid/ftrack integration

---

## 2. Three-Widget System Architecture

### 2.1 Widget Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                        Open RV Main Window                     │
├─────────────────┬─────────────────────────┬─────────────────────┤
│   Search &      │                         │   Comments &        │
│ Media Library   │     RV Viewport         │   Annotations       │
│                 │                         │                     │
│ • Thumbnail     │                         │ • Threaded         │
│   Grid          │                         │   Comments          │
│ • Hierarchical  │                         │ • User Tagging      │
│   Filtering     │                         │ • Emoji Reactions   │
│ • Advanced      │                         │ • Frame-Specific    │
│   Search        │                         │   Annotations       │
│                 │                         │                     │
├─────────────────┴─────────────────────────┴─────────────────────┤
│                    Timeline Editor Widget                      │
│                                                                 │
│ • Multi-track Timeline    • OTIO Integration                   │
│ • Drag-and-Drop          • Playlist Management                │
│ • Version Switching      • EDL Import/Export                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Widget Independence Architecture
Each widget operates as a standalone Open RV package with:
- **Independent Data Models**: Separate data management and caching
- **Isolated UI Components**: No direct widget-to-widget dependencies
- **Event-Based Communication**: Loose coupling through Open RV's event system
- **Individual Docking**: Can be undocked, repositioned, or hidden independently

---

## 3. Widget 1: Search & Media Library

### 3.1 Design Philosophy
Transform the current tree-based navigation into an Adobe Premiere-style media grid with advanced filtering and search capabilities.

### 3.2 Core Features
**Thumbnail Grid Layout:**
- Configurable thumbnail sizes (small: 64x64, medium: 128x128, large: 256x256)
- Metadata overlay with file info, status indicators, and version numbers
- Color-coded status system (approved: green, pending: yellow, rejected: red)
- Drag-and-drop support for timeline integration

**Hierarchical Filtering:**
- Episode/Sequence/Shot breadcrumb navigation
- Department-specific filtering (animation, lighting, compositing, etc.)
- Version filtering with "latest only" toggle
- Date range filtering with calendar picker
- File type filtering (image sequences, video files, audio tracks)

**Advanced Search:**
- Real-time search with 300ms debounce
- Metadata field search (task ID, artist name, description, tags)
- Saved search presets for common queries
- Search history with quick access

### 3.3 Technical Implementation
```python
# Package structure
horus_media_library/
├── package.py
├── python/
│   ├── horus_media_library/
│   │   ├── __init__.py
│   │   ├── media_grid_widget.py      # Main grid interface
│   │   ├── thumbnail_generator.py    # Async thumbnail creation
│   │   ├── filter_manager.py         # Advanced filtering logic
│   │   ├── search_engine.py          # Search and indexing
│   │   ├── metadata_cache.py         # Performance optimization
│   │   └── montu_connector.py        # Enhanced data integration
│   └── rv_integration/
│       └── media_library_mode.py     # Open RV mode integration
├── resources/
│   ├── icons/                        # UI icons and status indicators
│   ├── stylesheets/                  # Adobe Premiere-inspired styling
│   └── thumbnails/                   # Thumbnail cache directory
└── tests/
    └── test_media_library.py
```

### 3.4 Data Model Enhancement
**Enhanced Media Record Schema:**
```python
{
    "id": "unique_media_id",
    "file_path": "/path/to/media/file.exr",
    "thumbnail_path": "/cache/thumbnails/file_thumb.jpg",
    "metadata": {
        "episode": "EP001",
        "sequence": "SEQ010", 
        "shot": "SH020",
        "department": "lighting",
        "version": "v003",
        "artist": "john.doe",
        "approval_status": "approved",
        "creation_date": "2025-08-22T10:30:00Z",
        "file_size": 52428800,
        "resolution": "1920x1080",
        "frame_range": "1001-1120",
        "color_space": "ACES - ACEScg"
    },
    "tags": ["hero", "final", "client_approved"],
    "related_files": ["audio_track.wav", "reference.mov"]
}
```

---

## 4. Widget 2: Comments & Annotations

### 4.1 Design Philosophy
Implement a Facebook-style threaded comment system with professional annotation tools for frame-specific feedback and collaboration.

### 4.2 Core Features
**Threaded Comment System:**
- Nested reply functionality with visual threading indicators
- User tagging with @username autocomplete and notifications
- Emoji reaction system (👍 👎 ✅ ❌ 🔥 💡)
- Real-time comment synchronization across users
- Comment history and edit tracking

**Frame-Specific Annotations:**
- Integration with Open RV's built-in drawing tools
- Shape annotations (rectangle, circle, arrow, freehand)
- Text annotations with customizable fonts and colors
- Persistent annotation storage linked to specific frames/timecodes
- Annotation layers with show/hide toggles

**Collaboration Features:**
- User presence indicators (who's currently viewing)
- Live cursor tracking for remote collaboration
- Comment notifications and mention alerts
- Export capabilities (JSON, XML, PDF reports)

### 4.3 Technical Implementation
```python
# Package structure
horus_comments_annotations/
├── package.py
├── python/
│   ├── horus_comments_annotations/
│   │   ├── __init__.py
│   │   ├── comment_widget.py         # Main comment interface
│   │   ├── thread_manager.py         # Comment threading logic
│   │   ├── annotation_tools.py       # Drawing and markup tools
│   │   ├── user_manager.py           # User authentication and presence
│   │   ├── notification_system.py    # Real-time notifications
│   │   └── export_manager.py         # Comment/annotation export
│   └── rv_integration/
│       ├── annotation_overlay.py     # GLSL overlay integration
│       └── comment_mode.py           # Open RV mode integration
├── database/
│   ├── comment_schema.sql            # Comment database schema
│   └── annotation_schema.sql         # Annotation storage schema
└── tests/
    └── test_comments_annotations.py
```

### 4.4 Database Schema Design
**Comment Schema:**
```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY,
    parent_id UUID REFERENCES comments(id),
    media_id VARCHAR(255) NOT NULL,
    frame_number INTEGER,
    timecode VARCHAR(20),
    user_id VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_resolved BOOLEAN DEFAULT FALSE,
    thread_depth INTEGER DEFAULT 0
);

CREATE TABLE comment_reactions (
    id UUID PRIMARY KEY,
    comment_id UUID REFERENCES comments(id),
    user_id VARCHAR(100) NOT NULL,
    reaction_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Annotation Schema:**
```sql
CREATE TABLE annotations (
    id UUID PRIMARY KEY,
    media_id VARCHAR(255) NOT NULL,
    frame_number INTEGER NOT NULL,
    annotation_type VARCHAR(50) NOT NULL, -- 'rectangle', 'circle', 'arrow', 'text'
    coordinates JSON NOT NULL,
    style_properties JSON,
    content TEXT,
    user_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_visible BOOLEAN DEFAULT TRUE
);
```

---

## 5. Widget 3: Timeline Editor

### 5.1 Design Philosophy
Create an Adobe Premiere-inspired timeline interface with OTIO integration for professional editorial workflows and playlist management.

### 5.2 Core Features
**Multi-Track Timeline:**
- Visual timeline with multiple video/audio tracks
- Drag-and-drop media placement from Media Library widget
- Timeline scrubbing with frame-accurate positioning
- Zoom controls for detailed editing
- Snap-to-frame functionality

**Version Management:**
- Per-clip version switching with dropdown menus
- Version comparison overlays (A/B comparison)
- Automatic latest version detection
- Version history tracking with rollback capability

**Playlist Management:**
- Episode-based playlists (full episode sequences)
- Sequence-based playlists (individual sequence cuts)
- Custom department playlists (e.g., "seq010_animation_latest")
- Playlist templates for common review scenarios
- Collaborative playlist sharing

**OTIO Integration:**
- Timeline import/export using OpenTimelineIO
- EDL import with metadata preservation
- AAF/XML timeline interchange
- Custom metadata field support
- Timeline versioning and branching

### 5.3 Technical Implementation
```python
# Package structure
horus_timeline_editor/
├── package.py
├── python/
│   ├── horus_timeline_editor/
│   │   ├── __init__.py
│   │   ├── timeline_widget.py        # Main timeline interface
│   │   ├── track_manager.py          # Multi-track management
│   │   ├── playlist_manager.py       # Playlist creation and management
│   │   ├── version_controller.py     # Version switching logic
│   │   ├── otio_integration.py       # OpenTimelineIO integration
│   │   └── edl_importer.py          # EDL/AAF/XML import
│   └── rv_integration/
│       └── timeline_mode.py          # Open RV mode integration
├── resources/
│   ├── timeline_icons/               # Timeline-specific UI icons
│   └── playlist_templates/           # Predefined playlist templates
└── tests/
    └── test_timeline_editor.py
```

### 5.4 OTIO Data Model
**Timeline Schema:**
```python
{
    "timeline_id": "unique_timeline_id",
    "name": "EP001_SEQ010_Review_v002",
    "description": "Animation review playlist for sequence 010",
    "created_by": "john.doe",
    "created_at": "2025-08-22T10:30:00Z",
    "tracks": [
        {
            "track_id": "video_track_01",
            "track_type": "video",
            "clips": [
                {
                    "clip_id": "clip_001",
                    "media_reference": "/path/to/shot_010_v003.exr",
                    "source_range": {"start_time": 1001, "duration": 120},
                    "timeline_range": {"start_time": 0, "duration": 120},
                    "metadata": {
                        "shot": "SH010",
                        "version": "v003",
                        "department": "animation"
                    }
                }
            ]
        }
    ],
    "metadata": {
        "project": "PROJECT_NAME",
        "episode": "EP001",
        "sequence": "SEQ010",
        "review_type": "animation_review"
    }
}
```

---

## 6. Inter-Widget Communication Architecture

### 6.1 Event-Based Communication
Widgets communicate through Open RV's event system to maintain loose coupling:

```python
# Event types for inter-widget communication
class HorusEvents:
    MEDIA_SELECTED = "horus.media.selected"
    FRAME_CHANGED = "horus.frame.changed"
    COMMENT_ADDED = "horus.comment.added"
    TIMELINE_UPDATED = "horus.timeline.updated"
    ANNOTATION_CREATED = "horus.annotation.created"
```

### 6.2 Data Synchronization
- **Shared Data Cache**: Common caching layer for media metadata
- **Event Broadcasting**: Automatic updates when data changes
- **Conflict Resolution**: Last-write-wins with user notification
- **Offline Support**: Local caching with sync on reconnection

---

## 7. Technical Requirements & Dependencies

### 7.1 Core Dependencies
- **Open RV 2.0+**: Base framework
- **Python 3.8+**: Primary development language
- **PySide2/Qt 5.15+**: UI framework
- **OpenTimelineIO 0.15+**: Timeline data management
- **SQLite/PostgreSQL**: Database storage
- **Pillow**: Thumbnail generation
- **asyncio**: Asynchronous operations

### 7.2 Development Standards
- **PEP 8 Compliance**: Strict code formatting
- **Google Style Docstrings**: Comprehensive documentation
- **Type Hints**: Full type annotation coverage
- **Unit Testing**: 90%+ test coverage
- **Performance**: <3 second load times, <500MB memory usage

---

## 8. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- Project rename to Horus
- Enhanced Montu data connector
- Base widget framework setup

### Phase 2: Media Library Widget (Weeks 3-4)
- Thumbnail grid implementation
- Advanced filtering system
- Search engine integration

### Phase 3: Comments & Annotations Widget (Weeks 5-6)
- Threaded comment system
- Annotation tools integration
- Database schema implementation

### Phase 4: Timeline Editor Widget (Weeks 7-8)
- Timeline interface development
- OTIO integration
- Playlist management system

### Phase 5: Integration & Testing (Weeks 9-10)
- Inter-widget communication
- Performance optimization
- Comprehensive testing

---

## 9. Future Extension Points

### 9.1 Studio Pipeline Integration
- **ShotGrid Connector**: Automated data synchronization
- **ftrack Integration**: Project management workflows
- **Slack/Teams Notifications**: Real-time collaboration alerts

### 9.2 Advanced Features
- **AI-Powered Search**: Content-based media discovery
- **Voice Annotations**: Audio comment recording
- **Mobile Companion App**: Remote review capabilities
- **Cloud Synchronization**: Multi-site collaboration

---

This architectural design provides a comprehensive foundation for transforming the current Monto-openRv application into the advanced Horus three-widget system, maintaining backward compatibility while enabling significant new capabilities for professional VFX workflows.
