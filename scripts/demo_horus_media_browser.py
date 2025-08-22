#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo: Horus-Integrated MediaBrowser
===================================

Demonstration of the MediaBrowserWidget with Horus data integration.
Shows how our Open RV MediaBrowser can display media data from the
Horus application's JSON database.

Usage:
    python scripts/demo_horus_media_browser.py

Features demonstrated:
- Connection to Horus's JSON database
- Project selection and media loading
- Horus-specific filters (approval status, tasks, authors, versions)
- Media grid display with Horus metadata
- Directory tree with project structure
- Annotations from Horus database
- Real-time data refresh
"""

import sys
import os
from pathlib import Path

# Add the media browser package to Python path
project_root = Path(__file__).parent.parent
media_browser_path = project_root / "src" / "packages" / "media_browser" / "python"
sys.path.insert(0, str(media_browser_path))

from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox
from PySide2.QtCore import Qt

# Import our Horus-integrated MediaBrowser
from media_browser.horus_media_browser_widget import HorusMediaBrowserWidget
from media_browser.horus_data_connector import get_horus_connector


class HorusMediaBrowserDemo(QMainWindow):
    """Demo application for Horus-integrated MediaBrowser."""
    
    def __init__(self):
        """Initialize the demo application."""
        super().__init__()
        
        self.setWindowTitle("Horus MediaBrowser Integration Demo")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create Horus-integrated MediaBrowser
        self.media_browser = HorusMediaBrowserWidget()
        layout.addWidget(self.media_browser)
        
        # Setup connections
        self.setup_connections()
        
        # Apply styling
        self.apply_demo_styling()
        
        # Show initial status
        self.show_initial_status()
    
    def setup_connections(self):
        """Setup signal connections for the demo."""
        # Connect to Horus-specific signals
        self.media_browser.projectChanged.connect(self.on_project_changed)
        self.media_browser.horusDataLoaded.connect(self.on_horus_data_loaded)
        self.media_browser.horusError.connect(self.on_horus_error)
        
        # Connect to base MediaBrowser signals
        self.media_browser.media_selected.connect(self.on_media_selected)
    
    def apply_demo_styling(self):
        """Apply demo-specific styling."""
        # Set dark theme similar to professional video applications
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            QWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QComboBox {
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
                background-color: #3a3a3a;
            }
            QComboBox:hover {
                border-color: #0078d4;
            }
            QPushButton {
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                background-color: #3a3a3a;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #0078d4;
            }
            QPushButton:pressed {
                background-color: #0078d4;
            }
        """)
    
    def show_initial_status(self):
        """Show initial status and information about Horus connection."""
        connector = get_horus_connector()
        stats = connector.get_stats()
        
        if stats['available']:
            # Show success message with statistics
            status_msg = f"""
🎉 Horus MediaBrowser Integration Demo

✅ Successfully connected to Horus database!

📊 Horus Database Statistics:
• Projects: {stats['projects_count']}
• Media Records: {stats['media_records_count']}
• Tasks: {stats['tasks_count']}
• Annotations: {stats['annotations_count']}

🎯 Features Available:
• Project selection and media loading
• Horus-specific filters (approval status, tasks, authors, versions)
• Media grid with Horus metadata
• Directory tree with project structure
• Annotations from Horus database
• Real-time data refresh

📋 Instructions:
1. Select a project from the dropdown
2. Use filters to refine media display
3. Click on media items to view details
4. Double-click to select for Open RV loading

Data Path: {stats['data_path']}
"""
            print(status_msg)
            self.statusBar().showMessage(f"Horus connected - {stats['projects_count']} projects, {stats['media_records_count']} media files")
        else:
            error_msg = """
⚠️  Horus Database Not Available

The Horus database could not be found or accessed.
Please ensure:
1. Horus database is available at: C:\\Users\\ADMIN\\Documents\\dev\\Montu
2. JSON database files exist in: data\\json_db\\
3. Files are readable and properly formatted

The MediaBrowser will work in filesystem-only mode.
"""
            print(error_msg)
            self.statusBar().showMessage("Horus database not available - filesystem mode only")
            
            # Show message box
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Horus Database Not Available")
            msg_box.setText("The Horus database could not be found.")
            msg_box.setDetailedText(error_msg)
            msg_box.exec_()
    
    def on_project_changed(self, project_id: str):
        """Handle project change."""
        print(f"📁 Project changed to: {project_id}")
        self.statusBar().showMessage(f"Loading project: {project_id}")
    
    def on_horus_data_loaded(self, item_count: int):
        """Handle Horus data loaded."""
        print(f"📊 Loaded {item_count} media items from Horus")
        self.statusBar().showMessage(f"Loaded {item_count} media items")
    
    def on_horus_error(self, error_message: str):
        """Handle Horus errors."""
        print(f"❌ Horus error: {error_message}")
        self.statusBar().showMessage(f"Error: {error_message}")
    
    def on_media_selected(self, file_path: str, metadata: dict):
        """Handle media selection."""
        file_name = os.path.basename(file_path)
        print(f"🎬 Selected media: {file_name}")
        
        # Show metadata in status bar
        if metadata:
            width = metadata.get('width', 0)
            height = metadata.get('height', 0)
            if width and height:
                self.statusBar().showMessage(f"Selected: {file_name} ({width}x{height})")
            else:
                self.statusBar().showMessage(f"Selected: {file_name}")
        else:
            self.statusBar().showMessage(f"Selected: {file_name}")
    
    def closeEvent(self, event):
        """Handle application close."""
        print("👋 Closing Horus MediaBrowser Demo")
        event.accept()


def main():
    """Main entry point for the demo."""
    print("🎬 Starting Horus MediaBrowser Integration Demo...")
    print("=" * 60)
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Horus MediaBrowser Demo")
    app.setApplicationVersion("1.0.0")
    
    # Set application style
    app.setStyle('Fusion')
    
    try:
        # Create and show demo window
        demo = HorusMediaBrowserDemo()
        demo.show()
        
        print("✅ Demo started successfully!")
        print("🎯 The MediaBrowser is now displaying media from Horus's database")
        print("📋 Select a project to see media files with Horus metadata")
        print("=" * 60)
        
        # Run application
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Failed to start demo: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
