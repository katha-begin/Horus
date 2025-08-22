---
type: "manual"
---

# MediaBrowserWidget User Guide
## Professional VFX Media Review Interface for Open RV

### Overview

The MediaBrowserWidget provides a professional, xStudio-inspired media review interface integrated with Open RV. It features a three-panel layout optimized for VFX workflows with advanced media browsing, annotation, and timeline capabilities.

### Interface Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Navigation Toolbar                                          │
├─────────────┬─────────────────────────────┬─────────────────┤
│ Search &    │        Media Grid           │ Comments &      │
│ Navigate    │                             │ Annotations     │
│ (Left)      │        (Center)             │    (Right)      │
│             │                             │                 │
├─────────────┴─────────────────────────────┴─────────────────┤
│                Timeline Sequence (Bottom)                   │
└─────────────────────────────────────────────────────────────┘
```

### Getting Started

#### Installation
1. Ensure Open RV is built at `c:/OpenRv/_build/stage/app/`
2. Run the installation script: `python scripts/install_rv_package.py`
3. Launch Open RV: `c:/OpenRv/_build/stage/app/bin/rv.exe`

#### Opening the Media Browser
- **Menu**: Tools > Media Browser > Show Browser
- **Keyboard**: `Ctrl+B` (toggle)
- **First Time**: The browser will open as a floating window

### Panel Features

#### Search & Navigate Panel (Left)
- **Search Field**: Real-time file and folder search with 300ms debounce
- **Quick Filters**: Toggle visibility for Images, Videos, and Sequences
- **Directory Tree**: Hierarchical navigation with expand/collapse
- **File Type Detection**: Automatic recognition of VFX formats (EXR, DPX, MOV, etc.)

#### Media Grid Panel (Center)
- **Thumbnail View**: 128x128px thumbnails (scalable 64-256px)
- **View Modes**: Grid, List, and Detail views
- **Multi-Selection**: Ctrl+click and Shift+click support
- **File Filtering**: Filter by All Files, Images, Sequences, or Videos
- **Sequence Detection**: Automatic grouping of image sequences

#### Comments & Annotations Panel (Right)
- **Comment List**: Scrollable list of frame-specific comments
- **Add Comments**: Text input for new annotations
- **Drawing Tools**: Text, Circle, Rectangle, and Arrow tools
- **Export Options**: Save annotations as JSON, XML, or FBX

#### Timeline Sequence Panel (Bottom)
- **Playback Controls**: Play/Pause/Stop with visual feedback
- **Frame Navigation**: Previous/Next frame buttons
- **Frame Counter**: Direct frame number input and timecode display
- **Playback Speed**: Adjustable speed (0.25x to 4x)
- **Timeline Track**: Visual representation with frame thumbnails
- **Annotation Markers**: Visual indicators for comments on timeline

### Keyboard Shortcuts

#### Global Shortcuts
- `Ctrl+B`: Toggle Media Browser visibility
- `F5`: Refresh current directory
- `Ctrl+L`: Load selected media in Open RV
- `Ctrl+Shift+L`: Add selected media to playlist

#### Timeline Controls
- `Space`: Play/Pause timeline
- `Left Arrow`: Previous frame
- `Right Arrow`: Next frame
- `Home`: Go to first frame
- `End`: Go to last frame

#### Navigation
- `Alt+Left`: Navigate back in history
- `Alt+Right`: Navigate forward in history
- `Alt+Up`: Go up one directory level

#### Selection
- `Ctrl+Click`: Multi-select files
- `Shift+Click`: Range select files
- `Ctrl+A`: Select all visible files
- `Escape`: Clear selection

### Supported File Formats

#### Image Formats
- **EXR**: OpenEXR high dynamic range
- **DPX**: Digital Picture Exchange
- **TIFF/TIF**: Tagged Image File Format
- **PNG**: Portable Network Graphics
- **JPG/JPEG**: Joint Photographic Experts Group
- **HDR**: High Dynamic Range
- **PIC, SGI, IFF, PSD, BMP, TGA, CIN, PPM**: Additional formats

#### Video Formats
- **MOV**: QuickTime Movie
- **MP4**: MPEG-4 Video
- **AVI**: Audio Video Interleave
- **MKV**: Matroska Video
- **MXF**: Material Exchange Format
- **R3D**: RED Digital Cinema
- **BRAW**: Blackmagic RAW

#### Sequence Detection
Automatically detects and groups image sequences with patterns:
- `filename.1001.exr` (frame.number.extension)
- `filename_1001.exr` (frame_number.extension)
- `filename1001.exr` (framenumber.extension)

### Workflow Integration

#### Loading Media in Open RV
1. **Single Selection**: Click a file and press `Ctrl+L` or double-click
2. **Multiple Selection**: Select multiple files and press `Ctrl+L`
3. **Sequence Loading**: Select any frame from a sequence - entire sequence loads
4. **Playlist Addition**: Use `Ctrl+Shift+L` to add to existing playlist

#### Annotation Workflow
1. **Navigate** to desired frame using timeline controls
2. **Add Comment** using the text input in the annotations panel
3. **Use Drawing Tools** to mark specific areas
4. **Export Annotations** in preferred format (JSON/XML/FBX)

#### Search and Filter Workflow
1. **Type** in search field to filter files in real-time
2. **Use Quick Filters** to show only specific file types
3. **Navigate Directories** using the tree view or path field
4. **Bookmark Locations** by adding to favorites (future feature)

### Performance Features

#### Thumbnail Generation
- **Threaded Processing**: 4 worker threads for smooth performance
- **Smart Caching**: LRU cache with 1000 thumbnail limit
- **Lazy Loading**: Thumbnails generated on-demand
- **Format Optimization**: Platform-specific thumbnail formats

#### Memory Management
- **Cache Cleanup**: Automatic cleanup when cache exceeds limits
- **Batch Loading**: Files loaded in batches of 50
- **Debounced Search**: 300ms delay prevents excessive filtering

### Troubleshooting

#### Common Issues
1. **Browser Not Appearing**: Check Tools menu, try `Ctrl+B`
2. **Slow Thumbnail Loading**: Reduce thumbnail size or clear cache
3. **Files Not Loading**: Verify file permissions and format support
4. **Menu Missing**: Ensure package is properly installed

#### Performance Tips
- Use smaller thumbnail sizes for large directories
- Enable file type filters to reduce visible items
- Close browser when not needed to free memory
- Regular cache cleanup for optimal performance

### Advanced Features

#### Studio Integration
- **Asset Connector**: Integration with studio asset management systems
- **Metadata Parser**: Extraction of technical metadata from media files
- **Color Space Awareness**: Integration with Open RV's color management

#### Customization
- **Theme Customization**: Modify colors and styling in configuration
- **Shortcut Remapping**: Customize keyboard shortcuts
- **Panel Layout**: Adjust panel sizes and positions

### Support and Development

#### Logging
- Log files located in Open RV's standard logging directory
- Debug mode available for troubleshooting
- Performance metrics tracked for optimization

#### Future Enhancements
- Enhanced sequence detection algorithms
- Advanced annotation tools (shapes, measurements)
- Integration with external review systems
- Collaborative annotation features
- Custom thumbnail generators for specialized formats

For technical support or feature requests, contact the Monto-openRv development team.
