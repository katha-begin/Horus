# Design Comparison: Current vs. New Proposal
## Horus Data Model and Architecture Analysis

**Date:** 2025-01-22  
**Status:** Comparison Analysis  

---

## Executive Summary

### Current Implementation
- **Database Type:** SQLite with Python ORM
- **Data Source:** Montu API (read-only from `C:\Users\ADMIN\Documents\dev\Montu\data\json_db\`)
- **Storage:** Hybrid (SQLite + JSON files)
- **Focus:** Integration with existing Montu project management system

### New Proposal
- **Database Type:** Pure JSON files
- **Data Source:** Self-contained Horus data
- **Storage:** JSON-only in `sample_db/`
- **Focus:** Standalone VFX review application with RV integration

---

## 1. Data Storage Architecture

### Current Implementation ✅

**Database Structure:**
```
SQLite Database (horus.db)
├── projects table
├── media_records table
├── comments table
└── annotations table

JSON Files (from Montu)
├── project_configs.json (read-only)
├── media_records.json (read-only)
├── tasks.json (read-only)
├── annotations.json (read-only)
└── versions.json (read-only)
```

**Advantages:**
- ✅ Relational database with ACID properties
- ✅ Efficient querying with SQL
- ✅ Data integrity with foreign keys
- ✅ Integration with Montu system
- ✅ Existing implementation working

**Disadvantages:**
- ❌ Requires SQLite dependency
- ❌ More complex setup
- ❌ Harder to backup/version control
- ❌ Dual storage (SQLite + JSON)

### New Proposal 🆕

**Database Structure:**
```
JSON Files Only (sample_db/)
├── project_configs.json
├── horus_playlists.json
├── media_metadata.json
├── comments.json
└── annotations.json
```

**Advantages:**
- ✅ Simple file-based storage
- ✅ Easy backup (copy folder)
- ✅ Version control friendly
- ✅ No database server needed
- ✅ Human-readable format
- ✅ Cross-platform compatible

**Disadvantages:**
- ❌ No ACID guarantees
- ❌ Slower for large datasets
- ❌ No relational integrity
- ❌ Manual data consistency

---

## 2. Data Model Comparison

### Playlists

**Current Implementation:**
```json
{
  "_id": "playlist_001",
  "name": "yy",
  "project_id": "proj_001",
  "clips": [
    {
      "clip_id": "clip_001",
      "media_id": "media_001",
      "position": 0,
      "duration": 120,
      "file_path": "/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov"
    }
  ],
  "tracks": [...],
  "metadata": {...}
}
```

**New Proposal:**
```json
{
  "_id": "playlist_001",
  "name": "Daily Review",
  "project_id": "SWA",
  "clips": [
    {
      "clip_id": "clip_001",
      "file_path": "/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov",
      "position": 0,
      "duration": 120,
      "metadata": {
        "department": "animation",
        "sequence": "sq0010",
        "shot": "sh0010",
        "version": "v003"
      }
    }
  ]
}
```

**Comparison:**
- ✅ **Same structure** - Both use similar playlist format
- ✅ **Same clip organization** - Position-based timeline
- ✅ **Same metadata** - Department, sequence, shot, version
- 🔄 **Minor difference** - New proposal embeds metadata in clip

### Media Records

**Current Implementation:**
```json
{
  "_id": "media_001",
  "project_id": "proj_001",
  "file_name": "seq010_shot010_anim_v003.mov",
  "file_path": "C:/Projects/DemoAlpha/shots/seq010/shot010/anim/seq010_shot010_anim_v003.mov",
  "file_type": "video",
  "linked_task_id": "task_001",
  "version": "v003",
  "approval_status": "approved",
  "metadata": {
    "width": 1920,
    "height": 1080,
    "frame_rate": 24,
    "codec": "H.264"
  }
}
```

**New Proposal:**
```json
{
  "_id": "media_001",
  "file_path": "/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov",
  "project_id": "SWA",
  "file_info": {
    "file_name": "sh0010_anim_v003.mov",
    "file_size": 52428800,
    "file_extension": ".mov",
    "created_date": "2025-01-20T14:30:00Z"
  },
  "media_properties": {
    "width": 1920,
    "height": 1080,
    "frame_rate": 24,
    "codec": "H.264",
    "duration": 120
  },
  "sequence_info": {
    "is_sequence": false
  },
  "project_metadata": {
    "department": "animation",
    "sequence": "sq0010",
    "shot": "sh0010",
    "version": "v003"
  }
}
```

**Comparison:**
- ✅ **Same core data** - File path, resolution, frame rate
- 🆕 **New proposal adds** - Sequence detection info
- 🆕 **New proposal adds** - More structured metadata grouping
- ❌ **Current has** - Task linking (Montu integration)

### Comments

**Current Implementation (annotations.json):**
```json
{
  "_id": "annotation_001",
  "media_id": "media_001",
  "text": "Great animation!",
  "author": "director.smith",
  "frame_number": 45,
  "annotation_type": "comment",
  "status": "open",
  "priority": "low"
}
```

**New Proposal (comments.json):**
```json
{
  "_id": "comment_001",
  "media_path": "/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov",
  "frame_reference": {
    "frame_number": 45,
    "timecode": "00:00:01:21"
  },
  "user_info": {
    "user_id": "director.smith",
    "user_name": "John Smith"
  },
  "content": "Great animation!",
  "status": "open",
  "priority": "low",
  "threading": {
    "parent_id": null,
    "thread_depth": 0,
    "reply_count": 0
  }
}
```

**Comparison:**
- ✅ **Same core data** - Frame number, text, author, status
- 🆕 **New proposal adds** - Timecode support
- 🆕 **New proposal adds** - Threading structure
- 🆕 **New proposal adds** - Reply count tracking
- 🔄 **Different** - Uses file_path instead of media_id


