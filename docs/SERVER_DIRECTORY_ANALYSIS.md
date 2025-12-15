# Server Directory Structure Analysis
## SWA Project on Remote Server (10.100.128.193)

**Date:** 2025-12-15  
**Project:** Horus VFX Review Application  
**Server:** ec2-user@10.100.128.193  

---

## 📁 **Directory Structure Overview**

### **Mount Points:**
- **Project Root (Movies):** `/mnt/igloo_swa_v/`
- **Image Root (Sequences):** `/mnt/igloo_swa_w/`

### **Project Structure:**
```
/mnt/igloo_swa_v/SWA/all/scene/
├── Ep01/                    # Episode 1
├── Ep02/                    # Episode 2 (analyzed)
│   ├── Media/              # Media assets
│   ├── Sequences/          # Editorial sequences
│   ├── sq0010/             # Sequence 0010
│   │   ├── SH0010/         # Shot 0010
│   │   │   ├── .Ep02_sq0010_SH0010.json  # Shot metadata
│   │   │   ├── anim/       # Animation department
│   │   │   │   ├── output/ # Movie outputs
│   │   │   │   └── version/# Work files
│   │   │   ├── comp/       # Compositing department
│   │   │   │   ├── output/ # Movie outputs (.mov)
│   │   │   │   ├── version/# Nuke scripts (.nk)
│   │   │   │   └── farm/   # Farm render files
│   │   │   ├── lighting/   # Lighting department
│   │   │   ├── layout/     # Layout department
│   │   │   └── hero/       # Hero assets
│   │   ├── SH0020/
│   │   └── SH0030/
│   ├── sq0020/
│   └── sq0030/
├── Ep03/
└── Ep04/

/mnt/igloo_swa_w/SWA/all/scene/
└── Ep02/
    └── sq0010/
        └── SH0010/
            └── comp/
                └── version/
                    ├── v001/  # EXR image sequences
                    ├── v002/
                    ├── v003/
                    ├── v006/
                    └── v007/
```

---

## 🎬 **File Naming Conventions**

### **Movie Files (.mov):**
**Location:** `{project_root}/{project}/all/scene/{episode}/{sequence}/{shot}/{department}/output/`

**Pattern:** `{Episode}_{Sequence}_{Shot}_{Version}.mov`

**Examples:**
- `Ep02_sq0010_SH0010_v006.mov` (40MB)
- `Ep02_sq0010_SH0010_v007.mov` (41MB)
- `Ep02_sq0010_SH0020_v004.mov` (32MB)

**Animation Department Variations:**
- `Ep02_sq0010_SH0010_anim_blocking_v002.mov`
- `Ep02_sq0010_SH0010_anim_playtex_v001.mov`
- `Ep02_sq0010_SH0010_anim_polish_v001.mov`
- `Ep02_sq0010_SH0010_anim_retime_v001.mov`
- `Ep02_sq0010_SH0010_anim_spline_v001.mov`

### **Image Sequences (.exr):**
**Location:** `{image_root}/{project}/all/scene/{episode}/{sequence}/{shot}/{department}/version/{version}/`

**Pattern:** `{Episode}_{Sequence}_{Shot}.{frame}.exr`

**Examples:**
- `Ep02_sq0010_SH0010.1001.exr` (359KB)
- `Ep02_sq0010_SH0010.1002.exr`
- `Ep02_sq0010_SH0010.1043.exr` (6.3MB)
- `Ep02_sq0010_SH0010_test.1001.exr` (374KB)

**Frame Range:** 1001-1043 (43 frames)

### **Work Files (.nk - Nuke Scripts):**
**Location:** `{project_root}/{project}/all/scene/{episode}/{sequence}/{shot}/{department}/version/`

**Pattern:** `{Episode}_{Sequence}_{Shot}_{Department}_{Version}.nk`

**Examples:**
- `Ep02_sq0010_SH0010_comp_v001.nk` (261KB)
- `Ep02_sq0010_SH0010_comp_v007.nk` (287KB)
- `Ep02_sq0010_SH0010_comp_test.nk` (244KB)

---

## 📊 **Shot Metadata JSON Structure**

**File:** `.Ep02_sq0010_SH0010.json` (hidden file in shot directory)

```json
{
  "metadata": {
    "maya_version": "2022",
    "scene_file": "V:/SWA/all/scene/Ep02/sq0010/SH0010/lighting/version/Ep02_sq0010_SH0010_lighting_master_v007.ma",
    "shot_node": "SWA_Ep02_SH0010_tab",
    "show_code": "SWA"
  },
  "shot_info": {
    "episode": "Ep02",
    "sequence": "sq0010",
    "shot": "SH0010",
    "shot_name": "SWA_Ep02_SH0010_tab",
    "start_frame": 1001,
    "end_frame": 1043,
    "frame_count": 43,
    "version": "v007"
  },
  "shot_attributes": {
    "sequenceStartFrame": 1001.0,
    "sequenceEndFrame": 1043.0,
    "preHold": 0.0,
    "postHold": 0.0,
    "clipDuration": 0.0,
    "scale": 1.0
  }
}
```

---

## 🏢 **Department Structure**

| Department | Has Output | Has Version | File Types |
|------------|-----------|-------------|------------|
| **anim** | ✅ Yes | ✅ Yes | .mov (multiple stages) |
| **comp** | ✅ Yes | ✅ Yes | .mov, .nk, .exr sequences |
| **lighting** | ❌ No | ✅ Yes | .ma (Maya scenes) |
| **layout** | ⚠️ Unknown | ✅ Yes | - |
| **hero** | ⚠️ Unknown | ❌ No | - |

---

## 📈 **Statistics (Ep02/sq0010/SH0010)**

### **Episodes:** 4 (Ep01, Ep02, Ep03, Ep04, RD00)
### **Sequences in Ep02:** 18 (sq0010 - sq0180)
### **Shots in sq0010:** 9 (SH0010 - SH0090)

### **Comp Department (SH0010):**
- **Movie Versions:** v006, v007 (2 files, ~81MB total)
- **EXR Versions:** v001, v002, v003, v006, v007 (5 versions)
- **Nuke Scripts:** v001-v007 (7 versions + test files)
- **Frame Range:** 1001-1043 (43 frames)

### **Anim Department (SH0010):**
- **Movie Files:** 20+ files across multiple stages
- **Stages:** blocking, playtex, polish, retime, spline
- **Total Size:** ~21MB


