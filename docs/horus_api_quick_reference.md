# Horus API Quick Reference
## Essential APIs for Directory Browser, Playlist, and RV Integration

**Project:** Horus  
**Version:** 2.0  
**Date:** 2025-01-22  

---

## 1. Data Manager API

### Initialize Data Manager

```python
from horus_database.data_manager import HorusDataManager

# Initialize with default data directory
data_mgr = HorusDataManager(data_dir="sample_db")

# Or specify custom directory
data_mgr = HorusDataManager(data_dir="/path/to/project/data")
```

---

## 2. Playlist Operations

### Create Playlist

```python
# Create a new playlist
playlist = data_mgr.create_playlist(
    name="Daily Animation Review",
    project_id="SWA",
    description="Daily review session",
    type="daily_review",
    created_by="animation_supervisor"
)

print(f"Created playlist: {playlist['_id']}")
```

### Get Playlist

```python
# Get specific playlist
playlist = data_mgr.get_playlist("playlist_001")

# Get all playlists for a project
playlists = data_mgr.get_all_playlists(project_id="SWA")

# Get all playlists
all_playlists = data_mgr.get_all_playlists()
```

### Add Clip to Playlist

```python
# Add a single clip
clip = data_mgr.add_clip_to_playlist(
    playlist_id="playlist_001",
    file_path="/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov",
    metadata={
        "department": "animation",
        "sequence": "sq0010",
        "shot": "sh0010",
        "version": "v003",
        "artist": "john_doe"
    }
)
```

### Remove Clip from Playlist

```python
# Remove clip by ID
success = data_mgr.remove_clip_from_playlist(
    playlist_id="playlist_001",
    clip_id="clip_001"
)
```

### Update Playlist

```python
# Update playlist properties
success = data_mgr.update_playlist(
    playlist_id="playlist_001",
    updates={
        "name": "Updated Playlist Name",
        "status": "locked",
        "settings": {
            "auto_play": False,
            "loop": True
        }
    }
)
```

### Delete Playlist

```python
# Delete a playlist
success = data_mgr.delete_playlist("playlist_001")
```

---

## 3. Media Metadata Operations

### Index Media File

```python
# Index a media file and extract metadata
metadata = data_mgr.index_media_file(
    file_path="/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov",
    project_id="SWA"
)

print(f"Resolution: {metadata['media_properties']['width']}x{metadata['media_properties']['height']}")
print(f"Frame rate: {metadata['media_properties']['frame_rate']}")
```

### Get Media Metadata

```python
# Get cached metadata
metadata = data_mgr.get_media_metadata(
    file_path="/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov"
)

if metadata:
    print(f"Codec: {metadata['media_properties']['codec']}")
else:
    print("Metadata not cached, need to index file")
```

### Search Media

```python
# Search media by filters
results = data_mgr.search_media(
    project_id="SWA",
    filters={
        "department": "animation",
        "sequence": "sq0010",
        "approval_status": "approved"
    }
)

for media in results:
    print(f"Found: {media['file_path']}")
```

---

## 4. Comments Operations

### Create Comment

```python
# Create a frame-specific comment
comment = data_mgr.create_comment(
    media_path="/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov",
    frame_number=45,
    content="The eye line doesn't match the previous shot",
    user_id="animation_supervisor",
    user_name="John Smith",
    priority="high",
    status="open"
)
```

### Get Comments

```python
# Get all comments for a media file
comments = data_mgr.get_comments_for_media(
    media_path="/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov"
)

# Get comments for specific frame
frame_comments = data_mgr.get_comments_for_frame(
    media_path="/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov",
    frame_number=45
)
```

### Reply to Comment

```python
# Reply to an existing comment
reply = data_mgr.reply_to_comment(
    parent_id="comment_001",
    content="I'll fix this in the next version",
    user_id="jane_doe",
    user_name="Jane Doe"
)
```

### Update Comment Status

```python
# Mark comment as resolved
success = data_mgr.update_comment_status(
    comment_id="comment_001",
    status="resolved"
)
```

---

## 5. RV Annotations Operations

### Export RV Annotations

```python
# Export annotations from RV for current media
annotations = data_mgr.export_rv_annotations(
    media_path="/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov"
)

for annotation in annotations:
    print(f"Frame {annotation['frame_number']}: {annotation['annotation_type']}")
```

### Save Annotation

```python
# Save a single annotation
annotation = data_mgr.save_annotation(
    media_path="/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov",
    frame_number=45,
    annotation_data={
        "annotation_type": "rectangle",
        "coordinates": {"x": 450, "y": 320, "width": 200, "height": 150},
        "style": {"color": "#ff0000", "line_width": 3},
        "content": {"text": "Fix eye line"}
    }
)
```

### Get Annotations for Frame

```python
# Get all annotations for a specific frame
annotations = data_mgr.get_annotations_for_frame(
    media_path="/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov",
    frame_number=45
)
```

---

## 6. File Path Utilities

### Normalize Path

```python
from horus_database.path_utils import normalize_path, get_relative_path

# Normalize path for cross-platform compatibility
normalized = normalize_path("V:\\SWA\\ep01\\sq0010\\sh0010\\anim\\v003\\file.mov")
# Result: "V:/SWA/ep01/sq0010/sh0010/anim/v003/file.mov"

# Get relative path from project root
relative = get_relative_path(
    file_path="V:/SWA/ep01/sq0010/sh0010/anim/v003/file.mov",
    project_root="V:/SWA"
)
# Result: "ep01/sq0010/sh0010/anim/v003/file.mov"
```

### Detect Image Sequence

```python
from horus_database.sequence_utils import detect_sequence_pattern, get_sequence_files

# Detect if file is part of a sequence
pattern = detect_sequence_pattern("sh0010_anim_v003.0045.exr")

if pattern['is_sequence']:
    print(f"Base name: {pattern['base_name']}")
    print(f"Frame number: {pattern['frame_number']}")
    print(f"Padding: {pattern['padding']}")
    print(f"Pattern: {pattern['pattern']}")
    
    # Get all files in sequence
    files = get_sequence_files("/path/to/directory", pattern)
    print(f"Found {len(files)} frames")
```

---

## 7. Complete Workflow Example

```python
# Complete workflow: Browse → Playlist → RV → Annotations

# 1. Initialize data manager
data_mgr = HorusDataManager()

# 2. Create a new playlist
playlist = data_mgr.create_playlist(
    name="Daily Review",
    project_id="SWA"
)

# 3. Add media files to playlist
media_files = [
    "/projects/SWA/ep01/sq0010/sh0010/animation/v003/sh0010_anim_v003.mov",
    "/projects/SWA/ep01/sq0010/sh0020/animation/v002/sh0020_anim_v002.mov"
]

for file_path in media_files:
    data_mgr.add_clip_to_playlist(
        playlist_id=playlist['_id'],
        file_path=file_path,
        metadata={"department": "animation"}
    )

# 4. Load playlist in RV (see RV integration section)

# 5. Create comments during review
comment = data_mgr.create_comment(
    media_path=media_files[0],
    frame_number=45,
    content="Great performance!",
    user_id="supervisor"
)

# 6. Export RV annotations
annotations = data_mgr.export_rv_annotations(media_path=media_files[0])

print(f"✅ Workflow complete!")
print(f"   Playlist: {playlist['name']}")
print(f"   Clips: {len(media_files)}")
print(f"   Comments: 1")
print(f"   Annotations: {len(annotations)}")
```

---

This quick reference covers all essential operations for the Horus application!

