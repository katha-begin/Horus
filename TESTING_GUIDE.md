# Horus UI Testing Guide

**Version:** 0.1.0-dev  
**Date:** 2025-12-15  
**Purpose:** Quick UI verification and testing

---

## 🎯 Quick Test Checklist

### **Pre-Launch Verification**

- [ ] Open RV installed at: `D:\Program Files\stage\app\bin\rv.exe`
- [ ] Horus project directory accessible
- [ ] Sample database files present in `sample_db/`

---

## 🚀 Launch Test

### **Step 1: Launch Horus-RV**

```bash
# Double-click or run from command line
horus-rv.exe
```

**Expected Output:**
```
============================================================
🎬 Horus-RV Launcher
   Open RV with Horus MediaBrowser Integration
============================================================

🔍 Searching for Open RV...
✅ Found Open RV: D:\Program Files\stage\app\bin\rv.exe
🔍 Searching for Horus project...
✅ Found project: [project_path]
✅ Found integration script: rv_horus_integration.py
🔍 Checking Horus database...
✅ Horus database found

🚀 Launching Open RV with Horus MediaBrowser integration...
```

---

## 🎨 UI Widget Verification

### **Widget 1: Search & Media Library** (Left Panel)

**Location:** Left dock area

**Components to Verify:**
- [ ] Project dropdown (shows available projects)
- [ ] Search input field
- [ ] Directory tree navigation
- [ ] File type filters (Images, Videos, Sequences)
- [ ] Media grid with thumbnails
- [ ] Status indicators (approved, pending, in_review)

**Test Actions:**
1. Select a project from dropdown
2. Type in search field
3. Click on directory tree items
4. Toggle file type filters
5. Click on media grid items
6. Verify status colors

---

### **Widget 2: Comments & Annotations** (Center Panel)

**Location:** Center dock area

**Components to Verify:**
- [ ] Comments header with count
- [ ] Frame info display
- [ ] Paint button
- [ ] Annotations button
- [ ] Scrollable comments list
- [ ] Threaded replies (indented)
- [ ] User avatars/names
- [ ] Timestamp display
- [ ] Comment input field at bottom
- [ ] Comment button

**Test Actions:**
1. Scroll through comments list
2. Click Paint button (should activate RV paint mode)
3. Click Annotations button (should open popup)
4. Type in comment input field
5. Click Comment button
6. Verify threaded reply indentation

---

### **Widget 3: Timeline Playlist** (Right Panel)

**Location:** Right dock area

**Components to Verify:**
- [ ] Playlist dropdown/selector
- [ ] Create Playlist button
- [ ] Playlist items list
- [ ] Shot information display
- [ ] Version numbers
- [ ] Status indicators
- [ ] Duration display
- [ ] Load to RV button
- [ ] Drag & drop reordering

**Test Actions:**
1. Select a playlist from dropdown
2. Click Create Playlist button
3. View playlist items
4. Click Load to RV button
5. Try drag & drop reordering (if enabled)
6. Verify shot metadata display

---

## 🔍 Detailed UI Checks

### **Color Scheme Verification**

Check that colors match the design:
- Background: Dark gray (#3a3a3a)
- Text: Light gray (#e0e0e0)
- Highlights: Blue (#0078d7)
- Buttons: Medium gray (#4a4a4a)

### **Layout Verification**

- [ ] All three widgets are dockable
- [ ] Widgets can be resized
- [ ] Widgets can be moved to different dock areas
- [ ] Widgets can be undocked (floating)
- [ ] Widgets maintain state when docked/undocked

### **Responsiveness**

- [ ] UI updates when project is changed
- [ ] Media grid updates when filters are applied
- [ ] Comments scroll smoothly
- [ ] Playlist updates when items are added/removed

---

## 🐛 Common Issues & Solutions

### **Issue 1: RV Not Found**
**Symptom:** Error message "Open RV executable not found"  
**Solution:** Verify RV is installed at `D:\Program Files\stage\app\bin\rv.exe`

### **Issue 2: Integration Script Not Found**
**Symptom:** Error message "Integration script not found"  
**Solution:** Ensure `rv_horus_integration.py` is in the project directory

### **Issue 3: Database Not Found**
**Symptom:** Warning "Horus database not found"  
**Solution:** Check that `sample_db/` directory exists with JSON files

### **Issue 4: Widgets Not Appearing**
**Symptom:** Open RV launches but no Horus widgets visible  
**Solution:** Check RV menu → Windows → Show Horus widgets

---

## 📊 Test Results Template

```
Test Date: _______________
Tester: _______________
RV Version: _______________

Launch Test:          [ ] Pass  [ ] Fail
Widget 1 (Media):     [ ] Pass  [ ] Fail
Widget 2 (Comments):  [ ] Pass  [ ] Fail
Widget 3 (Playlist):  [ ] Pass  [ ] Fail
Color Scheme:         [ ] Pass  [ ] Fail
Layout/Docking:       [ ] Pass  [ ] Fail
Responsiveness:       [ ] Pass  [ ] Fail

Notes:
_________________________________
_________________________________
_________________________________
```

---

## 🎯 Next Steps After UI Verification

Once UI is verified and working:

1. **Document any UI issues** found during testing
2. **Take screenshots** of the three widgets
3. **Test workflow scenarios** (load media, add comments, create playlist)
4. **Provide feedback** on UI/UX improvements
5. **Plan configuration wizard** implementation

---

**Happy Testing!** 🚀

