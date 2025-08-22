---
type: "manual"
description: "Example description"
---
# MediaBrowserWidget UI Design Specification
## Based on xStudio Professional VFX UI Patterns

### Overview
This document defines the visual design and interaction patterns for the MediaBrowserWidget, following xStudio's proven professional VFX interface standards. The design emphasizes dark themes, efficient workflows, and familiar patterns that VFX artists expect.

### Design Principles (Inspired by xStudio)
1. **Dark Theme First**: Professional VFX tools use dark interfaces to reduce eye strain during long sessions
2. **Information Density**: Maximize useful information while maintaining readability
3. **Consistent Spacing**: Use 8px grid system for consistent visual rhythm
4. **Performance Indicators**: Always show loading states and progress feedback
5. **Keyboard-First**: All actions accessible via keyboard shortcuts
6. **Context Awareness**: UI adapts based on selected content and current workflow

### Color Palette (xStudio-Inspired Dark Theme)

#### Primary Colors
- **Background Dark**: `#1e1e1e` (Main background)
- **Background Medium**: `#2d2d2d` (Panel backgrounds)
- **Background Light**: `#3c3c3c` (Elevated surfaces)
- **Border**: `#4a4a4a` (Subtle borders and dividers)

#### Text Colors
- **Primary Text**: `#e0e0e0` (Main text, high contrast)
- **Secondary Text**: `#b0b0b0` (Labels, metadata)
- **Disabled Text**: `#707070` (Inactive elements)

#### Accent Colors
- **Primary Accent**: `#0078d4` (Selection, focus states)
- **Success**: `#107c10` (Successful operations)
- **Warning**: `#ff8c00` (Warnings, attention needed)
- **Error**: `#d13438` (Errors, critical states)

#### Media-Specific Colors
- **Image Indicator**: `#00bcf2` (Image file types)
- **Video Indicator**: `#9d4edd` (Video file types)
- **Sequence Indicator**: `#f72585` (Image sequences)

### Layout Specifications

#### Overall Widget Dimensions
- **Minimum Size**: 800x600px
- **Preferred Size**: 1200x800px
- **Maximum Size**: Unlimited (responsive)

#### Panel Layout (Three-Panel Design)
```
┌─────────────────────────────────────────────────────────────┐
│ Navigation Toolbar (40px height)                           │
├─────────────┬─────────────────────────────┬─────────────────┤
│ Search &    │        Media Grid           │ Comments &      │
│ Navigate    │                             │ Annotations     │
│ (250px)     │        (flexible)           │    (300px)      │
│             │                             │                 │
├─────────────┼─────────────────────────────┼─────────────────┤
│             │    Timeline Sequence        │                 │
│             │       (200px height)        │                 │
└─────────────┴─────────────────────────────┴─────────────────┘
```

#### Navigation Toolbar (40px height)
- **Back Button**: 32x32px, tooltip "Go back (Alt+Left)"
- **Forward Button**: 32x32px, tooltip "Go forward (Alt+Right)"
- **Up Button**: 32x32px, tooltip "Go up one directory (Alt+Up)"
- **Path Field**: Flexible width, editable path with autocomplete
- **View Mode Selector**: 120px width, dropdown with Grid/List/Detail options
- **Refresh Button**: 32x32px, tooltip "Refresh current directory (F5)"

#### Search & Navigate Panel (250px width)
- **Header**: "Search & Navigate" with search icon, 24px height
- **Search Field**: Full-width search input with filter options
  - Placeholder: "Search files and folders..."
  - Real-time filtering with 300ms debounce
- **Directory Tree**: Hierarchical file system navigation
  - Indent: 16px per level
  - Row height: 24px
  - Icons: 16x16px folder icons
  - Expand/collapse: Triangle indicators
- **Quick Filters**: Checkboxes for file types (Images, Videos, Sequences)

#### Media Grid Panel (Flexible width)
- **Header**: "Media Files" with controls, 32px height
  - Filter dropdown: 120px width
  - Thumbnail size slider: 100px width
  - View mode toggle: Grid/List/Detail
- **Grid Layout**:
  - Thumbnail size: 128x128px (default), scalable 64-256px
  - Grid spacing: 8px between items
  - Item padding: 4px
  - Label height: 20px below thumbnail
  - Selection indicators: Blue border for selected items

#### Comments & Annotations Panel (300px width)
- **Header**: "Comments & Annotations" with comment icon, 24px height
- **Active Annotations**: List of annotations for current frame/selection
- **Comment Input**: Text area for adding new comments
- **Annotation Tools**: Drawing tools (rectangle, circle, arrow, text)
- **Collaboration**: User avatars and real-time updates
- **Export Options**: Save annotations to JSON/XML/FBX

#### Timeline Sequence Panel (200px height)
- **Header**: "Timeline" with playback controls, 32px height
  - Play/Pause button
  - Frame counter and timecode display
  - Playback speed control
- **Timeline Track**: Visual representation of media sequence
  - Frame thumbnails at key intervals
  - Current frame indicator (red playhead)
  - In/Out point markers
  - Annotation markers on timeline
- **Transport Controls**: Previous/Next frame, Go to frame input

### Typography

#### Font Family
- **Primary**: "Inter", "Segoe UI", "Roboto", sans-serif
- **Monospace**: "Consolas", "Monaco", "Courier New", monospace

#### Font Sizes
- **Large Headers**: 14px, weight 600
- **Small Headers**: 12px, weight 600
- **Body Text**: 11px, weight 400
- **Small Text**: 10px, weight 400
- **Monospace**: 10px (for technical data)

### Interactive Elements

#### Buttons
- **Primary Button**: Blue background (#0078d4), white text
- **Secondary Button**: Transparent background, border, primary text
- **Icon Button**: 32x32px, hover state with subtle background
- **Hover State**: 10% lighter background
- **Active State**: 10% darker background
- **Focus State**: 2px blue outline

#### Input Fields
- **Background**: #2d2d2d
- **Border**: 1px solid #4a4a4a
- **Focus Border**: 2px solid #0078d4
- **Padding**: 8px horizontal, 6px vertical
- **Border Radius**: 4px

#### Thumbnails
- **Default Size**: 128x128px
- **Border**: 1px solid #4a4a4a
- **Selected Border**: 2px solid #0078d4
- **Hover Effect**: Subtle glow, scale 1.02
- **Loading State**: Skeleton animation
- **Error State**: Gray background with error icon

### Responsive Behavior

#### Panel Resizing
- **Minimum Directory Panel**: 200px
- **Minimum Properties Panel**: 250px
- **Grid Panel**: Takes remaining space, minimum 400px
- **Splitter Width**: 4px with hover state

#### Thumbnail Grid Adaptation
- **Auto-fit**: Columns adjust based on available width
- **Minimum Columns**: 2
- **Maximum Columns**: 8
- **Responsive Breakpoints**:
  - < 800px: Hide properties panel
  - < 600px: Collapse directory tree to overlay

### Animation and Transitions

#### Micro-interactions
- **Hover Transitions**: 150ms ease-out
- **Selection Changes**: 200ms ease-in-out
- **Panel Resize**: 300ms ease-in-out
- **Loading States**: Smooth skeleton animations

#### Performance Considerations
- **Thumbnail Loading**: Progressive loading with fade-in
- **Scroll Performance**: Virtual scrolling for large directories
- **Debounced Search**: 300ms delay for search input

### Accessibility

#### Keyboard Navigation
- **Tab Order**: Logical flow through all interactive elements
- **Arrow Keys**: Navigate grid items and tree nodes
- **Enter/Space**: Activate selected items
- **Escape**: Cancel operations, close dialogs

#### Screen Reader Support
- **ARIA Labels**: All interactive elements properly labeled
- **Live Regions**: Status updates announced
- **Semantic HTML**: Proper heading hierarchy and landmarks

### Integration with Open RV

#### Docking Behavior
- **Dock Position**: Right panel in Open RV interface
- **Minimum Docked Size**: 400x300px
- **Floating Window**: Resizable, remembers position
- **Tab Integration**: Appears as "Media Browser" tab

#### RV-Specific Features
- **Load in RV**: Double-click or Enter loads media in current session
- **Add to Playlist**: Drag-and-drop or Ctrl+Shift+L
- **Sequence Detection**: Automatic frame range detection
- **Color Space**: Integration with RV's color management

This specification ensures the MediaBrowserWidget provides a professional, efficient, and familiar interface that VFX artists will find intuitive and powerful.
