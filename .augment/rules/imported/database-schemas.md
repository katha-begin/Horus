---
type: "agent_requested"
description: "Example description"
---
# Horus Database Schemas
## Mock Database Structures for Enhanced Features

**Project:** Horus  
**Version:** 2.0  
**Date:** 2025-08-22  

---

## 1. PostgreSQL Production Schema

### 1.1 Core Media Management Tables

```sql
-- Enhanced media records table
CREATE TABLE horus_media_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_path TEXT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT,
    file_hash VARCHAR(64), -- SHA-256 hash for deduplication
    mime_type VARCHAR(100),
    
    -- Project hierarchy
    project_id VARCHAR(100) NOT NULL,
    episode VARCHAR(50),
    sequence VARCHAR(50),
    shot VARCHAR(50),
    
    -- Version information
    version VARCHAR(20) NOT NULL,
    version_number INTEGER,
    is_latest_version BOOLEAN DEFAULT FALSE,
    
    -- Production metadata
    department VARCHAR(50),
    task_type VARCHAR(50),
    artist_id VARCHAR(100),
    artist_name VARCHAR(255),
    approval_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'on_hold'
    
    -- Technical metadata
    resolution VARCHAR(20), -- '1920x1080', '4096x2160', etc.
    frame_rate DECIMAL(5,2),
    color_space VARCHAR(50),
    bit_depth INTEGER,
    compression VARCHAR(50),
    
    -- Frame range for sequences
    start_frame INTEGER,
    end_frame INTEGER,
    frame_count INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    file_modified_at TIMESTAMP WITH TIME ZONE,
    
    -- Soft delete
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes for performance
    INDEX idx_media_project_shot (project_id, shot),
    INDEX idx_media_department_status (department, approval_status),
    INDEX idx_media_artist_created (artist_id, created_at DESC),
    INDEX idx_media_version_latest (version_number, is_latest_version),
    INDEX idx_media_file_hash (file_hash),
    INDEX idx_media_file_path (file_path)
);

-- Media tags for flexible categorization
CREATE TABLE horus_media_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_id UUID REFERENCES horus_media_records(id) ON DELETE CASCADE,
    tag_name VARCHAR(100) NOT NULL,
    tag_category VARCHAR(50), -- 'status', 'priority', 'custom', etc.
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(media_id, tag_name),
    INDEX idx_tags_media (media_id),
    INDEX idx_tags_name_category (tag_name, tag_category)
);

-- Thumbnail cache table
CREATE TABLE horus_thumbnails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_id UUID REFERENCES horus_media_records(id) ON DELETE CASCADE,
    thumbnail_size VARCHAR(20) NOT NULL, -- 'small', 'medium', 'large'
    thumbnail_path TEXT NOT NULL,
    thumbnail_hash VARCHAR(64),
    frame_number INTEGER DEFAULT 1, -- For video/sequence thumbnails
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(media_id, thumbnail_size, frame_number),
    INDEX idx_thumbnails_media_size (media_id, thumbnail_size)
);
```

### 1.2 Comments and Collaboration Tables

```sql
-- Threaded comments system
CREATE TABLE horus_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES horus_comments(id) ON DELETE CASCADE,
    
    -- Media reference
    media_id UUID REFERENCES horus_media_records(id) ON DELETE CASCADE,
    frame_number INTEGER,
    timecode VARCHAR(20),
    
    -- User information
    user_id VARCHAR(100) NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    user_email VARCHAR(255),
    user_avatar_url TEXT,
    
    -- Comment content
    content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text', -- 'text', 'markdown', 'html'
    
    -- Threading
    thread_depth INTEGER DEFAULT 0,
    thread_path TEXT, -- Materialized path for efficient queries
    
    -- Status
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP WITH TIME ZONE,
    
    -- Mentions
    mentioned_users TEXT[], -- Array of mentioned user IDs
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft delete
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by VARCHAR(100),
    
    -- Indexes
    INDEX idx_comments_media_frame (media_id, frame_number),
    INDEX idx_comments_user_created (user_id, created_at DESC),
    INDEX idx_comments_parent_thread (parent_id, thread_depth),
    INDEX idx_comments_mentions (mentioned_users),
    INDEX idx_comments_resolved (is_resolved, resolved_at)
);

-- Comment reactions (likes, approvals, etc.)
CREATE TABLE horus_comment_reactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id UUID REFERENCES horus_comments(id) ON DELETE CASCADE,
    user_id VARCHAR(100) NOT NULL,
    reaction_type VARCHAR(20) NOT NULL, -- 'like', 'dislike', 'approve', 'reject', 'love', 'laugh'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(comment_id, user_id, reaction_type),
    INDEX idx_reactions_comment (comment_id),
    INDEX idx_reactions_user (user_id)
);

-- Comment attachments
CREATE TABLE horus_comment_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id UUID REFERENCES horus_comments(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    uploaded_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_attachments_comment (comment_id)
);
```

### 1.3 Annotations and Drawing Tables

```sql
-- Frame-specific annotations
CREATE TABLE horus_annotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Media reference
    media_id UUID REFERENCES horus_media_records(id) ON DELETE CASCADE,
    frame_number INTEGER NOT NULL,
    
    -- Annotation type and data
    annotation_type VARCHAR(50) NOT NULL, -- 'rectangle', 'circle', 'arrow', 'text', 'freehand', 'polygon'
    coordinates JSONB NOT NULL, -- Flexible coordinate storage
    style_properties JSONB, -- Color, line width, font, opacity, etc.
    
    -- Content
    content TEXT, -- Text content for text annotations
    content_type VARCHAR(20) DEFAULT 'text',
    
    -- User information
    user_id VARCHAR(100) NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    
    -- Organization
    layer_name VARCHAR(100) DEFAULT 'default',
    layer_order INTEGER DEFAULT 0,
    
    -- Visibility and status
    is_visible BOOLEAN DEFAULT TRUE,
    is_locked BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft delete
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    INDEX idx_annotations_media_frame (media_id, frame_number),
    INDEX idx_annotations_user_created (user_id, created_at DESC),
    INDEX idx_annotations_layer (layer_name, layer_order),
    INDEX idx_annotations_type (annotation_type),
    INDEX idx_annotations_visible (is_visible, is_deleted)
);

-- Annotation layers for organization
CREATE TABLE horus_annotation_layers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_id UUID REFERENCES horus_media_records(id) ON DELETE CASCADE,
    layer_name VARCHAR(100) NOT NULL,
    layer_color VARCHAR(7), -- Hex color code
    is_visible BOOLEAN DEFAULT TRUE,
    is_locked BOOLEAN DEFAULT FALSE,
    layer_order INTEGER DEFAULT 0,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(media_id, layer_name),
    INDEX idx_layers_media_order (media_id, layer_order)
);
```

### 1.4 Timeline and Playlist Tables

```sql
-- Timeline/playlist definitions
CREATE TABLE horus_timelines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Project context
    project_id VARCHAR(100) NOT NULL,
    episode VARCHAR(50),
    sequence VARCHAR(50),
    
    -- Timeline type
    timeline_type VARCHAR(50) NOT NULL, -- 'episode', 'sequence', 'department', 'dailies', 'client', 'custom'
    
    -- OTIO data
    otio_data JSONB, -- Serialized OTIO timeline
    
    -- Metadata
    frame_rate DECIMAL(5,2) DEFAULT 24.0,
    resolution VARCHAR(20),
    duration_frames INTEGER,
    duration_timecode VARCHAR(20),
    
    -- User information
    created_by VARCHAR(100) NOT NULL,
    created_by_name VARCHAR(255),
    last_modified_by VARCHAR(100),
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'review', 'approved', 'published'
    version VARCHAR(20) DEFAULT 'v001',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft delete
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    INDEX idx_timelines_project_type (project_id, timeline_type),
    INDEX idx_timelines_creator_created (created_by, created_at DESC),
    INDEX idx_timelines_status_version (status, version),
    INDEX idx_timelines_episode_sequence (episode, sequence)
);

-- Timeline clips (for quick queries without parsing OTIO)
CREATE TABLE horus_timeline_clips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timeline_id UUID REFERENCES horus_timelines(id) ON DELETE CASCADE,
    
    -- Media reference
    media_id UUID REFERENCES horus_media_records(id),
    media_path TEXT NOT NULL,
    
    -- Timeline position
    track_name VARCHAR(100) NOT NULL,
    track_type VARCHAR(20) NOT NULL, -- 'video', 'audio'
    track_index INTEGER NOT NULL,
    
    -- Timing
    start_time_frames INTEGER NOT NULL,
    duration_frames INTEGER NOT NULL,
    source_start_frames INTEGER DEFAULT 0,
    source_duration_frames INTEGER,
    
    -- Clip metadata
    clip_name VARCHAR(255),
    clip_metadata JSONB,
    
    -- Order within track
    clip_order INTEGER NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_clips_timeline_track (timeline_id, track_index, clip_order),
    INDEX idx_clips_media (media_id),
    INDEX idx_clips_timing (start_time_frames, duration_frames)
);
```

### 1.5 User Management and Collaboration Tables

```sql
-- User profiles
CREATE TABLE horus_users (
    id VARCHAR(100) PRIMARY KEY, -- Usually from external auth system
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    
    -- Role and permissions
    role VARCHAR(50) DEFAULT 'artist', -- 'admin', 'supervisor', 'artist', 'client'
    department VARCHAR(50),
    permissions JSONB, -- Flexible permissions structure
    
    -- Preferences
    ui_preferences JSONB,
    notification_preferences JSONB,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_users_username (username),
    INDEX idx_users_email (email),
    INDEX idx_users_department_role (department, role),
    INDEX idx_users_active_login (is_active, last_login_at DESC)
);

-- User sessions for collaboration
CREATE TABLE horus_user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) REFERENCES horus_users(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    
    -- Session context
    media_id UUID REFERENCES horus_media_records(id),
    current_frame INTEGER,
    
    -- Connection info
    ip_address INET,
    user_agent TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    INDEX idx_sessions_user_active (user_id, is_active),
    INDEX idx_sessions_media_active (media_id, is_active),
    INDEX idx_sessions_token (session_token),
    INDEX idx_sessions_activity (last_activity_at DESC)
);

-- Notifications system
CREATE TABLE horus_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) REFERENCES horus_users(id),
    
    -- Notification content
    type VARCHAR(50) NOT NULL, -- 'comment_mention', 'comment_reply', 'annotation_added', etc.
    title VARCHAR(255) NOT NULL,
    message TEXT,
    
    -- Related objects
    related_media_id UUID REFERENCES horus_media_records(id),
    related_comment_id UUID REFERENCES horus_comments(id),
    related_annotation_id UUID REFERENCES horus_annotations(id),
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_notifications_user_unread (user_id, is_read, created_at DESC),
    INDEX idx_notifications_type_created (type, created_at DESC),
    INDEX idx_notifications_media (related_media_id)
);
```

---

## 2. SQLite Development Schema

For development and testing, a simplified SQLite schema:

```sql
-- Simplified media records for development
CREATE TABLE media_records (
    id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    project_id TEXT NOT NULL,
    shot TEXT,
    version TEXT,
    department TEXT,
    artist_name TEXT,
    approval_status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Simplified comments
CREATE TABLE comments (
    id TEXT PRIMARY KEY,
    parent_id TEXT REFERENCES comments(id),
    media_id TEXT REFERENCES media_records(id),
    frame_number INTEGER,
    user_name TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Simplified annotations
CREATE TABLE annotations (
    id TEXT PRIMARY KEY,
    media_id TEXT REFERENCES media_records(id),
    frame_number INTEGER NOT NULL,
    annotation_type TEXT NOT NULL,
    coordinates TEXT NOT NULL, -- JSON string
    user_name TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Data Migration Strategy

### 3.1 From Current Montu JSON to New Schema

```python
class MontuDataMigrator:
    """Migrate existing Montu JSON data to new Horus schema."""
    
    def migrate_media_records(self, json_data: List[Dict]) -> List[Dict]:
        """Transform Montu media records to Horus format."""
        migrated_records = []
        
        for record in json_data:
            migrated_record = {
                "id": record.get("_id", str(uuid.uuid4())),
                "file_path": record.get("storage_url", ""),
                "file_name": Path(record.get("storage_url", "")).name,
                "project_id": record.get("linked_task_id", "").split("_")[0] if record.get("linked_task_id") else "",
                "version": self._extract_version(record.get("storage_url", "")),
                "department": record.get("department", "unknown"),
                "artist_name": record.get("created_by", "unknown"),
                "approval_status": self._map_approval_status(record.get("status")),
                "created_at": record.get("created_at", datetime.utcnow().isoformat())
            }
            migrated_records.append(migrated_record)
        
        return migrated_records
```

This database schema provides a comprehensive foundation for the enhanced Horus features while maintaining compatibility with existing Montu data structures.
