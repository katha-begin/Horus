# Horus-RV Launcher

## 🎬 **horus-rv.exe** - One-Click Launch for Open RV with Horus Integration

### Quick Start

**Simply double-click `horus-rv.exe` to launch Open RV with Horus MediaBrowser integration!**

### What It Does

The `horus-rv.exe` executable automatically:

1. **Finds Open RV** - Searches for Open RV installation
2. **Locates Project** - Finds the Horus project directory
3. **Checks Horus Database** - Verifies Horus data availability
4. **Launches Integration** - Starts Open RV with MediaBrowser dock widgets

### Usage Options

#### Option 1: Executable (Recommended)
```bash
# Double-click in Windows Explorer
horus-rv.exe

# Or from command line
./dist/horus-rv.exe
```

#### Option 2: Batch File (Backup)
```bash
# Double-click in Windows Explorer
horus-rv.bat

# Or from command line
horus-rv.bat
```

#### Option 3: Python Script (Development)
```bash
# Direct Python execution
python horus_rv_launcher.py
```

### Requirements

- **Open RV** installed at one of these locations:
  - `C:\OpenRv\_build\stage\app\bin\rv.exe`
  - `C:\OpenRV\bin\rv.exe`
  - `C:\Program Files\OpenRV\bin\rv.exe`
  - `C:\Program Files (x86)\OpenRV\bin\rv.exe`

- **Horus Project** with `rv_horus_integration.py` at:
  - `C:\Users\ADMIN\Documents\augment-projects\Horus\`
  - Same directory as `horus-rv.exe`
  - Current working directory

- **Horus Database** (optional) at:
  - `C:\Users\ADMIN\Documents\dev\Montu\data\json_db\`

### Troubleshooting

#### "Open RV not found"
1. **Install Open RV** at one of the supported locations
2. **Check installation path** matches expected locations
3. **Verify rv.exe exists** and is executable

#### "Project directory not found"
1. **Ensure rv_horus_integration.py exists** in project directory
2. **Check current working directory** contains the integration script
3. **Verify file permissions** allow reading the script

#### "Horus database not found"
1. **Install Horus** at the expected location
2. **Check database files exist** in `data\json_db\`
3. **Verify JSON files** are readable and properly formatted

**Note:** MediaBrowser will work in filesystem-only mode without Horus database

#### "Launch failed"
1. **Check Open RV installation** is complete and functional
2. **Verify Python environment** supports PySide2
3. **Test integration script** manually: `python rv_horus_integration.py`

4. **Use Fallback Methods**
   - Try `horus-rv.bat`
   - Use the original command line method

### File Structure

```
Horus/
├── horus-rv.exe                 # Main executable launcher
├── horus-rv.bat                 # Batch file launcher
├── rv_horus_integration.py      # Integration script
├── dist/
│   └── horus-rv.exe            # Built executable
└── src/packages/media_browser/  # MediaBrowser package
```

### Building from Source

To rebuild the executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
python -m PyInstaller --onefile --name horus-rv --console horus_rv_launcher.py

# Result will be in dist/horus-rv.exe
```

---

## 🎉 **Ready to Use!**

The Horus-RV launcher provides the easiest way to get started with Open RV and Horus MediaBrowser integration. Just double-click and start reviewing your media!
