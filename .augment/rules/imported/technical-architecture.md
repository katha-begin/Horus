---
type: "always_apply"
---

# Technical Architecture Document
## Custom Open RV Studio Pipeline Integration

**Project:** Monto-openRv  
**Version:** 1.0  
**Date:** 2025-08-21  
**Status:** Phase 1 Architecture Design  

---

## 1. System Overview

### 1.1 Architecture Principles
**Core Design Philosophy:**
- **Modular Architecture:** Component-based design with clear separation of concerns
- **Cross-Platform Compatibility:** Consistent behavior across Windows, macOS, and Linux
- **Rez-Managed Dependencies:** All components managed through Rez package system
- **Open RV API Compliance:** Strict adherence to Open RV's documented APIs and patterns
- **Future Extensibility:** Well-defined integration points for studio pipeline tools

### 1.2 System Components
```
┌─────────────────────────────────────────────────────────────┐
│                    Studio Pipeline Layer                    │
├─────────────────────────────────────────────────────────────┤
│  ShotGrid  │  ftrack  │  RVSync  │  Slack  │  RocketChat   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Custom Open RV Application                 │
├─────────────────────────────────────────────────────────────┤
│  Media     │ Annotation │ Timeline  │ Enhanced │ Database   │
│  Browser   │  Tracker   │ Sequencer │   OCIO   │  Module    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Open RV Core Framework                   │
├─────────────────────────────────────────────────────────────┤
│  Qt UI     │  Python    │   GLSL    │  Session │  Package   │
│ Framework  │    API     │   Nodes   │ Manager  │  System    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Rez Package Management                     │
├─────────────────────────────────────────────────────────────┤
│ Dependency │ Environment │ Version  │  Build   │ Repository │
│ Resolution │   Isolation │ Control  │ System   │ Management │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 Technology Stack
**Core Technologies:**
- **Open RV 2.0+:** Base media review and playback framework
- **Python 3.7+:** Primary scripting and package development language
- **Qt 5.15+:** User interface framework and widget system
- **Rez 3.2.1+:** Package management and environment resolution
- **CMake 3.16+:** Cross-platform build system

**Supporting Libraries:**
- **OpenTimelineIO 0.15+:** Timeline and editorial data exchange
- **OpenColorIO 2.1+:** Color management and pipeline integration
- **OpenImageIO 2.3+:** Image format support and processing
- **FFmpeg 4.4+:** Media encoding and decoding
- **SQLite/PostgreSQL:** Database storage and metadata management

---

## 2. Component Architecture

### 2.1 Media Browser Package
**Purpose:** File system navigation and media asset management

**Technical Implementation:**
```python
# Package structure
media_browser/
├── package.py                 # Rez package definition
├── python/
│   ├── media_browser/
│   │   ├── __init__.py
│   │   ├── browser_widget.py  # Qt-based browser interface
│   │   ├── thumbnail_cache.py # Thumbnail generation and caching
│   │   ├── metadata_parser.py # Media metadata extraction
│   │   └── asset_connector.py # Studio asset management API
│   └── rv_integration/
│       └── media_browser_mode.py # Open RV mode integration
├── resources/
│   ├── icons/                 # UI icons and graphics
│   └── stylesheets/          # Qt stylesheets
└── tests/
    └── test_media_browser.py  # Unit tests
```

**Key APIs and Integration Points:**
- **RvFileIOManager:** File system operations and media detection
- **Open RV Property System:** Metadata storage and retrieval
- **Qt QTreeView/QListView:** File system navigation widgets
- **REST API Connector:** Studio asset management integration

**Future Extension Points:**
- **Asset Management Plugins:** ShotGrid, ftrack, custom systems
- **Cloud Storage Integration:** AWS S3, Google Cloud, Azure
- **Version Control Integration:** Perforce, Git LFS
- **Custom Metadata Extractors:** Studio-specific metadata formats

### 2.2 Comment and Annotation Tracker Package
**Purpose:** Frame-accurate commenting and visual annotation system

**Technical Implementation:**
```python
# Package structure
annotation_tracker/
├── package.py
├── python/
│   ├── annotation_tracker/
│   │   ├── __init__.py
│   │   ├── annotation_widget.py    # Main annotation interface
│   │   ├── drawing_tools.py        # Shape and text drawing tools
│   │   ├── comment_manager.py      # Comment storage and retrieval
│   │   ├── collaboration_sync.py   # Real-time collaboration
│   │   └── export_formats.py       # JSON, XML, FBX export
│   └── rv_integration/
│       ├── annotation_mode.py      # Open RV mode integration
│       └── glsl_overlays/          # Custom GLSL overlay nodes
│           ├── shape_overlay.glsl
│           ├── text_overlay.glsl
│           └── arrow_overlay.glsl
├── database/
│   ├── schema.sql                  # Database schema definition
│   └── migrations/                 # Database migration scripts
└── tests/
    └── test_annotations.py
```

**Key APIs and Integration Points:**
- **RvSession APIs:** Timeline coordinate system and frame tracking
- **Custom GLSL Nodes:** Overlay rendering (Reference Manual Chapter 3)
- **Open RV Event System:** Mouse and keyboard event handling
- **Database Layer:** SQLite/PostgreSQL for persistence
- **WebSocket API:** Real-time collaboration support

**Future Extension Points:**
- **Review System Integration:** Automated comment sync with ShotGrid/ftrack
- **AI-Powered Annotations:** Automatic object detection and tagging
- **Voice Annotations:** Audio comment recording and playback
- **Mobile App Integration:** Remote annotation via mobile devices

### 2.3 Timeline Sequencer with OTIO Integration Package
**Purpose:** Multi-track timeline editing with industry-standard data exchange

**Technical Implementation:**
```python
# Package structure
timeline_sequencer/
├── package.py
├── python/
│   ├── timeline_sequencer/
│   │   ├── __init__.py
│   │   ├── timeline_widget.py      # Custom Qt timeline widget
│   │   ├── track_manager.py        # Multi-track management
│   │   ├── edit_operations.py      # Cut, splice, trim operations
│   │   ├── otio_connector.py       # OpenTimelineIO integration
│   │   └── playback_sync.py        # Transport control sync
│   └── rv_integration/
│       ├── timeline_mode.py        # Open RV mode integration
│       └── sequence_builder.py     # RvSequenceGroup management
├── otio_adapters/
│   ├── custom_adapter.py           # Studio-specific OTIO adapters
│   └── metadata_adapter.py         # Custom metadata handling
└── tests/
    └── test_timeline.py
```

**Key APIs and Integration Points:**
- **RvSession and RvSequenceGroup:** Open RV sequence management
- **OpenTimelineIO Python API:** Timeline data import/export
- **Qt Custom Widgets:** Timeline visualization and interaction
- **Open RV Transport Controls:** Playback synchronization
- **Edit List Management:** Frame-accurate editing operations

**Future Extension Points:**
- **NLE Integration:** Avid, Premiere, Resolve timeline import
- **Conform Tools:** Automated sequence conforming
- **Color Pipeline Integration:** Shot-based color management
- **Audio Synchronization:** Multi-channel audio timeline support

### 2.4 Enhanced OpenColorIO Integration Package
**Purpose:** Advanced color management beyond Open RV's built-in OCIO support

**Technical Implementation:**
```python
# Package structure
enhanced_ocio/
├── package.py
├── python/
│   ├── enhanced_ocio/
│   │   ├── __init__.py
│   │   ├── color_manager.py        # Extended color space management
│   │   ├── lut_processor.py        # Real-time LUT application
│   │   ├── grading_tools.py        # Custom color grading interface
│   │   └── pipeline_config.py      # Studio color pipeline integration
│   └── rv_integration/
│       ├── color_mode.py           # Open RV color mode extension
│       └── glsl_color_nodes/       # Custom GLSL color processing
│           ├── lut_node.glsl
│           ├── cdl_node.glsl
│           └── grading_node.glsl
├── configs/
│   ├── studio_config.ocio          # Studio OCIO configuration
│   └── luts/                       # Studio LUT collection
└── tests/
    └── test_color_management.py
```

**Key APIs and Integration Points:**
- **OpenColorIO 2.1+ API:** Color space transformations and management
- **Open RV Color Pipeline:** Integration with existing color processing
- **Custom GLSL Nodes:** GPU-accelerated color processing
- **Qt Color Widgets:** Interactive color grading interface
- **Configuration Management:** Dynamic OCIO config loading

### 2.5 Database Connection Module with Montu Integration
**Purpose:** Asset tracking and metadata management with production data sync

**Technical Implementation:**
```python
# Package structure
database_module/
├── package.py
├── python/
│   ├── database_module/
│   │   ├── __init__.py
│   │   ├── connection_manager.py   # Database connection handling
│   │   ├── asset_tracker.py        # Asset metadata management
│   │   ├── user_sessions.py        # User session and preferences
│   │   ├── sync_manager.py         # Production data synchronization
│   │   └── montu_connector.py      # Montu project integration
│   └── rv_integration/
│       ├── database_mode.py        # Open RV database integration
│       └── preference_manager.py   # Hierarchical preferences extension
├── schemas/
│   ├── postgresql_schema.sql       # PostgreSQL database schema
│   ├── sqlite_schema.sql           # SQLite database schema
│   └── migrations/                 # Database migration scripts
├── api/
│   ├── rest_endpoints.py           # RESTful API implementation
│   └── websocket_handlers.py       # Real-time data sync
└── tests/
    └── test_database.py
```

**Key APIs and Integration Points:**
- **Montu Project Patterns:** Database architecture and ORM patterns
- **Open RV Hierarchical Preferences:** Preference storage extension
- **SQLAlchemy/Django ORM:** Database abstraction layer
- **RESTful API Framework:** Studio pipeline connectivity
- **WebSocket Support:** Real-time data synchronization

---

## 3. Rez Package Management Architecture

### 3.1 Package Organization Strategy
**Repository Structure:**
```
/studio/packages/
├── core/                           # Core Open RV packages
│   ├── openrv-2.0.0/              # Base Open RV installation
│   ├── openrv-2.0.1/              # Updated versions
│   └── openrv-dev/                # Development builds
├── ui_packages/                    # Custom UI components
│   ├── media_browser-1.0.0/
│   ├── annotation_tracker-1.0.0/
│   ├── timeline_sequencer-1.0.0/
│   ├── enhanced_ocio-1.0.0/
│   └── database_module-1.0.0/
├── dependencies/                   # Third-party dependencies
│   ├── qt-5.15.2/
│   ├── python-3.7.8/
│   ├── cmake-3.16.3/
│   ├── ffmpeg-4.4.0/
│   ├── opencolorio-2.1.0/
│   ├── openimageio-2.3.0/
│   └── opentimelineio-0.15.0/
└── suites/                         # Environment suites
    ├── openrv_dev/                 # Development environment
    ├── openrv_production/          # Production environment
    └── openrv_testing/             # Testing environment
```

### 3.2 Package Dependency Graph
```
openrv_studio_suite
├── openrv-2.0+
│   ├── qt-5.15+
│   ├── python-3.7+
│   ├── ffmpeg-4.4+
│   ├── opencolorio-2.1+
│   └── openimageio-2.3+
├── media_browser-1.0+
│   ├── openrv-2.0+
│   └── requests-2.25+
├── annotation_tracker-1.0+
│   ├── openrv-2.0+
│   ├── sqlalchemy-1.4+
│   └── websockets-8.1+
├── timeline_sequencer-1.0+
│   ├── openrv-2.0+
│   └── opentimelineio-0.15+
├── enhanced_ocio-1.0+
│   ├── openrv-2.0+
│   └── opencolorio-2.1+
└── database_module-1.0+
    ├── openrv-2.0+
    ├── sqlalchemy-1.4+
    └── psycopg2-2.8+
```

### 3.3 Build and Deployment Pipeline
**Automated Build Process:**
```yaml
# CI/CD Pipeline Configuration
stages:
  - dependency_resolution
  - cross_platform_build
  - testing
  - packaging
  - deployment

dependency_resolution:
  script:
    - rez-env cmake qt python -- rez-depends openrv
    - rez-env cmake qt python -- rez-test dependencies

cross_platform_build:
  parallel:
    matrix:
      - PLATFORM: [windows, linux, osx]
  script:
    - rez-env cmake qt python -- rez-build --install
    - rez-env openrv -- rez-test functionality

packaging:
  script:
    - rez-release --repository /studio/packages/production
    - rez-suite-create openrv_production
```

---

## 4. Integration Points and Extension Architecture

### 4.1 Studio Pipeline Integration Hooks
**ShotGrid Integration Points:**
```python
# Extension interface for ShotGrid integration
class ShotGridConnector:
    """Interface for ShotGrid API integration."""
    
    def get_shot_data(self, shot_id: str) -> Dict:
        """Retrieve shot metadata from ShotGrid."""
        pass
    
    def update_review_notes(self, shot_id: str, notes: List[Dict]) -> bool:
        """Upload review notes to ShotGrid."""
        pass
    
    def sync_media_versions(self, shot_id: str) -> List[Dict]:
        """Synchronize media versions with ShotGrid."""
        pass
```

**ftrack Integration Points:**
```python
# Extension interface for ftrack integration
class FtrackConnector:
    """Interface for ftrack API integration."""
    
    def get_task_data(self, task_id: str) -> Dict:
        """Retrieve task information from ftrack."""
        pass
    
    def create_review_session(self, project_id: str, media_list: List) -> str:
        """Create ftrack review session."""
        pass
    
    def publish_annotations(self, session_id: str, annotations: List) -> bool:
        """Publish annotations to ftrack review session."""
        pass
```

### 4.2 Communication System Integration
**Slack Integration Framework:**
```python
# Slack notification system
class SlackNotifier:
    """Slack integration for review notifications."""
    
    def send_review_notification(self, channel: str, shot_data: Dict) -> bool:
        """Send review notification to Slack channel."""
        pass
    
    def create_review_thread(self, channel: str, review_data: Dict) -> str:
        """Create threaded discussion for review."""
        pass
```

**RocketChat Integration Framework:**
```python
# RocketChat integration
class RocketChatConnector:
    """RocketChat integration for team communication."""
    
    def post_review_update(self, room: str, update_data: Dict) -> bool:
        """Post review updates to RocketChat room."""
        pass
    
    def create_review_channel(self, project: str, shot: str) -> str:
        """Create dedicated review channel."""
        pass
```

### 4.3 Plugin Architecture
**Plugin Interface Definition:**
```python
# Base plugin interface
class OpenRVPlugin:
    """Base class for Open RV plugins."""
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
    
    def initialize(self, rv_session) -> bool:
        """Initialize plugin with RV session."""
        pass
    
    def register_ui_components(self) -> List[Dict]:
        """Register UI components with Open RV."""
        pass
    
    def handle_events(self, event_type: str, event_data: Dict) -> bool:
        """Handle Open RV events."""
        pass
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources."""
        pass
```

---

## 5. Performance and Scalability Considerations

### 5.1 Performance Optimization Strategies
**Memory Management:**
- Lazy loading of UI components and media thumbnails
- Efficient caching strategies for metadata and thumbnails
- Memory pool management for large media files
- Garbage collection optimization for Python components

**GPU Acceleration:**
- GLSL shader optimization for overlay rendering
- GPU-accelerated color processing and LUT application
- Efficient texture management for media playback
- Parallel processing for thumbnail generation

**Network Optimization:**
- Asynchronous API calls for studio system integration
- Intelligent caching of remote data
- Compression for annotation and metadata sync
- Connection pooling for database operations

### 5.2 Scalability Architecture
**Horizontal Scaling:**
- Microservice architecture for database and API components
- Load balancing for multiple Open RV instances
- Distributed caching for shared metadata
- Message queue integration for asynchronous processing

**Vertical Scaling:**
- Multi-threading for I/O operations
- Process isolation for stability
- Resource monitoring and optimization
- Dynamic memory allocation

---

## 6. Security and Access Control

### 6.1 Security Framework
**Authentication and Authorization:**
- Integration with studio LDAP/Active Directory
- Role-based access control for features and data
- Secure API token management
- Session management and timeout handling

**Data Protection:**
- Encryption for sensitive metadata
- Secure communication protocols (HTTPS, WSS)
- Database access control and auditing
- File system permission management

### 6.2 Compliance and Auditing
**Audit Trail:**
- User action logging and tracking
- Change history for annotations and metadata
- Access logging for sensitive operations
- Compliance reporting and data retention

---

## 7. Testing and Quality Assurance Architecture

### 7.1 Testing Framework
**Unit Testing:**
- Comprehensive test coverage for all Python modules
- Mock objects for Open RV API interactions
- Automated test execution with CI/CD integration
- Performance regression testing

**Integration Testing:**
- Cross-platform compatibility testing
- API integration testing with mock services
- Database migration and schema testing
- UI automation testing with Qt Test Framework

### 7.2 Quality Metrics
**Code Quality:**
- PEP 8 compliance monitoring
- Code coverage reporting (target: 90%+)
- Static analysis and security scanning
- Documentation coverage and accuracy

**Performance Metrics:**
- Application startup time monitoring
- Memory usage profiling
- Network latency measurement
- UI responsiveness benchmarking

---

## 8. Deployment and Operations

### 8.1 Deployment Strategy
**Rez-Based Deployment:**
- Automated package building and testing
- Staged deployment (dev → staging → production)
- Rollback capabilities for failed deployments
- Environment-specific configuration management

**Cross-Platform Distribution:**
- Platform-specific package variants
- Automated installer generation
- Update mechanism and version management
- Dependency verification and resolution

### 8.2 Monitoring and Maintenance
**Application Monitoring:**
- Performance metrics collection
- Error tracking and alerting
- User activity analytics
- Resource utilization monitoring

**Maintenance Procedures:**
- Regular package updates and security patches
- Database maintenance and optimization
- Log rotation and cleanup
- Backup and disaster recovery procedures

This technical architecture provides a comprehensive foundation for the Custom Open RV Studio Pipeline Integration project, ensuring scalability, maintainability, and extensibility for future studio requirements.
