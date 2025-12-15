# Horus Application Architecture
## UI Navigation, Directory Browser, and Playlist Integration

**Project:** Horus  
**Version:** 2.0  
**Date:** 2025-01-22  

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Horus Application                                │
│                    (Open RV Integration Layer)                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
┌───────▼────────┐        ┌─────────▼────────┐      ┌─────────▼──────────┐
│   Directory    │        │    Playlist      │      │   Comments &       │
│    Browser     │───────▶│    Manager       │◀─────│   Annotations      │
│                │        │                  │      │                    │
│ • File tree    │        │ • Create/edit    │      │ • Frame comments   │
│ • Thumbnails   │        │ • Add/remove     │      │ • RV annotations   │
│ • Metadata     │        │ • Reorder clips  │      │ • Export/import    │
│ • Multi-select │        │ • Load in RV     │      │ • Status tracking  │
└────────┬───────┘        └─────────┬────────┘      └─────────┬──────────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
                          ┌─────────▼─────────┐
                          │   Data Manager    │
                          │   (JSON-based)    │
                          └─────────┬─────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
┌───────▼────────┐        ┌─────────▼────────┐      ┌─────────▼──────────┐
│  Playlists     │        │   Comments       │      │   Annotations      │
│  .json         │        │   .json          │      │   .json            │
│                │        │                  │      │                    │
│ • Clip lists   │        │ • Frame notes    │      │ • RV exports       │
│ • Metadata     │        │ • Threading      │      │ • Coordinates      │
│ • Settings     │        │ • Status         │      │ • Styles           │
└────────────────┘        └──────────────────┘      └────────────────────┘
```

---

## 2. Component Integration Flow

### 2.1 Directory Browser → Playlist Workflow

```
User Action: Browse and select media files
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  Directory Browser Widget                   │
│  • Display file tree                        │
│  • Generate thumbnails                      │
│  • Extract metadata                         │
│  • Multi-select support                     │
└─────────────────┬───────────────────────────┘
                  │ User clicks "Add to Playlist"
                  ▼
┌─────────────────────────────────────────────┐
│  Playlist Selection Dialog                  │
│  • Choose existing playlist                 │
│  • Or create new playlist                   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Playlist Manager                           │
│  • Add clips to playlist                    │
│  • Calculate positions                      │
│  • Update metadata                          │
│  • Save to horus_playlists.json            │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Timeline Playlist Widget                   │
│  • Display clips in timeline                │
│  • Show thumbnails and metadata             │
│  • Enable reordering                        │
└─────────────────────────────────────────────┘
```

### 2.2 RV Annotation Export Workflow

```
User Action: Create annotations in RV
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  Open RV Paint Mode                         │
│  • Draw shapes (rectangle, circle, arrow)   │
│  • Add text annotations                     │
│  • Set colors and styles                    │
└─────────────────┬───────────────────────────┘
                  │ User clicks "Export Annotations"
                  ▼
┌─────────────────────────────────────────────┐
│  RV Annotations Manager                     │
│  • Extract RV paint node data               │
│  • Convert to Horus format                  │
│  • Link to media file and frame             │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Save to annotations.json                   │
│  • Store coordinates                        │
│  • Store style properties                   │
│  • Store RV node data                       │
│  • Link to comments if applicable           │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Comments & Annotations Widget              │
│  • Display annotations list                 │
│  • Show on timeline                         │
│  • Enable editing/deletion                  │
└─────────────────────────────────────────────┘
```

### 2.3 Playlist Load in RV Workflow

```
User Action: Select playlist and click "Load in RV"
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  Playlist Manager                           │
│  • Load playlist from JSON                  │
│  • Get all clips in order                   │
│  • Prepare file paths                       │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Media Type Detection                       │
│  • Check if image sequence or video         │
│  • Detect sequence patterns                 │
│  • Get frame ranges                         │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  RV Session Builder                         │
│  • Clear current session                    │
│  • Load each clip via rv.commands           │
│  • Set playback settings                    │
│  • Apply color space                        │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Open RV Playback                           │
│  • Display loaded clips                     │
│  • Enable playback controls                 │
│  • Show timeline                            │
└─────────────────────────────────────────────┘
```

---

## 3. Data Flow Diagram

```
┌──────────────┐
│ File System  │
└──────┬───────┘
       │ Scan directories
       ▼
┌──────────────────────┐
│ Directory Browser    │
│ • Detect media files │
│ • Generate thumbs    │
└──────┬───────────────┘
       │ Add to playlist
       ▼
┌──────────────────────┐      ┌──────────────────┐
│ Playlist Manager     │─────▶│ horus_playlists  │
│ • Organize clips     │      │ .json            │
└──────┬───────────────┘      └──────────────────┘
       │ Load in RV
       ▼
┌──────────────────────┐
│ Open RV Session      │
│ • Playback           │
│ • Annotations        │
└──────┬───────────────┘
       │ Export annotations
       ▼
┌──────────────────────┐      ┌──────────────────┐
│ RV Annotations Mgr   │─────▶│ annotations.json │
│ • Extract data       │      └──────────────────┘
└──────┬───────────────┘
       │ Create comments
       ▼
┌──────────────────────┐      ┌──────────────────┐
│ Comments Manager     │─────▶│ comments.json    │
│ • Frame notes        │      └──────────────────┘
└──────────────────────┘
```

