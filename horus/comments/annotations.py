"""
Horus Annotations
================

Annotation tools, popup window, and Open RV integration.
"""

from horus.utils.globals import comments_dock


def create_annotations_popup():
    """Create the annotations popup window."""
    try:
        from PySide2.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                       QPushButton, QTextEdit, QFrame, QGroupBox,
                                       QCheckBox, QComboBox, QSpinBox)
        from PySide2.QtCore import Qt

        # Create popup dialog
        popup = QDialog()
        popup.setWindowTitle("Annotations Manager")
        popup.setModal(False)
        popup.resize(400, 500)
        popup.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout(popup)
        layout.setSpacing(10)

        # Header
        header_label = QLabel("Open RV Annotations")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #e0e0e0;")
        layout.addWidget(header_label)

        # Current frame info
        frame_info = QLabel("Frame: 1047 | Time: 00:43:15")
        frame_info.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(frame_info)

        # Annotation tools group
        tools_group = QGroupBox("Drawing Tools")
        tools_layout = QVBoxLayout(tools_group)

        # Tool buttons
        tools_button_layout = QHBoxLayout()
        
        paint_btn = QPushButton("🎨 Paint Mode (F10)")
        paint_btn.clicked.connect(on_open_rv_paint)
        tools_button_layout.addWidget(paint_btn)

        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.clicked.connect(lambda: on_clear_annotations(popup))
        tools_button_layout.addWidget(clear_btn)

        tools_layout.addLayout(tools_button_layout)

        # Annotation settings
        settings_layout = QHBoxLayout()
        
        color_label = QLabel("Color:")
        settings_layout.addWidget(color_label)
        
        color_combo = QComboBox()
        color_combo.addItems(["Red", "Green", "Blue", "Yellow", "White"])
        settings_layout.addWidget(color_combo)
        
        size_label = QLabel("Size:")
        settings_layout.addWidget(size_label)
        
        size_spin = QSpinBox()
        size_spin.setRange(1, 20)
        size_spin.setValue(3)
        settings_layout.addWidget(size_spin)

        settings_layout.addStretch()
        tools_layout.addLayout(settings_layout)

        layout.addWidget(tools_group)

        # Annotation list group
        list_group = QGroupBox("Current Annotations")
        list_layout = QVBoxLayout(list_group)

        # Sample annotations
        annotations_text = QTextEdit()
        annotations_text.setMaximumHeight(150)
        annotations_text.setPlainText("""Frame 1047: Eye line adjustment needed
Frame 1052: Shadow correction applied
Frame 1089: Particle density increased""")
        annotations_text.setReadOnly(True)
        list_layout.addWidget(annotations_text)

        layout.addWidget(list_group)

        # Export/Save group
        export_group = QGroupBox("Export & Save")
        export_layout = QVBoxLayout(export_group)

        export_button_layout = QHBoxLayout()
        
        export_btn = QPushButton("📤 Export Annotations")
        export_btn.clicked.connect(on_export_rv_annotations)
        export_button_layout.addWidget(export_btn)

        save_btn = QPushButton("💾 Save to Database")
        save_btn.clicked.connect(lambda: on_save_annotations(popup))
        export_button_layout.addWidget(save_btn)

        export_layout.addLayout(export_button_layout)

        # Export options
        options_layout = QHBoxLayout()
        
        include_frames_cb = QCheckBox("Include frame numbers")
        include_frames_cb.setChecked(True)
        options_layout.addWidget(include_frames_cb)
        
        include_timestamps_cb = QCheckBox("Include timestamps")
        include_timestamps_cb.setChecked(True)
        options_layout.addWidget(include_timestamps_cb)

        export_layout.addLayout(options_layout)
        layout.addWidget(export_group)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(popup.close)
        layout.addWidget(close_btn)

        # Apply styling
        from horus.ui_components.styling import apply_rv_styling
        apply_rv_styling(popup)

        return popup

    except Exception as e:
        print(f"Error creating annotations popup: {e}")
        return None


def on_open_rv_paint():
    """Open Open RV's built-in paint/annotation tools."""
    try:
        # Try to access Open RV's paint mode
        import rv.commands as rvc
        
        # Switch to paint mode (F10 equivalent)
        try:
            # Try different methods to activate paint mode
            rvc.setViewNode("defaultPaint")
            print("✅ Activated Open RV paint mode")
        except:
            try:
                # Alternative method
                rvc.sendInternalEvent("key-down--F10", "")
                print("✅ Sent F10 key event for paint mode")
            except:
                try:
                    # Another alternative
                    rvc.sendInternalEvent("paint-mode", "")
                    print("✅ Sent paint mode event")
                except:
                    print("⚠️  Could not activate paint mode - please press F10 manually")
        
        # Additional paint mode setup if needed
        try:
            # Set paint brush properties
            rvc.setFloatProperty("defaultPaint.brush.size", [3.0])
            rvc.setFloatProperty("defaultPaint.brush.opacity", [1.0])
            print("✅ Paint brush configured")
        except:
            pass
            
    except Exception as e:
        print(f"❌ Error opening RV paint mode: {e}")
        print("💡 Tip: Press F10 to manually enter paint mode")


def on_export_rv_annotations():
    """Export annotations from Open RV's annotation system."""
    try:
        import rv.commands as rvc
        import json
        import os
        from datetime import datetime
        
        # Try to get annotation data from Open RV
        try:
            # Get current session annotations
            annotations = []
            
            # Try to access paint/annotation nodes
            paint_nodes = rvc.nodesOfType("RVPaint")
            for node in paint_nodes:
                try:
                    # Get paint strokes/annotations from this node
                    strokes = rvc.getProperty(f"{node}.paint.strokes")
                    if strokes:
                        annotations.append({
                            "node": node,
                            "strokes": len(strokes[0]) if strokes and len(strokes) > 0 else 0,
                            "frame": rvc.frame()
                        })
                except:
                    pass
            
            # Create export data
            export_data = {
                "export_time": datetime.now().isoformat(),
                "current_frame": rvc.frame(),
                "annotations": annotations,
                "session_info": {
                    "sources": rvc.sources(),
                    "fps": rvc.fps()
                }
            }
            
            # Save to file
            export_dir = "cache/annotations"
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = os.path.join(export_dir, f"rv_annotations_{timestamp}.json")
            
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Annotations exported to: {export_file}")
            print(f"   Found {len(annotations)} annotation nodes")
            
        except Exception as e:
            print(f"⚠️  Could not access RV annotation data: {e}")
            
            # Fallback: Create sample export
            sample_data = {
                "export_time": datetime.now().isoformat(),
                "current_frame": get_current_frame(),
                "annotations": [
                    {"frame": 1047, "type": "paint", "description": "Eye line adjustment"},
                    {"frame": 1052, "type": "paint", "description": "Shadow correction"},
                    {"frame": 1089, "type": "paint", "description": "Particle density"}
                ],
                "note": "Sample annotation data - RV integration pending"
            }
            
            export_dir = "cache/annotations"
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = os.path.join(export_dir, f"sample_annotations_{timestamp}.json")
            
            with open(export_file, 'w') as f:
                json.dump(sample_data, f, indent=2)
            
            print(f"✅ Sample annotations exported to: {export_file}")
            
    except Exception as e:
        print(f"❌ Error exporting annotations: {e}")


def on_clear_annotations(popup=None):
    """Handle clearing all annotations."""
    try:
        import rv.commands as rvc
        
        # Try to clear Open RV annotations
        try:
            paint_nodes = rvc.nodesOfType("RVPaint")
            for node in paint_nodes:
                try:
                    # Clear paint strokes for this node
                    rvc.setProperty(f"{node}.paint.strokes", [])
                    print(f"✅ Cleared annotations for node: {node}")
                except:
                    pass
            
            if paint_nodes:
                print(f"✅ Cleared annotations from {len(paint_nodes)} paint nodes")
            else:
                print("ℹ️  No paint nodes found to clear")
                
        except Exception as e:
            print(f"⚠️  Could not clear RV annotations: {e}")
            print("💡 Tip: Use Open RV's clear annotation tools manually")
            
    except Exception as e:
        print(f"❌ Error clearing annotations: {e}")


def on_save_annotations(popup=None):
    """Handle saving annotations to database."""
    try:
        # This would integrate with the Horus database system
        print("💾 Saving annotations to Horus database...")
        
        # For now, just export to JSON as a backup
        on_export_rv_annotations()
        
        print("✅ Annotations saved (exported to JSON)")
        
    except Exception as e:
        print(f"❌ Error saving annotations: {e}")


def get_current_frame():
    """Get current frame from Open RV."""
    try:
        import rv.commands as rvc
        return rvc.frame()
    except:
        return 1047  # Default frame for demo


def update_frame_info():
    """Update frame information display."""
    global comments_dock

    try:
        comments_widget = comments_dock.widget() if comments_dock else None
        if not comments_widget:
            return

        current_frame = get_current_frame()
        # TODO: Get actual timecode from Open RV
        timecode = "00:43:15"

        frame_info_text = f"Frame: {current_frame} | Time: {timecode}"
        comments_widget.frame_info_label.setText(frame_info_text)

    except Exception as e:
        print(f"Error updating frame info: {e}")
