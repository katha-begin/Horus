# 🦅 Horus Web Player

## OpenRV-Inspired VFX Review System for the Web

A professional web-based video player inspired by OpenRV, designed for VFX artists, animators, and production teams to review media with frame-accurate playback, annotation tools, and color management capabilities.

---

## ✨ Features

### 🎬 Professional Playback Controls
- **Frame-Accurate Navigation**: Step forward/backward frame by frame
- **Variable Playback Speed**: 0.25x to 2x speed control
- **Loop Mode**: Seamless looping for review cycles
- **Configurable FPS**: Support for any frame rate (1-120 FPS)
- **Timecode Display**: Professional SMPTE timecode (HH:MM:SS:FF)

### 🎯 Timeline & Scrubbing
- **Interactive Timeline**: Click or drag to scrub through media
- **Timeline Markers**: Add and navigate to specific frames (press 'M')
- **Visual Progress Bar**: Real-time playback progress indication
- **Ruler Marks**: Time markers for easy navigation

### 🖊️ Annotation System
- **Drawing Tools**:
  - ✏️ Pen Tool (P) - Freehand drawing
  - ➤ Arrow Tool (A) - Directional annotations
  - ▭ Rectangle Tool (R) - Area highlighting
  - ○ Circle Tool (C) - Circular annotations
  - T Text Tool (T) - Text labels
- **Frame-Accurate Annotations**: Annotations tied to specific frames
- **Color Picker**: Customizable annotation colors
- **Export/Import**: Save and load annotations as JSON
- **Annotation List**: View and navigate all annotations

### 🎨 Color Management
- **Brightness Control**: -100 to +100 adjustment
- **Contrast Control**: -100 to +100 adjustment
- **Saturation Control**: -100 to +100 adjustment
- **Exposure Control**: -2 to +2 stops
- **Real-Time Preview**: Instant color adjustments
- **Reset Function**: Quick return to default settings

### 🖼️ Image Sequence Support
- **Multi-Frame Loading**: Load entire image sequences
- **Format Support**: PNG, JPG, and other web-compatible formats
- **Frame-by-Frame Playback**: Professional sequence review
- **Automatic Sorting**: Intelligent frame ordering
- **Single Image Support**: Display static images

### 💅 Professional UI
- **Dark Theme**: VFX industry-standard interface
- **Responsive Design**: Adapts to different screen sizes
- **Keyboard Shortcuts**: Efficient workflow navigation
- **Drag & Drop**: Easy media loading
- **Status Bar**: Real-time feedback and information

---

## 🚀 Getting Started

### Quick Start

1. **Open the Player**
   ```bash
   # Simply open index.html in a modern web browser
   # Or serve with a local web server:
   python -m http.server 8000
   # Then navigate to http://localhost:8000
   ```

2. **Load Media**
   - Click "📁 Load Media" button
   - Or drag and drop video/image files onto the player
   - For image sequences: select multiple files at once

3. **Start Reviewing**
   - Use transport controls or keyboard shortcuts
   - Add annotations as needed
   - Adjust color settings in real-time

---

## ⌨️ Keyboard Shortcuts

### Playback Controls
| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `←` | Previous Frame |
| `→` | Next Frame |
| `Home` | First Frame |
| `End` | Last Frame |
| `L` | Toggle Loop |
| `M` | Add Marker |

### Annotation Tools
| Key | Tool |
|-----|------|
| `V` | Select Tool |
| `P` | Pen Tool |
| `A` | Arrow Tool |
| `R` | Rectangle Tool |
| `C` | Circle Tool |
| `T` | Text Tool |

---

## 📁 Project Structure

```
web-player/
├── index.html              # Main HTML file
├── css/
│   └── player.css         # Professional dark theme styles
├── js/
│   ├── player.js          # Core player functionality
│   ├── timeline.js        # Timeline and scrubbing
│   ├── annotations.js     # Annotation system
│   ├── color-management.js # Color grading controls
│   └── image-sequence.js  # Image sequence support
├── assets/                # (Future: thumbnails, icons)
└── README.md             # This file
```

---

## 🎯 Use Cases

### Daily Review Sessions
- Load dailies and rushes for team review
- Add frame-specific notes and annotations
- Adjust color for consistent viewing
- Export annotations for production tracking

### VFX Shot Review
- Frame-by-frame analysis of VFX shots
- Color-accurate review with exposure controls
- Annotation for artist feedback
- Timeline markers for key frames

### Animation Review
- Playback control for timing analysis
- Frame stepping for pose review
- Drawing tools for director notes
- Loop mode for motion studies

### Client Presentations
- Professional playback interface
- Clean, distraction-free viewing
- Real-time color adjustments
- Export annotations for approval

---

## 🔧 Technical Details

### Browser Requirements
- **Recommended**: Chrome 90+, Firefox 88+, Edge 90+, Safari 14+
- **HTML5 Video**: Required for video playback
- **Canvas API**: Required for annotations and sequences
- **ES6 Support**: Modern JavaScript features

### Supported Formats

**Video Formats**:
- MP4 (H.264, H.265)
- WebM (VP8, VP9)
- OGG (Theora)
- MOV (browser-dependent)

**Image Formats**:
- PNG
- JPG/JPEG
- WebP
- GIF
- BMP

### Performance Notes
- **4K Playback**: Dependent on browser and hardware capabilities
- **Image Sequences**: Limited by browser memory (recommended < 1000 frames)
- **Annotations**: Lightweight, minimal performance impact
- **Color Grading**: Hardware-accelerated CSS filters

---

## 🎨 OpenRV Feature Comparison

| Feature | OpenRV | Horus Web Player |
|---------|--------|------------------|
| Frame-Accurate Playback | ✅ | ✅ |
| Timeline Scrubbing | ✅ | ✅ |
| Variable Speed | ✅ | ✅ |
| Annotations | ✅ | ✅ |
| Color Management | ✅ (Full OCIO) | ✅ (Basic) |
| Image Sequences | ✅ | ✅ |
| LUT Support | ✅ | ⏳ (Future) |
| Stereo 3D | ✅ | ❌ |
| Multi-Source | ✅ | ❌ |
| Web-Based | ❌ | ✅ |
| No Installation | ❌ | ✅ |

---

## 🔮 Future Enhancements

### Planned Features
- [ ] WebGL-based 3D LUT support
- [ ] CDL (Color Decision List) support
- [ ] Multi-source comparison (A/B split, wipe)
- [ ] Advanced timeline editing
- [ ] Audio waveform visualization
- [ ] Cloud storage integration
- [ ] Real-time collaboration
- [ ] Custom keyboard mapping
- [ ] Session save/restore
- [ ] Thumbnail generation

### Advanced Color Management
- [ ] OpenColorIO.js integration
- [ ] Custom LUT loading (.cube, .3dl)
- [ ] Look management
- [ ] Color space conversion
- [ ] HDR support

---

## 📊 Integration with Horus

This web player complements the main Horus project:

- **Horus Desktop**: OpenRV Python integration for studio pipelines
- **Horus Web Player**: Browser-based review for remote work
- **Shared Annotations**: Compatible JSON format
- **Unified Workflow**: Consistent user experience

---

## 🤝 Contributing

### Development Setup

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd Horus/web-player
   ```

2. Serve locally
   ```bash
   python -m http.server 8000
   ```

3. Open in browser
   ```
   http://localhost:8000
   ```

### Code Style
- Clean, readable JavaScript (ES6+)
- Google Style docstrings
- Modular architecture
- Progressive enhancement

---

## 📝 Annotation Format

Annotations are exported in JSON format:

```json
{
  "version": "1.0",
  "fps": 24,
  "annotations": {
    "120": [
      {
        "type": "arrow",
        "start": {"x": 100, "y": 150},
        "end": {"x": 200, "y": 250},
        "color": "#ff0000",
        "frame": 120
      }
    ]
  }
}
```

---

## 🐛 Troubleshooting

### Video Won't Play
- Check browser compatibility
- Verify video codec support
- Try different file format
- Check browser console for errors

### Annotations Not Saving
- Ensure annotations are added before exporting
- Check browser console for errors
- Try clearing browser cache

### Poor Performance
- Reduce video resolution
- Close other browser tabs
- Update graphics drivers
- Try a different browser

### Image Sequence Issues
- Ensure files are named sequentially
- Check file format compatibility
- Reduce number of frames if memory issues
- Verify all files are valid images

---

## 📄 License

Part of the Horus VFX Review Application project.

---

## 🙏 Credits

Inspired by [OpenRV](https://github.com/AcademySoftwareFoundation/OpenRV) from the Academy Software Foundation.

Built as a web-based companion to professional VFX review workflows.

---

## 📞 Support

For issues and feature requests, please use the main Horus project issue tracker.

---

**Ready to review? Load your media and start creating!** 🎬
