"""
Horus Table Utilities
====================

Utilities for managing the media table display and data.
"""

from horus.utils.globals import search_dock


def update_media_table(project_id, media_items):
    """Update media table with thumbnails."""
    global search_dock

    try:
        search_widget = search_dock.widget() if search_dock else None
        if not search_widget:
            return

        table = search_widget.media_table
        
        # Clear existing rows
        table.setRowCount(0)
        
        if not media_items:
            return

        # Set row count
        table.setRowCount(len(media_items))

        # Get current scale for row height
        scale = search_widget.scale_combo.currentText()
        scale_heights = {"Small": 60, "Medium": 80, "Large": 120}
        row_height = scale_heights.get(scale, 60)

        # Populate table
        for row, item in enumerate(media_items):
            # Set row height
            table.setRowHeight(row, row_height)

            # Thumbnail column
            thumbnail_item = create_thumbnail_table_item(item, row_height)
            table.setItem(row, 0, thumbnail_item)

            # Task Entity column
            task_entity = item.get('task_entity', item.get('shot', 'Unknown'))
            task_item = QTableWidgetItem(task_entity)
            task_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 1, task_item)

            # Name column (store file path in user data)
            file_name = item.get('file_name', 'Unknown')
            name_item = QTableWidgetItem(file_name)
            name_item.setData(Qt.UserRole, item.get('file_path', ''))
            table.setItem(row, 2, name_item)

            # Version column
            version = item.get('version', 'v001')
            version_item = QTableWidgetItem(version)
            version_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 3, version_item)

            # Department column
            department = item.get('department', 'Unknown').title()
            dept_item = QTableWidgetItem(department)
            dept_item.setTextAlignment(Qt.AlignCenter)
            
            # Color code by department
            dept_colors = {
                'Animation': '#1f4e79',
                'Lighting': '#d68910', 
                'Compositing': '#196f3d',
                'Fx': '#6c3483',
                'Modeling': '#a93226'
            }
            dept_color = dept_colors.get(department, '#888888')
            dept_item.setBackground(QColor(dept_color))
            dept_item.setForeground(QColor('#ffffff'))
            
            table.setItem(row, 4, dept_item)

            # Created date column
            created_date = item.get('created_date', 'Unknown')
            if created_date and created_date != 'Unknown':
                try:
                    from datetime import datetime
                    # Parse ISO format date
                    dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_date = created_date
            else:
                formatted_date = 'Unknown'
            
            date_item = QTableWidgetItem(formatted_date)
            date_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 5, date_item)

        print(f"✅ Updated media table with {len(media_items)} items")

    except Exception as e:
        print(f"❌ Error updating media table: {e}")
        import traceback
        traceback.print_exc()


def create_thumbnail_table_item(media_item, row_height):
    """Create a table item with thumbnail."""
    try:
        from PySide2.QtWidgets import QTableWidgetItem, QLabel
        from PySide2.QtCore import Qt
        from PySide2.QtGui import QPixmap

        # Create table item
        item = QTableWidgetItem()
        
        # Try to load thumbnail
        thumbnail_path = media_item.get('thumbnail_path', '')
        if thumbnail_path:
            try:
                pixmap = QPixmap(thumbnail_path)
                if not pixmap.isNull():
                    # Scale pixmap to fit cell
                    thumbnail_size = int(row_height * 0.8)  # 80% of row height
                    scaled_pixmap = pixmap.scaled(
                        thumbnail_size, thumbnail_size, 
                        Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    
                    # Create a label to hold the pixmap
                    label = QLabel()
                    label.setPixmap(scaled_pixmap)
                    label.setAlignment(Qt.AlignCenter)
                    label.setStyleSheet("background-color: transparent;")
                    
                    # Set the label as the item's widget (this won't work directly)
                    # Instead, we'll set the icon
                    item.setData(Qt.DecorationRole, scaled_pixmap)
                else:
                    item.setText("📁")
            except:
                item.setText("📁")
        else:
            item.setText("📁")

        item.setTextAlignment(Qt.AlignCenter)
        return item

    except Exception as e:
        print(f"Error creating thumbnail item: {e}")
        from PySide2.QtWidgets import QTableWidgetItem
        item = QTableWidgetItem("📁")
        item.setTextAlignment(Qt.AlignCenter)
        return item


def update_shot_filter(media_items):
    """Update shot filter dropdown with available shots."""
    global search_dock

    try:
        search_widget = search_dock.widget() if search_dock else None
        if not search_widget:
            return

        shot_combo = search_widget.shot_combo
        
        # Get unique shots
        shots = set()
        for item in media_items:
            shot = item.get('shot', '')
            if shot:
                shots.add(shot.upper())

        # Update combo box
        current_selection = shot_combo.currentText()
        shot_combo.clear()
        shot_combo.addItem("All")
        
        for shot in sorted(shots):
            shot_combo.addItem(shot)

        # Restore selection if it still exists
        if current_selection in [shot_combo.itemText(i) for i in range(shot_combo.count())]:
            shot_combo.setCurrentText(current_selection)

        print(f"✅ Updated shot filter with {len(shots)} shots")

    except Exception as e:
        print(f"❌ Error updating shot filter: {e}")


# Import required Qt classes at module level
try:
    from PySide2.QtWidgets import QTableWidgetItem
    from PySide2.QtCore import Qt
    from PySide2.QtGui import QColor
except ImportError:
    print("Warning: PySide2 not available for table utilities")
