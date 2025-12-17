# Horus VFX Review Application - Release 0.1.0-dev

**Release Date:** 2025-12-15
**Status:** Development Preview
**Build:** Initial Release

---

## 🎯 Overview

Horus is a professional VFX review and collaboration tool built on Open RV, featuring an integrated media browser, annotation system, and playlist management for production workflows.

---

## ✨ Key Features

### 🎬 **Open RV Integration**
- **Three Modular Dock Widgets**: Search & Media Library, Comments & Annotations, Timeline Playlist
- **Native RV Styling**: Professional dark theme matching Open RV's interface
- **Direct Media Loading**: Click-to-load media files into RV sessions
- **Dockable Panels**: Flexible workspace organization

### 📊 **Media Library Widget**
- **Project Selection**: Browse and switch between multiple projects
- **Hierarchical Navigation**: Episode → Sequence → Shot structure
- **Media Grid View**: Thumbnail-based media browsing with metadata
- **File Type Filters**: Filter by images, videos, sequences
- **Search Functionality**: Quick search across media files
- **Status Indicators**: Visual approval status (approved, pending, in_review)

### 💬 **Comments & Annotations Widget**
- **Frame-Accurate Comments**: Link comments to specific frames/timecodes
- **Threaded Discussions**: Reply to comments with visual threading
- **User Mentions**: @username support with autocomplete
- **Emoji Reactions**: Quick feedback without full comments
- **Drawing Tools**: Paint mode integration for visual annotations
- **Annotations Popup**: Dedicated window for detailed annotation management
- **Status Tracking**: Open, in progress, resolved states
- **Priority Levels**: High, medium, low priority indicators

### 📽️ **Timeline Playlist Widget**
- **Playlist Management**: Create and manage review playlists (dailies, weeklies)
- **Drag & Drop**: Easy playlist item reordering
- **Version Comparison**: Compare multiple versions side-by-side
- **Batch Operations**: Add multiple shots to playlists
- **Playlist Export**: Export playlists for external review
- **Auto-Load**: Automatically load playlist items into RV
- **Metadata Display**: Shot info, version, status, duration

### 🗄️ **Database Integration**
- **JSON Database**: Lightweight file-based data storage
- **Project Configs**: Hierarchical project structure definitions
- **Media Records**: Comprehensive media metadata tracking
- **Annotations Storage**: Persistent comment and annotation data
- **Playlist Data**: Saved playlists with item ordering
- **Real-Time Sync**: Live data updates across widgets

---

## 🚀 Installation & Usage

### **Quick Start**

1. **Extract the release package**
   ```
   horus-0.1.0-dev-windows.zip
   ```

2. **Launch Horus-RV**
   - Double-click `horus-rv.exe`
   - Or run from command line: `horus-rv.exe`

3. **First Launch**
   - Horus will automatically detect Open RV installation
   - Sample database included for testing

### **System Requirements**

- **Operating System**: Windows 10/11 (64-bit)
- **Open RV**: Version 2.0+ installed at one of these locations:
  - `D:\Program Files\stage\app\bin\rv.exe` (Test path - Priority)
  - `C:\OpenRv\_build\stage\app\bin\rv.exe`
  - `C:\OpenRV\bin\rv.exe`
  - `C:\Program Files\OpenRV\bin\rv.exe`
- **Python**: 3.7+ (bundled with Open RV)
- **Disk Space**: 50MB minimum

### **Configuration**

Horus uses a JSON database located in:
- `sample_db/` directory (included in release)
- Custom database path can be configured in future releases

---

## 📦 What's Included

### **Executables**
- `horus-rv.exe` - Main launcher executable (PyInstaller bundled)

### **Database Files**
- `sample_db/project_configs.json` - Sample project configurations
- `sample_db/media_records.json` - Sample media metadata
- `sample_db/annotations.json` - Sample annotations and comments
- `sample_db/tasks.json` - Sample task definitions
- `sample_db/horus_playlists.json` - Sample playlists

### **Documentation**
- `docs/horus_api_quick_reference.md` - API documentation
- `docs/horus_application_architecture.md` - Architecture overview
- `docs/horus_data_model_design.md` - Database schema
- `docs/horus_implementation_guide.md` - Implementation details
- `docs/user-guide.md` - User guide

### **Configuration Files**
- `version.json` - Version information
- `swa_project_config.json` - SWA project example

---

## 🎨 User Interface

### **Layout**
```
┌─────────────────────────────────────────────────────────────┐
│                    Open RV Viewport                         │
│                  (Media Playback Area)                      │
└─────────────────────────────────────────────────────────────┘
┌──────────────────┬──────────────────┬──────────────────────┐
│  Search & Media  │   Comments &     │   Timeline Playlist  │
│     Library      │   Annotations    │                      │
├──────────────────┼──────────────────┼──────────────────────┤
│ • Project Select │ • Frame Comments │ • Playlist Manager   │
│ • Directory Tree │ • Threaded Reply │ • Drag & Drop        │
│ • Media Grid     │ • Annotations    │ • Version Compare    │
│ • File Filters   │ • Paint Mode     │ • Auto-Load          │
└──────────────────┴──────────────────┴──────────────────────┘
```

### **Color Scheme**
- **Background**: `#3a3a3a` (Dark gray)
- **Text**: `#e0e0e0` (Light gray)
- **Highlight**: `#0078d7` (Blue)
- **Buttons**: `#4a4a4a` (Medium gray)
- **Borders**: `#555555` (Border gray)

---

## 🔧 Technical Details

### **Architecture**
- **Framework**: PySide2 (Qt for Python)
- **Integration**: Open RV Python API
- **Database**: JSON file-based storage
- **Build Tool**: PyInstaller (single executable)

### **Key Components**
- `horus_rv_launcher.py` - Main launcher script
- `rv_horus_integration.py` - RV integration and UI widgets
- `src/packages/media_browser/` - Media browser package
- `horus_data_connector.py` - Database connector

---

## 🐛 Known Issues

### **Current Limitations**
1. **Database Path**: Currently hardcoded to `sample_db/` directory
2. **Windows Only**: Linux/macOS support planned for future releases
3. **Single User**: Multi-user collaboration not yet implemented
4. **File Watching**: Real-time file system monitoring not implemented
5. **OCIO Config**: Color management configuration not yet integrated

### **Workarounds**
- Use provided sample database for testing
- Manual refresh required for database updates
- Single workstation usage recommended

---

## 🔮 Roadmap

### **Phase 2: Enhanced Features** (Planned)
- [ ] First-time setup wizard (RV path, project root, OCIO config)
- [ ] User configuration storage (`~/.horus/config.json`)
- [ ] Multi-project support with project switching
- [ ] Real-time file system monitoring (Watchdog)
- [ ] REST API server for multi-user collaboration

### **Phase 3: Production Features** (Future)
- [ ] Linux/macOS support
- [ ] PostgreSQL database backend
- [ ] ShotGrid/ftrack integration
- [ ] LLM-powered project structure analysis
- [ ] Advanced annotation tools (shapes, arrows, text)
- [ ] Video export with annotations

---

## 📝 Release Notes

### **Version 0.1.0-dev** (2025-12-15)

#### ✨ New Features
- Initial release of Horus VFX Review Application
- Three-widget modular interface for Open RV
- Media library with project/episode/sequence/shot hierarchy
- Comments and annotations system with threading
- Timeline playlist management with drag & drop
- JSON database integration for metadata storage
- Sample database with demo projects included
- PyInstaller executable for easy deployment

#### 🔧 Configuration Changes
- Added test RV path: `D:\Program Files\stage\app\bin\rv.exe` (Priority)
- Updated launcher to check test path first
- Sample database included in release package

#### 📚 Documentation
- Added comprehensive API documentation
- Added architecture and data model documentation
- Added implementation guide
- Added user guide

#### 🐛 Bug Fixes
- Fixed git repository ownership detection
- Fixed PyInstaller resource path handling
- Fixed widget docking and layout issues

---

## 👥 Contributors

- **Katha Nab** - Lead Developer
- **Horus Development Team**

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🔗 Links

- **Repository**: https://github.com/katha-begin/Horus.git
- **Issues**: https://github.com/katha-begin/Horus/issues
- **Documentation**: https://github.com/katha-begin/Horus/tree/main/docs

---

## 💬 Support

For questions, issues, or feature requests:
1. Check the documentation in `docs/` directory
2. Open an issue on GitHub
3. Contact the development team

---

**Thank you for using Horus VFX Review Application!** 🎬

