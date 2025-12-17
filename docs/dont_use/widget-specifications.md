# Horus Widget Technical Specifications
## Detailed Implementation Guidelines for Three-Widget System

**Project:** Horus  
**Version:** 2.0  
**Date:** 2025-08-22  

---

## 1. Search & Media Library Widget Specification

### 1.1 UI Framework Recommendations

**Primary Framework: PySide2/Qt with Custom Components**
- **QGraphicsView**: For high-performance thumbnail grid with smooth scrolling
- **QStandardItemModel**: For efficient data management and filtering
- **QSortFilterProxyModel**: For real-time search and filtering
- **Custom QGraphicsItem**: For thumbnail items with overlay metadata

**Alternative Framework Consideration: QML**
- **Pros**: Better performance for large grids, modern animations, touch support
- **Cons**: Additional complexity, learning curve, debugging challenges
- **Recommendation**: Stick with PySide2 for consistency with existing codebase

### 1.2 Thumbnail Generation System

**Async Thumbnail Pipeline:**
```python
class ThumbnailGenerator:
    """Asynchronous thumbnail generation with caching."""
    
    def __init__(self, cache_dir: Path, max_workers: int = 4):
        self.cache_dir = cache_dir
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.cache = {}
    
    async def generate_thumbnail(self, media_path: str, size: tuple) -> str:
        """Generate thumbnail with caching."""
        cache_key = f"{media_path}_{size[0]}x{size[1]}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Generate thumbnail in background thread
        thumbnail_path = await asyncio.get_event_loop().run_in_executor(
            self.executor, self._create_thumbnail, media_path, size
        )
        
        self.cache[cache_key] = thumbnail_path
        return thumbnail_path
```

**Supported Media Types:**
- **Image Sequences**: EXR, DPX, TIFF, PNG, JPG
- **Video Files**: MOV, MP4, AVI, MXF
- **Audio Files**: WAV, AIFF (waveform thumbnails)
- **3D Files**: FBX, OBJ, USD (wireframe previews)

### 1.3 Advanced Filtering Architecture

**Filter Categories:**
```python
class MediaFilters:
    """Comprehensive filtering system."""
    
    DEPARTMENT_FILTERS = [
        "animation", "lighting", "compositing", "fx", 
        "modeling", "texturing", "rigging", "layout"
    ]
    
    STATUS_FILTERS = [
        "approved", "pending_review", "in_progress", 
        "rejected", "on_hold", "final"
    ]
    
    FILE_TYPE_FILTERS = [
        "image_sequence", "video", "audio", "3d_model", 
        "texture", "cache", "reference"
    ]
    
    VERSION_FILTERS = [
        "latest_only", "all_versions", "specific_version",
        "published_only", "work_in_progress"
    ]
```

### 1.4 Search Engine Implementation

**Multi-Field Search with Indexing:**
```python
class MediaSearchEngine:
    """Advanced search with full-text indexing."""
    
    def __init__(self):
        self.index = {}
        self.search_fields = [
            "file_name", "shot_name", "sequence", "episode",
            "artist", "department", "description", "tags"
        ]
    
    def build_index(self, media_records: List[Dict]):
        """Build searchable index from media records."""
        for record in media_records:
            searchable_text = self._extract_searchable_text(record)
            self.index[record['id']] = searchable_text
    
    def search(self, query: str, filters: Dict = None) -> List[str]:
        """Perform search with optional filters."""
        # Implement fuzzy search, stemming, and ranking
        pass
```

---

## 2. Comments & Annotations Widget Specification

### 2.1 Database Schema Design

**PostgreSQL Schema (Production):**
```sql
-- Comments table with threading support
CREATE TABLE horus_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES horus_comments(id) ON DELETE CASCADE,
    media_id VARCHAR(255) NOT NULL,
    frame_number INTEGER,
    timecode VARCHAR(20),
    user_id VARCHAR(100) NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_resolved BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    thread_depth INTEGER DEFAULT 0,
    mention_users TEXT[], -- Array of mentioned usernames
    
    -- Indexes for performance
    INDEX idx_comments_media_frame (media_id, frame_number),
    INDEX idx_comments_user (user_id),
    INDEX idx_comments_parent (parent_id),
    INDEX idx_comments_created (created_at DESC)
);

-- Reactions table
CREATE TABLE horus_comment_reactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id UUID REFERENCES horus_comments(id) ON DELETE CASCADE,
    user_id VARCHAR(100) NOT NULL,
    reaction_type VARCHAR(20) NOT NULL, -- 'like', 'dislike', 'approve', 'reject', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(comment_id, user_id, reaction_type)
);

-- Annotations table
CREATE TABLE horus_annotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_id VARCHAR(255) NOT NULL,
    frame_number INTEGER NOT NULL,
    annotation_type VARCHAR(50) NOT NULL, -- 'rectangle', 'circle', 'arrow', 'text', 'freehand'
    coordinates JSONB NOT NULL, -- Flexible coordinate storage
    style_properties JSONB, -- Color, line width, font, etc.
    content TEXT, -- Text content for text annotations
    user_id VARCHAR(100) NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_visible BOOLEAN DEFAULT TRUE,
    layer_name VARCHAR(100) DEFAULT 'default',
    
    INDEX idx_annotations_media_frame (media_id, frame_number),
    INDEX idx_annotations_user (user_id),
    INDEX idx_annotations_layer (layer_name)
);
```

### 2.2 Real-Time Collaboration Architecture

**WebSocket Integration:**
```python
class CollaborationManager:
    """Real-time collaboration using WebSockets."""
    
    def __init__(self, websocket_url: str):
        self.websocket_url = websocket_url
        self.connection = None
        self.user_presence = {}
        
    async def connect(self, user_id: str, session_id: str):
        """Connect to collaboration server."""
        self.connection = await websockets.connect(
            f"{self.websocket_url}?user_id={user_id}&session_id={session_id}"
        )
        
        # Start listening for events
        asyncio.create_task(self._listen_for_events())
    
    async def broadcast_comment(self, comment_data: Dict):
        """Broadcast new comment to all connected users."""
        message = {
            "type": "comment_added",
            "data": comment_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.connection.send(json.dumps(message))
    
    async def broadcast_annotation(self, annotation_data: Dict):
        """Broadcast new annotation to all connected users."""
        message = {
            "type": "annotation_created",
            "data": annotation_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.connection.send(json.dumps(message))
```

### 2.3 Annotation Storage Decision

**Recommendation: Hybrid Approach**
- **Vector Annotations**: Store as JSON coordinates for scalability and editability
- **Raster Annotations**: Store complex freehand drawings as PNG overlays
- **Performance**: Vector for simple shapes, raster for complex drawings

**Storage Schema:**
```python
# Vector annotation example
{
    "type": "rectangle",
    "coordinates": {
        "x": 100, "y": 150, "width": 200, "height": 100
    },
    "style": {
        "stroke_color": "#ff0000",
        "stroke_width": 2,
        "fill_color": "transparent"
    }
}

# Raster annotation example
{
    "type": "freehand",
    "image_data": "base64_encoded_png_data",
    "bounding_box": {
        "x": 50, "y": 75, "width": 300, "height": 200
    }
}
```

---

## 3. Timeline Editor Widget Specification

### 3.1 OTIO Integration Architecture

**Timeline Data Model:**
```python
import opentimelineio as otio

class HorusTimeline:
    """Enhanced OTIO timeline with Horus-specific features."""
    
    def __init__(self, name: str):
        self.timeline = otio.schema.Timeline(name=name)
        self.horus_metadata = {
            "project_id": "",
            "episode": "",
            "sequence": "",
            "review_type": "",
            "created_by": "",
            "version": "v001"
        }
    
    def add_media_clip(self, media_path: str, metadata: Dict):
        """Add media clip with Horus metadata."""
        # Create OTIO clip
        clip = otio.schema.Clip(
            name=metadata.get('shot_name', ''),
            media_reference=otio.schema.ExternalReference(
                target_url=media_path
            )
        )
        
        # Add Horus-specific metadata
        clip.metadata.update({
            "horus": {
                "shot_id": metadata.get('shot_id'),
                "version": metadata.get('version'),
                "department": metadata.get('department'),
                "approval_status": metadata.get('approval_status')
            }
        })
        
        # Add to timeline
        video_track = self._get_or_create_video_track()
        video_track.append(clip)
    
    def export_edl(self, output_path: str):
        """Export timeline as EDL with metadata."""
        # Use OTIO's EDL adapter
        otio.adapters.write_to_file(self.timeline, output_path)
```

### 3.2 Playlist Management System

**Playlist Types:**
```python
class PlaylistManager:
    """Manage different types of playlists."""
    
    PLAYLIST_TYPES = {
        "episode": "Full episode sequence",
        "sequence": "Individual sequence cuts", 
        "department": "Department-specific reviews",
        "dailies": "Daily review sessions",
        "client": "Client presentation cuts",
        "custom": "User-defined playlists"
    }
    
    def create_episode_playlist(self, episode_id: str) -> HorusTimeline:
        """Create playlist for entire episode."""
        timeline = HorusTimeline(f"Episode_{episode_id}_Complete")
        
        # Auto-populate with all shots in episode order
        shots = self._get_episode_shots(episode_id)
        for shot in shots:
            latest_version = self._get_latest_approved_version(shot['id'])
            if latest_version:
                timeline.add_media_clip(
                    latest_version['file_path'],
                    latest_version['metadata']
                )
        
        return timeline
    
    def create_department_playlist(self, department: str, date_range: tuple) -> HorusTimeline:
        """Create playlist for specific department review."""
        timeline = HorusTimeline(f"{department}_Review_{date_range[0]}")
        
        # Filter media by department and date range
        media_items = self._filter_by_department_and_date(department, date_range)
        for item in media_items:
            timeline.add_media_clip(item['file_path'], item['metadata'])
        
        return timeline
```

### 3.3 Version Management System

**Version Switching Architecture:**
```python
class VersionController:
    """Handle version switching within timeline context."""
    
    def __init__(self, timeline: HorusTimeline):
        self.timeline = timeline
        self.version_cache = {}
    
    def get_available_versions(self, shot_id: str) -> List[Dict]:
        """Get all available versions for a shot."""
        if shot_id in self.version_cache:
            return self.version_cache[shot_id]
        
        versions = self._query_shot_versions(shot_id)
        self.version_cache[shot_id] = versions
        return versions
    
    def switch_clip_version(self, clip_index: int, new_version: str):
        """Switch a timeline clip to different version."""
        track = self.timeline.timeline.video_tracks()[0]
        clip = track[clip_index]
        
        # Get new version data
        shot_id = clip.metadata['horus']['shot_id']
        new_version_data = self._get_version_data(shot_id, new_version)
        
        # Update clip reference
        clip.media_reference.target_url = new_version_data['file_path']
        clip.metadata['horus']['version'] = new_version
        
        # Notify UI of change
        self._emit_version_changed_event(clip_index, new_version)
```

---

## 4. UI Framework Recommendations

### 4.1 Recommended UI Libraries

**Primary Choice: PySide2 with Custom Components**
- **Pros**: Mature, well-documented, consistent with Open RV, extensive widget library
- **Cons**: Can be verbose, requires custom styling for modern look
- **Best For**: All three widgets due to stability and Open RV integration

**Alternative: PyQt5/6**
- **Pros**: Similar to PySide2, slightly better performance
- **Cons**: Licensing considerations, potential conflicts with Open RV
- **Recommendation**: Avoid due to licensing complexity

**Alternative: Tkinter with ttk**
- **Pros**: Built into Python, lightweight
- **Cons**: Limited styling options, outdated appearance
- **Recommendation**: Not suitable for professional VFX interface

### 4.2 Custom Styling Framework

**Adobe Premiere-Inspired Theme:**
```python
class HorusStyleSheet:
    """Custom stylesheet for Adobe Premiere-like appearance."""
    
    COLORS = {
        "background_dark": "#1e1e1e",
        "background_medium": "#2d2d2d", 
        "background_light": "#3c3c3c",
        "accent_blue": "#0078d4",
        "text_primary": "#e0e0e0",
        "text_secondary": "#b0b0b0",
        "border": "#4a4a4a",
        "success": "#107c10",
        "warning": "#ff8c00",
        "error": "#d13438"
    }
    
    @classmethod
    def get_widget_stylesheet(cls, widget_type: str) -> str:
        """Get stylesheet for specific widget type."""
        if widget_type == "media_grid":
            return cls._get_media_grid_style()
        elif widget_type == "comment_thread":
            return cls._get_comment_thread_style()
        elif widget_type == "timeline":
            return cls._get_timeline_style()
```

---

## 5. Performance Optimization Guidelines

### 5.1 Memory Management
- **Lazy Loading**: Load thumbnails and metadata on-demand
- **Virtual Scrolling**: Only render visible items in large lists
- **Cache Management**: LRU cache with configurable size limits
- **Memory Profiling**: Regular monitoring of memory usage patterns

### 5.2 Database Optimization
- **Connection Pooling**: Reuse database connections
- **Query Optimization**: Use indexes and prepared statements
- **Batch Operations**: Group multiple operations for efficiency
- **Async Operations**: Non-blocking database queries

### 5.3 UI Responsiveness
- **Background Threading**: Move heavy operations off UI thread
- **Progressive Loading**: Show partial results while loading continues
- **Debounced Search**: Prevent excessive search queries
- **Smooth Animations**: Use Qt's animation framework for transitions

---

This specification provides detailed technical guidance for implementing each of the three Horus widgets with professional-grade performance and user experience.
