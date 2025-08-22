# Horus Database Integration Documentation
## Data Access Strategy and Architecture

**Project:** Horus  
**Version:** 2.0  
**Date:** 2025-08-22  
**Status:** Current Implementation

---

## 1. Database Integration Strategy

### 1.1 Primary Data Source: Montu API

**Horus uses the existing Montu API for all data access operations.**

The Horus application is designed to integrate with the Montu project management system by:

1. **Reading from Montu's JSON database** located at `C:\Users\ADMIN\Documents\dev\Montu\data\json_db\`
2. **Using Montu's established data formats** and schema structures
3. **Leveraging Montu's existing API endpoints** when available
4. **Following Montu's MongoDB-compatible JSON format** for data consistency

### 1.2 Current Data Files

The following JSON files are currently used by Horus:

- **`project_configs.json`** - Project definitions and settings
- **`media_records.json`** - Media file metadata and references  
- **`tasks.json`** - Task definitions and assignments
- **`annotations.json`** - Comments and annotations data
- **`versions.json`** - Version control and history
- **`directory_operations.json`** - File system operations log

### 1.3 Data Access Pattern

```python
# Horus Data Connector Pattern
class HorusDataConnector:
    """
    Connects to Montu's JSON database for read-only access.
    Translates Montu data formats to Horus UI requirements.
    """
    
    def __init__(self):
        self.montu_data_path = Path(r"C:\Users\ADMIN\Documents\dev\Montu\data\json_db")
    
    def get_available_projects(self) -> List[Dict]:
        """Read projects from Montu's project_configs.json"""
        return self._load_json_file("project_configs.json")
    
    def get_media_for_project(self, project_id: str) -> List[Dict]:
        """Read media records from Montu's media_records.json"""
        return self._load_json_file("media_records.json")
```

---

## 2. Data Format Specifications

### 2.1 Montu JSON Schema Compliance

All data structures follow Montu's established MongoDB-compatible format:

**Project Configuration Format:**
```json
{
  "_id": "SWA",
  "name": "SWA",
  "description": "SWA Animation Project",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-08-22T00:00:00Z",
  "status": "active",
  "templates": {
    "shot_template": "V:/SWA/all/scene/{episode}/{sequence}/{shot}/{task}/version/",
    "render_template": "V:/SWA/all/render/{episode}/{sequence}/{shot}/{task}/version/"
  },
  "drive_mapping": {
    "project_root": "V:/SWA",
    "render_root": "V:/SWA/all/render"
  },
  "departments": ["animation", "lighting", "compositing", "fx"],
  "settings": {
    "frame_rate": 24,
    "resolution": "1920x1080",
    "color_space": "Rec709"
  }
}
```

**Media Records Format:**
```json
{
  "_id": "swa_ep00_sq0010_sh0020_lighting_v002",
  "project_id": "SWA",
  "file_name": "SWA_Ep00_SH0020_lighting_v002.exr",
  "file_path": "V:/SWA/all/scene/Ep00/sq0010/SH0020/lighting/version/SWA_Ep00_SH0020_lighting_v002.exr",
  "file_type": "image_sequence",
  "linked_task_id": "ep00_ep00_sq0010_ep00_sh0020_lighting",
  "version": "v002",
  "approval_status": "published",
  "author": "test_user",
  "created_at": "2025-08-05T20:36:24Z",
  "metadata": {
    "width": 1920,
    "height": 1080,
    "frame_rate": 24,
    "format": "OpenEXR",
    "frame_range": {
      "start": 1001,
      "end": 10153
    }
  }
}
```

**Task Definition Format:**
```json
{
  "_id": "ep00_ep00_sq0010_ep00_sh0020_lighting",
  "name": "Lighting - SWA Ep00 SH0020",
  "project_id": "SWA",
  "task_type": "lighting",
  "department": "lighting",
  "episode": "Ep00",
  "sequence": "SWA_Ep00_sq0010",
  "shot": "SWA_Ep00_SH0020",
  "assigned_to": "test_user",
  "status": "published",
  "priority": "medium",
  "frame_range": {
    "start": 1001,
    "end": 10153
  }
}
```

---

## 3. Future Data Requirements

### 3.1 API-First Approach

**For any additional data needs, Horus will:**

1. **Request new API endpoints from Montu** rather than creating custom schemas
2. **Wait for Montu to implement missing functionality** instead of duplicating data structures
3. **Use Montu's established patterns** for any temporary JSON data files
4. **Maintain compatibility** with Montu's MongoDB format

### 3.2 Temporary JSON Data Files

**If immediate data is needed before Montu API implementation:**

- Create JSON files following Montu's MongoDB format
- Place files in `/Montu/data/json_db/` directory
- Use Montu's `_id`, `_created_at`, `_updated_at` field conventions
- Follow Montu's project hierarchy and naming patterns

**Example temporary file structure:**
```json
[
  {
    "_id": "unique_identifier",
    "project_id": "SWA",
    "_created_at": "2025-08-22T00:00:00Z",
    "_updated_at": "2025-08-22T00:00:00Z",
    // ... additional fields following Montu patterns
  }
]
```

### 3.3 Integration Guidelines

**Data Access Principles:**
- **Read-only access** to Montu database
- **No direct database modifications** by Horus
- **Use Montu APIs** for any write operations
- **Cache data locally** only for performance optimization
- **Respect Montu's data ownership** and access patterns

---

## 4. Current Implementation Status

### 4.1 Working Data Sources

✅ **project_configs.json** - Project definitions  
✅ **media_records.json** - Media file metadata  
✅ **tasks.json** - Task definitions  
✅ **annotations.json** - Comments and annotations  
✅ **versions.json** - Version control data  

### 4.2 Data Connector Implementation

The `HorusDataConnector` class provides:
- Project listing and selection
- Media file discovery and metadata
- Task-based file organization
- Annotation and comment retrieval
- Version history access

### 4.3 Future Enhancements

**Pending Montu API Development:**
- Real-time data synchronization
- Write operations (comments, annotations)
- User authentication and permissions
- Advanced search and filtering
- Collaborative features

---

## 5. Conclusion

**Horus follows a strict integration pattern:**

1. **Use existing Montu API** for all data operations
2. **Follow Montu's data formats** and conventions
3. **Wait for Montu development** rather than creating custom solutions
4. **Maintain data consistency** with Montu's MongoDB patterns

This approach ensures long-term compatibility and reduces maintenance overhead while providing immediate functionality through Montu's existing JSON database structure.
