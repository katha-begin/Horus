"""
Horus Search Handlers
====================

Event handlers for search panel interactions and filtering.
"""

from horus.utils.globals import search_dock, current_project_id, horus_connector, media_grid_dock
from horus.media_browser.media_grid_panel import populate_media_grid
from horus.media_browser.table_utils import update_media_table, update_shot_filter


def on_project_changed():
    """Handle project selection change."""
    global current_project_id, horus_connector, search_dock, media_grid_dock

    try:
        search_widget = search_dock.widget() if search_dock else None
        if not search_widget:
            return

        project_id = search_widget.project_combo.currentText()
        
        if project_id == "Select Project...":
            return
        
        current_project_id = project_id
        horus_connector.set_current_project(project_id)

        print(f"Loading project: {project_id}")

        # Load media
        media_items = horus_connector.get_media_for_project(project_id)
        
        # Update grid
        populate_media_grid(media_items)
        
        # Update media table
        update_media_table(project_id, media_items)

        # Update shot filter options
        update_shot_filter(media_items)
        
        # Update status
        media_grid_widget = media_grid_dock.widget() if media_grid_dock else None
        if media_grid_widget:
            media_grid_widget.path_label.setText(f"Project: {project_id}")
            media_grid_widget.status_label.setText(f"Loaded {len(media_items)} items")
        
        print(f"Loaded {len(media_items)} media items")
        
    except Exception as e:
        print(f"Error loading project: {e}")


def apply_filters():
    """Apply filters to the media table."""
    global search_dock, current_project_id, horus_connector

    try:
        search_widget = search_dock.widget() if search_dock else None
        if not search_widget or not current_project_id or not horus_connector:
            return

        # Get filter values
        department = search_widget.dept_combo.currentText()
        episode = search_widget.episode_combo.currentText()
        sequence = search_widget.sequence_combo.currentText()
        shot = search_widget.shot_combo.currentText()
        search_text = search_widget.search_text.text().strip().lower()

        print(f"Applying filters - Dept: {department}, Ep: {episode}, Seq: {sequence}, Shot: {shot}, Search: '{search_text}'")

        # Get all media for project
        all_media = horus_connector.get_media_for_project(current_project_id)
        
        # Apply filters
        filtered_media = []
        for item in all_media:
            # Department filter
            if department != "All":
                item_dept = item.get('department', '').title()
                if item_dept != department:
                    continue
            
            # Episode filter
            if episode != "All":
                item_episode = item.get('episode', '').upper()
                if item_episode != episode:
                    continue
            
            # Sequence filter
            if sequence != "All":
                item_sequence = item.get('sequence', '').upper()
                if item_sequence != sequence:
                    continue
            
            # Shot filter
            if shot != "All":
                item_shot = item.get('shot', '').upper()
                if item_shot != shot:
                    continue
            
            # Text search filter
            if search_text:
                searchable_text = f"{item.get('file_name', '')} {item.get('task_entity', '')} {item.get('version', '')}".lower()
                if search_text not in searchable_text:
                    continue
            
            filtered_media.append(item)

        # Update displays
        populate_media_grid(filtered_media)
        update_media_table(current_project_id, filtered_media)

        # Update status
        media_grid_widget = media_grid_dock.widget() if media_grid_dock else None
        if media_grid_widget:
            media_grid_widget.status_label.setText(f"Showing {len(filtered_media)} of {len(all_media)} items")

        print(f"Filtered to {len(filtered_media)} items")

    except Exception as e:
        print(f"Error applying filters: {e}")


def on_scale_changed():
    """Handle scale change for table size."""
    global search_dock

    try:
        search_widget = search_dock.widget() if search_dock else None
        if not search_widget:
            return

        scale = search_widget.scale_combo.currentText()
        table = search_widget.media_table

        # Adjust row height based on scale
        scale_heights = {
            "Small": 60,
            "Medium": 80,
            "Large": 120
        }
        
        row_height = scale_heights.get(scale, 60)
        
        # Update all existing rows
        for row in range(table.rowCount()):
            table.setRowHeight(row, row_height)

        # Update thumbnail column width
        scale_widths = {
            "Small": 80,
            "Medium": 100,
            "Large": 140
        }
        
        thumbnail_width = scale_widths.get(scale, 80)
        table.setColumnWidth(0, thumbnail_width)

        print(f"Changed scale to {scale} (height: {row_height}px, width: {thumbnail_width}px)")

    except Exception as e:
        print(f"Error changing scale: {e}")


def on_media_table_double_click(item):
    """Handle double-click on media table item."""
    try:
        search_widget = search_dock.widget() if search_dock else None
        if not search_widget:
            return

        table = search_widget.media_table
        row = item.row()

        # Get file path from the row data
        file_path_item = table.item(row, 2)  # Name column stores file path in user data
        if file_path_item:
            file_path = file_path_item.data(Qt.UserRole)
            if file_path:
                try:
                    import rv.commands as rvc
                    rvc.addSource(file_path)
                    print(f"Loaded in RV: {file_path}")
                except Exception as e:
                    print(f"Error loading in RV: {e}")
            else:
                print("No file path available")

    except Exception as e:
        print(f"Error handling double-click: {e}")
